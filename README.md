# LNG Carrier OT Cybersecurity Lab

[![quality](https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab/actions/workflows/quality.yml/badge.svg)](https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab/actions/workflows/quality.yml)


A software-defined, research-backed OT cybersecurity laboratory for learning how an LNG carrier behaves as a cyber-physical system.

The project is designed for engineers who want more than a dashboard and a few containers. The learning path is:

```text
Understand the vessel
        ↓
Understand the physical process
        ↓
Model the process with explicit physics
        ↓
Run IEC 61131-3 control logic
        ↓
Exchange real industrial protocol traffic
        ↓
Observe the operator and historian views
        ↓
Capture packets and investigate failures
        ↓
Map the result back to real marine systems
```

## Why a software-defined testbed?

A home lab cannot reproduce an LNG carrier's certified cryogenic cargo plant, propulsion system, switchboards, navigation suite and safety systems without substantial marine hardware.

The project therefore uses a **physics-based process model** together with **real protocol/runtime implementations**:

- OpenModelica for dynamic Cargo, marine power and propulsion process equations and FMI co-simulation
- OpenPLC Runtime for IEC 61131-3 PLC execution
- Modbus TCP for controller/I/O interaction
- OPC UA for process information exchange
- InfluxDB + Grafana for time-series history and visualization
- GPSD replay tooling for recorded NMEA 0183 data
- packet capture and protocol inspection for defensive analysis

The distinction matters:

> Process values are calculated by a documented dynamic model, not inserted as arbitrary dashboard numbers.

## What is based on real marine systems?

The architecture and teaching material are grounded in public material from:

- Kongsberg Maritime K-Chief / K-Safe
- ABB marine power management
- Wärtsilä LNG and gas systems
- SIGTTO ESD / ship-shore guidance
- NMEA marine data interface standards
- IEC 61162-450 / 460
- IACS UR E26 / E27
- IMO maritime cyber-risk guidance

The lab is vendor-neutral and does not claim to duplicate any specific ship or approved marine system.

## Core software architecture

> **Visual reference:** Study Figure 3 and Figure 10 in Lee (2024), the CC BY 4.0 LNG-carrier PMS HIL paper, before reading the software topology below: https://www.mdpi.com/2077-1312/12/7/1236
>
> **What to notice:** controller under test vs simulator, named interfaces, and bidirectional exchange. **Lab mapping:** OpenPLC ↔ software I/O ↔ Modelica/FMU with separate operations/evidence paths.

```text
OpenPLC Editor
      │
      ▼
OpenPLC Runtime
      │ Modbus TCP
      ▼
Virtual Remote I/O
      │
      ▼
Physics Process Runtime
      │
      ├── tank levels
      ├── flow
      ├── pressure
      └── equipment feedback

OpenPLC Runtime
      │ OPC UA
      ▼
Telegraf → InfluxDB → Grafana

Engineering / PLC / I/O conduit
      │
      └── PCAP / Wireshark / Zeek-style analysis
```


## Target-server fast path

The reference runtime is a continuously running Linux server, not a one-shot laptop demo.

```bash
cp .env.example .env
# replace every placeholder credential/token first
./labctl preflight
./labctl test
./labctl config-check
./labctl build
./labctl smoke
```

Then commission the three OpenPLC projects, discover live OPC UA nodes, install verified historian bindings, bind/validate FUXA, and complete `docs/04-build/server-acceptance-test.md`.

After full commissioning:

```bash
./labctl runtime-verify
sudo ./deploy/install-systemd.sh
```

Use `./labctl capture cargo modbus` (or PMS/propulsion) to preserve protocol evidence from the actual software control conduit.

## Start here

Read the ten-chapter course first:

