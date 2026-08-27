# Cross-Layer Evidence Workbook

Use this worksheet for every meaningful scenario.

The goal is to stop an investigation from becoming a collection of disconnected screenshots.

## Scenario identity

```text
Exercise:
Operator objective:
Initial plant state:
Expected final state:
Domain(s): Cargo / PMS / Propulsion / Navigation / cross-system
```

## 1 — Establish the expected process story

Before touching Wireshark, write the expected causal sequence.

Example:

```text
Cargo transfer enable
→ valve command
→ valve feedback
→ pump command
→ pump feedback
→ flow
→ source level ↓
→ receiving level ↑
→ Cargo pump kW ↑
→ PMS load ↑
```

If you cannot write the expected story, you do not yet have a useful baseline.

## 2 — Command / protocol table

| Time | Source | Destination | Protocol | Operation | Address / Node | Expected meaning |
|---|---|---|---|---|---|---|
| | | | Modbus TCP | | | |
| | | | OPC UA | | | |

For Modbus, record:

- function code,
- address,
- raw value,
- decoded engineering meaning,
- whether the source belongs to the expected conduit.

## 3 — Controller table

| Time | PLC symbol | Previous | New | Why did it change? |
|---|---|---:|---:|---|
| | | | | |

Distinguish:

```text
operator command
controller output
field/I/O feedback
process measurement
protective condition
```

## 4 — Process table

| Time | Process variable | Value | Expected direction | Consistent? |
|---|---|---:|---|---|
| | flow | | ↑ / ↓ / stable | |
| | level | | ↑ / ↓ / stable | |
| | frequency | | ↑ / ↓ / stable | |
| | RPM | | ↑ / ↓ / stable | |

## 5 — Alarm chronology

| Time | Alarm | Transition | Priority | Initiating cause or downstream symptom? |
|---|---|---|---|---|
| | | ACTIVE / ACK / CLEARED | | |

The earliest alarm is not automatically the root cause, but chronology prevents you from treating every symptom as an independent incident.

## 6 — Historian / visibility check

For each important point record:

```text
PLC online value:
OPC UA NodeId:
Quality/status:
Source/server timestamp:
Historian timestamp:
Grafana value:
```

Ask whether the information layer is fresh and trustworthy.

## 7 — Competing explanations

Write at least three plausible explanations before deciding.

Example for `pump command ON + feedback ON + measured flow low`:

1. pump/process failure,
2. flow-measurement problem,
3. I/O / mapping problem,
4. power dependency problem,
5. unauthorized command / control-path issue.

## 8 — Evidence that eliminates each explanation

| Hypothesis | Evidence for | Evidence against | Result |
|---|---|---|---|
| | | | |

## 9 — Root cause and propagation

```text
Initiating event
→ first affected layer
→ cross-system dependency
→ downstream alarms
→ operator consequence
```

## 10 — Recovery proof

Do not end at “alarm cleared.”

Verify:

- expected PLC program/control state,
- correct I/O map,
- process returned to a known operating state,
- communications path is expected,
- alarm state returned normally,
- historian freshness recovered,
- the normal scenario can be repeated.

## 11 — Explain-back

A complete exercise ends when you can explain the event from memory:

> who intended what → which message crossed which conduit → which PLC/I/O point changed → how the process responded → which alarms appeared → which evidence proved the root cause.
