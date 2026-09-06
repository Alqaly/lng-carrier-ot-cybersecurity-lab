#!/usr/bin/env python3
"""Evaluate experiments from concrete retained evidence.

Schema v3 separates three questions:
1. Are all required artifacts present, well-formed, and hashed?
2. Does the retained evidence prove the experiment's declared causal semantics?
3. Which declared metrics are actually measurable from the retained evidence?

A metric is never invented. Every manifest metric is emitted as either
``measured`` with source/unit/timestamp semantics or ``unavailable`` with an
explicit reason.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = {
    "cargo_modbus_pcap": "cargo-modbus.pcap",
    "pms_modbus_pcap": "pms-modbus.pcap",
    "propulsion_modbus_pcap": "propulsion-modbus.pcap",
    "cargo_state_timeline": "cargo-state.jsonl",
    "pms_state_timeline": "pms-state.jsonl",
    "propulsion_state_timeline": "propulsion-state.jsonl",
    "vessel_state_timeline": "vessel-state.jsonl",
    "alarm_timeline": "alarm-timeline.jsonl",
    "cargo_state_csv": "cargo-state.csv",
    "process_residual_json": "process-residual.json",
    "modbus_conn_log": "conn.log",
    "conduit_classification_json": "conduit-classification.json",
    "historian_freshness_before": "freshness-before.json",
    "historian_freshness_after": "freshness-after.json",
    "cargo_modbus_log": "zeek/modbus.log",
    "opcua_outage_record": "opcua-outage.json",
}
PCAP_KEYS = {"cargo_modbus_pcap", "pms_modbus_pcap", "propulsion_modbus_pcap"}
JSON_KEYS = {
    "process_residual_json",
    "conduit_classification_json",
    "historian_freshness_before",
    "historian_freshness_after",
    "opcua_outage_record",
}
JSONL_KEYS = {
    "cargo_state_timeline",
    "pms_state_timeline",
    "propulsion_state_timeline",
    "vessel_state_timeline",
    "alarm_timeline",
}
ZEEK_KEYS = {"modbus_conn_log", "cargo_modbus_log"}
PCAP_MAGICS = {
    b"\xd4\xc3\xb2\xa1",
    b"\xa1\xb2\xc3\xd4",
    b"\x4d\x3c\xb2\xa1",
    b"\xa1\xb2\x3c\x4d",
    b"\x0a\x0d\x0d\x0a",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        if not isinstance(item, dict):
            raise ValueError(f"line {line_no} is not a JSON object")
        rows.append(item)
    return rows


def state_records(path: Path) -> list[dict[str, Any]]:
    rows = []
    for item in read_jsonl(path):
        state = item.get("state", item)
        if isinstance(state, dict):
            rows.append({"record": item, "state": state})
    return rows


def alarm_records(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path)


def resolve(run: Path, key: str, meta: dict[str, Any]) -> Path:
    rel = (meta.get("evidence_files") or {}).get(key, DEFAULT_FILES.get(key, key))
    path = (run / rel).resolve()
    base = run.resolve()
    if path != base and base not in path.parents:
        raise ValueError(f"evidence path escapes run directory: {rel}")
    return path


def parse_zeek(path: Path) -> list[dict[str, str]]:
    fields: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        if line.startswith("#fields"):
            parts = line.split("\t")
            fields = parts[1:]
            continue
        if not line or line.startswith("#"):
            continue
        if fields is None:
            raise ValueError("Zeek log missing #fields header before data")
        values = line.split("\t")
        rows.append(dict(zip(fields, values)))
    if fields is None:
        raise ValueError("Zeek log #fields header missing")
    return rows


def validate_artifact(key: str, path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError("missing")
    if path.stat().st_size == 0 and key != "alarm_timeline":
        raise ValueError("empty")
    detail: dict[str, Any] = {
        "path": str(path.name) if path.parent.name != "zeek" else f"zeek/{path.name}",
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if key in PCAP_KEYS:
        with path.open("rb") as handle:
            magic = handle.read(4)
        if magic not in PCAP_MAGICS:
            raise ValueError("not recognized PCAP/PCAPNG magic")
    elif key in JSON_KEYS:
        value = json.loads(path.read_text(encoding="utf-8"))
        detail["json_type"] = type(value).__name__
    elif key in JSONL_KEYS:
        rows = read_jsonl(path)
        if not rows and key != "alarm_timeline":
            raise ValueError("JSONL contains no records")
        detail["records"] = len(rows)
    elif key == "cargo_state_csv":
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        if not rows:
            raise ValueError("CSV contains no data rows")
        for col in ("time_s", "levelSource", "flowMeasured"):
            if col not in rows[0]:
                raise ValueError(f"CSV missing {col}")
        detail["records"] = len(rows)
    elif key in ZEEK_KEYS:
        rows = parse_zeek(path)
        detail["records"] = len(rows)
        if key == "cargo_modbus_log" and rows and "ts" not in rows[0]:
            raise ValueError("Zeek Modbus log missing ts field")
    return detail


def event_epoch(record: dict[str, Any]) -> float | None:
    try:
        return float(record["event_epoch"])
    except (KeyError, TypeError, ValueError):
        return None


def source_time(row: dict[str, Any]) -> float | None:
    record, state = row["record"], row["state"]
    for candidate in (record.get("source_time_s"), state.get("time_s")):
        try:
            return float(candidate)
        except (TypeError, ValueError):
            pass
    return None


def iso_epoch(value: Any) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def first(rows: list[Any], predicate: Callable[[Any], bool], *, start: int = 0) -> tuple[int, Any] | None:
    for index in range(start, len(rows)):
        if predicate(rows[index]):
            return index, rows[index]
    return None


def active_alarm(item: dict[str, Any], ids: set[str]) -> bool:
    return item.get("alarm_id") in ids and str(item.get("transition", "")).startswith("ACTIVE")


def measured(value: float, unit: str, source: str, timestamp_semantics: str, note: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "status": "measured",
        "value": value,
        "unit": unit,
        "source": source,
        "timestamp_semantics": timestamp_semantics,
    }
    if note:
        out["note"] = note
    return out


def unavailable(reason: str, unit: str, source: str, timestamp_semantics: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "reason": reason,
        "unit": unit,
        "source": source,
        "timestamp_semantics": timestamp_semantics,
    }


def semantic_and_metrics(exp: dict[str, Any], run: Path, meta: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    exp_id = exp["id"]
    checks: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(ok), "detail": detail})

    if exp_id == "EXP-CARGO-NORMAL":
        rows = state_records(resolve(run, "cargo_state_timeline", meta))
        causal = first(rows, lambda r: bool(r["state"].get("pumpFeedback")) and bool(r["state"].get("valveFeedback")) and float(r["state"].get("flowMeasured", 0) or 0) > 0.05)
        add("normal cargo causal state observed", causal is not None, "pump+valve feedback true with positive measured flow")
        command = first(rows, lambda r: bool(r["state"].get("pumpCmd")) and float(r["state"].get("valveCommand", 0) or 0) > 0.05)
        if command and causal and causal[0] >= command[0]:
            t0, t1 = source_time(command[1]), source_time(causal[1])
            if t0 is not None and t1 is not None and t1 >= t0:
                metrics["process_response_time_s"] = measured(t1 - t0, "s", "cargo_state_timeline", "process source time_s")
            else:
                metrics["process_response_time_s"] = unavailable("command/response source times were not both retained", "s", "cargo_state_timeline", "process source time_s")
        else:
            metrics["process_response_time_s"] = unavailable("no ordered command-to-causal-response pair was retained", "s", "cargo_state_timeline", "process source time_s")
        metrics["event_order_accuracy"] = unavailable(
            "a formal expected cross-layer event sequence is not encoded for this baseline experiment",
            "fraction",
            "cargo_state_timeline + alarm_timeline + packet evidence",
            "mixed source clocks",
        )

    elif exp_id == "EXP-CARGO-BLOCKED-FLOW":
        rows = state_records(resolve(run, "cargo_state_timeline", meta))
        contradiction = first(rows, lambda r: bool(r["state"].get("pumpFeedback")) and bool(r["state"].get("valveFeedback")) and r["state"].get("flowMeasured") is not None and abs(float(r["state"]["flowMeasured"])) <= 0.05)
        add("blocked-flow process contradiction observed", contradiction is not None, "healthy pump/valve feedback with near-zero measured flow")
        alarms = alarm_records(resolve(run, "alarm_timeline", meta))
        alarm = first(alarms, lambda x: active_alarm(x, {"CARGO_NO_FLOW", "CARGO_FLOW_MISMATCH"}))
        add("blocked-flow alarm observed", alarm is not None, "active CARGO_NO_FLOW/CARGO_FLOW_MISMATCH transition")
        if contradiction and alarm:
            t0 = event_epoch(contradiction[1]["record"])
            t1 = event_epoch(alarm[1])
            if t0 is not None and t1 is not None and t1 >= t0:
                metrics["detection_latency_s"] = measured(t1 - t0, "s", "cargo_state_timeline + alarm_timeline", "observer receive timestamp to source alarm timestamp", "cross-source upper-bound chronology")
            else:
                metrics["detection_latency_s"] = unavailable("ordered observer/alarm timestamps were not retained", "s", "cargo_state_timeline + alarm_timeline", "mixed observer/source timestamps")
        else:
            metrics["detection_latency_s"] = unavailable("process contradiction and active alarm were not both retained", "s", "cargo_state_timeline + alarm_timeline", "mixed observer/source timestamps")
        metrics["cross_layer_reconstruction_completeness"] = measured(
            1.0,
            "fraction",
            "cargo_modbus_pcap + cargo_state_timeline + alarm_timeline",
            "artifact-set completeness",
            "all three required packet/process/alarm evidence layers validated before semantic evaluation",
        )

    elif exp_id == "EXP-CARGO-SENSOR-BIAS":
        payload = json.loads(resolve(run, "process_residual_json", meta).read_text(encoding="utf-8"))
        values = payload.get("results", payload if isinstance(payload, list) else [])
        anomalies = [x for x in values if isinstance(x, dict) and bool(x.get("anomaly"))]
        add("process residual anomaly observed", bool(anomalies), "at least one independent mass-balance residual exceeded threshold")
        residuals = []
        for item in anomalies:
            try:
                residuals.append(abs(float(item.get("residual_pct"))))
            except (TypeError, ValueError):
                pass
        if residuals:
            metrics["residual_pct"] = measured(max(residuals), "%", "process_residual_json", "process source time_s inside residual calculation")
        else:
            metrics["residual_pct"] = unavailable("no anomalous residual_pct value was retained", "%", "process_residual_json", "process source time_s")
        metrics["detection_latency_s"] = unavailable(
            "alarm chronology is not required evidence for the sensor-bias experiment",
            "s",
            "process_residual_json",
            "not measurable from retained evidence",
        )

    elif exp_id == "EXP-PMS-GEN-TRIP":
        rows = state_records(resolve(run, "pms_state_timeline", meta))
        trip = first(rows, lambda r: bool(r["state"].get("faultGen1Trip")))
        online_before = bool(trip and any(bool(x["state"].get("gen1BreakerFB")) for x in rows[: trip[0]]))
        add("generator 1 online before trip", online_before, "Gen1 breaker feedback was true before the injected trip")
        add("generator 1 trip intervention observed", trip is not None, "faultGen1Trip=true retained in PMS process state")
        loss = first(rows, lambda r: not bool(r["state"].get("gen1BreakerFB")), start=(trip[0] + 1 if trip else 0)) if trip else None
        add("generator 1 breaker feedback lost after trip", loss is not None, "Gen1 breaker feedback becomes false after fault injection")
        excursion = first(
            rows,
            lambda r: bool(r["state"].get("underFrequency")) or bool(r["state"].get("blackout")) or float(r["state"].get("frequencyHz", 60) or 60) < 58.5,
            start=(loss[0] if loss else (trip[0] if trip else 0)),
        ) if trip else None
        add("PMS frequency/blackout excursion observed", excursion is not None, "underFrequency/blackout or frequency below 58.5 Hz observed after trip")

        vessel = state_records(resolve(run, "vessel_state_timeline", meta))
        trip_epoch = event_epoch(trip[1]["record"]) if trip else None
        consequence = None
        for idx, row in enumerate(vessel):
            links = row["state"].get("links", row["state"])
            epoch = event_epoch(row["record"])
            if trip_epoch is not None and epoch is not None and epoch < trip_epoch:
                continue
            if isinstance(links, dict) and (links.get("cargoPowerAvailable") is False or links.get("propulsionAuxPowerAvailable") is False):
                consequence = (idx, row)
                break
        add("cross-system power consequence observed", consequence is not None, "Cargo or propulsion auxiliary power availability becomes false")

        alarms = alarm_records(resolve(run, "alarm_timeline", meta))
        pms_alarm = first(alarms, lambda x: active_alarm(x, {"PMS_UNDER_FREQUENCY", "PMS_BLACKOUT", "PMS_GEN1_UNAVAILABLE"}))
        add("PMS alarm chronology observed", pms_alarm is not None, "active PMS under-frequency, blackout, or Gen1-unavailable alarm retained")

        ordered = False
        order_epochs: list[float] = []
        if trip and loss and excursion and consequence:
            candidates = [event_epoch(trip[1]["record"]), event_epoch(loss[1]["record"]), event_epoch(excursion[1]["record"]), event_epoch(consequence[1]["record"])]
            if all(x is not None for x in candidates):
                order_epochs = [float(x) for x in candidates if x is not None]
                ordered = order_epochs == sorted(order_epochs)
        add("trip-to-cross-system event order is causal", ordered, "trip → breaker loss → excursion → vessel consequence using observer timestamps")

        if trip:
            post = rows[trip[0] :]
            freqs = []
            for row in post:
                try:
                    freqs.append(float(row["state"].get("frequencyHz")))
                except (TypeError, ValueError):
                    pass
            if freqs:
                metrics["frequency_nadir_hz"] = measured(min(freqs), "Hz", "pms_state_timeline", "process state value observed on observer timeline")
            else:
                metrics["frequency_nadir_hz"] = unavailable("no numeric frequencyHz samples retained after trip", "Hz", "pms_state_timeline", "observer timeline")
        else:
            metrics["frequency_nadir_hz"] = unavailable("trip intervention not retained", "Hz", "pms_state_timeline", "observer timeline")

        shed = first(rows, lambda r: bool(r["state"].get("shedCargo")) or bool(r["state"].get("shedHotel")), start=(trip[0] if trip else 0)) if trip else None
        if trip and shed:
            t0, t1 = event_epoch(trip[1]["record"]), event_epoch(shed[1]["record"])
            if t0 is not None and t1 is not None and t1 >= t0:
                metrics["load_shed_latency_s"] = measured(t1 - t0, "s", "pms_state_timeline", "observer receive timestamps")
            else:
                metrics["load_shed_latency_s"] = unavailable("ordered trip/load-shed observer timestamps unavailable", "s", "pms_state_timeline", "observer receive timestamps")
        else:
            metrics["load_shed_latency_s"] = unavailable("no load-shed transition retained after trip", "s", "pms_state_timeline", "observer receive timestamps")

        if order_epochs:
            adjacent = [order_epochs[i] <= order_epochs[i + 1] for i in range(len(order_epochs) - 1)]
            metrics["event_order_accuracy"] = measured(sum(adjacent) / len(adjacent), "fraction", "pms_state_timeline + vessel_state_timeline", "observer receive timestamps")
        else:
            metrics["event_order_accuracy"] = unavailable("four required causal event timestamps were not all retained", "fraction", "pms_state_timeline + vessel_state_timeline", "observer receive timestamps")

    elif exp_id == "EXP-PROP-COOLING-FAULT":
        rows = state_records(resolve(run, "propulsion_state_timeline", meta))
        fault = first(rows, lambda r: bool(r["state"].get("faultCoolingFail")) and bool(r["state"].get("engineEnable")))
        running_before = bool(fault and any(bool(x["state"].get("engineRunning")) or bool(x["state"].get("engineEnable")) for x in rows[: fault[0] + 1]))
        add("engine enabled/running before cooling fault", running_before, "engine was enabled or running before/at fault injection")
        add("cooling impairment intervention observed", fault is not None, "faultCoolingFail=true while engineEnable=true")
        high = first(rows, lambda r: bool(r["state"].get("highCoolantTemp")), start=(fault[0] if fault else 0)) if fault else None
        add("high coolant protective condition observed", high is not None, "highCoolantTemp=true after cooling impairment")
        inhibit = first(rows, lambda r: r["state"].get("engineEnable") is False, start=(high[0] + 1 if high else 0)) if high else None
        add("PLC protective inhibit visible at process input", inhibit is not None, "engineEnable becomes false after high coolant condition")
        alarms = alarm_records(resolve(run, "alarm_timeline", meta))
        prop_alarm = first(alarms, lambda x: active_alarm(x, {"PROP_HIGH_COOLANT"}))
        add("high coolant alarm observed", prop_alarm is not None, "active PROP_HIGH_COOLANT alarm transition retained")

        temps = []
        if fault:
            for row in rows[fault[0] :]:
                try:
                    temps.append(float(row["state"].get("coolantTempC")))
                except (TypeError, ValueError):
                    pass
        if temps:
            metrics["peak_temperature_c"] = measured(max(temps), "degC", "propulsion_state_timeline", "process state value on source time_s timeline")
        else:
            metrics["peak_temperature_c"] = unavailable("no numeric coolantTempC samples retained after fault", "degC", "propulsion_state_timeline", "process source time_s")

        if high and inhibit:
            t0, t1 = source_time(high[1]), source_time(inhibit[1])
            if t0 is not None and t1 is not None and t1 >= t0:
                metrics["trip_latency_s"] = measured(t1 - t0, "s", "propulsion_state_timeline", "process source time_s")
            else:
                metrics["trip_latency_s"] = unavailable("ordered source time_s values unavailable for high-coolant to inhibit", "s", "propulsion_state_timeline", "process source time_s")
        else:
            metrics["trip_latency_s"] = unavailable("high coolant and later engine inhibit were not both retained", "s", "propulsion_state_timeline", "process source time_s")

    elif exp_id == "EXP-UNEXPECTED-MODBUS-SOURCE":
        payload = json.loads(resolve(run, "conduit_classification_json", meta).read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("results", [])
        classified = [x for x in rows if isinstance(x, dict)]
        unexpected = [x for x in classified if x.get("classification") == "UNEXPECTED"]
        add("unexpected Modbus source observed", bool(unexpected), "classifier output contains an UNEXPECTED connection")
        if classified:
            metrics["classification_accuracy"] = measured(
                len(unexpected) / len(classified),
                "fraction",
                "conduit_classification_json",
                "controlled-run classification rows",
                "This is meaningful only because the experiment intentionally introduces an unexpected source.",
            )
        else:
            metrics["classification_accuracy"] = unavailable("classifier produced no rows", "fraction", "conduit_classification_json", "controlled-run rows")

    elif exp_id == "EXP-OPCUA-STALE-CARGO":
        before = json.loads(resolve(run, "historian_freshness_before", meta).read_text(encoding="utf-8"))
        after = json.loads(resolve(run, "historian_freshness_after", meta).read_text(encoding="utf-8"))
        outage = json.loads(resolve(run, "opcua_outage_record", meta).read_text(encoding="utf-8"))
        add("historian transitions fresh to stale", before.get("fresh") is True and after.get("fresh") is False, "freshness-before=true and freshness-after=false")
        outage_truth = outage.get("domain") == "cargo" and outage.get("control_preserved") is True and bool(outage.get("started_at"))
        add("supervisory-only outage ground truth retained", outage_truth, "outage record proves cargo domain, started_at, and control_preserved=true")

        before_t = before.get("checked_epoch")
        after_t = after.get("checked_epoch")
        start_t = iso_epoch(outage.get("started_at"))
        restored_t = iso_epoch(outage.get("restored_at"))
        try:
            before_t = float(before_t)
            after_t = float(after_t)
        except (TypeError, ValueError):
            before_t = after_t = None
        bracketed = bool(before_t is not None and start_t is not None and after_t is not None and before_t <= start_t <= after_t and (restored_t is None or after_t <= restored_t))
        add("freshness checks bracket the outage", bracketed, "fresh-before ≤ outage-start ≤ stale-after ≤ restore when restore evidence exists")

        modbus_rows = parse_zeek(resolve(run, "cargo_modbus_log", meta))
        in_window = False
        if start_t is not None and after_t is not None:
            for item in modbus_rows:
                try:
                    ts = float(item.get("ts", ""))
                except (TypeError, ValueError):
                    continue
                if start_t <= ts <= after_t:
                    in_window = True
                    break
        add("Cargo Modbus activity continues during OPC UA outage window", in_window, "Zeek modbus.log contains a transaction between outage start and stale-after observation")

        if start_t is not None and after_t is not None and after_t >= start_t:
            metrics["historian_stale_detection_latency_s"] = measured(
                after_t - start_t,
                "s",
                "opcua_outage_record + historian_freshness_after",
                "outage helper UTC action time to historian check wall clock",
                "upper bound: staleness may have become detectable before the explicit after-check",
            )
        else:
            metrics["historian_stale_detection_latency_s"] = unavailable("outage start and stale-after check times were not both retained", "s", "opcua_outage_record + historian_freshness_after", "UTC wall clock")

    else:
        add("experiment semantic evaluator exists", False, f"no semantic evaluator implemented for {exp_id}")

    for metric in exp.get("metrics", []):
        if metric not in metrics:
            metrics[metric] = unavailable("metric evaluator did not produce a result", "unspecified", "experiment evaluator", "unspecified")
    return checks, metrics


def evaluate(run: Path, *, write: bool = True) -> dict[str, Any]:
    meta = json.loads((run / "run.json").read_text(encoding="utf-8"))
    experiments = json.loads((ROOT / "experiments/manifest.json").read_text(encoding="utf-8"))["experiments"]
    exp = next(x for x in experiments if x["id"] == meta["experiment_id"])

    artifacts: dict[str, Any] = {}
    missing: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for key in exp["required_evidence"]:
        path = resolve(run, key, meta)
        try:
            artifacts[key] = validate_artifact(key, path)
            artifacts[key]["path"] = str(path.relative_to(run.resolve()))
        except Exception as exc:
            issue = {
                "key": key,
                "path": str(path.relative_to(run)) if path.is_relative_to(run) else str(path),
                "reason": str(exc),
            }
            (missing if not path.exists() else invalid).append(issue)

    checks: list[dict[str, Any]] = []
    metrics = {
        metric: unavailable("required evidence was incomplete or invalid", "unspecified", "required evidence", "unavailable")
        for metric in exp.get("metrics", [])
    }
    if not missing and not invalid:
        try:
            checks, metrics = semantic_and_metrics(exp, run, meta)
        except Exception as exc:
            checks = [{"name": "experiment-specific semantic evaluation", "pass": False, "detail": f"{type(exc).__name__}: {exc}"}]
            metrics = {
                metric: unavailable(f"semantic evaluator failed: {type(exc).__name__}: {exc}", "unspecified", "semantic evaluator", "unavailable")
                for metric in exp.get("metrics", [])
            }

    required = len(exp["required_evidence"])
    valid = len(artifacts)
    passed = valid == required and bool(checks) and all(item["pass"] for item in checks)
    out = {
        "schema_version": 3,
        "experiment_id": exp["id"],
        "run_git": meta.get("git"),
        "release_manifest_sha256": meta.get("release_manifest_sha256"),
        "run_metadata_sha256": sha256(run / "run.json"),
        "evidence_completeness": valid / required if required else 1.0,
        "artifacts": artifacts,
        "missing_evidence": missing,
        "invalid_evidence": invalid,
        "semantic_checks": checks,
        "experiment_checks": checks,
        "metrics": metrics,
        "pass": passed,
    }
    if write:
        (run / "evidence-index.json").write_text(
            json.dumps({"schema_version": 2, "experiment_id": exp["id"], "run_metadata_sha256": out["run_metadata_sha256"], "artifacts": artifacts}, indent=2) + "\n",
            encoding="utf-8",
        )
        (run / "evaluation.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    out = evaluate(Path(args.run_dir))
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if out["pass"] else 2)


if __name__ == "__main__":
    main()
