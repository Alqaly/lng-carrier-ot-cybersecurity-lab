import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app=FastAPI(title='OT Learning Portal')
app.mount('/static',StaticFiles(directory='/app/static'),name='static')
S={
 'cargo':'http://cargo-plant:8100/state',
 'pms':'http://pms-plant:8200/state',
 'propulsion':'http://propulsion-plant:8300/state',
 'vessel':'http://vessel-coordinator:8600/state',
 'alarms':'http://alarm-engine:8400/alarms',
 'catalog':'http://alarm-engine:8400/catalog',
 'history':'http://alarm-engine:8400/history?limit=30',
 'alarm_metrics':'http://alarm-engine:8400/metrics',
}
C={
 'cargo':'http://cargo-plant:8100/contract',
 'pms':'http://pms-plant:8200/contract',
 'propulsion':'http://propulsion-plant:8300/contract',
}

@app.get('/')
def home(): return FileResponse('/app/static/index.html')

@app.get('/health')
def health():
    return {'ready': True, 'service': 'learning-portal'}

async def fetch_json(client,url):
    try: return (await client.get(url)).json()
    except Exception as e: return {'ready':False,'error':str(e)}

@app.get('/api/snapshot')
async def snapshot():
    async with httpx.AsyncClient(timeout=1) as c:
        out={}
        for k,u in S.items(): out[k]=await fetch_json(c,u)
        return out

@app.get('/api/contracts')
async def contracts():
    async with httpx.AsyncClient(timeout=1) as c:
        return {k:await fetch_json(c,u) for k,u in C.items()}

if __name__=='__main__': uvicorn.run(app,host='0.0.0.0',port=8500)
