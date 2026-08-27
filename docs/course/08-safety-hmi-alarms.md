# 08 — Safety, HMI and Alarm Engineering

## Why this matters

A beautiful dashboard can be a bad operator interface. An alarm can be technically correct and still be operationally useless if it chatters or floods the operator.

## Visual tour

Study:

- SIGTTO ESD Systems: https://www.sigtto.org/publications/esd-systems/
- SIGTTO Cargo Control Room HMI guidance: https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/
- Kongsberg K-Chief operator panel: https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/343101_tcp_datasheet_kchief600.pdf

## Memory hook

```text
CONTROL asks “how do we operate?”
SAFETY asks “how do we stop/protect?”
HMI asks “what must the human understand now?”
ALARM asks “what requires attention/action?”
```

## Operator vs engineering view

The operator should primarily see process meaning:

- permit,
- command,
- feedback,
- flow/level/frequency/RPM,
- active abnormal condition,
- required action.

The engineer can additionally see:

- NodeId,
- register,
- raw scaling,
- protocol status,
- diagnostic details.

## Alarm rationalization

Each important alarm has:

- trigger,
- activation delay,
- priority,
- consequence,
- operator response,
- clear behavior.

The **Teaching Alarm Chronicle** is an independent evidence/timeline service. It must not be confused with a certified vessel alarm system.

## Worked example — no flow

A delay prevents transient run-up from creating an immediate false alarm. Only persistent disagreement between running/valve feedback and flow should activate the teaching alarm.

## Lab action

During a Cargo fault run, capture:

1. FUXA operator screen,
2. alarm chronology,
3. Modbus packet evidence,
4. process state timeline.

Check that the visual story and evidence story agree.

## Explain it in 60 seconds

Why should a security analyst not design the operator HMI around IP addresses and register numbers?

## Go deeper

- [HMI & alarm system](../04-build/hmi-and-alarm-system.md)
- [Alarm rationalization](../04-build/alarm-rationalization.md)
- [Safety vs control](../02-ot-foundations/safety-vs-control.md)
