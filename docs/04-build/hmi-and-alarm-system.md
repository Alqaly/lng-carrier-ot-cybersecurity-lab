# Operator HMI and Alarm System

The lab now separates **operator control**, **engineering/learning**, and **historical analysis**.

## Visual tour

Do not design the operator view from a web-dashboard template. Study:

- SIGTTO Cargo Control Room HMI recommendations: https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/
- Kongsberg K-Chief operator-panel material: https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/343101_tcp_datasheet_kchief600.pdf

Then compare those principles with the FUXA screen captured from your actual running lab.

## Why this matters

A training lab often makes the dashboard do everything. Real automation separates responsibilities:

- the PLC executes control logic,
- the HMI presents state and operator commands,
- the alarm system manages abnormal conditions,
- the historian stores time-series data,
- the learning portal explains the implementation.

The HMI should not become a second controller.

## Operator display

The project includes FUXA as the SCADA/HMI engineering surface at:

```text
http://127.0.0.1:1881
```

FUXA is an open-source web SCADA/HMI platform with Modbus and OPC UA connectivity, an SVG editor, alarms, alarm acknowledgement and alarm history.

### Recommended final connection

```text
OpenPLC OPC UA server
        ↓
FUXA OPC UA client
        ↓
operator displays / alarms
```

This intentionally keeps the operator layer above the controller rather than connecting the HMI directly to the physics runtime.

## Display philosophy

Public ISA material on high-performance HMI practice emphasizes muted/grayscale normal displays and sparse, meaningful use of color for abnormal conditions. The project follows the spirit of that guidance without claiming ISA-101 compliance.

Use:
- neutral background,
- thin equipment outlines,
- numerical values close to the relevant equipment,
- trends where rate-of-change matters,
- color primarily for abnormal conditions,
- text/shape in addition to color so alarm meaning does not depend on color alone.

Avoid:
- decorative gradients,
- green/red everywhere,
- animated pipes that do not add information,
- giant gauges for every value,
- normal-state color competing with alarms.

## Display hierarchy

### Level 1 — Vessel overview
Show Cargo / Power / Propulsion / Safety status and only the most important abnormalities.

### Level 2 — Domain overview
Example: Cargo transfer overview with source tank, destination tank, valve, pump and key trends.

### Level 3 — Detailed process
Detailed I/O, permissives, controller variables and alarm status.

### Level 4 — Diagnostic
Raw Modbus mapping, OPC UA metadata, packet capture, controller timing and communication diagnostics.

## Alarm ≠ event ≠ trip

**Event**: something happened and should be recorded.

**Alarm**: an abnormal condition requiring timely operator response.

**Trip**: protective control action that moves equipment/process toward a safe state.

The lab alarm chronicle uses a simple lifecycle:

```text
NORMAL
  ↓ condition true
ACTIVE / UNACK
  ↓ acknowledge
ACTIVE / ACK
  ↓ condition clears
RETURNED TO NORMAL
```

The separate `alarm-engine` service records transitions in SQLite and exposes current/history APIs for teaching. FUXA should be configured with the corresponding operator alarms once the OPC UA project is commissioned.

## Initial alarm rationalization table

| Alarm | Priority | Trigger | Operator meaning | First response |
|---|---|---|---|---|
| Cargo destination HH | High | destination ≥ 0.95 m in model | transfer is approaching modeled destination limit | verify transfer sequence and stop condition |
| Cargo source LL | High | source ≤ 0.08 m | source is nearly depleted | stop transfer / verify source state |
| Cargo no flow | Medium | pump + valve feedback but near-zero flow | equipment says running but process response is absent | inspect command, feedback and process path |
| PMS under-frequency | High | bus < 58.5 Hz in training model | generation/load balance is degraded | verify generation, load shed and breaker state |
| PMS blackout | Critical | bus unavailable | electrical supply is lost | establish power state and recovery sequence |
| Propulsion low lube | Critical | engine running and pressure < 2 bar | machinery damage risk | remove engine enable / inspect lube system |
| Propulsion high coolant | High | coolant > 92 °C | thermal stress | reduce load / inspect cooling |

These thresholds are **training-model settings**, not operating limits for a real vessel.

## Learning Portal

Open:

```text
http://127.0.0.1:8500
```

This is deliberately **not** the operator HMI. It explains the source chain across Cargo, PMS and propulsion and shows the teaching alarm chronicle.


## Build specifications

Continue with:

- `task-based-hmi-design.md` — screen hierarchy and Cargo loading-task design,
- `alarm-rationalization.md` — alarm lifecycle, delay and rationalization,
- `fuxa-commissioning.md` — connect the operator HMI to OpenPLC OPC UA.

Importable design assets are provided in `fuxa/widgets/`.
