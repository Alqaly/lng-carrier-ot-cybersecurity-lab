import json
from pathlib import Path

import pytest

from commissioning import acceptance_orchestrator as commission
from evidence.build_acceptance_dossier import build
from experiments.verify_run import verify

ROOT = Path(__file__).resolve().parents[1]


def snapshot():
    return {
        "git_commit": "abc", "git_tree": "synthetic-test-tree", "tree_dirty": False,
        "release_manifest_sha256": commission.sha256_file(ROOT / "release-manifest.json"),
        "commissioning_plan_sha256": commission.sha256_file(commission.PLAN_PATH),
        "dossier_contract_sha256": commission.sha256_file(commission.DOSSIER_CONTRACT),
    }


def test_baseline_retains_complete_run_and_rejects_wrong_commit(evaluated_run, tmp_path):
    current = snapshot()
    run = commission.initialise(tmp_path / "acceptance", current)
    source = evaluated_run("baseline")
    output = commission.record_artifact(run, "normal-baseline-run.json", {"baseline-run": source}, "Normal transfer observed with the required retained evidence.", "test-operator", current=current)
    payload = json.loads(output.read_text())
    retained = run / payload["evidence"][0]["path"]
    assert verify(retained)["pass"]
    (source / "cargo-state.jsonl").write_text("external source changed\n")
    assert verify(retained)["pass"]
    wrong = evaluated_run("different-commit", commit="other")
    with pytest.raises(ValueError, match="clean source commit"):
        commission.record_artifact(run, "normal-baseline-run.json", {"baseline-run": wrong}, "This run came from another source revision.", "test-operator", replace=True, current=current)
    assert verify(retained)["pass"]


def test_gate_f_retains_verified_repeats_without_external_dependency(evaluated_run, tmp_path, monkeypatch):
    current = snapshot()
    run = commission.initialise(tmp_path / "acceptance", current)
    sources = [evaluated_run("runs/normal-" + str(i)) for i in range(3)]
    # Restrict only this orchestration unit test to one real registered experiment.
    manifest = tmp_path / "one-experiment.json"
    manifest.write_text(json.dumps({"experiments": [{"id": "EXP-CARGO-NORMAL"}]}))
    monkeypatch.setattr(commission, "EXPERIMENT_MANIFEST", manifest)
    assert commission.run_gate_f(run, tmp_path / "runs", runner=lambda command: (0, "unit-test runner"), current=current)
    payload = json.loads((run / "experiment-run-index.json").read_text())
    retained = [run / e["path"] for e in payload["evidence"] if e["kind"] == "directory"]
    assert len(retained) == 3
    for source in sources:
        (source / "cargo-state.jsonl").write_text("changed externally\n")
    assert all(verify(path)["pass"] for path in retained)
    (retained[0] / "cargo-state.jsonl").write_text("tampered acceptance copy\n")
    result = build(run, commission.DOSSIER_CONTRACT)
    assert result["gates"]["F"]["pass"] is False


def test_dossier_accepts_required_manual_maps_and_rejects_provenance_drift(tmp_path):
    current = snapshot()
    run = commission.initialise(tmp_path / "acceptance", current)
    sources = {}
    for label in ("cargo-map", "pms-map", "propulsion-map"):
        source = tmp_path / (label + ".txt")
        source.write_text("Synthetic map-review fixture, not live acceptance.")
        sources[label] = source
    output = commission.record_artifact(run, "plc-io-map-review.json", sources, "The three map review records were retained for this unit test.", "test-operator", current=current)
    result = build(run, commission.DOSSIER_CONTRACT)
    artifact = next(a for a in result["gates"]["C"]["artifacts"] if a["path"] == output.name)
    assert artifact["pass"]
    payload = json.loads(output.read_text())
    payload["project"]["git_tree"] = "wrong-tree"
    output.write_text(json.dumps(payload))
    result = build(run, commission.DOSSIER_CONTRACT)
    assert not next(a for a in result["gates"]["C"]["artifacts"] if a["path"] == output.name)["pass"]
