from pathlib import Path
import importlib.util
import json

import yaml


R = Path(__file__).resolve().parents[1]


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, R / rel)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_public_identity_is_canonical():
    expected = "LNG Carrier Virtual Engineering Lab"
    for rel in ["README.md", "docs/index.md", "CITATION.cff", "mkdocs.yml", "release-manifest.json"]:
        assert expected in (R / rel).read_text(), rel


def test_release_manifest_records_recovered_candidate_and_test_count():
    manifest = json.loads((R / "release-manifest.json").read_text())
    assert manifest["artifact_state"] == "source_validated_commissioning_automation_ready"
    assert manifest["static_validation"]["pytest_expected"] == 130
    assert manifest["runtime_validation_in_build_environment"] is False


def test_project_scope_separates_executable_scope_from_claims():
    scope = json.loads((R / "config/project-scope.json").read_text())
    assert scope["public_identity"] == "LNG Carrier Virtual Engineering Lab"
    assert len(scope["executable_scope"]) >= 7
    assert all(value is False for value in scope["claim_boundaries"].values())


def test_architecture_contract_separates_control_supervisory_and_coupling_paths():
    contract = json.loads((R / "config/architecture-contract.json").read_text())
    paths = contract["paths"]
    assert "Modbus TCP" in paths["control"]
    assert "OPC UA" in paths["supervisory"]
    assert "HTTP API" in paths["cross_domain_coupling"]
    assert len(set(paths.values())) == len(paths)


def test_vessel_coordinator_implementation_matches_direct_model_coupling_contract():
    source = (R / "vessel/coordinator.py").read_text()
    for service in ["cargo-plant", "pms-plant", "propulsion-plant"]:
        assert service in source
    assert "client.post" in source
    assert "Modbus" not in source


def test_vessel_coverage_is_explicitly_partial():
    coverage = json.loads((R / "vessel/coverage-contract.json").read_text())
    assert set(coverage["executable_domains"]) == {"cargo", "power_management", "propulsion_machinery", "cross_domain"}
    assert "class-approved vessel digital twin" in coverage["outside_current_scope"]


def test_data_semantics_contract_fails_closed():
    contract = json.loads((R / "config/data-semantics-contract.json").read_text())
    assert "timestamp_semantics" in contract["required_fields"]
    assert "unavailable_behavior" in contract["required_fields"]
    assert all(contract["rules"].values())


def test_historian_binding_and_publication_loss_do_not_fabricate_values():
    labctl = (R / "labctl").read_text()
    historian = (R / "historian/README.md").read_text()
    assert "Missing $src" in labctl and "refusing historian install" in labctl
    assert "receives no new samples" in historian
    assert "--force-recreate telegraf" in labctl


def test_timebase_contract_names_independent_clocks():
    contract = json.loads((R / "config/timebase-contract.json").read_text())
    assert set(contract["clocks"]) >= {"observer_receive", "model_time", "alarm_source", "packet_capture", "historian_sample"}
    assert any("Never silently substitute" in rule for rule in contract["rules"])


def test_runtime_observer_implements_declared_timestamp_separation():
    source = (R / "tools/runtime_observer.py").read_text()
    assert "observer_receive_timestamp" in source
    assert "source_time_s" in source
    assert "source_alarm_timestamp" in source


def test_image_provenance_distinguishes_reference_runtime_and_schematic():
    provenance = json.loads((R / "docs/09-research/image-provenance.json").read_text())
    assert provenance["runtime_visual_policy"]["status"] == "pending_target_server_commissioning"
    assert provenance["project_authored_diagrams"]["evidence_status"] == "not runtime evidence"
    assert provenance["project_authored_diagrams"]["primary_publication_visual"] is False


def test_external_visual_manifest_has_reuse_and_mapping_provenance():
    manifest = json.loads((R / "docs/09-research/visual-manifest.json").read_text())
    for items in manifest["chapters"].values():
        for item in items:
            assert item["source"]
            assert item["license_or_reuse_status"]
            assert item["lab_mapping"]
            assert item["limitation"]


def test_repeated_run_aggregation_preserves_missing_evidence(tmp_path):
    module = load_module("aggregate_missing", "evidence/aggregate_runs.py")
    result = module.aggregate([tmp_path / "missing"])
    assert result["usable_runs"] == 0
    assert result["claim_ready"] is False
    assert result["runs"][0]["usable"] is False


def test_repeated_run_aggregation_computes_measured_metrics(evaluated_run):
    module = load_module("aggregate_measured", "evidence/aggregate_runs.py")
    runs = [evaluated_run(str(i), response=float(i + 1), nested=False) for i in range(3)]
    result = module.aggregate(runs)
    assert result["claim_ready"] is True
    assert result["metrics"]["process_response_time_s"]["mean"] == 2.0
    assert result["metrics"]["process_response_time_s"]["units"] == ["s"]


