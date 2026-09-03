#!/usr/bin/env python3
"""Resumable, evidence-backed target-server commissioning for Gates A-G.

The orchestrator automates what can be measured from the host and stops at the
OpenPLC, HMI, reboot and restore observations that require a commissioned
system. Recorded observations are copied into the run and hashed; a checkbox or
an unreferenced JSON file is never accepted as evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "commissioning" / "commissioning-plan.json"
DOSSIER_CONTRACT = ROOT / "evidence" / "acceptance-dossier-contract.json"
EXPERIMENT_MANIFEST = ROOT / "experiments" / "manifest.json"
STATE_NAME = "commissioning-state.json"
DOMAINS = ("cargo", "pms", "propulsion")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CommandRunner = Callable[[list[str]], tuple[int, str]]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(str(item.relative_to(path)).encode())
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(item)))
    return digest.hexdigest()


def path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return data


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def git_value(*args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()


def project_snapshot() -> dict[str, Any]:
    dirty = bool(git_value("status", "--porcelain"))
    return {
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_tree": git_value("show", "-s", "--format=%T", "HEAD"),
        "git_origin": git_value("remote", "get-url", "origin"),
        "tree_dirty": dirty,
        "release_manifest_sha256": sha256_file(ROOT / "release-manifest.json"),
        "commissioning_plan_sha256": sha256_file(PLAN_PATH),
        "dossier_contract_sha256": sha256_file(DOSSIER_CONTRACT),
    }


def host_snapshot() -> dict[str, Any]:
    boot = Path("/proc/sys/kernel/random/boot_id")
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "boot_id": boot.read_text().strip() if boot.exists() else None,
    }


def initialise(evidence_root: Path, project: dict[str, Any] | None = None, timestamp: str | None = None) -> Path:
    project = project or project_snapshot()
    if project.get("tree_dirty"):
        raise ValueError("Refusing commissioning from a dirty Git tree. Commit or preserve local changes first.")
    stamp = timestamp or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    base = evidence_root / f"{stamp}-gates-a-g"
    run = base
    suffix = 1
    while run.exists():
        suffix += 1
        run = Path(f"{base}-{suffix}")
    run.mkdir(parents=True)
    (run / "logs").mkdir()
    (run / "provenance").mkdir()
    shutil.copy2(PLAN_PATH, run / "provenance" / PLAN_PATH.name)
    shutil.copy2(DOSSIER_CONTRACT, run / "provenance" / DOSSIER_CONTRACT.name)
    state = {
        "schema_version": 1,
        "run_id": run.name,
        "created_at": now(),
        "updated_at": now(),
        "status": "in_progress",
        "project": project,
        "host_at_start": host_snapshot(),
        "gate_runs": {},
    }
    write_json(run / STATE_NAME, state)
    return run


def load_state(run: Path) -> dict[str, Any]:
    path = run / STATE_NAME
    if not path.is_file():
        raise ValueError(f"Missing {path}; initialise the commissioning run first.")
    return read_json(path)


def load_plan() -> dict[str, Any]:
    return read_json(PLAN_PATH)


def assert_source_matches(state: dict[str, Any], current: dict[str, Any] | None = None) -> None:
    current = current or project_snapshot()
    expected = state["project"]
    if current.get("tree_dirty"):
        raise ValueError("Git tree became dirty during commissioning; refusing to mix evidence with changed source.")
    for key in ("git_commit", "git_tree", "release_manifest_sha256", "commissioning_plan_sha256"):
        if current.get(key) != expected.get(key):
            raise ValueError(f"Source drift for {key}: {current.get(key)} != {expected.get(key)}")


def run_command(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return completed.returncode, completed.stdout


def evidence_entry(run: Path, path: Path, label: str) -> dict[str, Any]:
    resolved_run = run.resolve()
    resolved_path = path.resolve()
    if resolved_run != resolved_path and resolved_run not in resolved_path.parents:
        raise ValueError(f"Evidence must be retained inside the commissioning run: {path}")
    return {
        "label": label,
        "path": str(resolved_path.relative_to(resolved_run)),
        "kind": "directory" if resolved_path.is_dir() else "file",
        "size_bytes": path_size(resolved_path),
        "sha256": sha256_path(resolved_path),
    }


def command_batch(run: Path, gate: str, commands: list[tuple[str, list[str]]], runner: CommandRunner = run_command) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for index, (label, command) in enumerate(commands, start=1):
        started = now()
        before = time.monotonic()
        code, output = runner(command)
        duration = time.monotonic() - before
        log = run / "logs" / f"gate-{gate}-{index:02d}-{label}.log"
        log.write_text(output)
        evidence.append(evidence_entry(run, log, f"command-{label}"))
        records.append({
            "label": label,
            "command": command,
            "started_at": started,
            "duration_seconds": round(duration, 3),
            "exit_code": code,
            "log": str(log.relative_to(run)),
        })
    return records, evidence


def artifact_payload(run: Path, state: dict[str, Any], gate: str, artifact: str, passed: bool, evidence: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "artifact": artifact,
        "gate": gate,
        "recorded_at": now(),
        "pass": bool(passed),
        "project": state["project"],
        "evidence": evidence,
        **extra,
    }


def update_gate_state(run: Path, gate: str, passed: bool) -> None:
    state = load_state(run)
    state["gate_runs"][gate] = {"last_attempt_at": now(), "pass": bool(passed)}
    state["updated_at"] = now()
    write_json(run / STATE_NAME, state)


def run_gate_a(run: Path, runner: CommandRunner = run_command, current: dict[str, Any] | None = None) -> bool:
    state = load_state(run)
    assert_source_matches(state, current)
    commands = [
        ("preflight", ["./labctl", "preflight"]),
        ("test", ["./labctl", "test"]),
        ("config-check", ["./labctl", "config-check"]),
        ("render-compose", ["docker", "compose", "-f", "docker-compose.yml", "-f", "compose.production.yml", "config", "--no-interpolate"]),
    ]
    records, evidence = command_batch(run, "A", commands, runner)
    rendered_record = records[-1]
    rendered_log = run / rendered_record["log"]
    rendered = run / "rendered-compose.txt"
    rendered.write_text(rendered_log.read_text())
    evidence.append(evidence_entry(run, rendered, "rendered-compose-no-interpolation"))
    passed = all(item["exit_code"] == 0 for item in records) and rendered.stat().st_size > 0
    write_json(run / "static-review.json", artifact_payload(run, state, "A", "static-review.json", passed, evidence, commands=records))
    update_gate_state(run, "A", passed)
    return passed


def run_gate_b(run: Path, runner: CommandRunner = run_command, current: dict[str, Any] | None = None) -> bool:
    state = load_state(run)
    assert_source_matches(state, current)
    commands = [
        ("build", ["./labctl", "build"]),
        ("smoke", ["./labctl", "smoke"]),
        ("cargo", ["./labctl", "demo", "cargo"]),
        ("pms", ["./labctl", "demo", "pms"]),
        ("propulsion", ["./labctl", "demo", "propulsion"]),
        ("vessel", ["./labctl", "demo", "vessel"]),
    ]
    records, evidence = command_batch(run, "B", commands, runner)
    passed = all(item["exit_code"] == 0 for item in records)
    write_json(run / "process-io-commissioning.json", artifact_payload(run, state, "B", "process-io-commissioning.json", passed, evidence, commands=records))
    update_gate_state(run, "B", passed)
    return passed


def find_artifact(plan: dict[str, Any], artifact: str) -> tuple[str, dict[str, Any]]:
    for gate, gate_plan in plan["gates"].items():
        if artifact in gate_plan["artifacts"]:
            return gate, gate_plan["artifacts"][artifact]
    raise ValueError(f"Unknown acceptance artifact: {artifact}")


def validate_record_semantics(artifact: str, sources: dict[str, Path]) -> None:
    if artifact == "hmi-alarm-review.json":
        for label in ("cargo-screen", "pms-screen", "propulsion-screen", "alarm-screen"):
            if sources[label].suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                raise ValueError(f"{label} must be an image captured from the live HMI.")
    if artifact == "normal-baseline-run.json":
        metadata = read_json(sources["run-metadata"])
        evaluation = read_json(sources["evaluation"])
        if metadata.get("experiment_id") != "EXP-CARGO-NORMAL":
            raise ValueError("normal-baseline-run requires EXP-CARGO-NORMAL metadata.")
        if evaluation.get("pass") is not True:
            raise ValueError("normal-baseline-run evaluation did not pass.")
        read_json(sources["evidence-index"])
    if artifact == "plc-commissioning.json" and sources["normal-modbus-pcap"].suffix.lower() not in {".pcap", ".pcapng"}:
        raise ValueError("normal-modbus-pcap must be a PCAP/PCAPNG file.")


def record_artifact(run: Path, artifact: str, sources: dict[str, Path], note: str, operator: str, replace: bool = False, current: dict[str, Any] | None = None) -> Path:
    state = load_state(run)
    assert_source_matches(state, current)
    gate, spec = find_artifact(load_plan(), artifact)
    if spec.get("mode") != "recorded":
        raise ValueError(f"{artifact} is generated automatically and cannot be manually recorded.")
    required = set(spec.get("required_evidence_labels", []))
    supplied = set(sources)
    if supplied != required:
        raise ValueError(f"Evidence labels must be exactly {sorted(required)}; received {sorted(supplied)}")
    if len(note.strip()) < 20:
        raise ValueError("Record a concrete observation of at least 20 characters; a bare PASS is not evidence.")
    if not operator.strip():
        raise ValueError("Operator/reviewer identity is required.")
    for label, source in sources.items():
        if not source.exists() or path_size(source) == 0:
            raise ValueError(f"Evidence is missing or empty for {label}: {source}")
    validate_record_semantics(artifact, sources)
    destination_root = run / "attachments" / Path(artifact).stem
    if destination_root.exists():
        if not replace:
            raise ValueError(f"Recorded evidence already exists: {destination_root}. Use --replace deliberately to supersede it.")
        shutil.rmtree(destination_root)
    destination_root.mkdir(parents=True)
    retained: list[dict[str, Any]] = []
    for label, source in sorted(sources.items()):
        suffix = source.suffix if source.is_file() else ""
        destination = destination_root / f"{label}{suffix}"
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        retained.append(evidence_entry(run, destination, label))
    payload = artifact_payload(run, state, gate, artifact, True, retained, operator=operator, observation=note.strip(), evidence_labels=sorted(sources))
    output = run / artifact
    write_json(output, payload)
    update_gate_state(run, gate, False)
    return output


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    evidence_root = (ROOT / "evidence").resolve()
    if evidence_root != resolved and evidence_root not in resolved.parents:
        raise ValueError("Automated commissioning runs must be under this repository's evidence directory.")
    return str(resolved.relative_to(ROOT.resolve()))


def run_gate_d(run: Path, runner: CommandRunner = run_command, current: dict[str, Any] | None = None) -> bool:
    from evidence.build_acceptance_dossier import build

    state = load_state(run)
    assert_source_matches(state, current)
    partial = build(run, DOSSIER_CONTRACT)
    if not partial["gates"]["C"]["pass"]:
        raise ValueError("Gate C evidence must pass before live OPC UA/historian commissioning.")
    rel = repo_relative(run)
    outdir = f"{rel}/opcua"
    freshness = f"{rel}/historian"
    commands: list[tuple[str, list[str]]] = []
    for domain in DOMAINS:
        commands.extend([
            (f"{domain}-opcua", ["./labctl", "opcua", domain, outdir]),
            (f"{domain}-bind", ["./labctl", "bind-plan", domain, outdir]),
            (f"{domain}-historian", ["./labctl", "hist-install", domain, outdir]),
            (f"{domain}-freshness", ["./labctl", "hist-fresh", domain, "--threshold", "5", "--out", f"{freshness}/{domain}-freshness.json"]),
        ])
    records, logs = command_batch(run, "D", commands, runner)
    discovery_evidence = list(logs)
    historian_evidence = list(logs)
    semantic_errors: list[str] = []
    for domain in DOMAINS:
        discovery = run / "opcua" / f"{domain}-opcua-discovery.json"
        discovery_md = run / "opcua" / f"{domain}-opcua-discovery.md"
        plan_path = run / "opcua" / f"{domain}-binding-plan.json"
        fragment = run / "opcua" / f"{domain}-telegraf-fragment.conf"
        fresh = run / "historian" / f"{domain}-freshness.json"
        for path, label, target in [
            (discovery, f"{domain}-discovery-json", discovery_evidence),
            (discovery_md, f"{domain}-discovery-markdown", discovery_evidence),
            (plan_path, f"{domain}-binding-plan", historian_evidence),
            (fragment, f"{domain}-telegraf-fragment", historian_evidence),
            (fresh, f"{domain}-historian-freshness", historian_evidence),
        ]:
            if path.is_file() and path.stat().st_size:
                target.append(evidence_entry(run, path, label))
            else:
                semantic_errors.append(f"missing {path.relative_to(run)}")
        if plan_path.is_file():
            plan = read_json(plan_path)
            if plan.get("missing") or plan.get("ambiguous") or not plan.get("bindings"):
                semantic_errors.append(f"{domain} binding plan is incomplete")
    commands_pass = all(item["exit_code"] == 0 for item in records)
    passed = commands_pass and not semantic_errors
    write_json(run / "opcua-discovery-index.json", artifact_payload(run, state, "D", "opcua-discovery-index.json", passed, discovery_evidence, commands=records, semantic_errors=semantic_errors))
    write_json(run / "historian-binding-review.json", artifact_payload(run, state, "D", "historian-binding-review.json", passed, historian_evidence, commands=records, semantic_errors=semantic_errors))
    update_gate_state(run, "D", passed)
    return passed


def run_git_metadata(run_data: dict[str, Any]) -> tuple[str | None, bool | None]:
    nested = run_data.get("git") if isinstance(run_data.get("git"), dict) else {}
    commit = nested.get("commit") or run_data.get("git_commit")
    dirty = nested.get("tree_dirty") if "tree_dirty" in nested else run_data.get("tree_dirty")
    return commit, dirty


def discover_runs(experiment_root: Path, expected_commit: str) -> dict[str, list[Path]]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    if not experiment_root.is_dir():
        return grouped
    for candidate in sorted(path for path in experiment_root.iterdir() if path.is_dir()):
        metadata_path = candidate / "run.json"
        evaluation_path = candidate / "evaluation.json"
        index_path = candidate / "evidence-index.json"
        if not (metadata_path.is_file() and evaluation_path.is_file() and index_path.is_file()):
            continue
        try:
            metadata = read_json(metadata_path)
            evaluation = read_json(evaluation_path)
        except (ValueError, json.JSONDecodeError):
            continue
        commit, dirty = run_git_metadata(metadata)
        experiment = metadata.get("experiment_id")
        if commit == expected_commit and dirty is False and evaluation.get("pass") is True and isinstance(experiment, str):
            grouped[experiment].append(candidate)
    return grouped


def run_gate_f(run: Path, experiment_root: Path, runner: CommandRunner = run_command, current: dict[str, Any] | None = None) -> bool:
    from evidence.aggregate_runs import aggregate

    state = load_state(run)
    assert_source_matches(state, current)
    expected = [item["id"] for item in read_json(EXPERIMENT_MANIFEST)["experiments"]]
    minimum = int(load_plan()["minimum_experiment_repeats"])
    grouped = discover_runs(experiment_root, state["project"]["git_commit"])
    verified_dir = run / "experiments" / "verified"
    aggregation_dir = run / "experiments" / "aggregations"
    verified_dir.mkdir(parents=True, exist_ok=True)
    aggregation_dir.mkdir(parents=True, exist_ok=True)
    index_rows: list[dict[str, Any]] = []
    verification_evidence: list[dict[str, Any]] = []
    aggregation_evidence: list[dict[str, Any]] = []
    aggregate_rows: dict[str, Any] = {}
    all_pass = True
    for experiment in expected:
        candidates = grouped.get(experiment, [])
        verified: list[Path] = []
        for candidate in candidates:
            code, output = runner(["./labctl", "verify-run", str(candidate)])
            verification = verified_dir / experiment.lower() / f"{candidate.name}.json"
            verification.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "experiment_id": experiment,
                "source_run": str(candidate),
                "verified_at": now(),
                "pass": code == 0,
                "verify_output": output[-4000:],
                "run_sha256": sha256_file(candidate / "run.json"),
                "evaluation_sha256": sha256_file(candidate / "evaluation.json"),
                "evidence_index_sha256": sha256_file(candidate / "evidence-index.json"),
            }
            write_json(verification, record)
            verification_evidence.append(evidence_entry(run, verification, f"{experiment}-{candidate.name}"))
            if code == 0:
                verified.append(candidate)
        result = aggregate(verified, minimum)
        aggregate_path = aggregation_dir / f"{experiment.lower()}-aggregation.json"
        write_json(aggregate_path, result)
        aggregation_evidence.append(evidence_entry(run, aggregate_path, experiment))
        aggregate_rows[experiment] = result
        experiment_pass = result.get("claim_ready") is True
        all_pass = all_pass and experiment_pass
        index_rows.append({"experiment_id": experiment, "discovered": len(candidates), "verified": len(verified), "minimum_required": minimum, "pass": experiment_pass})
    write_json(run / "experiment-run-index.json", artifact_payload(run, state, "F", "experiment-run-index.json", all_pass, verification_evidence, experiments=index_rows, experiment_root=str(experiment_root)))
    write_json(run / "repeated-run-aggregation.json", artifact_payload(run, state, "F", "repeated-run-aggregation.json", all_pass, aggregation_evidence, minimum_repeats=minimum, aggregations=aggregate_rows))
    update_gate_state(run, "F", all_pass)
    return all_pass


def run_gate_g_resources(run: Path, samples: int, interval: float, runner: CommandRunner = run_command, current: dict[str, Any] | None = None) -> bool:
    state = load_state(run)
    assert_source_matches(state, current)
    rel = repo_relative(run)
    command = ["./labctl", "profile-resources", "--samples", str(samples), "--interval", str(interval), "--out", f"{rel}/resources"]
    records, logs = command_batch(run, "G", [("resource-profile", command)], runner)
    source_meta = run / "resources" / "resource-profile.json"
    stats = run / "resources" / "docker-stats.jsonl"
    evidence = list(logs)
    if source_meta.is_file():
        evidence.append(evidence_entry(run, source_meta, "resource-profile-metadata"))
    if stats.is_file():
        evidence.append(evidence_entry(run, stats, "docker-stats"))
    meta = read_json(source_meta) if source_meta.is_file() else {}
    passed = records[0]["exit_code"] == 0 and meta.get("rows", 0) > 0 and stats.is_file() and stats.stat().st_size > 0
    write_json(run / "resource-profile.json", artifact_payload(run, state, "G", "resource-profile.json", passed, evidence, commands=records, measurement=meta))
    update_gate_state(run, "G", False)
    return passed


def dossier(run: Path) -> dict[str, Any]:
    from evidence.build_acceptance_dossier import build
    return build(run, DOSSIER_CONTRACT)


def print_status(run: Path) -> dict[str, Any]:
    result = dossier(run)
    print(f"Commissioning run: {run}")
    print(f"Git commit: {load_state(run)['project']['git_commit']}")
    for gate, item in result["gates"].items():
        status = "PASS" if item["pass"] else "BLOCKED"
        missing = [artifact["path"] for artifact in item["artifacts"] if not artifact["pass"]]
        suffix = "" if not missing else " — " + ", ".join(missing)
        print(f"Gate {gate}: {status}{suffix}")
    print("FINAL: " + ("PASS" if result["pass"] else "NOT YET COMMISSIONED"))
    return result


def print_record_guidance(run: Path, gate: str) -> None:
    plan = load_plan()["gates"][gate]
    print(f"Gate {gate} requires retained live-system evidence: {plan['title']}")
    for artifact, spec in plan["artifacts"].items():
        if spec.get("mode") != "recorded" or (run / artifact).is_file():
            continue
        labels = " ".join(f"--evidence {label}=PATH" for label in spec["required_evidence_labels"])
        print(f"  ./labctl commission record {run} {artifact} {labels} --operator NAME --note 'Describe the observed causal result' ")


def resume(run: Path, experiment_root: Path, samples: int, interval: float) -> int:
    result = dossier(run)
    for gate in "ABCDEFG":
        if result["gates"][gate]["pass"]:
            continue
        if gate == "A":
            return 0 if run_gate_a(run) else 2
        if gate == "B":
            return 0 if run_gate_b(run) else 2
        if gate in {"C", "E"}:
            print_record_guidance(run, gate)
            return 3
        if gate == "D":
            return 0 if run_gate_d(run) else 2
        if gate == "F":
            return 0 if run_gate_f(run, experiment_root) else 3
        if gate == "G":
            if not (run / "resource-profile.json").is_file():
                return 0 if run_gate_g_resources(run, samples, interval) else 2
            print_record_guidance(run, gate)
            return 3
    return finalize(run)


def finalize(run: Path) -> int:
    result = dossier(run)
    write_json(run / "acceptance-dossier.json", result)
    state = load_state(run)
    state["updated_at"] = now()
    state["status"] = "accepted" if result["pass"] else "blocked"
    write_json(run / STATE_NAME, state)
    print_status(run)
    print(f"Dossier: {run / 'acceptance-dossier.json'}")
    return 0 if result["pass"] else 2


def parse_evidence(values: list[str]) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--evidence must use LABEL=PATH")
        label, path = value.split("=", 1)
        if not re.fullmatch(r"[a-z0-9-]+", label):
            raise ValueError(f"Invalid evidence label: {label}")
        if label in parsed:
            raise ValueError(f"Duplicate evidence label: {label}")
        parsed[label] = Path(path)
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Run and resume evidence-backed target-server commissioning.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create an empty commissioning evidence run")
    init.add_argument("--root", type=Path, default=Path("evidence/commissioning"))
    start = sub.add_parser("start", help="Create a run and execute automatic Gates A and B")
    start.add_argument("--root", type=Path, default=Path("evidence/commissioning"))
    status = sub.add_parser("status", help="Show pass/block state for every gate")
    status.add_argument("run", type=Path)
    run_parser = sub.add_parser("run", help="Run one automatic gate")
    run_parser.add_argument("run", type=Path)
    run_parser.add_argument("--gate", choices=["A", "B", "D", "F", "G"], required=True)
    run_parser.add_argument("--experiment-root", type=Path, default=Path("evidence/runs"))
    run_parser.add_argument("--samples", type=int, default=24)
    run_parser.add_argument("--interval", type=float, default=5.0)
    resume_parser = sub.add_parser("resume", help="Run the next automatic gate or print the exact live evidence needed")
    resume_parser.add_argument("run", type=Path)
    resume_parser.add_argument("--experiment-root", type=Path, default=Path("evidence/runs"))
    resume_parser.add_argument("--samples", type=int, default=24)
    resume_parser.add_argument("--interval", type=float, default=5.0)
    record = sub.add_parser("record", help="Copy and hash required live evidence into a recorded artifact")
    record.add_argument("run", type=Path)
    record.add_argument("artifact")
    record.add_argument("--evidence", action="append", default=[], metavar="LABEL=PATH")
    record.add_argument("--operator", default=os.getenv("USER", ""))
    record.add_argument("--note", required=True)
    record.add_argument("--replace", action="store_true")
    final = sub.add_parser("finalize", help="Build the final dossier; fail unless every artifact is valid")
    final.add_argument("run", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            print(initialise(args.root))
            return
        if args.command == "start":
            run = initialise(args.root)
            print(f"Commissioning run: {run}")
            if not run_gate_a(run) or not run_gate_b(run):
                print_status(run)
                raise SystemExit(2)
            print_status(run)
            print_record_guidance(run, "C")
            return
        if args.command == "status":
            print_status(args.run)
            return
        if args.command == "record":
            print(record_artifact(args.run, args.artifact, parse_evidence(args.evidence), args.note, args.operator, args.replace))
            return
        if args.command == "run":
            functions = {
                "A": lambda: run_gate_a(args.run),
                "B": lambda: run_gate_b(args.run),
                "D": lambda: run_gate_d(args.run),
                "F": lambda: run_gate_f(args.run, args.experiment_root),
                "G": lambda: run_gate_g_resources(args.run, args.samples, args.interval),
            }
            raise SystemExit(0 if functions[args.gate]() else 2)
        if args.command == "resume":
            raise SystemExit(resume(args.run, args.experiment_root, args.samples, args.interval))
        if args.command == "finalize":
            raise SystemExit(finalize(args.run))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"COMMISSIONING BLOCKED: {error}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
