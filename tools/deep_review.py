#!/usr/bin/env python3
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
problems=[]
checks={
    "process physics": ["docs/04-build/process-model.md","plant/modelica/CargoTransferPlant.mo"],
    "PLC": ["docs/04-build/plc-build.md","openplc/cargo/CargoControl.st"],
    "Modbus": ["docs/05-protocols/modbus-tcp.md","io_emulator/server.py"],
    "OPC UA": ["docs/05-protocols/opc-ua.md","historian/telegraf.conf"],
    "navigation": ["docs/05-protocols/nmea.md","navigation/README.md"],
    "incident response": ["docs/07-security/incident-walkthrough.md"],
    "alarm source boundary": ["docs/04-build/alarm-source-boundary.md"],
    "live historian binding": ["docs/04-build/opcua-commissioning.md", "historian/README.md"],
    "cross-system coupling": ["docs/03-architecture/vessel-profile.md","vessel/coordinator.py","docs/06-scenarios/integrated-power-cargo-event.md"],
    "HMI alarms": ["docs/04-build/hmi-and-alarm-system.md","alarms/service.py"],
    "PMS": ["docs/04-build/pms-module.md","plant/modelica/PowerManagementPlant.mo","openplc/pms/PowerManagement.st"],
    "propulsion": ["docs/04-build/propulsion-module.md","plant/modelica/PropulsionPlant.mo","openplc/propulsion/PropulsionControl.st"],
    "I/O traceability": ["docs/08-reference/generated-io-map.md","tools/generate_io_reference.py","tools/traceability_check.py"],
    "research": ["docs/09-research/research-framework.md","experiments/manifest.json"],
    "deployment": ["docs/04-build/server-daemon-deployment.md","deploy/systemd/lng-ot-lab.service","compose.production.yml"],
    "pedagogy": ["docs/00-learning/memory-and-explain-back.md","docs/00-learning/chapter-contract.md"],
    "scope and architecture claims": ["config/project-scope.json","config/architecture-contract.json","vessel/coverage-contract.json"],
    "evidence semantics": ["config/data-semantics-contract.json","config/timebase-contract.json","docs/09-research/image-provenance.json"],
    "claim boundaries": ["config/opcua-security-boundary.json","config/detection-claims.json","docs/09-research/experimental-claim-boundaries.md"],
    "repeated evidence": ["evidence/aggregate_runs.py","evidence/build_acceptance_dossier.py","evidence/acceptance-dossier-contract.json"],
    "target commissioning": ["commissioning/acceptance_orchestrator.py","commissioning/commissioning-plan.json","docs/04-build/commissioning-orchestrator.md"],
}
for topic,rels in checks.items():
    for rel in rels:
        if not (R/rel).exists(): problems.append(f"{topic}: missing {rel}")

# Publication visual quality is source/evidence driven.
try:
    vm=json.loads((R/'docs/09-research/visual-manifest.json').read_text())
    if len(vm.get('chapters',{})) != 10: problems.append('visual manifest must cover Chapters 1-10')
    for ch,items in vm.get('chapters',{}).items():
        if len(items)<2: problems.append(f'{ch}: fewer than two real visual references')
        for item in items:
            for key in ('source','license_or_reuse_status','what_to_notice','lab_mapping','limitation'):
                if not item.get(key): problems.append(f'{ch}: visual missing {key}')
except Exception as e: problems.append('visual manifest invalid: '+str(e))

# Public Markdown must not use our old custom SVGs as primary images.
for p in [R/'README.md',R/'docs/index.md',*list((R/'docs').rglob('*.md'))]:
    t=p.read_text(errors='ignore')
    if re.search(r'!\[[^\]]*\]\([^)]*assets/diagrams/[^)]*\.svg\)',t):
        problems.append(f'{p.relative_to(R)} still embeds a custom SVG as publication visual')

review=(R/'docs/08-reference/engineering-review.md').read_text(errors='ignore')
for phrase in ["OpenPLC Editor","OPC UA NodeIds","Process-model boundary","Runtime validation still required"]:
    if phrase not in review: problems.append('engineering review missing: '+phrase)
for rel in ["docs/05-protocols/modbus-tcp.md","docs/05-protocols/opc-ua.md","docs/05-protocols/nmea.md"]:
    t=(R/rel).read_text(errors='ignore').lower()
    if not any(k in t for k in ['capture','wireshark','browse','replay']): problems.append(f'{rel}: no practical observation workflow')
print('DEEP REVIEW')
if problems:
    print('FAIL'); [print(' -',p) for p in problems]; raise SystemExit(1)
print('PASS')
print(' - theory/implementation pairs checked')
print(' - Chapters 1-10 have real visual-source coverage')
print(' - old custom SVGs are not primary publication visuals')
print(' - explicit commissioning/limitation review present')
print(' - protocol observation workflows present')
