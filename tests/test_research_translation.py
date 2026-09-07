import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_gate():
    spec = importlib.util.spec_from_file_location("research_translation_gate", ROOT / "tools/research_gate.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_inputs():
    contract = json.loads((ROOT / "docs/09-research/research-translation.json").read_text())
    experiments = json.loads((ROOT / "experiments/manifest.json").read_text())["experiments"]
    return contract, experiments


def test_current_paper_to_engineering_contract_is_valid():
    contract, experiments = load_inputs()
    assert load_gate().validate_translation_contract(contract, experiments, ROOT) == []


def test_translation_fails_when_a_claim_has_no_real_implementation_path():
    contract, experiments = load_inputs()
    changed = copy.deepcopy(contract)
    changed["translations"][0]["implementation_paths"][0] = "missing/research-theatre.py"
    problems = load_gate().validate_translation_contract(changed, experiments, ROOT)
    assert any("implementation path does not exist" in problem for problem in problems)


def test_translation_fails_when_experiment_or_evidence_is_not_declared():
    contract, experiments = load_inputs()
    changed = copy.deepcopy(contract)
    changed["translations"][0]["experiment_ids"] = ["EXP-NOT-REAL"]
    problems = load_gate().validate_translation_contract(changed, experiments, ROOT)
    assert any("unknown experiments" in problem for problem in problems)

    changed = copy.deepcopy(contract)
    changed["translations"][0]["expected_evidence"].append("imaginary_proof")
    problems = load_gate().validate_translation_contract(changed, experiments, ROOT)
    assert any("evidence not declared" in problem for problem in problems)


def test_every_paper_states_what_would_disprove_it_and_what_is_not_claimed():
    contract, _ = load_inputs()
    for translation in contract["translations"]:
        assert translation["source_type"] == "research_paper"
        assert translation["finding_used"] != translation["engineering_decision"]
        assert len(translation["falsification_condition"]) >= 70
        assert len(translation["excluded_claims"]) >= 2
