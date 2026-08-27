#!/usr/bin/env python3
from pathlib import Path
import argparse, json, hashlib
R=Path(__file__).resolve().parents[1]
OUT=R/'docs/08-reference/generated-io-map.md'
MAP=json.loads((R/'openplc/mapping_contract.json').read_text())

def object_name(x):
    return {'coil':'Coil','holding':'Holding Register','input':'Input Register','discrete':'Discrete Input'}[x]

def raw_meaning(spec, direction):
    scale=spec.get('scale',1.0); offset=spec.get('offset',0.0)
    unit=spec.get('unit','')
    if direction=='command':
        if spec['source']=='coil': return '0 / 1'
        return f'model = raw × {scale:g}' + (f' + {offset:g}' if offset else '') + (f' {unit}' if unit else '')
    if spec['dest']=='discrete': return '0 / 1'
    return f'model = raw × {scale:g}' + (f' + {offset:g}' if offset else '') + (f' {unit}' if unit else '')

def plc_symbol(domain, group, model_name, spec):
    # Instructor fault channels intentionally live outside the normal PLC program.
    if spec.get('role')=='Instructor-only fault': return '— instructor only —'
    return MAP[domain][group].get(model_name,'⚠ UNMAPPED')

parts=['# Generated I/O Map','',
       '> Generated from `io_emulator/configs/*.json` + `openplc/mapping_contract.json`. Do not hand-edit this page.','']
h=hashlib.sha256()
for p in sorted((R/'io_emulator/configs').glob('*.json')): h.update(p.read_bytes())
h.update((R/'openplc/mapping_contract.json').read_bytes())
parts += [f'Configuration digest: `{h.hexdigest()[:16]}`','']
for p in sorted((R/'io_emulator/configs').glob('*.json')):
    c=json.loads(p.read_text()); key=c['domain']; domain=key.title()
    parts += [f'## {domain}', '', f'Endpoint: TCP `{c["port"]}`, Unit ID `1`', '', '### Commands / instructor inputs','',
              '| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |',
              '|---|---:|---|---|---|---|---|']
    for n,s in c.get('commands',{}).items():
        parts.append('| {} | {} | `{}` | `{}` | {} | {} | {} |'.format(object_name(s['source']),s['address'],n,plc_symbol(key,'commands',n,s),s.get('description',''),s.get('role',''),raw_meaning(s,'command')))
    parts += ['', '### Measurements / feedback','',
              '| Object | Address | Model variable | PLC symbol | Meaning | Role | Raw conversion |',
              '|---|---:|---|---|---|---|---|']
    for n,s in c.get('outputs',{}).items():
        parts.append('| {} | {} | `{}` | `{}` | {} | {} | {} |'.format(object_name(s['dest']),s['address'],n,plc_symbol(key,'outputs',n,s),s.get('description',''),s.get('role',''),raw_meaning(s,'output')))
    parts.append('')
text='\n'.join(parts)+'\n'
ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
if args.check:
    if not OUT.exists() or OUT.read_text()!=text:
        print('FAIL: generated I/O reference is stale. Run: python3 tools/generate_io_reference.py')
        raise SystemExit(1)
    print('PASS: generated I/O reference matches I/O + PLC mapping source of truth')
else:
    OUT.write_text(text); print(f'wrote {OUT.relative_to(R)}')
