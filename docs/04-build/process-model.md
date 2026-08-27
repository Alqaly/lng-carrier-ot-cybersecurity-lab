# Cargo Process Model — From LNG Reference to Executable Equations

## Visual tour

For the real LNG context, use Wärtsilä Gas Solutions and SIGTTO cargo/ESD material. For the executable model, plot actual Modelica outputs from a run: valve position, pump speed, measured flow, ship-tank level and pump electrical demand.

Reference: https://www.wartsila.com/marine/products/gas-solutions

The executable Cargo plant is a **dynamic teaching model**, not a collection of scripted values.

## Real-world anchor

Wärtsilä's public reference for a typical 138,000 m³ LNG tanker describes four membrane cargo tanks with two 1700 m³/h electric submerged pumps per tank. That gives a public equipment anchor of:

```text
4 tanks × 2 pumps × 1700 m³/h = 13,600 m³/h
```

The software model aggregates that eight-pump bank into one equivalent transfer train. The public reference anchors the **capacity concept**; pump head, efficiency, tank geometry and control time constants are explicitly teaching assumptions.

Official reference:
https://www.wartsila.com/encyclopedia/term/cargo-handling-equipment-of-a-typical-138-000m3-lng-tanker

## What the model contains

```text
Source tank
    │
    ▼
Equivalent cargo pump bank
    │
    ▼
Motorized transfer valve
    │
    ▼
Destination tank
```

State and measured values include:

- source/destination tank level,
- source/destination hydrostatic teaching pressure,
- actual aggregate flow,
- lagged measured flow,
- pump-bank speed,
- valve position,
- pump electrical demand,
- high-high / low-low conditions.

## Pump dynamics

A commanded pump does not jump instantly to 100% speed:

```text
d(pumpSpeed)/dt = (target - pumpSpeed) / τpump
```

The target becomes zero if:

- power is unavailable,
- an instructor pump failure is active,
- the command is removed.

That makes a power-system event visible as a physical Cargo transient rather than a dashboard-only Boolean.

## Valve dynamics

```text
d(valvePosition)/dt = (valveCommand - valvePosition) / τvalve
```

A valve-stuck fault freezes the actuator state deliberately. No random failure is generated.

## Flow relationship

The model calculates available pump head from pump speed and liquid-level difference. Aggregate flow then depends on:

```text
nominal pump-bank capacity
× valve opening
× available-head factor
```

The model therefore produces causal behavior:

```text
valve closed        → no transfer
pump stopped        → no transfer
power removed       → pump decelerates → flow decays
source level falls  → hydraulic conditions change
```

## Measurement dynamics

The measured-flow signal is a separate state with first-order response:

```text
d(flowMeasured)/dt = (biasedActualFlow - flowMeasured) / τsensor
```

This lets the course distinguish:

```text
actual process value
vs
measured / reported value
```

A sensor-bias exercise changes only the measurement path; it does not magically change the true process flow.

## Tank balance

For the aggregate source and receiving tanks:

```text
d(levelSource)/dt      = -flow / areaSource
d(levelDestination)/dt =  flow / areaDestination
```

The model therefore conserves transferred liquid volume under its simplified geometry.

## Pressure

Hydrostatic teaching pressure is:

```text
p = ρgh
```

This is useful for understanding measurement/control causality but is not an LNG containment-pressure model.

## Pump electrical demand

The model derives approximate pump load from hydraulic power:

```text
P ≈ ρ g Q H / η
```

That calculated `pumpPowerKW` becomes a **real input to the PMS model through the Vessel Coordinator**.

So the integrated chain is:

```text
Cargo equations
→ pumpPowerKW
→ PMS external Cargo load
→ bus/load-shed state
→ Cargo powerAvailable
→ Cargo equations
```

## Verify the model before the PLC

Run:

```bash
./labctl build
./labctl demo cargo
```

During the demo, verify the sequence rather than just watching numbers move:

1. valve command changes,
2. valve position moves over time,
3. valve feedback becomes true,
4. pump command changes,
5. pump speed rises over time,
6. measured flow rises after the process responds,
7. source level falls,
8. destination level rises,
9. pump electrical demand rises.

Capture Modbus in another terminal:

```bash
./labctl capture cargo modbus
```

Then prove one value end to end with `docs/08-reference/generated-io-map.md`.

## Explicit limitations

This model does not claim fidelity for:

- cryogenic thermodynamics,
- tank membrane heat transfer,
- BOG generation/reliquefaction,
- real pump curves/NPSH/cavitation,
- surge/water hammer,
- terminal loading-arm hydraulics,
- class-approved ESD timing.

Those limitations are part of the lesson, not hidden behind the UI.