1. [`01 — What Are We Building?`](docs/course/01-project-orientation.md)
2. [`02 — Understand the LNG Carrier`](docs/course/02-lng-carrier-system.md)
3. [`03 — OT Foundations`](docs/course/03-ot-foundations.md)
4. [`04 — Architecture`](docs/course/04-architecture.md)
5. [`05 — Build and Commission`](docs/course/05-build-and-commission.md)
6. [`06 — Cargo`](docs/course/06-cargo.md)
7. [`07 — Protocol Academy`](docs/course/07-protocol-academy.md)
8. [`08 — Safety, HMI and Alarms`](docs/course/08-safety-hmi-alarms.md)
9. [`09 — Navigation`](docs/course/09-navigation.md)
10. [`10 — Detection and Reconstruction`](docs/course/10-detection-reconstruction.md)

Use the deeper subsystem/build/reference chapters when the course links to them.

## Repository philosophy

Every technical layer must answer:

- What is it?
- Why does it exist?
- Where does it appear on a real vessel?
- Why are we adding it at this stage?
- How is it represented in the software lab?
- Which protocol carries the data?
- How do we verify normal behavior?
- What evidence should we collect?
- What are the security and safety implications?
- What are the limits of the representation?

## GitHub quality gate

```bash
python3 tools/quality_gate.py
```

The publication gates check documentation structure, broken local links, executable↔documentation traceability, real visual-source coverage, research/experiment contracts, pedagogy coverage and the absence of stale internal release language.

## Documentation site

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Then open:

```text
http://127.0.0.1:8000
```

## Status of the software-defined modules

| Module | Implementation |
|---|---|
| Cargo process | dynamic Modelica transfer model with pump/valve response, levels, pressure and flow |
| Power Management process | dynamic two-generator teaching model with bus frequency, reserve, breakers and load shedding |
| Propulsion & machinery process | dynamic pre-lube / engine / shaft / propeller / vessel-response model |
| PLC control | three IEC 61131-3 Structured Text projects in OpenPLC Runtime |
| Remote I/O | three Modbus TCP software I/O devices with documented contracts |
| Cross-system coupling | Cargo and machinery auxiliary electrical loads coupled into PMS; PMS power state feeds dependent systems |
| OPC UA commissioning | live address-space discovery → binding plan → verified HMI/historian bindings |
| Operator visualization | FUXA task-based operator views; project export/validation workflow |
| Teaching / explanation | Learning Portal with data provenance, contracts, diagrams and Teaching Alarm Chronicle |
| Historian | verified OPC UA bindings → Telegraf → InfluxDB → Grafana |
| Security evidence | namespace-level PCAP capture + Zeek offline Modbus analysis + integrated evidence timeline |
| Navigation | replay of recorded NMEA 0183 data using GPSD tooling; NMEA 2000 / IEC 61162 taught as scoped reference/extension |
| Ship/shore ESD | marine reference architecture and teaching exercise; not a certified SSL |

## Safety

This is a defensive and educational project. It is not a vessel-control package, class-approved design, safety system, or operational procedure for a real ship.


## Expanded training domains

The executable stack now includes three dynamic domains:

- **Cargo** — pump/valve dynamics, tank levels, pressure/head, flow transmitter response and explicit equipment/sensor faults.
- **Power Management** — two generator sets, breaker feedback, load groups, reserve, bus-frequency response and load shedding.
- **Propulsion & Machinery** — pre-lube permissive, engine/fuel/pitch control, shaft dynamics, lube pressure, coolant temperature and vessel-speed response.

Two user interfaces are intentionally separated:

- **FUXA (`:1881`)** — operator/SCADA engineering surface; configure it against OpenPLC OPC UA.
- **Learning Portal (`:8500`)** — read-only explanation surface showing where values come from and the teaching alarm chronicle.

See `docs/04-build/hmi-and-alarm-system.md` before designing operator screens.

## Always-on server deployment

The reference target is a Linux server running Docker Compose v2 under systemd:

```bash
cp .env.example .env
./labctl test
sudo ./deploy/install-systemd.sh
```

Kubernetes/k3s is intentionally optional; see `docs/03-architecture/deployment-decision.md`.

## Research experiments

```bash
./labctl new-run EXP-CARGO-BLOCKED-FLOW
# collect required artifacts
./labctl evaluate evidence/runs/<run-dir>
```

## Canonical GitHub

https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab

Static CI is publication evidence; it does not replace target-server runtime acceptance.
