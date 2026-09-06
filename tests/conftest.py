"""Synthetic fixtures for code regression tests; never target-host evidence."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def evaluated_run(tmp_path):
    from experiments.evaluate import evaluate

    def create(name="normal", response=1.0, commit="abc", dirty=False, nested=True):
        run = tmp_path / name
        run.mkdir(parents=True)
        metadata = {"schema_version": 2, "experiment_id": "EXP-CARGO-NORMAL", "created_at": name, "notes": "SYNTHETIC UNIT TEST ONLY"}
        if nested:
            metadata["git"] = {"commit": commit, "tree_dirty": dirty}
        else:
            metadata.update({"git_commit": commit, "tree_dirty": dirty})
        (run / "run.json").write_text(json.dumps(metadata))
        (run / "cargo-modbus.pcap").write_bytes(b"\xd4\xc3\xb2\xa1" + b"\0" * 24)
        rows = [
            {"source_time_s": 0, "state": {"pumpCmd": True, "valveCommand": 1, "pumpFeedback": False, "valveFeedback": False, "flowMeasured": 0}},
            {"source_time_s": response, "state": {"pumpCmd": True, "valveCommand": 1, "pumpFeedback": True, "valveFeedback": True, "flowMeasured": .4}},
        ]
        (run / "cargo-state.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        (run / "alarm-timeline.jsonl").write_text("")
        assert evaluate(run)["pass"]
        return run

    return create
