#!/usr/bin/env python3
"""Build an evidence-backed Gates A-G acceptance dossier."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PLAN_PATH = Path(__file__).resolve().parents[1] / "commissioning/commissioning-plan.json"
ROOT = PLAN_PATH.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(root: Path, contract_path: Path) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text())
    state_path = root / "commissioning-state.json"
    try:
        state = json.loads(state_path.read_text()) if state_path.is_file() else {}
    except (ValueError, OSError):
        state = {}
    project = state.get("project", {}) if isinstance(state, dict) else {}
    if not isinstance(project, dict):
        project = {}
    expected_commit = project.get("git_commit")
    plan = json.loads(PLAN_PATH.read_text())
    gates = {}
    for gate, names in contract["gates"].items():
        artifacts = []
        for name in names:
            path = root / name
            present = path.is_file() and path.stat().st_size > 0
            problems = []
            if present and path.suffix == ".json":
                try:
                    payload = json.loads(path.read_text())
                except (json.JSONDecodeError, UnicodeDecodeError) as error:
                    problems.append(f"invalid JSON: {error}")
                    payload = {}
                if not isinstance(payload, dict):
                    problems.append("artifact must be a JSON object")
                    payload = {}
                if payload.get("artifact") != name:
                    problems.append("artifact identity does not match filename")
                if payload.get("gate") != gate:
                    problems.append("gate identity does not match contract")
                if payload.get("pass") is not True:
                    problems.append("artifact does not record pass=true")
                artifact_project = payload.get("project", {})
                if not isinstance(artifact_project, dict):
                    artifact_project = {}
                artifact_commit = artifact_project.get("git_commit")
                if not expected_commit:
                    problems.append("commissioning-state.json with Git provenance is missing")
                elif artifact_commit != expected_commit:
                    problems.append(f"Git commit mismatch: {artifact_commit} != {expected_commit}")
                if project.get("tree_dirty") is not False or artifact_project != project:
                    problems.append("artifact provenance must match the clean commissioning snapshot")
                if payload.get("semantic_errors"):
                    problems.append("artifact records semantic errors")
                required_commands = {
                    "static-review.json": ["preflight", "test", "config-check", "render-compose"],
                    "process-io-commissioning.json": ["build", "smoke", "pms", "cargo", "propulsion", "vessel"],
                    "opcua-discovery-index.json": [f"{domain}-{action}" for domain in ("cargo", "pms", "propulsion") for action in ("opcua", "bind", "historian", "freshness")],
                    "historian-binding-review.json": [f"{domain}-{action}" for domain in ("cargo", "pms", "propulsion") for action in ("opcua", "bind", "historian", "freshness")],
                    "resource-profile.json": ["resource-profile"],
                }.get(name)
                if required_commands is not None:
                    commands = payload.get("commands", [])
                    if not isinstance(commands, list) or [item.get("label") for item in commands if isinstance(item, dict)] != required_commands:
                        problems.append("automatic artifact is missing its exact command sequence")
                if "commands" in payload:
                    commands = payload["commands"]
                    if not isinstance(commands, list) or not commands or any(not isinstance(c, dict) or type(c.get("exit_code")) is not int or c["exit_code"] != 0 for c in commands):
                        problems.append("automatic command results did not all succeed")
                evidence = payload.get("evidence")
                if not isinstance(evidence, list) or not evidence:
                    problems.append("artifact has no retained evidence entries")
                    evidence = []
                spec = plan["gates"].get(gate, {}).get("artifacts", {}).get(name, {})
                if spec.get("mode") == "recorded":
                    labels = [item.get("label") for item in evidence if isinstance(item, dict)]
                    if sorted(labels, key=str) != sorted(spec["required_evidence_labels"]):
                        problems.append("recorded artifact must retain the exact required evidence labels")
                    if not isinstance(payload.get("operator"), str) or not payload["operator"].strip() or len(str(payload.get("observation", "")).strip()) < 20:
                        problems.append("recorded artifact requires an operator and concrete observation")
                for entry in evidence:
                    if not isinstance(entry, dict) or not entry.get("path") or not entry.get("sha256"):
                        problems.append("malformed evidence entry")
                        continue
                    evidence_path = Path(str(entry["path"]))
                    if evidence_path.is_absolute() or ".." in evidence_path.parts:
                        problems.append(f"evidence path escapes run: {evidence_path}")
                        continue
                    retained = (root / evidence_path).resolve()
                    if root.resolve() != retained and root.resolve() not in retained.parents:
                        problems.append(f"evidence path escapes run: {evidence_path}")
                        continue
                    if not retained.exists():
                        problems.append(f"retained evidence missing: {evidence_path}")
                        continue
                    if (root / evidence_path).is_symlink() or (retained.is_dir() and any(p.is_symlink() for p in retained.rglob("*"))):
                        problems.append(f"symbolic links are not retained evidence: {evidence_path}")
                        continue
                    if retained.is_dir():
                        digest = hashlib.sha256()
                        for item in sorted(p for p in retained.rglob("*") if p.is_file()):
                            digest.update(str(item.relative_to(retained)).encode())
                            digest.update(b"\0")
                            digest.update(bytes.fromhex(file_hash(item)))
                        actual = digest.hexdigest()
                    else:
                        actual = file_hash(retained)
                    if actual != entry["sha256"]:
                        problems.append(f"evidence hash mismatch: {evidence_path}")
                    if name == "normal-baseline-run.json" and entry.get("label") == "baseline-run":
                        from experiments.verify_run import verify
                        result = verify(retained)
                        if not result["pass"] or result["experiment_id"] != "EXP-CARGO-NORMAL":
                            problems.append("retained normal baseline failed semantic verification")
                    if name == "experiment-run-index.json" and entry.get("kind") == "directory":
                        from experiments.verify_run import verify
                        if not verify(retained)["pass"]:
                            problems.append("retained repeated experiment failed semantic verification")
            artifacts.append({
                "path": name,
                "present": present,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if present else None,
                "semantic_errors": problems,
                "pass": present and not problems,
            })
        gates[gate] = {"pass": all(item["pass"] for item in artifacts), "artifacts": artifacts}
    return {
        "schema_version": 2,
        "evidence_root": str(root),
        "git_commit": expected_commit,
        "gates": gates,
        "pass": all(item["pass"] for item in gates.values()),
        "claim_boundary": contract["rule"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Gates A-G acceptance dossier from retained artifacts.")
    parser.add_argument("evidence_root", type=Path)
    parser.add_argument("--contract", type=Path, default=Path("evidence/acceptance-dossier-contract.json"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = build(args.evidence_root, args.contract)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    print(rendered, end="")
    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
