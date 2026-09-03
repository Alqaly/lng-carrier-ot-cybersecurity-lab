#!/usr/bin/env python3
from pathlib import Path
import re, sys, yaml

R = Path(__file__).resolve().parents[1]
problems = []

required = [
    "README.md",
    "START-HERE.md",
    "docs/04-build/software-lab-walkthrough.md",
    "docs/05-protocols/modbus-tcp.md",
    "docs/05-protocols/opc-ua.md",
    "docs/09-research/source-registry.md",
    "plant/modelica/CargoTransferPlant.mo",
    "plant/modelica/PowerManagementPlant.mo",
    "plant/modelica/PropulsionPlant.mo",
    "docs/04-build/hmi-and-alarm-system.md",
    "docs/04-build/pms-module.md",
    "docs/04-build/propulsion-module.md",
    "openplc/cargo/CargoControl.st",
    "docker-compose.yml",
    "vessel/coordinator.py",
    "docs/03-architecture/vessel-profile.md",
    "docs/06-scenarios/integrated-power-cargo-event.md",
    "docs/04-build/openplc-editor-commissioning.md",
    "docs/03-architecture/software-realism.md",
    "DEPENDENCIES.md",
    "tools/generate_io_reference.py",
    "tools/traceability_check.py",
    "docs/08-reference/generated-io-map.md",
    "docs/04-build/operator-alarm-workflow.md",
    "docs/09-research/research-to-model-matrix.md",
    "docs/06-scenarios/cross-layer-evidence-workbook.md",
    "docs/06-scenarios/cross-domain-operational-event.md",
    "docs/04-build/opcua-commissioning.md",
    "docs/04-build/fuxa-project-workflow.md",
    "docs/08-reference/endpoints-and-interfaces.md",
    "commissioning/opcua_tool.py",
    "commissioning/fuxa_tool.py",
    "fuxa/project-unbound.fuxap",
    "docs/04-build/alarm-source-boundary.md",
    "historian/README.md",
    "config/project-scope.json",
    "config/architecture-contract.json",
    "config/data-semantics-contract.json",
    "config/timebase-contract.json",
    "config/opcua-security-boundary.json",
    "config/detection-claims.json",
    "vessel/coverage-contract.json",
    "docs/09-research/image-provenance.json",
    "evidence/acceptance-dossier-contract.json",
    "evidence/aggregate_runs.py",
    "evidence/build_acceptance_dossier.py",
    "commissioning/acceptance_orchestrator.py",
    "commissioning/commissioning-plan.json",
    "docs/04-build/commissioning-orchestrator.md",
    "docs/09-research/recovery-2026-09-03.md",
]

for rel in required:
    if not (R/rel).exists():
        problems.append(f"missing required file: {rel}")

# Old internal release/version language should not appear in user-facing docs.
for p in list(R.glob("README.md")) + list((R/"docs").rglob("*.md")):
    text = p.read_text(errors="ignore")
    banned_project_history = [
        r"\\bV5(?:\\.1)?\\b",
        r"\\bV4(?:\\.1)?\\b(?=\\s+(?:changes|project|lab|release|architecture))",
        r"mock[- ]?data",
        r"old lab",
        r"previous version",
        r"previous project version",
    ]
    for bad in banned_project_history:
        if re.search(bad, text, re.I):
            problems.append(f"{p.relative_to(R)} contains obsolete project-history phrase matching {bad}")


# Public docs must not drift back to obsolete service/tag examples.
stale_patterns={
    r"\bvirtual-io\b": "obsolete generic virtual-io service name",
    r"\bplant-runtime\b": "obsolete generic plant-runtime service name",
    r"\bconduit-capture\b": "obsolete generic capture service name",
    r"Flow_Lpm": "obsolete Cargo flow tag name",
    r"L/min\s*[x×]\s*10": "obsolete Cargo flow scaling",
}
for p in [R/"README.md", R/"START-HERE.md", *list((R/"docs").rglob("*.md"))]:
    text=p.read_text(errors="ignore")
    for pat,label in stale_patterns.items():
        if re.search(pat,text,re.I):
            problems.append(f"{p.relative_to(R)} contains {label}")

# Local Markdown links should resolve.
link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for p in [R/"README.md", R/"START-HERE.md", *list((R/"docs").rglob("*.md"))]:
    text = p.read_text(errors="ignore")
    for target in link_re.findall(text):
        if "://" in target or target.startswith("#") or target.startswith("mailto:"):
            continue
        path = (p.parent/target.split("#",1)[0]).resolve()
        if not path.exists():
            problems.append(f"broken local link: {p.relative_to(R)} -> {target}")

# Compose must parse as YAML.
try:
    yaml.safe_load((R/"docker-compose.yml").read_text())
except Exception as e:
    problems.append(f"docker-compose.yml YAML error: {e}")

# Core runtime image must be pinned to the reviewed stable release.
compose_text=(R/"docker-compose.yml").read_text()
if "ghcr.io/autonomy-logic/openplc-runtime:v4.1.9" not in compose_text:
    problems.append("OpenPLC Runtime image is not pinned to v4.1.9")

# Diagrams
for d in ["system-architecture.svg","vessel-domains.svg","protocol-map.svg"]:
    if not (R/"assets/diagrams"/d).exists():
        problems.append("missing diagram: "+d)

# Key dependency drift checks.
compose_text=(R/"docker-compose.yml").read_text()
if "frangoteam/fuxa:1.3.4" not in compose_text:
    problems.append("FUXA 1.3.4 pin missing")
if "frangoteam/fuxa:1.3.3" in compose_text:
    problems.append("obsolete FUXA 1.3.3 pin remains")

# Generated architecture/I/O documentation must match source-of-truth configuration.
import subprocess
for script,args,label in [
    (R/"tools/generate_io_reference.py", ["--check"], "generated I/O reference"),
    (R/"tools/traceability_check.py", [], "traceability"),
]:
    cp=subprocess.run([sys.executable,str(script),*args],capture_output=True,text=True)
    if cp.returncode:
        problems.append(f"{label} check failed: {cp.stdout.strip()} {cp.stderr.strip()}")


# Historian must not ship guessed live OPC UA NodeIds.
historian_base=(R/"historian/telegraf.conf").read_text()
if "[[inputs.opcua]]" in historian_base or "nodes = [" in historian_base:
    problems.append("active historian config contains pre-commissioned/guessed OPC UA inputs")
labctl_text=(R/"labctl").read_text()
if "cmd_hist_install" not in labctl_text:
    problems.append("verified historian install workflow missing from labctl")
if "cmd_aggregate_runs" not in labctl_text or "cmd_acceptance_dossier" not in labctl_text:
    problems.append("repeated-run aggregation or acceptance-dossier workflow missing from labctl")
if "cmd_commission" not in labctl_text or "acceptance_orchestrator.py" not in labctl_text:
    problems.append("resumable commissioning orchestrator missing from labctl")

# Public source registry must include marine + software sources.
sources=(R/"docs/09-research/source-registry.md").read_text()
for token in ["Kongsberg","SIGTTO","NMEA","OpenPLC","OpenModelica","FUXA","asyncua"]:
    if token not in sources:
        problems.append("source registry missing "+token)

print("QUALITY GATE")
if problems:
    print("FAIL")
    for p in problems:
        print(" -",p)
    raise SystemExit(1)

print("PASS")
print(" - required files present")
print(" - user-facing docs free of internal release labels")
print(" - local Markdown links resolve")
print(" - Compose YAML parses")
print(" - required diagrams present")
print(" - source registry coverage present")
