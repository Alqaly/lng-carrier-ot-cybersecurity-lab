# Troubleshooting Cases

These cases are designed to force evidence-driven reasoning.

## Case 1 — Pump command but no flow

**Symptoms**
- pump command true,
- pump feedback true or ambiguous,
- measured flow near zero.

**Possible layers**
- pump model fault,
- valve not actually open,
- source depleted,
- flow measurement bias,
- I/O mapping issue.

**Evidence order**
1. PLC command.
2. Modbus write.
3. valve/pump feedback.
4. FMU state.
5. flow input register.
6. historian timeline.

## Case 2 — Valve command with missing feedback

Look for actuator dynamics versus stuck-valve fault. A valve can require time to reach position, so an immediate mismatch is not necessarily a fault. This introduces **alarm delay/debounce** thinking.

## Case 3 — Flow value disagrees with levels

Inject flow-sensor bias. The source/destination levels continue according to actual hydraulic flow while the measured flow is biased.

Question:
> Which independent process variables can reveal that the measurement is inconsistent?

## Case 4 — Generator loss

Trip Gen 1 under high demand. Observe:
- frequency response,
- reserve,
- Gen 2 start/close sequence,
- load shedding,
- alarm chronology.

## Case 5 — Premature breaker command

The breaker command can be true while breaker feedback remains false until generator readiness exists.

This is the electrical equivalent of command versus feedback in Cargo.

## Case 6 — Propulsion low lube

Fail the lube pump while engine is loaded. Track:
- pressure decay,
- alarm activation,
- protective trip,
- RPM decay,
- vessel-speed lag.

## Case 7 — Historian goes stale

Stop the OPC UA source or Telegraf. Process control continues while historical visibility stops.

Question:
> Is this a process failure or an observability failure?

## Case 8 — Unexpected Modbus source

Capture a Modbus request from a client that is not the expected PLC address.

The detection is cyber-relevant because it violates the expected conduit, but you still validate whether process state changed.
