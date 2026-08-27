#!/usr/bin/env python3
from pathlib import Path
import json, yaml, ast
R=Path(__file__).resolve().parents[1]
problems=[]
for f in ['RELEASE-READINESS.md','release-manifest.json','docs/08-reference/component-inventory.md','docs/04-build/server-acceptance-test.md','tools/service_probe.py','config/readiness-contract.json','docs/09-research/github-publication-control.md','.github/workflows/quality.yml']:
    if not (R/f).exists(): problems.append('missing '+f)
m=json.loads((R/'release-manifest.json').read_text())
c=yaml.safe_load((R/'docker-compose.yml').read_text())
ex=json.loads((R/'experiments/manifest.json').read_text())['experiments']
vis=json.loads((R/'docs/09-research/visual-manifest.json').read_text())['chapters']
def collected_test_functions():
    count=0
    for path in (R/'tests').glob('test_*.py'):
        tree=ast.parse(path.read_text())
        count += sum(isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_') for node in ast.walk(tree))
    return count
checks={
 'pytest_expected':collected_test_functions(),
 'course_chapters':len(list((R/'docs/course').glob('*.md'))),
 'experiments':len(ex),
 'compose_services':len(c['services']),
 'compose_networks':len(c['networks']),
 'visual_manifest_chapters':len(vis),
}
for k,v in checks.items():
    if m['static_validation'].get(k)!=v: problems.append(f'manifest drift {k}: {m["static_validation"].get(k)} != {v}')
if m.get('runtime_validation_in_build_environment') is not False:
    problems.append('release manifest must not overclaim runtime validation')
if m.get('canonical_repository') != 'https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab':
    problems.append('canonical GitHub repository missing or drifted')
if problems:
    print('RELEASE GATE\nFAIL')
    [print(' -',p) for p in problems]
    raise SystemExit(1)
print('RELEASE GATE\nPASS')
for k,v in checks.items(): print(f' - {k}: {v}')
print(' - runtime validation correctly marked pending target-server commissioning')
