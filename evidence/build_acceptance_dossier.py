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
    gates = {}
    for gate, names in contract["gates"].items():
        artifacts = []
        for name in names:
            path = root / name
            present = path.is_file() and path.stat().st_size > 0
            artifacts.append({
                "path": name,
                "present": present,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if present else None,
            })
        gates[gate] = {"pass": all(item["present"] for item in artifacts), "artifacts": artifacts}
    return {
        "schema_version": 1,
        "evidence_root": str(root),
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
