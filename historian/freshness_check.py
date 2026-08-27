#!/usr/bin/env python3
"""Check the age of the latest InfluxDB sample for a commissioned domain measurement."""
import argparse
import csv
import datetime
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


def query(host, org, bucket, token, measurement):
    flux = f'from(bucket: "{bucket}") |> range(start: -30m) |> filter(fn:(r)=> r._measurement == "{measurement}") |> last()'
    req = urllib.request.Request(
        host.rstrip('/') + '/api/v2/query?org=' + urllib.parse.quote(org),
        data=flux.encode(), method='POST',
        headers={'Authorization': 'Token ' + token, 'Content-Type': 'application/vnd.flux', 'Accept': 'application/csv'},
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.read().decode()


def last_epoch(csv_text):
    times = []
    body = '\n'.join(x for x in csv_text.splitlines() if not x.startswith('#'))
    for row in csv.DictReader(io.StringIO(body)):
        if row.get('_time'):
            times.append(datetime.datetime.fromisoformat(row['_time'].replace('Z', '+00:00')).timestamp())
    return max(times) if times else None


def load_dotenv(path=Path('.env')):
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line=raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key,value=line.split('=',1)
        key=key.strip(); value=value.strip()
        if value[:1] == value[-1:] and value[:1] in {"'", '"'}:
            value=value[1:-1]
        os.environ.setdefault(key,value)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('measurement')
    ap.add_argument('--max-age', type=float, default=10.0)
    ap.add_argument('--out', default=None, help='optional JSON evidence path')
    a = ap.parse_args()
    load_dotenv()
    host = os.getenv('INFLUX_URL', 'http://127.0.0.1:8086')
    org = os.getenv('INFLUX_ORG', 'otlab')
    bucket = os.getenv('INFLUX_BUCKET', 'vessel')
    token = os.getenv('INFLUX_TOKEN', '')
    if not token:
        print('INFLUX_TOKEN is required', file=sys.stderr)
        raise SystemExit(3)
    ts = last_epoch(query(host, org, bucket, token, a.measurement))
    observed = time.time()
    age = (observed - ts) if ts else None
    result = {
        'measurement': a.measurement,
        'last_sample_epoch': ts,
        'last_sample_time': datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat() if ts else None,
        'checked_epoch': observed,
        'checked_time': datetime.datetime.fromtimestamp(observed, tz=datetime.timezone.utc).isoformat(),
        'age_s': age,
        'fresh': age is not None and age <= a.max_age,
        'max_age_s': a.max_age,
        'timestamp_semantics': 'Influx sample timestamp compared with observer wall clock',
    }
    text = json.dumps(result, indent=2) + '\n'
    if a.out:
        out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text)
    print(text, end='')
    raise SystemExit(0 if result['fresh'] else 2)


if __name__ == '__main__':
    main()
