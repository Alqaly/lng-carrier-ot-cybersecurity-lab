# Task-Based Cargo HMI Design

SIGTTO's public Cargo Control Room HMI guidance recommends a human-centred design process and specifically discusses task-based displays for operations such as loading.

Official source:
https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/

The lab therefore designs screens around **operator tasks**, not around “show every tag on one dashboard.”

## Cargo loading task display

The operator needs to answer quickly:

```text
Are we permitted to transfer?
Is the valve actually open?
Is the pump actually running?
Is flow responding?
Where are both tank levels?
Are pressure and level trends moving in the expected direction?
Are there active alarms/trips?
```

The recommended screen contains:

- source/destination tank levels,
- transfer line,
- actual valve position + command state,
- pump command + running feedback,
- flow and short trend,
- pressure,
- transfer-permit state,
- safety/trip state,
- highest-priority active alarms.

It does **not** need raw MBAP fields or NodeIds. Those belong on diagnostic/engineering screens.

## Display hierarchy used by the project

### Level 1 — Vessel / system overview

Only the important state of Cargo, Power, Propulsion, Safety and Communications.

### Level 2 — Domain/task overview

Cargo loading, power-management overview or propulsion overview.

### Level 3 — Detailed control

Permissives, controller values, equipment detail and trends.

### Level 4 — Engineering diagnostics

I/O map, Modbus addresses, OPC UA metadata, packet capture and timing.

## Color philosophy

Normal state is visually quiet.

Color is reserved primarily for abnormal state / attention, supported by text and shape so color is not the only cue.

The project uses this high-performance-HMI principle as design guidance; it does not claim ISA-101 or SIGTTO compliance.

## FUXA implementation

Import/use the supplied SVG assets in `fuxa/widgets/` and bind them to the commissioned OpenPLC OPC UA nodes.

Use FUXA as the operator surface.

Use the Learning Portal for protocol/source explanations.

Do not merge those two roles.
