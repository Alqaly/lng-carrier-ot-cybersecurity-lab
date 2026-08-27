#!/usr/bin/env python3
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
problems=[]

# Plant config ↔ I/O configuration.
for io_path in sorted((R/'io_emulator/configs').glob('*.json')):
    domain=io_path.stem; io=json.loads(io_path.read_text()); plant=json.loads((R/f'plant/configs/{domain}.json').read_text())
    pin=set(plant['inputs']); pout=set(plant['outputs'])
    for name,s in io.get('commands',{}).items():
        if name not in pin: problems.append(f'{domain}: I/O command {name} absent from plant inputs')
        for k in ('unit','description','role'):
            if k not in s: problems.append(f'{domain}: command {name} missing metadata {k}')
    for name,s in io.get('outputs',{}).items():
        if name not in pout: problems.append(f'{domain}: I/O output {name} absent from plant outputs')
        for k in ('unit','description','role'):
            if k not in s: problems.append(f'{domain}: output {name} missing metadata {k}')
    # detect duplicate object/address pairs within commands/outputs
    seen={}
    for group,key in [('commands','source'),('outputs','dest')]:
        for name,s in io[group].items():
            ident=(group,s[key],s['address'])
            if ident in seen: problems.append(f'{domain}: duplicate {ident}: {seen[ident]} and {name}')
            seen[ident]=name


# I/O configuration ↔ OpenPLC symbol contract.
mapping=json.loads((R/'openplc/mapping_contract.json').read_text())
for domain in ('cargo','pms','propulsion'):
    io=json.loads((R/f'io_emulator/configs/{domain}.json').read_text())
    m=mapping[domain]
    st=(R/m['program']).read_text()
    # Instructor-only fault channels intentionally bypass normal PLC mapping.
    normal_commands={name for name,s in io['commands'].items() if s.get('role')!='Instructor-only fault'}
    mapped_commands=set(m['commands'])
    if normal_commands != mapped_commands:
        problems.append(f'{domain}: PLC command mapping mismatch normal={sorted(normal_commands)} mapped={sorted(mapped_commands)}')
    if set(io['outputs']) != set(m['outputs']):
        problems.append(f'{domain}: PLC output mapping does not cover all I/O outputs')
    for group in ('commands','outputs'):
        for model_name,symbol in m[group].items():
            if not re.search(rf'\b{re.escape(symbol)}\b',st):
                problems.append(f'{domain}: PLC symbol {symbol} for {model_name} absent from {m["program"]}')

# Coordinator referenced fields must exist in configs.
c=(R/'vessel/coordinator.py').read_text()
required_coupling={
 'cargo': ['pumpPowerKW','powerAvailable'],
 'pms': ['externalCargoLoadKW','externalAuxLoadKW','busEnergized','voltagePU','shedCargo'],
 'propulsion': ['auxiliaryElectricalLoadKW','auxPowerAvailable'],
}
for d,names in required_coupling.items():
    pc=json.loads((R/f'plant/configs/{d}.json').read_text()); allowed=set(pc['inputs'])|set(pc['outputs'])
    for n in names:
        if n not in allowed: problems.append(f'coordinator contract: {d}.{n} absent from plant config')
        if n not in c: problems.append(f'coordinator implementation does not reference {d}.{n}')

# Alarm fields must refer to plant output/input fields or the special stale flag.
catalog=json.loads((R/'alarms/catalog.json').read_text())['alarms']
for a in catalog:
    domain=a['domain']; pc=json.loads((R/f'plant/configs/{domain}.json').read_text()); fields=set(pc['inputs'])|set(pc['outputs'])|{'__stale__'}
    for cond in a.get('conditions',[])+a.get('clear_conditions',[]):
        if cond.get('field') not in fields:
            problems.append(f'alarm {a["id"]}: field {cond.get("field")} not in {domain} plant contract')

# Each domain needs implementation + walkthrough docs.
for d in ('cargo','pms','propulsion'):
    if not (R/f'io_emulator/configs/{d}.json').exists(): problems.append(f'{d}: missing I/O config')
for p in ['docs/04-build/software-lab-walkthrough.md','docs/08-reference/generated-io-map.md','docs/08-reference/data-provenance.md']:
    if not (R/p).exists(): problems.append('missing traceability doc '+p)

print('TRACEABILITY CHECK')
if problems:
    print('FAIL')
    for p in problems: print(' -',p)
    raise SystemExit(1)
print('PASS')
print(' - plant ↔ I/O contracts aligned')
print(' - I/O entries carry engineering metadata')
print(' - I/O ↔ OpenPLC symbol mapping is complete')
print(' - cross-system coordinator fields exist')
print(' - alarm conditions resolve to domain contracts')
