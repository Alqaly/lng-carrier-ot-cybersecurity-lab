#!/usr/bin/env python3
"""Inspect and validate the same learning contract consumed by the website."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/assets/learning-journey.json"


def validate(data: dict, root: Path = ROOT) -> list[str]:
    errors = []
    if data.get("schema_version") != 1 or not data.get("claim_boundary"):
        errors.append("learning contract needs schema_version=1 and claim_boundary")
    modules = data.get("modules", [])
    ids = [item.get("id") for item in modules]
    if len(ids) != len(set(ids)) or ids != [f"{i:02d}" for i in range(1, 11)]:
        errors.append("journey must map chapters 01–10 exactly once in order")
    seen = set()
    chapters = set()
    for item in modules:
        identity = item.get("id")
        for field in ("title", "phase", "objective", "practice", "evidence", "explain", "checkpoint"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{identity}: missing {field}")
        path = Path(item.get("chapter", ""))
        resolved = (root / "docs" / path).resolve()
        if path.is_absolute() or ".." in path.parts or not resolved.is_relative_to((root / "docs").resolve()) or not resolved.is_file():
            errors.append(f"{identity}: invalid chapter path")
        chapters.add(str(path))
        if not set(item.get("prerequisites", [])) <= seen:
            errors.append(f"{identity}: prerequisites must refer to earlier modules (no cycles)")
        if not item.get("tracks") or not set(item["tracks"]) <= set(data.get("tracks", {})):
            errors.append(f"{identity}: unknown or empty track")
        seen.add(identity)
    expected = {str(path.relative_to(root / "docs")) for path in (root / "docs/course").glob("[0-9][0-9]-*.md")}
    if chapters != expected:
        errors.append("course chapter coverage has drifted")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=("list", "check", "show"), default="list")
    parser.add_argument("module", nargs="?")
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text())
    errors = validate(data)
    if errors:
        parser.exit(2, "LEARNING CONTRACT FAIL\n" + "\n".join(errors) + "\n")
    if args.action == "check":
        print("LEARNING CONTRACT PASS — ten mapped chapters, ordered prerequisites and evidence checkpoints")
    elif args.action == "show":
        item = next((m for m in data["modules"] if m["id"] == str(args.module).zfill(2)), None)
        if item is None:
            parser.error("show requires a module number from 01 to 10")
        for key in ("title", "chapter", "objective", "practice", "evidence", "explain", "checkpoint"):
            print(f"{key.upper()}: {item[key]}")
    else:
        for item in data["modules"]:
            print(f"{item['id']}  {item['phase']:12} {item['title']}")
        print("\nNext: ./labctl learn show 01")
    print(data["claim_boundary"])


if __name__ == "__main__":
    main()