def test_repeated_run_aggregation_rejects_mixed_or_dirty_provenance(evaluated_run):
    module = load_module("aggregate_provenance", "evidence/aggregate_runs.py")
    runs = [evaluated_run(str(index), commit=commit, dirty=index == 1, nested=False) for index, commit in enumerate(["a", "a", "b"])]
    result = module.aggregate(runs)
    assert result["comparable"] is False
    assert result["claim_ready"] is False
    assert result["contains_dirty_run"] is True


def test_detection_contract_keeps_conclusion_prospective():
    contract = json.loads((R / "config/detection-claims.json").read_text())
    assert "may improve" in contract["prospective_claim"]
    assert set(contract["required_comparators"]) == {"network_only", "process_only", "cross_layer"}
    assert "improves detection" in contract["forbidden_without_evidence"]


def test_opcua_security_observation_does_not_claim_conformance_or_pki():
    contract = json.loads((R / "config/opcua-security-boundary.json").read_text())
    assert "live endpoint discovery" in contract["implemented_observations"]
    assert "production PKI commissioning" in contract["not_yet_claimed"]
    assert "OPC UA conformance certification" in contract["not_yet_claimed"]


def test_acceptance_dossier_contract_has_exactly_gates_a_through_g():
    contract = json.loads((R / "evidence/acceptance-dossier-contract.json").read_text())
    assert list(contract["gates"]) == list("ABCDEFG")
    assert all(contract["gates"].values())


def test_acceptance_dossier_hashes_present_artifacts_and_rejects_missing(tmp_path):
    module = load_module("acceptance_dossier", "evidence/build_acceptance_dossier.py")
    orchestrator = load_module("acceptance_orchestrator", "commissioning/acceptance_orchestrator.py")
    contract_path = R / "evidence/acceptance-dossier-contract.json"
    contract = json.loads(contract_path.read_text())
    partial = module.build(tmp_path, contract_path)
    assert partial["pass"] is False
    project = {"git_commit": "abc", "tree_dirty": False}
    (tmp_path / "commissioning-state.json").write_text(json.dumps({"project": project}))
    for gate, names in contract["gates"].items():
        for name in names:
            if name == "rendered-compose.txt":
                (tmp_path / name).write_text("services: {}\n")
                continue
            evidence = tmp_path / "attachments" / name / "proof.txt"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("retained evidence\n")
            payload = orchestrator.artifact_payload(
                tmp_path,
                {"project": project},
                gate,
                name,
                True,
                [orchestrator.evidence_entry(tmp_path, evidence, "proof")],
            )
            orchestrator.write_json(tmp_path / name, payload)
    complete = module.build(tmp_path, contract_path)
    assert complete["pass"] is False  # Generic proof.txt is not the required manual evidence.
    assert all(item["sha256"] for gate in complete["gates"].values() for item in gate["artifacts"])


def test_preflight_is_location_independent_and_fuxa_runtime_state_is_ignored():
    preflight = (R / "deploy/preflight.sh").read_text()
    ignore = (R / ".gitignore").read_text()
    assert 'dirname "${BASH_SOURCE[0]}"' in preflight and 'cd "$ROOT"' in preflight
    for path in ["fuxa/appdata/", "fuxa/db/", "fuxa/logs/", "fuxa/images/"]:
        assert path in ignore


def test_runtime_health_and_service_probe_fail_closed():
    plant = (R / "plant/runtime/runner.py").read_text()
    vessel = (R / "vessel/coordinator.py").read_text()
    alarms = (R / "alarms/service.py").read_text()
    probe = (R / "tools/service_probe.py").read_text()
    assert "status_code=200 if ready else 503" in plant
    assert "status_code=200 if ready else 503" in vessel
    assert "status_code=200 if ready else 503" in alarms
    assert "200 <= r.status < 300" in probe and "r.status < 500" not in probe


def test_compose_waits_for_healthy_models_and_io_services_have_healthchecks():
    compose = yaml.safe_load((R / "docker-compose.yml").read_text())
    for domain in ["cargo", "pms", "propulsion"]:
        io_service = compose["services"][f"{domain}-io"]
        assert io_service["depends_on"][f"{domain}-plant"]["condition"] == "service_healthy"
        assert "healthcheck" in io_service
    assert compose["services"]["learning-portal"]["depends_on"]["vessel-coordinator"]["condition"] == "service_healthy"


def test_public_language_uses_cross_domain_not_full_vessel():
    public = [R / "README.md", R / "docs/index.md", *list((R / "docs").rglob("*.md")), R / "portal/static/index.html"]
    offenders = [str(path.relative_to(R)) for path in public if "full-vessel" in path.read_text(errors="ignore").lower()]
    assert not offenders, offenders
    assert (R / "docs/06-scenarios/cross-domain-operational-event.md").exists()
