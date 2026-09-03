import asyncio, json, time
from pathlib import Path
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

PROFILE=json.loads(Path('/config/profile.json').read_text())
URLS={
    'cargo':'http://cargo-plant:8100',
    'pms':'http://pms-plant:8200',
    'propulsion':'http://propulsion-plant:8300',
}
app=FastAPI(title='Vessel Cross-System Coordinator')
snapshot={'ready':False,'profile':PROFILE,'last_update':None,'links':{}}

async def get(client, base):
    r=await client.get(base+'/state')
    j=r.json()
    return j if j.get('ready') else {}

async def post(client, base, data):
    r=await client.post(base+'/command',json=data)
    r.raise_for_status()
    return r.json()

async def loop():
    async with httpx.AsyncClient(timeout=1.5) as c:
        while True:
            try:
                cargo=await get(c,URLS['cargo'])
                pms=await get(c,URLS['pms'])
                prop=await get(c,URLS['propulsion'])

                cargo_kw=max(0.0,float(cargo.get('pumpPowerKW',0.0)))
                aux_kw=max(0.0,float(prop.get('auxiliaryElectricalLoadKW',0.0)))

                await post(c,URLS['pms'],{
                    'externalCargoLoadKW':cargo_kw if PROFILE.get('cargo_power_from_pms') else 0.0,
                    'externalAuxLoadKW':aux_kw if PROFILE.get('propulsion_aux_power_from_pms') else 0.0,
                })

                bus_ok=bool(pms.get('busEnergized')) and float(pms.get('voltagePU',0.0))>0.80
                cargo_power=bus_ok and not bool(pms.get('shedCargo'))
                prop_aux=bus_ok

                if PROFILE.get('cargo_power_from_pms'):
                    await post(c,URLS['cargo'],{'powerAvailable':cargo_power})
                if PROFILE.get('propulsion_aux_power_from_pms'):
                    await post(c,URLS['propulsion'],{'auxPowerAvailable':prop_aux})

                snapshot.update({
                    'ready':True,
                    'last_update':time.time(),
                    'links':{
                        'cargoElectricalLoadKW':cargo_kw,
                        'propulsionAuxLoadKW':aux_kw,
                        'busAvailable':bus_ok,
                        'cargoPowerAvailable':cargo_power,
                        'propulsionAuxPowerAvailable':prop_aux,
                    }
                })
            except Exception as e:
                snapshot.update({'ready':False,'last_update':time.time(),'error':repr(e)})
            await asyncio.sleep(0.2)

@app.on_event('startup')
async def startup():
    asyncio.create_task(loop())

@app.get('/state')
def state():
    return snapshot

@app.get('/health')
def health():
    ready = bool(snapshot.get('ready'))
    payload = {
        'ready': ready,
        'service': 'vessel-coordinator',
        'last_update': snapshot.get('last_update'),
        'error': snapshot.get('error'),
    }
    return JSONResponse(payload, status_code=200 if ready else 503)

@app.get('/profile')
def profile():
    return PROFILE

if __name__=='__main__':
    uvicorn.run(app,host='0.0.0.0',port=8600)
