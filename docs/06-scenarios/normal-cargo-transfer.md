# Scenario — Normal Cargo Transfer

For your first direct-I/O learning session, use the
[guided Cargo investigation](first-cargo-investigation.md): it includes power
setup, exact commands, register decoding and expected observations. This page
describes the later commissioned PLC sequence and its evidence requirements.

## Objective

Prove the expected state transition.

## Initial state

```text
pump command = OFF
valve command = CLOSED
flow ≈ 0
source level stable
destination level stable
```

## Action

Enable transfer mode and request valve/pump operation.

## Expected sequence

```text
valve command
→ valve feedback
→ pump command
→ pump feedback
→ flow rises
→ source level falls
→ destination level rises
```

## Evidence

Collect:
- Modbus packet sequence,
- PLC online state,
- process-runtime state,
- historian trend.

The scenario is complete only if all four tell the same story.
