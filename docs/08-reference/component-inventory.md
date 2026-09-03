# Component Inventory and Validation Level

This page answers a simple question: **what exists in the project, what role does it play, and what has actually been validated?**

Machine-readable boundaries are maintained in `config/project-scope.json`, `config/architecture-contract.json`, `vessel/coverage-contract.json`, and `config/data-semantics-contract.json`.

Validation labels:

- **Static PASS** — source/configuration/contract is covered by automated local gates.
- **Target runtime required** — must be exercised on the Docker-capable server before publication evidence is complete.
- **Reference only** — taught from real maritime/standards sources; not claimed as an executable conformant implementation.

## Cyber-physical core

| Component | Role | Representation | Validation now | Target-server acceptance |
|---|---|---|---|---|
| Cargo process | ship-unloading teaching profile | Modelica/FMI dynamic simulation | Static PASS | run causal baseline + blockage + bias experiments |
| PMS process | two-generator teaching plant | Modelica/FMI dynamic simulation | Static PASS | run load-step, trip, reserve/shedding tests |
| Propulsion process | engine/shaft/auxiliary teaching plant | Modelica/FMI dynamic simulation | Static PASS | run pre-lube/start/cooling-fault tests |
| Vessel coordinator | cross-domain electrical/operational coupling | real software service | Static PASS | verify coupled event ordering |
| Cargo/PMS/Propulsion I/O | protocol-facing remote I/O abstraction | Modbus TCP emulation | Static PASS | capture packets and compare with tag map |
| Cargo/PMS/Propulsion PLC | control logic | IEC 61131-3 Structured Text on OpenPLC Runtime | source/mapping PASS | deploy three Editor projects and verify online state |

The Vessel Coordinator exchanges dependency values through the three process HTTP APIs. It is intentionally separate from the OpenPLC ↔ Modbus Remote I/O control path; its events must not be described as Modbus traffic unless a capture actually shows a separate Modbus action.

## Operations and evidence

| Component | Role | Representation | Validation now | Target-server acceptance |
|---|---|---|---|---|
| OPC UA | structured supervisory interface | real OpenPLC OPC UA service | discovery/binding tooling PASS | discover exact live NodeIds; reject missing/ambiguous bindings |
| Telegraf | OPC UA ingestion | real software | config contract PASS | ingest verified live nodes only |
| InfluxDB | historian store | real software | explicit dependency pin | verify fresh samples and outage gaps |
| Grafana | historical visualization | real software | explicit dependency pin | compare plots with PLC/process values |
| FUXA | operator/HMI surface | real software | project lifecycle tooling PASS | bind live tags; validate/export commissioned project |
| Alarm Chronicle | teaching event/alarm timeline | real software teaching service | logic tests PASS | compare chronology with process/PLC evidence |
| Learning Portal | explain-back/data-provenance surface | real software | static/read-only contract PASS | verify live state without control authority |
| Namespace capture | PCAP evidence | tcpdump sidecars sharing target namespace | architecture tests PASS | capture Modbus/OPC UA traffic |
| Zeek | offline protocol/connection analysis | real evidence tool | explicit LTS pin + classifier tests | generate logs from captured PCAP |
| Historian freshness checker | supervisory data-loss evidence | real analysis tool | tests PASS | prove OPC UA/historian outage separately from process-source loss |
| Process residual analyzer | cyber-physical integrity evidence | real analysis tool | tests PASS | compare measured vs inferred Cargo flow |
| Conduit classifier | expected/unexpected network source evidence | real analysis tool | tests PASS | classify Zeek flows against fixed conduit ground truth |
| Commissioning orchestrator | resumable Gates A–G execution and evidence integrity | real host-side state machine | unit/static PASS | execute on the clean target commit; finalize the hashed dossier |

## Navigation and maritime-reference layer

| Component | Role | Status |
|---|---|---|
| NMEA 0183 | legacy serial navigation teaching | recorded-data replay without GNSS hardware; real protocol concepts |
| NMEA 2000 | CAN-based marine network teaching | reference/optional extension; licensed PGN database not redistributed |
| CAN/J1939 | machinery network concepts | scoped software/CAN teaching extension, equipment-specific use stated explicitly |
| IEC 61162-450/-460 | marine navigation Ethernet | standards/reference layer only; no conformity claim |
| Ship/shore ESD | gas-carrier transfer safety context | SIGTTO-backed reference + teaching permissive; not a certified SSL |
| K-Chief/K-Safe/K-Gauge, ABB PEMS, Wärtsilä gas/engine systems | real-vessel architecture anchors | official vendor/industry reference; not cloned or vendor-equivalent |

## Deployment

The reference always-on deployment is **Docker Compose v2 + systemd on one Linux server**. k3s/Kubernetes is intentionally an optional research extension because the default laboratory depends on stable OT identities and easy namespace-level packet attribution.

All externally exposed application ports in the reference Compose file bind to `127.0.0.1`. Remote access should be provided through an explicitly designed secure administration path rather than opening the laboratory directly to the Internet.

## What “complete” means

The repository can be called **source-complete** when all static/research/pedagogy/traceability gates pass. It can be called **runtime-commissioned** only after the target server completes Gates A–G in `docs/04-build/server-acceptance-test.md` and retains the evidence.
