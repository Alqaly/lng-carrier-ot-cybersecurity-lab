# Technology Selection and Version Policy

The project does not choose a technology because it is newest. It chooses the best fit for a specific engineering role.

## Runtime/orchestration

**Docker Compose v2 + systemd** — reference single-server deployment. It keeps network identities and namespace-level packet capture simple and reproducible.

**k3s/Kubernetes** — optional research extension. Kubernetes 1.37 was released on 26 August 2026; k3s is a lightweight conformant distribution. It is intentionally not the default because the CNI layer is not required for this lab's core OT learning goals.

## Process simulation

**OpenModelica 1.27.0** — current official stable release and an appropriate open-source Modelica/FMI toolchain.

## Controller runtime

**OpenPLC Runtime 4.1.9 + OpenPLC Editor 4.2.10** — chosen because the project needs an IEC 61131-3 educational PLC runtime with Modbus and OPC UA integration.

## Operator HMI

**FUXA 1.3.4** — current project release selected for open-source SCADA/HMI teaching. It must stay bound to loopback/reverse proxy in a shared server and is not exposed directly to the Internet.

## Historian

**Telegraf 1.39.3 + InfluxDB 2.9.1 + Grafana 13.2** — explicit pins avoid silent major-version drift. InfluxDB 2.9.1 is the reviewed 2.x patch used here; 2.9 enables API-token hashing by default, so an existing persistent deployment must preserve any plaintext client token it still needs and pass backup/restore validation before the upgrade is accepted. InfluxDB's Docker documentation warns that the `latest` tag will switch to InfluxDB 3 Core in September 2026, so the project never uses `influxdb:latest`.

## Network evidence

**Zeek 8.0.10 LTS** — selected over the newer feature branch because evidence tooling benefits from LTS stability. Zeek 8.2 is available, while 9.0 is still release-candidate at the time of this review.

**Suricata 8** — optional signature/IDS extension. Zeek remains the primary protocol/evidence analyzer because the core exercises emphasize connection and Modbus transaction evidence rather than signature-only alerts.

## Network-fidelity extension

**Containerlab 0.77.0** — selected only as the optional explicit-dataplane extension. Its `ext-container` kind can attach links to Compose-owned containers without taking over their lifecycle, and 0.77 adds `apply` reconciliation. It is not the canonical daemon because restart/interface restoration must first be proven on the target server.

**Linux static routing + nftables** — first-choice routed/default-deny enforcement. The goal is auditable conduit policy, not imitation of a specific industrial firewall product.

**Open vSwitch** — candidate only when a passive SPAN/mirror observation point is required by an experiment. Namespace/interface capture remains simpler for the reference lab.

**GNS3 / EVE-NG** — optional appliance-centric comparison environments, not reference dependencies. GNS3 explicitly does not position its Docker support as real container-infrastructure management, while EVE-NG requires users to supply their own vendor images.

**FRRouting** — not selected for Phase 3A. Linux static routing is enough until dynamic-routing behavior is itself a research or teaching objective.

The detailed decision and runtime acceptance gates live in `docs/03-architecture/network-fidelity-decision.md` and `network/fidelity-contract.json`.

## Protocol selection

Protocols are chosen by system role, not recency:

- **Modbus TCP** — simple legacy-style process I/O teaching and packet inspection.
- **OPC UA** — modern structured supervisory/historian integration with discovery, information modeling and security mechanisms.
- **NMEA 0183** — recorded-data replay for legacy serial navigation learning.
- **NMEA 2000/CAN** — scoped architecture/CAN extension; no licensed PGN database is redistributed.
- **IEC 61162-450/460** — current marine Ethernet safety/security reference. IEC 61162-460:2024 is an add-on to 61162-450 for higher safety/security requirements; the lab does not claim compliance.

A newer protocol is not automatically a better fit.
