#!/usr/bin/env python3
"""Post-commissioning service probe for the always-on server deployment.

This checks reachability/health only. It does NOT prove PLC tag mappings, OPC UA
semantic correctness, HMI bindings, historian freshness, or experiment results.
Those are covered by the Server Acceptance Test and evidence gates.
"""
from __future__ import annotations
import json, socket, ssl, sys, urllib.request, urllib.error

HTTP_PROBES = [
    ("Cargo process", "http://127.0.0.1:8100/health"),
    ("PMS process", "http://127.0.0.1:8200/health"),
    ("Propulsion process", "http://127.0.0.1:8300/health"),
    ("Alarm chronicle", "http://127.0.0.1:8400/health"),
    ("Learning portal", "http://127.0.0.1:8500/"),
    ("Vessel coordinator", "http://127.0.0.1:8600/state"),
    ("InfluxDB", "http://127.0.0.1:8086/health"),
    ("Grafana", "http://127.0.0.1:3000/api/health"),
    ("FUXA", "http://127.0.0.1:1881/"),
]

TCP_PROBES = [
    ("Cargo Modbus I/O", "127.0.0.1", 5020),
    ("PMS Modbus I/O", "127.0.0.1", 5021),
    ("Propulsion Modbus I/O", "127.0.0.1", 5022),
    ("Cargo OpenPLC HTTPS", "127.0.0.1", 8443),
    ("PMS OpenPLC HTTPS", "127.0.0.1", 8444),
    ("Propulsion OpenPLC HTTPS", "127.0.0.1", 8445),
    ("Cargo OPC UA", "127.0.0.1", 4840),
    ("PMS OPC UA", "127.0.0.1", 4841),
    ("Propulsion OPC UA", "127.0.0.1", 4842),
]

def probe_http(name: str, url: str) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "lng-ot-lab-service-probe/1"})
        with urllib.request.urlopen(req, timeout=4) as r:
            body = r.read(2048)
            return 200 <= r.status < 300, f"HTTP {r.status}, {len(body)} bytes"
    except urllib.error.HTTPError as e:
        # Auth-protected UIs are reachable only when they explicitly answer
        # with an authentication/authorization status. A 404/5xx is a failure.
        return e.code in (401, 403), f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)

def probe_tcp(name: str, host: str, port: int) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=3):
            return True, "TCP connect OK"
    except Exception as e:
        return False, str(e)

def main() -> int:
    failures=[]
    print("POST-COMMISSIONING SERVICE PROBE")
    for name,url in HTTP_PROBES:
        ok,detail=probe_http(name,url)
        print(f" {'PASS' if ok else 'FAIL':4}  {name:24} {detail}")
        if not ok: failures.append(name)
    for name,host,port in TCP_PROBES:
        ok,detail=probe_tcp(name,host,port)
        print(f" {'PASS' if ok else 'FAIL':4}  {name:24} {detail}")
        if not ok: failures.append(name)
    if failures:
        print("\nFAIL — unreachable services: " + ", ".join(failures))
        return 1
    print("\nPASS — service reachability is healthy.")
    print("NOTE: semantic PLC/OPC/HMI/historian/experiment acceptance is still required.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
