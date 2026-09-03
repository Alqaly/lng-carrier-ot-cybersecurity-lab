#!/usr/bin/env python3
from pathlib import Path
import json,re,yaml
R=Path(__file__).resolve().parents[1]; problems=[]
required=[
 'docs/00-learning/how-to-use-this-course.md','docs/00-learning/chapter-contract.md',
 'docs/03-architecture/deployment-decision.md','docs/04-build/server-daemon-deployment.md',
 'docs/05-protocols/can-j1939.md','docs/05-protocols/ethernet-ip-stack.md',
 'docs/09-research/research-framework.md','docs/09-research/standards-mapping.md',
 'docs/09-research/visual-source-registry.md','docs/08-reference/technology-selection.md',
 'experiments/manifest.json','security/conduits.json','historian/freshness_check.py',
 'config/project-scope.json','config/architecture-contract.json','config/data-semantics-contract.json',
 'config/timebase-contract.json','config/opcua-security-boundary.json','config/detection-claims.json',
 'vessel/coverage-contract.json','docs/09-research/image-provenance.json',
 'evidence/acceptance-dossier-contract.json','evidence/aggregate_runs.py','evidence/build_acceptance_dossier.py']
for x in required:
    if not (R/x).exists(): problems.append('missing '+x)
for p in (R/'docs/05-protocols').glob('*.md'):
    t=p.read_text(errors='ignore').lower()
    if p.name in {'protocol-map.md','iec-61162-450-460.md'}: continue
    if not any(k in t for k in ['60-second explain-back','capture','replay','candump','wireshark','worked example']): problems.append(f'{p}: insufficient practical/pedagogy content')
m=json.loads((R/'experiments/manifest.json').read_text())['experiments']; ids=[x['id'] for x in m]
if len(ids)!=len(set(ids)): problems.append('duplicate experiment ids')
for e in m:
    for k in ['hypothesis','metrics','required_evidence']:
        if not e.get(k): problems.append(f"{e['id']}: missing {k}")
pol=json.loads((R/'security/conduits.json').read_text())
for rule in pol['modbus']:
    if not re.match(r'^172\.28\.',rule['src']) or not re.match(r'^172\.28\.',rule['dst']): problems.append('non-lab conduit IP')
cat=(R/'alarms/catalog.json').read_text()
for old in ['CARGO_DATA_STALE','PMS_DATA_STALE','PROPULSION_DATA_STALE']:
    if f'"{old}"' in cat: problems.append('ambiguous stale alarm id remains: '+old)
# Reachability controls introduced for two previously unreachable teaching conditions.
cargo=json.loads((R/'plant/configs/cargo.json').read_text()); prop=json.loads((R/'plant/configs/propulsion.json').read_text())
if 'faultFlowPathBlocked' not in cargo['inputs']: problems.append('Cargo blocked-flow fault missing')
if 'faultCoolingFail' not in prop['inputs']: problems.append('Propulsion cooling impairment fault missing')
net=json.loads((R/'network/fidelity-contract.json').read_text())
if net.get('status')!='design_accepted_runtime_unvalidated': problems.append('network fidelity status must remain runtime-unvalidated until NF gates run')
if net.get('canonical_baseline',{}).get('must_remain_runnable_without_extension') is not True: problems.append('network extension may not replace the canonical Compose baseline')
clab=net.get('selected_extension',{}).get('topology_orchestrator',{})
if clab.get('name')!='Containerlab' or clab.get('reviewed_version')!='0.77.0': problems.append('network fidelity Containerlab decision drift')
if net.get('selected_extension',{}).get('routing',{}).get('dynamic_routing_suite')!='not selected': problems.append('dynamic routing was introduced without a recorded admission decision')
if len(net.get('runtime_acceptance_gates',[]))!=7: problems.append('network fidelity NF-A through NF-G contract incomplete')
scope=json.loads((R/'config/project-scope.json').read_text())
if scope.get('current_validation_state')!='static_validated_pending_target_server_commissioning': problems.append('project scope validation state overclaims runtime readiness')
claims=json.loads((R/'config/detection-claims.json').read_text())
if len(claims.get('required_comparators',[]))!=3: problems.append('detection comparison contract incomplete')
opc=json.loads((R/'config/opcua-security-boundary.json').read_text())
if not opc.get('not_yet_claimed'): problems.append('OPC UA security claim boundary missing')
print('RESEARCH/PUBLICATION GATE')
if problems:
    print('FAIL'); [print(' -',x) for x in problems]; raise SystemExit(1)
print('PASS')
print(f' - {len(m)} registered experiments with hypotheses/metrics/evidence')
print(' - pedagogy, deployment, standards, visual-source and technology-selection contracts present')
