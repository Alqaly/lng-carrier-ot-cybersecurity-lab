#!/usr/bin/env python3
"""Build an evidence-backed Gates A-G acceptance dossier."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def build(root: Path, contract_path: Path) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text())
    state_path = root / "commissioning-state.json"
    state = json.loads(state_path.read_text()) if state_path.is_file() else {}
    expected_commit = state.get("project", {}).get("git_commit")
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
                artifact_commit = payload.get("project", {}).get("git_commit")
                if not expected_commit:
                    problems.append("commissioning-state.json with Git provenance is missing")
                elif artifact_commit != expected_commit:
                    problems.append(f"Git commit mismatch: {artifact_commit} != {expected_commit}")
                evidence = payload.get("evidence")
                if not isinstance(evidence, list) or not evidence:
                    problems.append("artifact has no retained evidence entries")
                    evidence = []
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
                    if retained.is_dir():
                        digest = hashlib.sha256()
                        for item in sorted(p for p in retained.rglob("*") if p.is_file()):
                            digest.update(str(item.relative_to(retained)).encode())
                            digest.update(b"\0")
                            digest.update(bytes.fromhex(hashlib.sha256(item.read_bytes()).hexdigest()))
                        actual = digest.hexdigest()
                    else:
                        actual = hashlib.sha256(retained.read_bytes()).hexdigest()
                    if actual != entry["sha256"]:
                        problems.append(f"evidence hash mismatch: {evidence_path}")
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
