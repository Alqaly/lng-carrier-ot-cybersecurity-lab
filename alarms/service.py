import asyncio, json, os, sqlite3, time
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
import uvicorn

DB=os.getenv('ALARM_DB','/data/alarms.sqlite')
CATALOG_PATH=os.getenv('ALARM_CATALOG','/app/catalog.json')
SOURCES={
 'cargo':'http://cargo-plant:8100/state',
 'pms':'http://pms-plant:8200/state',
 'propulsion':'http://propulsion-plant:8300/state',
}
CATALOG={a['id']:a for a in json.loads(Path(CATALOG_PATH).read_text())['alarms']}
PRIORITY_ORDER={'CRITICAL':0,'HIGH':1,'MEDIUM':2,'LOW':3}
app=FastAPI(title='Learning Alarm Chronicle')

Path(DB).parent.mkdir(parents=True,exist_ok=True)
con=sqlite3.connect(DB,check_same_thread=False)
con.execute('create table if not exists alarm_state (id text primary key, active integer, acked integer, since real, last_change real, priority text, message text, domain text)')
con.execute('create table if not exists chronicle (ts real, id text, transition text, priority text, message text, domain text)')
con.commit()

pending_on={}
pending_off={}
last_poll={'ts':0.0,'sources':{}}

def compare(actual, op, expected=None):
    if op=='is_true': return bool(actual)
    if op=='is_false': return not bool(actual)
    if actual is None: return False
    a=float(actual)
    if op=='lt': return a<float(expected)
    if op=='le': return a<=float(expected)
    if op=='gt': return a>float(expected)
    if op=='ge': return a>=float(expected)
    if op=='eq': return a==float(expected)
    raise ValueError(op)

def eval_conditions(conditions,state,mode='all'):
    values=[compare(state.get(c['field']),c['op'],c.get('value')) for c in conditions]
    if mode=='all': return all(values)
    if mode=='any': return any(values)
    raise ValueError(f'unsupported condition logic: {mode}')

def current_active(aid):
    row=con.execute('select active from alarm_state where id=?',(aid,)).fetchone()
    return bool(row[0]) if row else False

def wanted_state(alarm,state):
    active=current_active(alarm['id'])
    # Hysteresis / distinct return-to-normal threshold: while active, stay
    # active until every explicit clear condition is satisfied.
    if active and alarm.get('clear_conditions'):
        return not eval_conditions(
            alarm['clear_conditions'],
            state,
            alarm.get('clear_logic','all')
        )
    return eval_conditions(
        alarm['conditions'],
        state,
        alarm.get('condition_logic','all')
    )

def write_transition(aid, active):
    a=CATALOG[aid]; domain=a['domain']; priority=a['priority']; message=a['title']; now=time.time()
    row=con.execute('select active,acked,since from alarm_state where id=?',(aid,)).fetchone()
    if row is None:
        con.execute(
            'insert into alarm_state values (?,?,?,?,?,?,?,?)',
            (aid,int(active),0 if active else 1,now if active else 0,now,priority,message,domain)
        )
        if active:
            con.execute('insert into chronicle values (?,?,?,?,?,?)',(now,aid,'ACTIVE_UNACK',priority,message,domain))
    else:
        was,acked,since=row
        if bool(was)!=bool(active):
            if active:
                con.execute('update alarm_state set active=1,acked=0,since=?,last_change=? where id=?',(now,now,aid))
                trans='ACTIVE_UNACK'
            else:
                con.execute('update alarm_state set active=0,last_change=? where id=?',(now,aid))
                trans='RETURN_TO_NORMAL_ACK' if acked else 'RETURN_TO_NORMAL_UNACK'
            con.execute('insert into chronicle values (?,?,?,?,?,?)',(now,aid,trans,priority,message,domain))
    con.commit()

