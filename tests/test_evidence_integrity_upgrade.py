import json
import shutil

from evidence.aggregate_runs import aggregate
from experiments.evaluate import evaluate
from experiments.verify_run import verify


def edit(path, change):
    value = json.loads(path.read_text())
    change(value)
    path.write_text(json.dumps(value))


def test_verification_is_read_only_and_accepts_evaluated_evidence(evaluated_run):
    run = evaluated_run()
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in run.iterdir()}
    assert verify(run)["pass"]
    assert before == {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in run.iterdir()}


def test_empty_index_cannot_pass(evaluated_run):
    run = evaluated_run()
    edit(run / "evidence-index.json", lambda d: d.update(artifacts={}))
    assert not verify(run)["pass"]


def test_failed_or_string_pass_evaluation_cannot_verify(evaluated_run):
    for i, value in enumerate((False, "true", 1, None)):
        run = evaluated_run(str(i))
        edit(run / "evaluation.json", lambda d: d.update({"pass": value}))
        assert not verify(run)["pass"]


def test_wrong_experiment_and_malformed_indexes_fail_closed(evaluated_run):
    run = evaluated_run()
    edit(run / "evidence-index.json", lambda d: d.update(experiment_id="EXP-PMS-GEN-TRIP"))
    assert not verify(run)["pass"]
    for value in ([], None, {"artifacts": []}, {"artifacts": {"x": 1}}):
        (run / "evidence-index.json").write_text(json.dumps(value))
        assert not verify(run)["pass"]


def test_metadata_changes_require_explicit_re_evaluation(evaluated_run):
    run = evaluated_run()
    edit(run / "run.json", lambda d: d["git"].update(commit="different"))
    assert not verify(run)["pass"]


def test_index_and_metric_tampering_fail(evaluated_run):
    run = evaluated_run()
    edit(run / "evaluation.json", lambda d: d["metrics"]["process_response_time_s"].update(value=999))
    assert not verify(run)["pass"]
    evaluate(run)
    edit(run / "evidence-index.json", lambda d: d["artifacts"]["cargo_state_timeline"].update(sha256="0" * 64))
    assert not verify(run)["pass"]


def test_nested_evidence_mapping_is_retained(evaluated_run):
    run = evaluated_run()
    (run / "captures").mkdir()
    (run / "cargo-modbus.pcap").rename(run / "captures/cargo.pcap")
    edit(run / "run.json", lambda d: d.update(evidence_files={"cargo_modbus_pcap": "captures/cargo.pcap"}))
    result = evaluate(run)
    assert result["artifacts"]["cargo_modbus_pcap"]["path"] == "captures/cargo.pcap"
    assert verify(run)["pass"]


def test_escaping_and_symlink_evidence_fail(evaluated_run, tmp_path):
    for i, path in enumerate(("../outside.pcap", "/tmp/outside.pcap")):
        run = evaluated_run(str(i))
        edit(run / "evidence-index.json", lambda d: d["artifacts"]["cargo_modbus_pcap"].update(path=path))
        assert not verify(run)["pass"]
    run = evaluated_run("symlink")
    source = tmp_path / "external.pcap"
    (run / "cargo-modbus.pcap").rename(source)
    (run / "cargo-modbus.pcap").symlink_to(source)
    assert not verify(run)["pass"]


def test_zero_flow_is_a_valid_blockage_observation(evaluated_run):
    run = evaluated_run()
    edit(run / "run.json", lambda d: d.update(experiment_id="EXP-CARGO-BLOCKED-FLOW"))
    (run / "cargo-state.jsonl").write_text(json.dumps({"state": {"pumpFeedback": True, "valveFeedback": True, "flowMeasured": 0}}) + "\n")
    (run / "alarm-timeline.jsonl").write_text(json.dumps({"alarm_id": "CARGO_NO_FLOW", "transition": "ACTIVE_UNACK"}) + "\n")
    assert evaluate(run)["pass"]
    assert verify(run)["pass"]


def test_duplicate_directories_and_copied_runs_do_not_count_as_repeats(evaluated_run, tmp_path):
    run = evaluated_run()
    assert not aggregate([run, run, run])["claim_ready"]
    copies = [tmp_path / "copy1", tmp_path / "copy2"]
    for copy in copies:
        shutil.copytree(run, copy)
    result = aggregate([run, *copies])
    assert result["usable_runs"] == 1
    assert not result["claim_ready"]


def test_unknown_cleanliness_or_commit_cannot_claim_readiness(evaluated_run):
    runs = [evaluated_run(str(i), dirty=None if i == 2 else False) for i in range(3)]
    assert not aggregate(runs)["claim_ready"]
    runs = [evaluated_run("c" + str(i), commit=None if i == 2 else "abc") for i in range(3)]
    assert not aggregate(runs)["claim_ready"]


def test_corrupt_or_missing_run_metadata_returns_failure(tmp_path):
    assert not verify(tmp_path)["pass"]
    (tmp_path / "run.json").write_text("not-json")
    assert not verify(tmp_path)["pass"]
