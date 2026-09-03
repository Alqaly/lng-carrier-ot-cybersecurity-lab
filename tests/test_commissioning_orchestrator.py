from pathlib import Path
import importlib.util
import json


R = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, R / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def project(module, dirty=False):
    return {
        "git_commit": "abc123",
        "git_tree": "tree123",
        "git_origin": "https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab",
        "tree_dirty": dirty,
        "release_manifest_sha256": module.sha256_file(R / "release-manifest.json"),
        "commissioning_plan_sha256": module.sha256_file(R / "commissioning/commissioning-plan.json"),
        "dossier_contract_sha256": module.sha256_file(R / "evidence/acceptance-dossier-contract.json"),
    }


def test_commissioning_plan_covers_every_dossier_artifact():
    plan = json.loads((R / "commissioning/commissioning-plan.json").read_text())
    contract = json.loads((R / "evidence/acceptance-dossier-contract.json").read_text())
    assert list(plan["gates"]) == list("ABCDEFG")
    assert plan["minimum_experiment_repeats"] >= 3
    for gate, names in contract["gates"].items():
        assert set(plan["gates"][gate]["artifacts"]) == set(names)


def test_labctl_and_docs_expose_resumable_commissioning():
    labctl = (R / "labctl").read_text()
    guide = (R / "docs/04-build/commissioning-orchestrator.md").read_text()
    assert "cmd_commission" in labctl
    for command in ("cmd_opcua", "cmd_bind_plan", "cmd_hist_install"):
        assert f'{command} "$@"' in labctl
    for command in ("start", "resume", "status", "record", "finalize"):
        assert f"commission {command}" in guide
    assert "a bare PASS" in (R / "commissioning/acceptance_orchestrator.py").read_text()


def test_initialise_refuses_dirty_source(tmp_path):
    module = load("commission_dirty", "commissioning/acceptance_orchestrator.py")
    try:
        module.initialise(tmp_path, project(module, dirty=True), "20260101-000000Z")
    except ValueError as error:
        assert "dirty Git tree" in str(error)
    else:
        raise AssertionError("dirty source was accepted")


def test_initialise_snapshots_source_and_contracts(tmp_path):
    module = load("commission_init", "commissioning/acceptance_orchestrator.py")
    run = module.initialise(tmp_path, project(module), "20260101-000000Z")
    state = json.loads((run / "commissioning-state.json").read_text())
    assert state["project"]["git_commit"] == "abc123"
    assert state["status"] == "in_progress"
    assert (run / "provenance/commissioning-plan.json").is_file()
    assert (run / "provenance/acceptance-dossier-contract.json").is_file()


def test_record_requires_exact_evidence_labels(tmp_path):
    module = load("commission_labels", "commissioning/acceptance_orchestrator.py")
    current = project(module)
    run = module.initialise(tmp_path / "runs", current, "20260101-000000Z")
    evidence = tmp_path / "cargo.txt"
    evidence.write_text("live map evidence")
    try:
        module.record_artifact(run, "plc-io-map-review.json", {"cargo-map": evidence}, "Verified the three live maps.", "engineer", current=current)
    except ValueError as error:
        assert "exactly" in str(error)
    else:
        raise AssertionError("incomplete labels were accepted")


def test_record_copies_and_hashes_live_evidence(tmp_path):
    module = load("commission_record", "commissioning/acceptance_orchestrator.py")
    current = project(module)
    run = module.initialise(tmp_path / "runs", current, "20260101-000000Z")
    sources = {}
    for label in ("cargo-map", "pms-map", "propulsion-map"):
        path = tmp_path / f"{label}.txt"
        path.write_text(f"verified {label} against live PLC")
        sources[label] = path
    output = module.record_artifact(run, "plc-io-map-review.json", sources, "Each live Editor address was checked against the generated map.", "engineer", current=current)
    payload = json.loads(output.read_text())
    assert payload["pass"] is True
    assert payload["project"]["git_commit"] == "abc123"
    assert len(payload["evidence"]) == 3
    for item in payload["evidence"]:
        retained = run / item["path"]
        assert retained.is_file()
        assert module.sha256_path(retained) == item["sha256"]


def test_gate_a_records_commands_and_fails_closed(tmp_path):
    module = load("commission_gate_a", "commissioning/acceptance_orchestrator.py")
    current = project(module)
    run = module.initialise(tmp_path / "runs", current, "20260101-000000Z")

    def runner(command):
        if command[1:2] == ["preflight"]:
            return 1, "preflight failed\n"
        return 0, "rendered compose or gate output\n"

    assert module.run_gate_a(run, runner=runner, current=current) is False
    artifact = json.loads((run / "static-review.json").read_text())
    assert artifact["pass"] is False
    assert any(item["exit_code"] != 0 for item in artifact["commands"])


