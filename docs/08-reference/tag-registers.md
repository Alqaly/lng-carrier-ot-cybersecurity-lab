# Tag and Register Reference

This page is the cross-layer I/O contract for the executable software lab.

A Modbus address is not meaningful by itself. The meaning comes from this documented contract.

## Cargo

### Commands

| Modbus object | Address | Meaning | Raw → model |
|---|---:|---|---|
| Coil | 0 | cargo pump-bank command | `0/1 → false/true` |
| Holding Register | 0 | aggregate transfer-valve command | `0…1000 → 0.0…1.0` |
| Coil | 20 | instructor pump-failure fault | Boolean |
| Coil | 21 | instructor valve-stuck fault | Boolean |
| Holding Register | 20 | instructor flow-sensor positive bias | `raw × 0.1 %` |

`powerAvailable` is not a normal Modbus operator point. In the integrated vessel profile it is supplied directly by the Vessel Coordinator from PMS bus/shedding state.

### Measurements and feedback

| Object | Address | Meaning | Raw representation |
|---|---:|---|---|
| Input Register | 0 | aggregate source-tank level | mm |
| Input Register | 1 | aggregate destination level | mm |
| Input Register | 2 | measured cargo flow | m³/h |
| Input Register | 3 | source hydrostatic pressure | kPa × 10 |
| Input Register | 4 | valve position | fraction × 1000 |
| Input Register | 5 | pump-bank speed | fraction × 1000 |
| Input Register | 6 | calculated pump-bank electrical demand | kW |
| Discrete Input | 0 | valve-open feedback | Boolean |
| Discrete Input | 1 | pump-running feedback | Boolean |
| Discrete Input | 2 | destination high-high | Boolean |
| Discrete Input | 3 | source low-low | Boolean |

## Power Management

### Commands and standalone load demands

| Object | Address | Meaning |
|---|---:|---|
| Coil | 0 | Generator 1 start |
| Coil | 1 | Generator 2 start |
| Coil | 2 | Generator 1 breaker command |
| Coil | 3 | Generator 2 breaker command |
| Coil | 4 | shed hotel/auxiliary teaching load |
| Coil | 5 | shed Cargo electrical load |
| Coil | 20 | instructor Gen 1 trip |
| Coil | 21 | instructor Gen 2 trip |
| Holding Register | 0 | standalone hotel load demand (`0/1`) |
| Holding Register | 1 | standalone Cargo load demand (`0/1`) |
| Holding Register | 2 | optional electric-propulsion exercise demand (`0/1`) |

The integrated Vessel Coordinator also supplies real-valued `externalCargoLoadKW` and `externalAuxLoadKW` directly to the PMS process model. Those values come from the Cargo and propulsion process models rather than from arbitrary registers.

### Measurements and feedback

| Object | Address | Meaning | Raw representation |
|---|---:|---|---|
| Input Register | 0 | bus frequency | Hz × 100 |
| Input Register | 1 | bus voltage | p.u. × 1000 |
| Input Register | 2 | Gen 1 active power | kW |
| Input Register | 3 | Gen 2 active power | kW |
| Input Register | 4 | total electrical load | kW |
| Input Register | 5 | spinning reserve | kW |
| Input Register | 6 | Gen 1 speed | p.u. × 1000 |
| Input Register | 7 | Gen 2 speed | p.u. × 1000 |
| Input Register | 8 | actual Cargo load contribution | kW |
| Input Register | 9 | actual propulsion-auxiliary load contribution | kW |
| Discrete Input | 0 | Gen 1 ready |
| Discrete Input | 1 | Gen 2 ready |
| Discrete Input | 2 | Gen 1 breaker feedback |
| Discrete Input | 3 | Gen 2 breaker feedback |
| Discrete Input | 4 | under-frequency |
| Discrete Input | 5 | blackout |
| Discrete Input | 6 | Gen 1 sync permissive |
| Discrete Input | 7 | Gen 2 sync permissive |
| Discrete Input | 8 | bus energized |

## Propulsion and machinery

### Commands

| Object | Address | Meaning | Raw representation |
|---|---:|---|---|
| Coil | 0 | pre-lube command | Boolean |
| Coil | 1 | engine enable | Boolean |
| Coil | 20 | instructor lube-pump failure | Boolean |
| Holding Register | 0 | fuel command | `0…1000 → 0.0…1.0` |
| Holding Register | 1 | propeller-pitch command | `0…1000 → 0.0…1.0` |

`auxPowerAvailable` is provided by the Vessel Coordinator in the integrated profile. It controls the electrically dependent pre-lube path; once the engine is turning the teaching model represents an engine-driven main lube-pump contribution.

### Measurements and feedback

| Object | Address | Meaning | Raw representation |
|---|---:|---|---|
| Input Register | 0 | engine speed | RPM × 10 |
| Input Register | 1 | lube-oil pressure | bar × 100 |
| Input Register | 2 | coolant temperature | °C × 10 |
| Input Register | 3 | vessel speed response | kn × 100 |
| Input Register | 4 | engine load | % × 10 |
| Input Register | 5 | propeller load torque | 10 N·m per count |
| Input Register | 6 | propulsion auxiliary electrical load | kW |
| Discrete Input | 0 | engine running |
| Discrete Input | 1 | low lube pressure |
| Discrete Input | 2 | high coolant temperature |
| Discrete Input | 3 | overspeed |

## Change-control rule

When adding or changing a tag, update every affected layer:

```text
Modelica variable
→ FMU contract
→ I/O configuration
→ Modbus map
→ PLC symbol
→ OPC UA node
→ HMI / alarm
→ historian
→ walkthrough
→ detection / evidence logic
```

A successful `pytest` run checks several of these mappings automatically.
