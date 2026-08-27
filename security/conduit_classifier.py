#!/usr/bin/env python3
"""Classify observed Zeek connections against declared Modbus conduit ground truth."""
import argparse
import json
from pathlib import Path


def load_tsv(path):
    fields = []
    for line in Path(path).read_text(errors='ignore').splitlines():
        if line.startswith('#fields'):
            fields = line.split('\t')[1:]
            continue
        if not line or line.startswith('#'):
            continue
        vals = line.split('\t')
        if fields and len(vals) >= len(fields):
            yield dict(zip(fields, vals))


def classify(conn_log, policy_path, domain=None):
    policy = json.loads(Path(policy_path).read_text())['modbus']
    if domain:
        policy = [x for x in policy if x['domain'] == domain]
    allowed = {(x['src'], x['dst'], str(x['port'])): x for x in policy}
    rows = []
    for row in load_tsv(conn_log):
        key = (row.get('id.orig_h'), row.get('id.resp_h'), row.get('id.resp_p'))
        rev = (row.get('id.resp_h'), row.get('id.orig_h'), row.get('id.orig_p'))
        rule = allowed.get(key) or allowed.get(rev)
        rows.append({
            'uid': row.get('uid'),
            'src': row.get('id.orig_h'),
            'dst': row.get('id.resp_h'),
            'port': row.get('id.resp_p'),
            'classification': 'EXPECTED' if rule else 'UNEXPECTED',
            'domain': rule.get('domain') if rule else domain,
            'matched_rule': rule,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('conn_log')
    ap.add_argument('--policy', default='security/conduits.json')
    ap.add_argument('--domain', choices=['cargo', 'pms', 'propulsion'], default=None)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--out', default=None, help='optional JSON evidence path')
    a = ap.parse_args()
    rows = classify(a.conn_log, a.policy, a.domain)
    if a.out:
        out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rows, indent=2) + '\n')
    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        for item in rows:
            print(f"{item['classification']:10} {item['src']} -> {item['dst']}:{item['port']} {item['domain'] or ''}")
    if any(x['classification'] == 'UNEXPECTED' for x in rows):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
