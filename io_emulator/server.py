import asyncio, json, logging, os
from pathlib import Path
import httpx
from pymodbus.server import ModbusTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
CFG=json.loads(Path(os.getenv('IO_CONFIG','/config/io.json')).read_text())
PLANT=CFG['plant_url']
PORT=int(os.getenv('MODBUS_PORT',str(CFG.get('port',5020))))

class TrackingBlock(ModbusSequentialDataBlock):
    def __init__(self,address,values,kind): super().__init__(address,values); self.kind=kind
    def setValues(self,address,values):
        super().setValues(address,values)
        if self.kind in ('coil','holding'):
            logging.info('MODBUS_WRITE domain=%s kind=%s address=%s values=%s',CFG['domain'],self.kind,address,values)

co=TrackingBlock(0,[0]*128,'coil'); di=ModbusSequentialDataBlock(0,[0]*128)
hr=TrackingBlock(0,[0]*128,'holding'); ir=ModbusSequentialDataBlock(0,[0]*256)
device=ModbusDeviceContext(di=di,co=co,hr=hr,ir=ir)
context=ModbusServerContext(devices={1:device},single=False)

def read_source(spec):
    kind=spec['source']; addr=int(spec['address'])
    if kind=='coil': return bool(device.getValues(1,addr,count=1)[0])
    if kind=='holding':
        raw=device.getValues(3,addr,count=1)[0]
        return float(raw)*float(spec.get('scale',1.0))+float(spec.get('offset',0.0))
    raise ValueError(kind)

def encode(v,spec):
    if spec['dest']=='discrete': return bool(v)
    scale=float(spec.get('scale',1.0)); offset=float(spec.get('offset',0.0))
    raw=int(round((float(v)-offset)/scale))
    return max(0,min(65535,raw))

async def sync_loop():
    async with httpx.AsyncClient(timeout=1.5) as client:
        while True:
            try:
                cmd={name:read_source(spec) for name,spec in CFG.get('commands',{}).items()}
                # Faults are instructor-side state in holding registers or coils when configured.
                await client.post(f'{PLANT}/command',json=cmd)
                s=(await client.get(f'{PLANT}/state')).json()
                if s.get('ready'):
                    for name,spec in CFG.get('outputs',{}).items():
                        if name not in s: continue
                        val=encode(s[name],spec); addr=int(spec['address'])
                        if spec['dest']=='input': device.setValues(4,addr,[val])
                        elif spec['dest']=='discrete': device.setValues(2,addr,[val])
            except Exception as e:
                logging.warning('sync error domain=%s: %s',CFG['domain'],e)
            await asyncio.sleep(float(CFG.get('poll_seconds',0.1)))

async def main():
    asyncio.create_task(sync_loop())
    logging.info('Starting %s Modbus server on %s',CFG['domain'],PORT)
    await ModbusTcpServer(context,address=('0.0.0.0',PORT)).serve_forever()
if __name__=='__main__': asyncio.run(main())
