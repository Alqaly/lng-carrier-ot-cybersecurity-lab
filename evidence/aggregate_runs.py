#!/usr/bin/env python3
"""Aggregate repeated evaluator outputs without manufacturing missing metrics."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def aggregate(run_dirs: list[Path], minimum_repeats: int = 3) -> dict[str, Any]:
    records = []
    for run_dir in run_dirs:
        evaluation_path = run_dir / "evaluation.json"
        run_path = run_dir / "run.json"
        if not evaluation_path.exists() or not run_path.exists():
            records.append({"run": str(run_dir), "usable": False, "reason": "missing run.json or evaluation.json"})
            continue
        evaluation = json.loads(evaluation_path.read_text())
        run = json.loads(run_path.read_text())
        records.append({
            "run": str(run_dir),
            "usable": bool(evaluation.get("pass")),
            "experiment_id": run.get("experiment_id"),
            "git_commit": run.get("git_commit"),
            "tree_dirty": run.get("tree_dirty"),
            "metrics": evaluation.get("metrics", {}),
        })

    usable = [record for record in records if record.get("usable")]
    experiments = Counter(record.get("experiment_id") for record in usable)
    commits = sorted({record.get("git_commit") for record in usable if record.get("git_commit")})
    dirty = any(bool(record.get("tree_dirty")) for record in usable)
    metrics: dict[str, Any] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in usable:
        for name, value in record.get("metrics", {}).items():
            grouped[name].append(value)
    for name, values in grouped.items():
        measured = [value for value in values if value.get("status") == "measured" and isinstance(value.get("value"), (int, float))]
        unavailable = [value.get("reason", "unspecified") for value in values if value.get("status") == "unavailable"]
        item: dict[str, Any] = {
            "measured_count": len(measured),
            "unavailable_count": len(unavailable),
            "unavailable_reasons": dict(Counter(unavailable)),
        }
        if measured:
            numeric = [float(value["value"]) for value in measured]
            units = sorted({str(value.get("unit")) for value in measured})
            item.update({"mean": statistics.fmean(numeric), "minimum": min(numeric), "maximum": max(numeric), "units": units})
        metrics[name] = item

    same_experiment = len(experiments) == 1
    same_commit = len(commits) == 1
    repeat_count = len(usable)
    return {
        "schema_version": 1,
        "minimum_repeats": minimum_repeats,
        "total_inputs": len(run_dirs),
        "usable_runs": repeat_count,
        "experiment_counts": dict(experiments),
        "git_commits": commits,
        "contains_dirty_run": dirty,
        "comparable": same_experiment and same_commit and not dirty,
        "claim_ready": repeat_count >= minimum_repeats and same_experiment and same_commit and not dirty,
        "metrics": metrics,
        "runs": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate repeated LNG lab experiment evaluations.")
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--minimum-repeats", type=int, default=3)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = aggregate(args.runs, args.minimum_repeats)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
