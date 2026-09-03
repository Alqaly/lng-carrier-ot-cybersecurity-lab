import json, os, time, threading
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import uvicorn

CONFIG_PATH = os.getenv('MODEL_CONFIG', '/config/model.json')
CONFIG = json.loads(Path(CONFIG_PATH).read_text())
FMU_PATH = os.getenv('FMU_PATH', CONFIG['fmu_path'])
STEP = float(os.getenv('STEP_SECONDS', str(CONFIG.get('step_seconds', 0.05))))

app = FastAPI(title=f"{CONFIG['name']} Process Runtime")
lock = threading.Lock()

class Plant:
    def __init__(self, path):
        md = read_model_description(path)
        self.vars = {v.name: v.valueReference for v in md.modelVariables}
        missing = [n for n in list(CONFIG['inputs']) + list(CONFIG['outputs']) if n not in self.vars]
        if missing:
            raise RuntimeError(f'FMU missing configured variables: {missing}')
        self.unzipdir = extract(path)
        self.fmu = FMU2Slave(
            guid=md.guid,
            unzipDirectory=self.unzipdir,
            modelIdentifier=md.coSimulation.modelIdentifier,
            instanceName=CONFIG['name'].replace(' ', '_').lower(),
        )
        self.fmu.instantiate()
        self.fmu.setupExperiment(startTime=0.0)
        self.fmu.enterInitializationMode()
        self.commands = dict(CONFIG.get('defaults', {}))
        self._write_inputs(self.commands)
        self.fmu.exitInitializationMode()
        self.t = 0.0

    def _write_inputs(self, values):
        bool_names=[]; bool_vals=[]; real_names=[]; real_vals=[]
        for name, kind in CONFIG['inputs'].items():
            if name not in values: continue
            if kind == 'boolean': bool_names.append(name); bool_vals.append(bool(values[name]))
            elif kind == 'real': real_names.append(name); real_vals.append(float(values[name]))
            else: raise ValueError(f'unsupported input type {kind} for {name}')
        if bool_names: self.fmu.setBoolean([self.vars[n] for n in bool_names], bool_vals)
        if real_names: self.fmu.setReal([self.vars[n] for n in real_names], real_vals)

    def set_commands(self, values):
        unknown=set(values)-set(CONFIG['inputs'])
        if unknown: raise ValueError(f'unknown inputs: {sorted(unknown)}')
        self.commands.update(values)
        self._write_inputs(values)

    def step(self):
        self._write_inputs(self.commands)
        self.fmu.doStep(currentCommunicationPoint=self.t, communicationStepSize=STEP)
        self.t += STEP

    def state(self):
        out={'time_s': self.t, **self.commands}
        bool_names=[n for n,k in CONFIG['outputs'].items() if k=='boolean']
        real_names=[n for n,k in CONFIG['outputs'].items() if k=='real']
        if bool_names:
            vals=self.fmu.getBoolean([self.vars[n] for n in bool_names])
            out.update(dict(zip(bool_names, [bool(v) for v in vals])))
        if real_names:
            vals=self.fmu.getReal([self.vars[n] for n in real_names])
            out.update(dict(zip(real_names, [float(v) for v in vals])))
        return out

plant=None
fatal_error=None

def loop():
    global plant, fatal_error
    try:
        while not os.path.exists(FMU_PATH):
            print(f'Waiting for {FMU_PATH}', flush=True); time.sleep(1)
        plant=Plant(FMU_PATH)
        while True:
            with lock: plant.step()
            time.sleep(STEP)
    except Exception as e:
        fatal_error=repr(e); print('FATAL', fatal_error, flush=True)

@app.get('/health')
def health():
    ready = plant is not None and fatal_error is None
    payload = {'ready': ready, 'error': fatal_error, 'model': CONFIG['name']}
    return JSONResponse(payload, status_code=200 if ready else 503)

@app.get('/state')
def state():
    if plant is None: return {'ready': False, 'error': fatal_error}
    with lock: return {'ready': True, **plant.state()}

@app.post('/command')
def command(values: dict):
    if plant is None: raise HTTPException(503, detail=fatal_error or 'FMU not ready')
    try:
        with lock:
            plant.set_commands(values)
            return {'ready': True, **plant.state()}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@app.get('/contract')
def contract():
    return CONFIG

threading.Thread(target=loop, daemon=True).start()
if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT','8100')))
