#!/usr/bin/env python3
"""Read-only runtime smoke checks for the already-started software lab."""
import json,math,sys,urllib.request

ENDPOINTS={
 'cargo':('http://127.0.0.1:8100/state', ['ready','levelSource','flowMeasured','pumpPowerKW']),
 'pms':('http://127.0.0.1:8200/state', ['ready','busFrequencyHz','totalLoadKW','spinningReserveKW']),
 'propulsion':('http://127.0.0.1:8300/state', ['ready','engineRPM','lubeOilPressureBar','coolantTempC']),
 'vessel':('http://127.0.0.1:8600/state', ['ready']),
}

def get(url):
    with urllib.request.urlopen(url,timeout=4) as r:
        return json.loads(r.read())

def finite(v): return isinstance(v,(int,float)) and math.isfinite(v)

problems=[]
for name,(url,keys) in ENDPOINTS.items():
    try: d=get(url)
    except Exception as e:
        problems.append(f'{name}: unavailable: {e}'); continue
    missing=[k for k in keys if k not in d]
    if missing: problems.append(f'{name}: missing keys {missing}')
    if d.get('ready') is False: problems.append(f'{name}: reports ready=false')
    for k,v in d.items():
        if isinstance(v,float) and not finite(v): problems.append(f'{name}: non-finite {k}={v}')
    print(f'{name:10s} PASS  {url}')

# Broad physical sanity bounds; these are guard rails, not validation of fidelity.
try:
    c=get(ENDPOINTS['cargo'][0])
    if c.get('levelSource',0) < 0 or c.get('flowMeasured',0) < -1e-9 or c.get('pumpPowerKW',0)<-1e-9:
        problems.append('cargo: negative physical state outside teaching model bounds')
except Exception: pass
try:
    p=get(ENDPOINTS['propulsion'][0])
    if p.get('engineRPM',0)<-1e-6 or p.get('lubeOilPressureBar',0)<-1e-6:
        problems.append('propulsion: negative RPM/pressure')
except Exception: pass

if problems:
    print('\nRUNTIME SMOKE: FAIL')
    for x in problems: print(' -',x)
    raise SystemExit(1)
print('\nRUNTIME SMOKE: PASS')
print('This proves service/state sanity only. It does not replace PLC/OPC UA/HMI/experiment commissioning.')
