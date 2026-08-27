# 06 — Cargo: From Transfer Physics to Evidence

## Why this matters

Cargo is where process physics, control sequencing, marine safety context and cybersecurity evidence become one story.

## Operational profile used by the executable model

The core model is explicitly a **ship unloading profile** so the ship cargo-pump electrical demand can be coupled defensibly to PMS.

It is not an ambiguous “tank A → tank B” animation.

## Visual tour — real Cargo HMI and safety context

Use:

- SIGTTO Cargo Control Room HMI guidance: https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/
- SIGTTO ESD Systems: https://www.sigtto.org/publications/esd-systems/
- Wärtsilä Gas Solutions: https://www.wartsila.com/marine/products/gas-solutions

## Memory hook

```text
PERMIT → VALVE → FEEDBACK → PUMP → FEEDBACK → FLOW → INVENTORY
```

## Process model

The model includes deterministic dynamics such as:

- valve travel,
- pump response,
- head-dependent transfer behavior,
- sensor lag,
- ship-tank inventory,
- source pressure,
- electrical demand,
- deterministic blockage/sensor faults.

Every simplification is documented in `model-assumptions.md`.

## Worked example — blocked path

Fault condition:

```text
Valve feedback = OPEN
Pump feedback  = RUNNING
Measured flow  ≈ 0
Pump electrical demand > 0
```

This is deliberately different from pump failure.

Network evidence can prove the commands were sent. Process evidence shows the commanded operation failed to produce expected hydraulic response.

## Experiment

```bash
./labctl new-run EXP-CARGO-BLOCKED-FLOW
```

Collect the Cargo Modbus capture, state timeline and alarm timeline, then evaluate the run.

## Cybersecurity lesson

A process-aware investigator asks whether **commanded state, equipment feedback and measured consequence agree**. That is more useful than labeling every unusual register write an “attack.”

## Explain it in 60 seconds

Explain the blocked-flow scenario using command, feedback, process response, electrical demand and packet evidence.

## Go deeper

- [Cargo system](../01-vessel/cargo-system.md)
- [Process model](../04-build/process-model.md)
- [Process integrity scenario](../06-scenarios/process-integrity.md)
