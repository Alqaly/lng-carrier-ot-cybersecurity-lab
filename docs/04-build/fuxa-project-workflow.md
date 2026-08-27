# FUXA Project Workflow — Build Once, Export, Review and Reproduce

FUXA is the operator-facing HMI/SCADA layer. It is deliberately kept separate from the Learning Portal.

## Responsibilities

```text
FUXA
  Operator task displays
  Commands allowed to operators
  Process alarms / status

Learning Portal
  Explains the lab
  Shows provenance and architecture
  Does not control the plant

OpenPLC Editor
  Engineering configuration
  PLC program deployment
```

## Why a pre-bound project is not shipped

The OpenPLC OPC UA address spaces are created by the deployed Editor projects. Shipping guessed NodeIds would make the repository look more finished while making the first real commissioning step unreliable.

The correct order is:

```text
Deploy OpenPLC
→ browse OPC UA
→ verify NodeIds
→ bind FUXA tags
→ test operator screen
→ export exact FUXA project
→ commit/share sanitized project
```

## Start FUXA

```bash
docker compose up -d fuxa
```

Open:

```text
http://127.0.0.1:1881
```

## Optional visual bootstrap

The repository ships an **unbound** three-view FUXA project shell:

```text
fuxa/project-unbound.fuxap
```

It contains the Cargo, PMS and Propulsion task-display artwork but deliberately contains **no devices and no fake tag bindings**.

After configuring a FUXA API key/token, it can be loaded as a visual starting point:

```bash
export FUXA_API_KEY='...'
./labctl fuxa bootstrap
```

Then bind the views to the NodeIds proven by OPC UA discovery/binding-plan evidence.

## Build the three operator views

The repository includes task-display design assets for:

- Cargo,
- Power Management,
- Propulsion.

Use the designs under:

```text
fuxa/widgets/
```

and the display philosophy in:

```text
docs/04-build/task-based-hmi-design.md
```

## Export the commissioned project

Current FUXA exposes a full-project API. After configuring authentication, provide either an access token or API key to the helper.

Example:

```bash
export FUXA_TOKEN='...'
./labctl fuxa export
```

Default evidence file:

```text
evidence/fuxa/fuxa-project.json
```

This file is the exact project returned by the running HMI.

## Validate an exported project

```bash
./labctl fuxa validate /evidence/fuxa/fuxa-project.json
```

The helper checks the mandatory project-shell fields and reports the number of devices/views.

## Import a reviewed project

Import replaces the full live project, so the helper requires an explicit action:

```bash
./labctl fuxa import /evidence/fuxa/fuxa-project.json
```

Review the file and remove credentials or environment-specific secrets before committing it to GitHub.

## Security lesson

An HMI project is not just artwork. It can contain:

- device endpoints,
- tag mappings,
- commands,
- scripts,
- navigation/layout,
- alarm configuration.

Treat project backup/change control as part of OT configuration management.
