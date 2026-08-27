# FUXA HMI Assets

FUXA is pinned to a current release and used as the operator-facing HMI/SCADA layer.

The repository includes:

```text
widgets/cargo-operator-display.svg
widgets/pms-operator-display.svg
widgets/propulsion-operator-display.svg
project-skeleton.json
```

## Why the repository does not ship guessed live bindings

The final HMI must bind to the **actual OPC UA NodeIds** exposed by the OpenPLC projects after deployment.

Generating a visually complete FUXA project with invented NodeIds would make the first screenshot look better but would make the engineering workflow worse.

## Import / API path

Current FUXA exposes a full-project REST endpoint at:

```text
GET  /api/project
POST /api/project
```

The API requires the appropriate authenticated admin token or API key for project writes.

`project-skeleton.json` contains the mandatory top-level project structure and is intended as a clean starting point after OPC UA commissioning.

## Security

Do not permanently leave FUXA in an unauthenticated training configuration.

Use the operator network for HMI access and keep OpenPLC engineering-management endpoints separated from normal operator access.
