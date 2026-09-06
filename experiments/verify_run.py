#!/usr/bin/env python3
"""Read-only verification of complete evidence, metadata and causal evaluation.

Checksums establish integrity relative to retained files, not authenticity of an
operator's observations. Legacy evaluations must be explicitly re-evaluated.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from experiments.evaluate import evaluate, sha256


def verify(run: Path) -> dict:
    problems = []
    experiment = None
    count = 0
    try:
        run = run.resolve()
        documents = {}
        for name in ("run.json", "evaluation.json", "evidence-index.json"):
            path = run / name
            if path.is_symlink():
                raise ValueError(f"{name}: symbolic links are not retained run metadata")
            documents[name] = json.loads(path.read_text())
            if not isinstance(documents[name], dict):
                raise ValueError(f"{name}: expected a JSON object")
        metadata, evaluation, index = (documents[name] for name in ("run.json", "evaluation.json", "evidence-index.json"))
        experiment = metadata.get("experiment_id")
        if "evidence_files" in metadata and not isinstance(metadata["evidence_files"], dict):
            raise ValueError("evidence_files must be a mapping of evidence keys to paths")
        manifest = json.loads((ROOT / "experiments/manifest.json").read_text())
        specification = next((item for item in manifest["experiments"] if item["id"] == experiment), None)
        if specification is None:
            raise ValueError("unregistered experiment_id")
        if evaluation.get("experiment_id") != experiment or index.get("experiment_id") != experiment:
            problems.append("experiment identity differs across run, evaluation and index")
        if evaluation.get("pass") is not True:
            problems.append("evaluation did not pass")
        metadata_hash = sha256(run / "run.json")
        if index.get("schema_version") != 2 or any(doc.get("run_metadata_sha256") != metadata_hash for doc in (index, evaluation)):
            problems.append("run metadata changed or evaluation is legacy; explicitly run labctl evaluate again")
        artifacts = index.get("artifacts")
        if not isinstance(artifacts, dict) or set(artifacts) != set(specification["required_evidence"]):
            raise ValueError("artifact index must contain the exact non-empty required evidence set")
        if artifacts != evaluation.get("artifacts"):
            problems.append("artifact index differs from evaluated artifacts")
        retained_paths = set()
        for key, item in artifacts.items():
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                problems.append(f"{key}: malformed artifact entry")
                continue
            relative = Path(item["path"])
            path = run / relative
            if relative.is_absolute() or ".." in relative.parts or not path.resolve().is_relative_to(run):
                problems.append(f"{key}: evidence path escapes run")
                continue
            if path.resolve() in retained_paths:
                problems.append(f"{key}: duplicate evidence path")
            retained_paths.add(path.resolve())
            if not path.is_file():
                problems.append(f"{key}: missing retained file")
            elif sha256(path) != item.get("sha256") or path.stat().st_size != item.get("bytes"):
                problems.append(f"{key}: SHA-256 or size mismatch")
            else:
                count += 1
        if not problems:
            # Recompute from current manifest and files without rewriting proof.
            fresh = evaluate(run, write=False)
            if fresh.get("pass") is not True or fresh != evaluation:
                problems.append("retained evaluation differs from read-only semantic re-evaluation")
    except (OSError, ValueError, TypeError, KeyError, StopIteration, RuntimeError) as error:
        problems.append(f"invalid or incomplete evidence: {error}")
    return {"schema_version": 2, "experiment_id": experiment, "verified_artifacts": count, "problems": problems, "pass": not problems}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    result = verify(args.run_dir)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
