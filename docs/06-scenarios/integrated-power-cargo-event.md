# Integrated Scenario — Generator Trip During Cargo Transfer

## Primary visual

The primary visual for this scenario is the **measured event timeline from the run**: Cargo pump electrical demand, PMS frequency/reserve/generator state, alarms and the corresponding PCAP/Zeek timestamps. Generate it from evidence rather than using a static cartoon.

This exercise proves that the three software layers are not independent dashboards.

The **Cargo process produces a calculated electrical load**, the PMS sees that load, and the PMS can remove Cargo power.

## Architecture

```text
Cargo FMU
  │ pumpPowerKW
  ▼
Vessel Coordinator
  │ externalCargoLoadKW
  ▼
PMS FMU
  │ bus / shedCargo
  ▼
Vessel Coordinator
  │ powerAvailable
  ▼
Cargo FMU
```

## Pre-PLC integrated commissioning

Start the process layer:

```bash
./labctl build
```

Capture Cargo and PMS traffic in separate terminals if desired:

```bash
./labctl capture cargo modbus
./labctl capture pms modbus
```

Run:

```bash
./labctl demo vessel
```

This commissioning exercise deliberately bypasses the PLCs and proves the **cross-system process/I/O dependency** first.

Expected narrative:

```text
Generator 1 starts
→ bus energizes
→ hotel load applied
→ Cargo valve opens
→ Cargo pump bank runs
→ Cargo pumpPowerKW rises
→ PMS total load rises
→ Generator 2 begins run-up
→ Generator 1 trips before redundancy is established
→ bus is lost
→ coordinator sets Cargo powerAvailable = FALSE
→ Cargo pump speed/flow decay
→ Generator 2 reaches ready state
→ Generator 2 breaker energizes dead bus
→ coordinator restores Cargo power
→ pump/flow recover
```

## After OpenPLC commissioning

Repeat the same operating story through:

```text
operator HMI
→ OpenPLC control logic
→ Modbus I/O
→ process models
```

The final evidence package should contain:

- Cargo Modbus PCAP,
- PMS Modbus PCAP,
- alarm chronicle,
- Cargo/PMS process state,
- PLC online state,
- historian trend,
- written incident timeline.

## What the scenario teaches

### Dependency
Cargo transfer depends on electrical availability.

### Context
A Cargo flow loss can be caused by the power system; it is not automatically a Cargo PLC fault.

### Correlation
Two domains must be placed on one timeline.

### Architecture specificity
This scenario does not claim that a generator trip directly removes mechanical shaft propulsion in the selected profile.
