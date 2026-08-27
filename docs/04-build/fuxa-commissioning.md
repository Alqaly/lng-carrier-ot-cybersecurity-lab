# FUXA Operator HMI Commissioning

FUXA is the operator HMI/SCADA surface in this project.

Official project:
https://github.com/frangoteam/FUXA

## Why FUXA

Its current open-source project supports industrial connectivity including OPC UA and Modbus, an SVG-based visual editor, alarms and alarm history.

The repository pins FUXA `1.3.4`. FUXA's 2026 security history is part of the lesson: an HMI is itself software that must be patched, authenticated and placed in the correct network zone.

## 1 — Start the HMI

```bash
docker compose up -d fuxa
```

Open:

```text
http://127.0.0.1:1881
```

## 2 — Commission OpenPLC OPC UA first

Do not build the screen against guessed tags.

For each domain:

1. deploy the PLC project,
2. enable OPC UA,
3. browse the server,
4. verify the exact NodeIds,
5. record security policy/mode and authentication,
6. only then create the FUXA device connection.

## 3 — Create Cargo device

Target the Cargo OpenPLC endpoint reachable from the FUXA container.

Use the security profile you commissioned in OpenPLC rather than leaving anonymous/no-security as the final exercise.

## 4 — Build the task display

Use/import:

```text
fuxa/widgets/cargo-operator-display.svg
```

Bind:

```text
Source level
Destination level
Flow
Pressure
Valve command/position/feedback
Pump command/feedback
Transfer permit
Safety trip
```

## 5 — Alarms

Create alarms from the PLC's operator-relevant tags.

Use `alarms/catalog.json` as the rationalization source, not as the final FUXA database itself.

For each alarm record:

- priority,
- trigger,
- consequence,
- operator response,
- expected delay.

FUXA's alarm engine manages active state, acknowledgement and history for project-defined alarms.

## 6 — Repeat for Power and Propulsion

Import/reference:

```text
fuxa/widgets/pms-operator-display.svg
fuxa/widgets/propulsion-operator-display.svg
```

The first screen should answer an operational question. Raw protocol details belong on engineering/diagnostic pages.

## 7 — Security exercise

After normal operation works:

- enable FUXA authentication,
- restrict the HMI to the operator network,
- keep OpenPLC management ports on the engineering path,
- compare the privileges of HMI writes and Editor deployment,
- capture the OPC UA session establishment and application traffic.

The lesson is **role separation**: operator control is not engineering/program deployment.


## Project bootstrap

The repository includes:

```text
fuxa/project-skeleton.json
```

FUXA's current API documents:

```text
GET  /api/project
POST /api/project
```

for full-project retrieval/replacement.

Do not use the API to inject guessed OPC UA NodeIds. First commission the OpenPLC nodes, then create/import the operator project and save/export it into version control.
