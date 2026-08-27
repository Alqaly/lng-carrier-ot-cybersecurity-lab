#!/usr/bin/env python3
"""Isolate only an OpenPLC operations-network path for OPC UA outage experiments.

The PLC remains connected to its control network. Ground-truth control and
operations IPs are read from security/conduits.json, then matched against the
live Docker network attachments before any mutation is performed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "security" / "conduits.json"
STATE_DIR = ROOT / "evidence" / "runtime"
SERVICES = {
    "cargo": "openplc-cargo",
    "pms": "openplc-pms",
    "propulsion": "openplc-propulsion",
}


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(*args: str, check: bool = True) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def ground_truth(domain: str) -> dict[str, str]:
    policy = json.loads(POLICY.read_text())
    modbus = next(x for x in policy["modbus"] if x["domain"] == domain)
    opcua = next(x for x in policy["opcua"] if x["domain"] == domain)
    return {"control_ip": modbus["src"], "operations_ip": opcua["dst"]}


def container_id(service: str) -> str:
    cid = run("docker", "compose", "ps", "-q", service)
    if not cid:
        raise RuntimeError(f"{service} is not running; outage experiment requires a running commissioned PLC")
    return cid.splitlines()[0].strip()


def network_map(cid: str) -> dict[str, dict[str, Any]]:
    raw = run("docker", "inspect", cid)
    doc = json.loads(raw)
    if not doc:
        raise RuntimeError(f"docker inspect returned no object for {cid}")
    return doc[0].get("NetworkSettings", {}).get("Networks", {}) or {}


def network_for_ip(networks: dict[str, dict[str, Any]], ip: str) -> str | None:
    matches = [name for name, cfg in networks.items() if cfg.get("IPAddress") == ip]
    if len(matches) > 1:
        raise RuntimeError(f"IP {ip} is attached through multiple networks: {matches}")
    return matches[0] if matches else None


def verify_control_attached(networks: dict[str, dict[str, Any]], control_ip: str) -> str:
    name = network_for_ip(networks, control_ip)
    if not name:
        raise RuntimeError(f"control path {control_ip} is not attached; refusing supervisory-only outage action")
    return name


def state_path(domain: str) -> Path:
    return STATE_DIR / f"opcua-outage-{domain}.json"


def start(domain: str) -> dict[str, Any]:
    service = SERVICES[domain]
    truth = ground_truth(domain)
    cid = container_id(service)
    before = network_map(cid)
    control_network = verify_control_attached(before, truth["control_ip"])
    operations_network = network_for_ip(before, truth["operations_ip"])
    if not operations_network:
        raise RuntimeError(f"operations path {truth['operations_ip']} is already absent; refusing ambiguous start")
    if operations_network == control_network:
        raise RuntimeError("control and operations resolved to the same Docker network; isolation would violate experiment design")

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "domain": domain,
        "service": service,
        "container_id": cid,
        "action": "start",
        "started_at": utc_iso(),
        "control_ip": truth["control_ip"],
        "operations_ip": truth["operations_ip"],
        "control_network": control_network,
        "operations_network": operations_network,
    }
    state_path(domain).write_text(json.dumps(record, indent=2) + "\n")

    run("docker", "network", "disconnect", operations_network, cid)
    after = network_map(cid)
    verify_control_attached(after, truth["control_ip"])
    if network_for_ip(after, truth["operations_ip"]):
        raise RuntimeError("operations network still attached after disconnect")
    record.update({"status": "isolated", "verified_at": utc_iso(), "control_preserved": True})
    state_path(domain).write_text(json.dumps(record, indent=2) + "\n")
    return record


def restore(domain: str) -> dict[str, Any]:
    path = state_path(domain)
    if not path.exists():
        raise RuntimeError(f"missing {path}; cannot prove which operations network should be restored")
    record = json.loads(path.read_text())
    truth = ground_truth(domain)
    service = SERVICES[domain]
    cid = container_id(service)
    networks = network_map(cid)
    verify_control_attached(networks, truth["control_ip"])

    existing = network_for_ip(networks, truth["operations_ip"])
    if existing is None:
        run(
            "docker", "network", "connect", "--ip", truth["operations_ip"],
            record["operations_network"], cid,
        )
    elif existing != record["operations_network"]:
        raise RuntimeError(f"operations IP is attached to unexpected network {existing}; refusing to mask drift")

    after = network_map(cid)
    verify_control_attached(after, truth["control_ip"])
    restored_network = network_for_ip(after, truth["operations_ip"])
    if restored_network != record["operations_network"]:
        raise RuntimeError("operations path did not restore to the recorded network/IP")
    record.update({
        "action": "restore",
        "status": "restored",
        "restored_at": utc_iso(),
        "control_preserved": True,
        "container_id_at_restore": cid,
    })
    path.write_text(json.dumps(record, indent=2) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/restore a supervisory-only OPC UA network outage.")
    parser.add_argument("domain", choices=sorted(SERVICES))
    parser.add_argument("action", choices=["start", "restore"])
    args = parser.parse_args()
    result = start(args.domain) if args.action == "start" else restore(args.domain)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
