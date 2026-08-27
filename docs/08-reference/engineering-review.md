# Engineering Review

This page records the current technical audit of the repository.

## What is executable

- dynamic Cargo transfer equations in Modelica,
- dynamic two-generator Power Management model,
- dynamic propulsion/machinery model,
- FMU Co-Simulation build path for all three domains,
- generic process runtime using FMPy,
- three Modbus TCP software I/O services,
- IEC 61131-3 Structured Text for Cargo, PMS and Propulsion,
- three OpenPLC Runtime containers,
- cross-system Vessel Coordinator coupling electrical dependencies,
- rationalized teaching alarm chronicle,
- FUXA operator-HMI runtime,
- live OPC UA discovery tooling,
- OPC UA historian architecture,
- InfluxDB / Grafana,
- namespace packet-capture sidecars,
- Zeek offline analysis,
- integrated three-domain commissioning scenario with structured evidence timeline,
- guided Learning Portal.

## What requires user commissioning

### OpenPLC Editor project
The repository provides Structured Text and the intended I/O map. The current OpenPLC Runtime architecture expects the Editor project to generate/deploy Remote-I/O and OPC-UA plugin configuration.

Therefore the learner must still:
1. create/import the project in OpenPLC Editor,
2. configure the Modbus Remote I/O device,
3. map the I/O groups,
4. enable/configure OPC UA,
5. deploy to Runtime.

This is documented rather than hidden.

### OPC UA NodeIds
The Telegraf configuration contains example names. The learner must browse the deployed OpenPLC OPC UA server and verify the actual namespace/NodeIds before treating historian ingestion as commissioned.

The repository now includes `./labctl opcua <domain>` which browses the **live** server and saves NodeId/namespace/type/status/timestamp evidence under `evidence/opcua/`.

## Process-model boundary

The Cargo process model is a simplified dynamic transfer model.

It is suitable for teaching:
- causal state changes,
- pump/valve sequencing,
- tank-level evolution,
- pressure/head concepts,
- control/feedback relationships.

It does not attempt:
- cryogenic thermodynamic fidelity,
- membrane containment mechanics,
- real LNG pump curves,
- BOG/reliquefaction dynamics,
- class-approved safety calculations.

Those belong to the marine reference/research layer unless a dedicated validated model is added.

## Navigation boundary

Without GNSS hardware, NMEA 0183 is taught through recorded-data replay using GPSD tooling.

Replay is useful for:
- sentence parsing,
- transport/client behavior,
- evidence analysis.

Replay is not presented as a live sensor.

## PMS and propulsion model boundary

PMS and propulsion now have dedicated dynamic Modelica models and IEC 61131-3 control programs. Their outputs are calculated from documented equations and explicit commands/fault inputs; they are not dashboard-only numbers.

They remain **teaching models**, not manufacturer digital twins.

The PMS model does not claim detailed generator electromagnetic transients, AVR/protection relay studies or proprietary marine load-management algorithms.

The propulsion model does not claim a WinGD/MAN/Wärtsilä engine model, combustion/turbocharger fidelity, torsional analysis or a validated hull/propeller design model.

See `model-assumptions.md` for the current modelling contract.

## Runtime validation still required

The repository passes static checks in this build environment, but this environment does not provide a Docker daemon. A contributor should perform the documented end-to-end runtime commissioning on a Docker-capable host and preserve evidence.

## Recursive review rule

Before extending the lab:

```text
process equation
↔ I/O map
↔ PLC tag
↔ protocol message
↔ historian point
↔ visual
↔ walkthrough
↔ source/reference
```

A change is incomplete if one of these layers drifts from the others.
