#!/usr/bin/env python3
"""Fail closed when the project's research claims lose their implementation trail."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_PATH = ROOT / "docs/09-research/research-translation.json"

REQUIRED_FILES = [
    "docs/00-learning/how-to-use-this-course.md",
    "docs/00-learning/chapter-contract.md",
    "docs/03-architecture/deployment-decision.md",
    "docs/04-build/server-daemon-deployment.md",
    "docs/05-protocols/can-j1939.md",
    "docs/05-protocols/ethernet-ip-stack.md",
    "docs/09-research/research-framework.md",
    "docs/09-research/research-to-model-matrix.md",
    "docs/09-research/research-translation.json",
    "docs/09-research/source-registry.md",
    "docs/09-research/standards-mapping.md",
    "docs/09-research/visual-source-registry.md",
    "docs/08-reference/technology-selection.md",
    "experiments/manifest.json",
    "security/conduits.json",
    "historian/freshness_check.py",
    "config/project-scope.json",
    "config/architecture-contract.json",
    "config/data-semantics-contract.json",
    "config/timebase-contract.json",
    "config/opcua-security-boundary.json",
    "config/detection-claims.json",
    "vessel/coverage-contract.json",
    "docs/09-research/image-provenance.json",
    "evidence/acceptance-dossier-contract.json",
    "evidence/aggregate_runs.py",
    "evidence/build_acceptance_dossier.py",
    "commissioning/acceptance_orchestrator.py",
    "commissioning/commissioning-plan.json",
    "docs/04-build/commissioning-orchestrator.md",
]

TRANSLATION_FIELDS = {
    "id",
    "source_type",
    "source",
    "finding_used",
    "engineering_decision",
    "implementation_paths",
    "learner_action",
    "experiment_ids",
    "expected_evidence",
    "falsification_condition",
    "excluded_claims",
}
SOURCE_FIELDS = {"title", "authors", "year", "doi", "url"}
PLACEHOLDER = re.compile(r"\b(?:tbd|todo|placeholder|fill me|coming soon)\b", re.I)


def read_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate_translation_contract(contract: dict, experiments: list[dict], root: Path = ROOT) -> list[str]:
    """Validate paper → decision → implementation → experiment traceability."""
    problems: list[str] = []
    if contract.get("schema_version") != 1:
        problems.append("research translation schema_version must be 1")

    purpose = contract.get("purpose", "")
    if not isinstance(purpose, str) or len(purpose) < 80:
        problems.append("research translation purpose is missing or too vague")

    translations = contract.get("translations")
    if not isinstance(translations, list) or len(translations) < 6:
        return problems + ["at least six concrete research translations are required"]

    experiment_by_id = {item["id"]: item for item in experiments}
    seen: set[str] = set()

    for index, item in enumerate(translations):
        label = item.get("id", f"entry-{index}") if isinstance(item, dict) else f"entry-{index}"
        if not isinstance(item, dict):
            problems.append(f"{label}: translation must be an object")
            continue

        missing = sorted(TRANSLATION_FIELDS - set(item))
        if missing:
            problems.append(f"{label}: missing fields {', '.join(missing)}")
            continue

        if not re.fullmatch(r"RT-[A-Z0-9-]+", str(item["id"])):
            problems.append(f"{label}: id must match RT-[A-Z0-9-]+")
        if item["id"] in seen:
            problems.append(f"{label}: duplicate translation id")
        seen.add(item["id"])

        if item["source_type"] != "research_paper":
            problems.append(f"{label}: source_type must be research_paper")
        source = item["source"]
        if not isinstance(source, dict):
            problems.append(f"{label}: source must be an object")
        else:
            for field in SOURCE_FIELDS:
                if not source.get(field):
                    problems.append(f"{label}: source.{field} is required")
            if source.get("url") and not str(source["url"]).startswith("https://"):
                problems.append(f"{label}: source.url must use https")
            if source.get("doi") and not re.match(r"^10\.\d{4,9}/\S+$", str(source["doi"])):
                problems.append(f"{label}: source.doi is not a DOI")
            if source.get("year") and not isinstance(source["year"], int):
                problems.append(f"{label}: source.year must be an integer")

        for field in ["finding_used", "engineering_decision", "learner_action", "falsification_condition"]:
            value = item[field]
            if not isinstance(value, str) or len(value) < 70:
                problems.append(f"{label}: {field} must be a concrete sentence of at least 70 characters")
            elif PLACEHOLDER.search(value):
                problems.append(f"{label}: {field} contains placeholder language")

        if item["finding_used"] == item["engineering_decision"]:
            problems.append(f"{label}: paper finding and project decision must be distinct")

        paths = item["implementation_paths"]
        if not isinstance(paths, list) or len(paths) < 3:
            problems.append(f"{label}: at least three implementation paths are required")
        else:
            for relative in paths:
                candidate = Path(relative)
                if candidate.is_absolute() or ".." in candidate.parts:
                    problems.append(f"{label}: implementation path must stay inside the repository: {relative}")
                elif not (root / candidate).exists():
                    problems.append(f"{label}: implementation path does not exist: {relative}")

        experiment_ids = item["experiment_ids"]
        if not isinstance(experiment_ids, list) or not experiment_ids:
            problems.append(f"{label}: at least one experiment id is required")
            continue
        unknown = sorted(set(experiment_ids) - set(experiment_by_id))
        if unknown:
            problems.append(f"{label}: unknown experiments {', '.join(unknown)}")
            continue

        declared_evidence = {
            evidence
            for experiment_id in experiment_ids
            for evidence in experiment_by_id[experiment_id]["required_evidence"]
        }
        evidence = item["expected_evidence"]
        if not isinstance(evidence, list) or not evidence:
            problems.append(f"{label}: expected_evidence cannot be empty")
        else:
            undeclared = sorted(set(evidence) - declared_evidence)
            if undeclared:
                problems.append(
                    f"{label}: evidence not declared by its experiments: {', '.join(undeclared)}"
                )

        excluded = item["excluded_claims"]
        if not isinstance(excluded, list) or len(excluded) < 2 or any(len(str(x)) < 25 for x in excluded):
            problems.append(f"{label}: at least two explicit excluded claims are required")

    matrix = (root / "docs/09-research/research-to-model-matrix.md").read_text(encoding="utf-8")
    registry = (root / "docs/09-research/source-registry.md").read_text(encoding="utf-8")
    for translation_id in seen:
        if translation_id not in matrix:
            problems.append(f"{translation_id}: missing from human-readable research matrix")
        if translation_id not in registry:
            problems.append(f"{translation_id}: missing from source registry")

    return problems


def validate_repository() -> tuple[list[str], int]:
    problems: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            problems.append(f"missing {relative}")

    protocol_dir = ROOT / "docs/05-protocols"
    for path in protocol_dir.glob("*.md"):
        text = path.read_text(errors="ignore").lower()
        if path.name in {"protocol-map.md", "iec-61162-450-460.md"}:
            continue
        practical = ["60-second explain-back", "capture", "replay", "candump", "wireshark", "worked example"]
        if not any(word in text for word in practical):
            problems.append(f"{path}: insufficient practical/pedagogy content")

    experiments = read_json("experiments/manifest.json")["experiments"]
    experiment_ids = [item["id"] for item in experiments]
    if len(experiment_ids) != len(set(experiment_ids)):
        problems.append("duplicate experiment ids")
    for experiment in experiments:
        for field in ["hypothesis", "metrics", "required_evidence"]:
            if not experiment.get(field):
                problems.append(f"{experiment['id']}: missing {field}")

    if TRANSLATION_PATH.exists():
        try:
            contract = json.loads(TRANSLATION_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"invalid research translation JSON: {exc}")
        else:
            problems.extend(validate_translation_contract(contract, experiments))

    policy = read_json("security/conduits.json")
    for rule in policy["modbus"]:
        if not re.match(r"^172\.28\.", rule["src"]) or not re.match(r"^172\.28\.", rule["dst"]):
            problems.append("non-lab conduit IP")

    alarm_catalog = (ROOT / "alarms/catalog.json").read_text(encoding="utf-8")
    for obsolete in ["CARGO_DATA_STALE", "PMS_DATA_STALE", "PROPULSION_DATA_STALE"]:
        if f'"{obsolete}"' in alarm_catalog:
            problems.append(f"ambiguous stale alarm id remains: {obsolete}")

    cargo = read_json("plant/configs/cargo.json")
    propulsion = read_json("plant/configs/propulsion.json")
    if "faultFlowPathBlocked" not in cargo["inputs"]:
        problems.append("Cargo blocked-flow fault missing")
    if "faultCoolingFail" not in propulsion["inputs"]:
        problems.append("Propulsion cooling impairment fault missing")

    network = read_json("network/fidelity-contract.json")
    if network.get("status") != "design_accepted_runtime_unvalidated":
        problems.append("network fidelity status must remain runtime-unvalidated until NF gates run")
    if network.get("canonical_baseline", {}).get("must_remain_runnable_without_extension") is not True:
        problems.append("network extension may not replace the canonical Compose baseline")
    containerlab = network.get("selected_extension", {}).get("topology_orchestrator", {})
    if containerlab.get("name") != "Containerlab" or containerlab.get("reviewed_version") != "0.77.0":
        problems.append("network fidelity Containerlab decision drift")
    if network.get("selected_extension", {}).get("routing", {}).get("dynamic_routing_suite") != "not selected":
        problems.append("dynamic routing was introduced without a recorded admission decision")
    if len(network.get("runtime_acceptance_gates", [])) != 7:
        problems.append("network fidelity NF-A through NF-G contract incomplete")

    scope = read_json("config/project-scope.json")
    if scope.get("current_validation_state") != "static_validated_pending_target_server_commissioning":
        problems.append("project scope validation state overclaims runtime readiness")

    claims = read_json("config/detection-claims.json")
    if len(claims.get("required_comparators", [])) != 3:
        problems.append("detection comparison contract incomplete")

    opcua = read_json("config/opcua-security-boundary.json")
    if not opcua.get("not_yet_claimed"):
        problems.append("OPC UA security claim boundary missing")

    return problems, len(experiments)


def main() -> int:
    problems, experiment_count = validate_repository()
    print("RESEARCH/PUBLICATION GATE")
    if problems:
        print("FAIL")
        for problem in problems:
            print(" -", problem)
        return 1
    print("PASS")
    print(f" - {experiment_count} registered experiments with hypotheses/metrics/evidence")
    print(" - 6 paper-to-engineering translations with implementation, learner, evidence and claim boundaries")
    print(" - pedagogy, deployment, standards, visual-source and technology-selection contracts present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
