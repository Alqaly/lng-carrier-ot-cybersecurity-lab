# Alarm Source Boundary

The repository contains two alarm concepts with different purposes. They must not be confused.

## 1 — Teaching Alarm Chronicle

The `alarm-engine` observes software process/vessel state and applies the rationalization catalogue.

Its purpose is to teach:

- alarm activation delay,
- clear delay,
- priority,
- acknowledgement state,
- chronological sequence,
- alarm floods / consequential alarms,
- root-cause timeline reconstruction.

It is an **independent teaching/validation layer**. It is not the vessel operator alarm system and is not class-approved.

## 2 — Operator HMI alarms

After OpenPLC commissioning, the operator HMI should consume the actual controller variables exposed through the commissioned interface.

The preferred chain is:

```text
process model
→ I/O
→ OpenPLC control/alarm state
→ live OPC UA NodeId
→ FUXA operator display/alarm
```

This prevents the operator screen from bypassing the controller and reading a teaching-only shortcut.

## Why keep both?

The teaching chronicle gives us an independent reference timeline.

That is useful when asking:

> Did the operator alarm arrive at the correct time, or did the HMI/controller path lose/delay the state?

## Rule

Do not call the `alarm-engine` the vessel alarm system in screenshots, publication text or demos. Label it **Teaching Alarm Chronicle**.
