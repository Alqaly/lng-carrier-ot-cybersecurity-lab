# Operator Alarm Workflow — From Abnormal Condition to Investigation

SIGTTO's current public publications include both **Recommendations for Cargo Control Room HMI** and **Recommendations for Management of Cargo Alarm Systems**. The first recommends an operator-centred HMI design process and provides a task-based loading-display example; the second recommends an alarm-management philosophy for gas-carrier cargo systems.

Official sources:
- https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/
- https://www.sigtto.org/publications/recommendations-for-management-of-cargo-alarm-systems/

The lab uses those ideas as teaching guidance. It does not claim SIGTTO compliance.

## What an operator needs from an alarm

An alarm should answer more than:

```text
RED = BAD
```

The learner should know:

```text
What changed?
Why does it matter?
How urgent is it?
What should I verify first?
What would clear it?
What other alarms are causally related?
```

## Alarm lifecycle

The `alarm-engine` tracks transitions:

```text
NORMAL
  │ condition persists for activation delay
  ▼
ACTIVE / UNACK
  │ acknowledge
  ▼
ACTIVE / ACK
  │ clear condition persists for clear delay
  ▼
RETURNED TO NORMAL
```

A history entry is written for the transition, so the course can compare alarm time with PCAP and process time.

## Hysteresis and debounce

Consider PMS low reserve:

```text
activate below 1200 kW for 5 s
clear at/above 1500 kW for 3 s
```

Using different activation/clear thresholds prevents an alarm from chattering around one exact boundary.

## Alarm flood versus cascading event

A large number of transitions can mean different things:

- one real initiating event caused many dependent alarms,
- thresholds/timers are poor,
- telemetry is unstable,
- multiple independent failures occurred.

The alarm engine exposes `transitions_last_10m` and a teaching flood-warning flag. That metric is not a real-vessel KPI limit; it exists so the learner notices alarm-system behavior itself.

## Example: generator trip during Cargo transfer

Possible chronology:

```text
Generator 1 unavailable
      ↓
PMS reserve / frequency changes
      ↓
Bus unavailable or Cargo shed
      ↓
Cargo power unavailable
      ↓
Cargo pump speed / measured flow decay
      ↓
Cargo no-flow may appear depending on feedback/timing
```

The correct response is not to investigate five unrelated alarms independently. Start with the earliest credible initiating event and confirm the dependency graph.

## Practical workflow

1. Open Learning Portal `http://127.0.0.1:8500`.
2. Keep the Alarm Chronicle visible.
3. Capture PMS and Cargo Modbus traffic in separate terminals.
4. Run `./labctl demo vessel` for process/I/O commissioning, or repeat through PLC after OpenPLC commissioning.
5. Export alarm history from `/history`.
6. Write a timeline with:
   - first abnormal process transition,
   - first alarm activation,
   - control/protective response,
   - dependent alarms,
   - recovery.
7. Explain which alarm was the best symptom of the initiating problem and which alarms were consequences.

## Design rule

Do not add an alarm merely because a tag exists.

Every new alarm definition requires:

- abnormal condition,
- consequence,
- priority,
- operator response,
- activation delay,
- clear condition,
- clear delay,
- rationale.
