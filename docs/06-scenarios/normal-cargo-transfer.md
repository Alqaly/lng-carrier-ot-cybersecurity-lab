# Scenario — Normal Cargo Transfer

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
