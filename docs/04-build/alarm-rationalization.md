# Alarm Rationalization and Chronicle

The alarm layer is not a list of red tags.

SIGTTO's public gas-carrier alarm-management guidance warns that modern cargo systems can generate alarm floods, chattering/fleeting/stale alarms and loss of operator trust. It recommends a lifecycle approach covering philosophy, identification, rationalisation, design, implementation, operation, maintenance, monitoring, management of change and audit.

Official source:
https://www.sigtto.org/publications/recommendations-for-management-of-cargo-alarm-systems/

## What this repository implements

Alarm definitions live in:

```text
alarms/catalog.json
```

Every definition includes:

- priority,
- process domain,
- trigger conditions,
- activation delay,
- clear delay,
- consequence,
- operator response,
- rationale.

The Learning Alarm Chronicle then manages:

```text
NORMAL
  ↓ condition persists for activation delay
ACTIVE / UNACKNOWLEDGED
  ↓ acknowledge
ACTIVE / ACKNOWLEDGED
  ↓ condition clears for clear delay
RETURN TO NORMAL
```

## Why delays exist

A flow alarm should not fire during the first fraction of a second while a pump/valve is still moving toward a steady operating state.

A slow coolant-temperature alarm should not chatter when one numerical sample crosses a threshold and immediately returns.

This is why alarms have deliberate time qualification.

## Alarm ≠ trip

The alarm engine describes the abnormal condition to the learner/operator.

Protective PLC/model logic determines the control action.

Those roles remain separate.

## Rationalization questions

For every new alarm, answer:

1. What abnormal condition does it represent?
2. Why does the operator need to know now?
3. What is the consequence of no response?
4. What is the expected first response?
5. Is an alarm needed, or is this only an event/status?
6. What priority is justified?
7. Should a delay/hysteresis suppress nuisance behavior?
8. What related alarms could flood at the same time?

## API

```text
GET  /catalog
GET  /alarms
GET  /history
POST /ack/{alarm_id}
```

The API is a teaching chronicle. The final FUXA operator alarm definitions should be created from the commissioned PLC OPC UA nodes.


## Hysteresis / return-to-normal thresholds

Some alarms use a different clearing condition from the activation threshold.

Example:

```text
Under-frequency activates below 58.5 Hz
Under-frequency clears at/above 59.0 Hz
```

The gap prevents repeated activation/clear transitions when the signal oscillates around one boundary.

The catalogue expresses this with:

```json
"conditions": [...],
"clear_conditions": [...]
```

## Stale-data alarms

The alarm engine also treats **loss of fresh process visibility** as a separate abnormal condition.

Examples:

```text
CARGO_DATA_STALE
PMS_DATA_STALE
PROPULSION_DATA_STALE
```

These do not mean the physical process has failed. They mean the operator/learning layer can no longer verify current state.

That distinction is central to OT incident response:

```text
process failure ≠ control failure ≠ visibility failure
```