def test_dossier_rejects_json_presence_without_semantic_pass(tmp_path):
    orchestrator = load("commission_dossier_setup", "commissioning/acceptance_orchestrator.py")
    dossier_module = load("commission_dossier", "evidence/build_acceptance_dossier.py")
    current = project(orchestrator)
    run = orchestrator.initialise(tmp_path / "runs", current, "20260101-000000Z")
    (run / "static-review.json").write_text(json.dumps({"pass": False}))
    (run / "rendered-compose.txt").write_text("services: {}\n")
    result = dossier_module.build(run, R / "evidence/acceptance-dossier-contract.json")
    assert result["gates"]["A"]["pass"] is False
    assert "artifact identity" in " ".join(result["gates"]["A"]["artifacts"][0]["semantic_errors"])


def test_dossier_accepts_only_hashed_commit_bound_artifacts(tmp_path):
    orchestrator = load("commission_complete_setup", "commissioning/acceptance_orchestrator.py")
    dossier_module = load("commission_complete", "evidence/build_acceptance_dossier.py")
    current = project(orchestrator)
    run = orchestrator.initialise(tmp_path / "runs", current, "20260101-000000Z")
    contract = json.loads((R / "evidence/acceptance-dossier-contract.json").read_text())
    for gate, names in contract["gates"].items():
        for name in names:
            if name == "rendered-compose.txt":
                (run / name).write_text("services: {}\n")
                continue
            retained = run / "attachments" / name / "proof.txt"
            retained.parent.mkdir(parents=True)
            retained.write_text(f"retained evidence for {name}\n")
            payload = orchestrator.artifact_payload(
                run,
                {"project": current},
                gate,
                name,
                True,
                [orchestrator.evidence_entry(run, retained, "proof")],
            )
            orchestrator.write_json(run / name, payload)
    result = dossier_module.build(run, R / "evidence/acceptance-dossier-contract.json")
    assert result["pass"] is True
    retained = run / "attachments/static-review.json/proof.txt"
    retained.write_text("tampered\n")
    tampered = dossier_module.build(run, R / "evidence/acceptance-dossier-contract.json")
    assert tampered["pass"] is False
    assert "hash mismatch" in " ".join(tampered["gates"]["A"]["artifacts"][0]["semantic_errors"])


def test_aggregate_reads_current_nested_git_provenance(tmp_path):
    module = load("aggregate_nested", "evidence/aggregate_runs.py")
    runs = []
    for index in range(3):
        run = tmp_path / str(index)
        run.mkdir()
        (run / "run.json").write_text(json.dumps({"experiment_id": "EXP-X", "git": {"commit": "abc", "tree_dirty": False}}))
        (run / "evaluation.json").write_text(json.dumps({"pass": True, "metrics": {}}))
        runs.append(run)
    result = module.aggregate(runs)
    assert result["claim_ready"] is True
    assert result["git_commits"] == ["abc"]
    assert result["contains_dirty_run"] is False


def test_gate_f_indexes_all_repeated_experiments(tmp_path):
    module = load("commission_gate_f", "commissioning/acceptance_orchestrator.py")
    current = project(module)
    run = module.initialise(tmp_path / "acceptance", current, "20260101-000000Z")
    experiment_root = tmp_path / "experiment-runs"
    ids = [item["id"] for item in json.loads((R / "experiments/manifest.json").read_text())["experiments"]]
    for experiment in ids:
        for index in range(3):
            item = experiment_root / f"{experiment}-{index}"
            item.mkdir(parents=True)
            (item / "run.json").write_text(json.dumps({"experiment_id": experiment, "git": {"commit": "abc123", "tree_dirty": False}}))
            (item / "evaluation.json").write_text(json.dumps({"pass": True, "metrics": {}}))
            (item / "evidence-index.json").write_text(json.dumps({"verified": True}))

    assert module.run_gate_f(run, experiment_root, runner=lambda command: (0, "verified"), current=current) is True
    index = json.loads((run / "experiment-run-index.json").read_text())
    aggregation = json.loads((run / "repeated-run-aggregation.json").read_text())
    assert index["pass"] is True
    assert aggregation["pass"] is True
    assert set(aggregation["aggregations"]) == set(ids)


def test_normal_baseline_record_rejects_wrong_experiment(tmp_path):
    module = load("commission_baseline", "commissioning/acceptance_orchestrator.py")
    current = project(module)
    run = module.initialise(tmp_path / "acceptance", current, "20260101-000000Z")
    metadata = tmp_path / "run.json"
    evaluation = tmp_path / "evaluation.json"
    index = tmp_path / "evidence-index.json"
    metadata.write_text(json.dumps({"experiment_id": "EXP-PMS-GEN-TRIP"}))
    evaluation.write_text(json.dumps({"pass": True}))
    index.write_text(json.dumps({"verified": True}))
    sources = {"run-metadata": metadata, "evaluation": evaluation, "evidence-index": index}
    try:
        module.record_artifact(run, "normal-baseline-run.json", sources, "This is the retained normal baseline run.", "engineer", current=current)
    except ValueError as error:
        assert "EXP-CARGO-NORMAL" in str(error)
    else:
        raise AssertionError("wrong experiment accepted as normal baseline")
