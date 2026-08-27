#!/usr/bin/env python3
"""Compare measured Cargo flow against an independent tank mass-balance estimate.

Accepts either CSV rows (`time_s`, `levelSource`, `flowMeasured`) or JSONL
produced by tools/runtime_observer.py. The process source clock is used for the
mass balance; observer wall-clock timestamps are not substituted for model time.
"""
import argparse
import csv
import json
from pathlib import Path

REQUIRED = {'time_s', 'levelSource', 'flowMeasured'}


def load_csv(path):
    return list(csv.DictReader(path.open()))


def load_jsonl(path):
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        state = item.get('state', item)
        if not isinstance(state, dict):
            continue
        if REQUIRED <= set(state):
            rows.append({k: state[k] for k in REQUIRED})
    return rows


def load_rows(path):
    suffix = path.suffix.lower()
    if suffix == '.csv':
        return load_csv(path)
    if suffix in {'.jsonl', '.ndjson'}:
        return load_jsonl(path)
    # Fail closed on ambiguous formats, but allow content-based JSONL for extensionless evidence.
    first = next((x for x in path.read_text().splitlines() if x.strip()), '')
    if first.startswith('{'):
        return load_jsonl(path)
    raise ValueError('input must be CSV or JSONL/NDJSON')


def calculate(rows, tank_area_m2, threshold_pct):
    out = []
    for prev, current in zip(rows, rows[1:]):
        dt = float(current['time_s']) - float(prev['time_s'])
        if dt <= 0:
            continue
        dh = float(prev['levelSource']) - float(current['levelSource'])
        estimated = max(0.0, tank_area_m2 * dh / dt)
        measured = float(current['flowMeasured'])
        denom = max(abs(estimated), 1e-6)
        residual_pct = 100.0 * (measured - estimated) / denom
        out.append({
            'time_s': float(current['time_s']),
            'estimated_flow_m3s': estimated,
            'measured_flow_m3s': measured,
            'residual_pct': residual_pct,
            'anomaly': abs(residual_pct) >= threshold_pct,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--tank-area-m2', type=float, default=1250.0)
    ap.add_argument('--threshold-pct', type=float, default=20.0)
    ap.add_argument('--out', default=None, help='optional JSON evidence path')
    a = ap.parse_args()
    path = Path(a.input)
    rows = load_rows(path)
    if len(rows) < 2:
        raise SystemExit('need at least two valid Cargo state samples')
    results = calculate(rows, a.tank_area_m2, a.threshold_pct)
    payload = {
        'input': str(path),
        'samples': len(rows),
        'comparisons': len(results),
        'tank_area_m2': a.tank_area_m2,
        'threshold_pct': a.threshold_pct,
        'results': results,
    }
    text = json.dumps(payload, indent=2) + '\n'
    if a.out:
        out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
