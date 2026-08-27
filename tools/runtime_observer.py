#!/usr/bin/env python3
"""Collect normalized runtime evidence without inventing source event times.

Process/vessel state snapshots are timestamped when the observer receives them and
retain any source clock fields (`time_s`, `last_update`) separately. Alarm
chronicle entries retain the alarm-engine timestamp as the event timestamp.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCES = {
    "cargo": "http://127.0.0.1:8100/state",
    "pms": "http://127.0.0.1:8200/state",
    "propulsion": "http://127.0.0.1:8300/state",
    "vessel": "http://127.0.0.1:8600/state",
}
ALARM_HISTORY = "http://127.0.0.1:8400/history?limit=2000"
ALARM_STATE = "http://127.0.0.1:8400/alarms"


def utc_iso(epoch: float | None = None) -> str:
    return datetime.fromtimestamp(epoch if epoch is not None else time.time(), tz=timezone.utc).isoformat()


def fetch_json(url: str, timeout: float = 2.0) -> Any:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n")


def snapshot_record(source: str, state: dict[str, Any], observed_epoch: float) -> dict[str, Any]:
    record: dict[str, Any] = {
        "event_type": "state_snapshot",
        "source": source,
        "event_epoch": observed_epoch,
        "event_time": utc_iso(observed_epoch),
        "timestamp_semantics": "observer_receive_timestamp",
        "state": state,
    }
    if "time_s" in state:
        record["source_time_s"] = state["time_s"]
    if "last_update" in state:
        record["source_last_update_epoch"] = state["last_update"]
    return record


def changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    if previous is None:
        return {k: v for k, v in current.items() if k not in {"time_s", "last_update"}}
    ignored = {"time_s", "last_update"}
    keys = (set(previous) | set(current)) - ignored
    return {k: current.get(k) for k in sorted(keys) if previous.get(k) != current.get(k)}


def alarm_event(item: dict[str, Any]) -> dict[str, Any]:
    ts = float(item["ts"])
    return {
        "event_type": "alarm_transition",
        "source": "alarm-engine",
        "domain": item.get("domain"),
        "event_epoch": ts,
        "event_time": utc_iso(ts),
        "timestamp_semantics": "source_alarm_timestamp",
        "alarm_id": item.get("id"),
        "transition": item.get("transition"),
        "priority": item.get("priority"),
        "message": item.get("message"),
    }


def safe_fetch(url: str) -> tuple[Any | None, str | None]:
    try:
        return fetch_json(url), None
    except Exception as exc:  # runtime evidence must preserve the failure, not hide it
        return None, f"{type(exc).__name__}: {exc}"


def run(duration_s: float, outdir: Path, interval_s: float) -> dict[str, Any]:
    if duration_s <= 0:
        raise ValueError("duration must be > 0 seconds")
    if interval_s <= 0:
        raise ValueError("interval must be > 0 seconds")

    outdir.mkdir(parents=True, exist_ok=True)
    events = outdir / "runtime-events.jsonl"
    alarms = outdir / "alarm-timeline.jsonl"
    for path in [events, alarms, *(outdir / f"{name}-state.jsonl" for name in SOURCES)]:
        path.write_text("", encoding="utf-8")

    started = time.time()
    started_mono = time.monotonic()
    previous: dict[str, dict[str, Any]] = {}
    seen_alarms: set[tuple[Any, ...]] = set()
    counts = {"state_snapshots": 0, "state_changes": 0, "alarm_transitions": 0, "service_errors": 0}

    initial_alarm_state, initial_error = safe_fetch(ALARM_STATE)
    (outdir / "alarm-state-start.json").write_text(
        json.dumps({"observed_at": utc_iso(), "alarms": initial_alarm_state, "error": initial_error}, indent=2) + "\n",
        encoding="utf-8",
    )

    while time.monotonic() - started_mono < duration_s:
        cycle_started = time.monotonic()
        for source, url in SOURCES.items():
            state, error = safe_fetch(url)
            observed = time.time()
            if error is not None or not isinstance(state, dict):
                record = {
                    "event_type": "service_error",
                    "source": source,
                    "event_epoch": observed,
                    "event_time": utc_iso(observed),
                    "timestamp_semantics": "observer_receive_timestamp",
                    "error": error or "non-object JSON response",
                }
                append_jsonl(events, record)
                counts["service_errors"] += 1
                continue

            snap = snapshot_record(source, state, observed)
            append_jsonl(outdir / f"{source}-state.jsonl", snap)
            counts["state_snapshots"] += 1

            changed = changed_fields(previous.get(source), state)
            if changed:
                event = {
                    "event_type": "state_change",
                    "source": source,
                    "event_epoch": observed,
                    "event_time": utc_iso(observed),
                    "timestamp_semantics": "observer_receive_timestamp",
                    "changed": changed,
                }
                if "time_s" in state:
                    event["source_time_s"] = state["time_s"]
                if "last_update" in state:
                    event["source_last_update_epoch"] = state["last_update"]
                append_jsonl(events, event)
                counts["state_changes"] += 1
            previous[source] = state

        history, history_error = safe_fetch(ALARM_HISTORY)
        observed = time.time()
        if history_error is not None:
            append_jsonl(events, {
                "event_type": "service_error",
                "source": "alarm-engine",
                "event_epoch": observed,
                "event_time": utc_iso(observed),
                "timestamp_semantics": "observer_receive_timestamp",
                "error": history_error,
            })
            counts["service_errors"] += 1
        elif isinstance(history, list):
            # Ignore old chronicle rows from before this run. Preserve actual alarm timestamps.
            for item in sorted(history, key=lambda x: float(x.get("ts", 0))):
                try:
                    ts = float(item.get("ts", 0))
                except (TypeError, ValueError):
                    continue
                if ts < started - 0.5:
                    continue
                key = (ts, item.get("id"), item.get("transition"))
                if key in seen_alarms:
                    continue
                seen_alarms.add(key)
                record = alarm_event(item)
                append_jsonl(alarms, record)
                append_jsonl(events, record)
                counts["alarm_transitions"] += 1

        sleep_for = interval_s - (time.monotonic() - cycle_started)
        if sleep_for > 0:
            time.sleep(sleep_for)

    final_alarm_state, final_error = safe_fetch(ALARM_STATE)
    (outdir / "alarm-state-end.json").write_text(
        json.dumps({"observed_at": utc_iso(), "alarms": final_alarm_state, "error": final_error}, indent=2) + "\n",
        encoding="utf-8",
    )
    ended = time.time()
    summary = {
        "started_at": utc_iso(started),
        "ended_at": utc_iso(ended),
        "duration_requested_s": duration_s,
        "duration_observed_s": ended - started,
        "poll_interval_s": interval_s,
        "timestamp_policy": {
            "state": "observer receive time; source time_s/last_update retained separately when present",
            "alarms": "alarm-engine source timestamp retained as event time",
        },
        "counts": counts,
        "files": {
            "normalized_events": "runtime-events.jsonl",
            "alarm_timeline": "alarm-timeline.jsonl",
            "state_timelines": [f"{name}-state.jsonl" for name in SOURCES],
        },
    }
    (outdir / "observer-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Observe runtime state and alarm chronology into a reproducible evidence directory.")
    parser.add_argument("duration", type=float, help="observation duration in seconds")
    parser.add_argument("outdir", help="evidence run directory")
    parser.add_argument("--interval", type=float, default=0.25, help="state polling interval in seconds")
    args = parser.parse_args()
    summary = run(args.duration, Path(args.outdir), args.interval)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