def debounce(aid,wanted):
    now=time.monotonic(); a=CATALOG[aid]; active=current_active(aid)
    if wanted==active:
        pending_on.pop(aid,None); pending_off.pop(aid,None); return active
    if wanted:
        pending_off.pop(aid,None)
        start=pending_on.setdefault(aid,now)
        if now-start >= float(a.get('activation_delay_s',0)): return True
    else:
        pending_on.pop(aid,None)
        start=pending_off.setdefault(aid,now)
        if now-start >= float(a.get('clear_delay_s',0)): return False
    return active

async def poll():
    async with httpx.AsyncClient(timeout=1.0) as c:
        while True:
            states={}
            health={}
            for domain,url in SOURCES.items():
                try:
                    response=await c.get(url)
                    s=response.json()
                    ok=bool(s.get('ready'))
                    states[domain]=dict(s) if ok else {}
                    states[domain]['__stale__']=not ok
                    health[domain]={'ok':ok,'http_status':response.status_code}
                except Exception as e:
                    states[domain]={'__stale__':True}
                    health[domain]={'ok':False,'error':repr(e)}
            last_poll.update({'ts':time.time(),'sources':health})

            for aid,a in CATALOG.items():
                wanted=wanted_state(a,states.get(a['domain'],{'__stale__':True}))
                debounced=debounce(aid,wanted)
                if debounced != current_active(aid):
                    write_transition(aid,debounced)
                elif con.execute('select 1 from alarm_state where id=?',(aid,)).fetchone() is None:
                    write_transition(aid,False)
            await asyncio.sleep(0.25)

@app.on_event('startup')
async def start():
    asyncio.create_task(poll())

@app.get('/health')
def health():
    return {'ready':True,'poll':last_poll}

@app.get('/catalog')
def catalog():
    return sorted(CATALOG.values(),key=lambda a:(PRIORITY_ORDER.get(a['priority'],9),a['domain'],a['id']))

@app.get('/alarms')
def alarms():
    rows=con.execute('select id,active,acked,since,last_change,priority,message,domain from alarm_state').fetchall()
    cols=['id','active','acked','since','last_change','priority','message','domain']
    out=[]
    for r in rows:
        item=dict(zip(cols,r))
        item['rationalization']=CATALOG[item['id']]
        item['priority_rank']=PRIORITY_ORDER.get(item['priority'],9)
        out.append(item)
    return sorted(out,key=lambda x:(not bool(x['active']),x['priority_rank'],x['domain'],x['id']))

@app.get('/history')
def history(limit:int=200):
    rows=con.execute(
        'select ts,id,transition,priority,message,domain from chronicle order by ts desc limit ?',
        (min(max(limit,1),2000),)
    ).fetchall()
    cols=['ts','id','transition','priority','message','domain']
    return [dict(zip(cols,r)) for r in rows]

@app.get('/metrics')
def metrics():
    now=time.time()
    active=con.execute('select priority,acked from alarm_state where active=1').fetchall()
    transitions_10m=con.execute('select count(*) from chronicle where ts>=?',(now-600,)).fetchone()[0]
    return {
        'active_total':len(active),
        'unacknowledged_total':sum(1 for _,acked in active if not acked),
        'active_by_priority':{
            p:sum(1 for priority,_ in active if priority==p)
            for p in ['CRITICAL','HIGH','MEDIUM','LOW']
        },
        'transitions_last_10m':transitions_10m,
        'flood_warning':transitions_10m>=20,
    }

@app.post('/ack/{alarm_id}')
def ack(alarm_id:str):
    row=con.execute('select active,acked,priority,message,domain from alarm_state where id=?',(alarm_id,)).fetchone()
    if not row:
        raise HTTPException(404,'alarm not found')
    active,acked,priority,message,domain=row
    if not acked:
        now=time.time()
        con.execute('update alarm_state set acked=1,last_change=? where id=?',(now,alarm_id))
        con.execute('insert into chronicle values (?,?,?,?,?,?)',(now,alarm_id,'ACKNOWLEDGED',priority,message,domain))
        con.commit()
    return {'ok':True,'id':alarm_id}

if __name__=='__main__':
    uvicorn.run(app,host='0.0.0.0',port=8400)
