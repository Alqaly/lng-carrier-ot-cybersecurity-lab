# Reusable Method for Future OT Projects

The LNG carrier is one application of a reusable project method.

## Step 1 — choose the process

Examples:
- water treatment,
- substation,
- manufacturing cell,
- offshore process,
- district cooling,
- building automation.

## Step 2 — map real functions

Research:
- equipment,
- control architecture,
- instrumentation,
- protocols,
- safety functions.

## Step 3 — build a dynamic process model

Do not begin with fake dashboards.

Create explicit state equations or a recognized simulation model.

## Step 4 — add real controller runtime

Use IEC 61131-3 logic where appropriate.

## Step 5 — add protocol-accurate I/O

Examples:
- Modbus,
- OPC UA,
- DNP3,
- IEC 60870-5-104,
- IEC 61850,
- BACnet,
- Profinet,
- CAN/J1939.

Only use protocols that make sense for the target system.

## Step 6 — add historian and HMI

Every point must have data provenance.

## Step 7 — add network/security model

Zones, conduits, remote access, monitoring.

## Step 8 — create normal-operation walkthrough

The learner should be able to explain the process before any fault scenario.

## Step 9 — create failure/investigation scenarios

Correlate:
- command,
- protocol,
- feedback,
- process,
- timeline.

## Step 10 — recursive review

Check:
- theory ↔ code,
- code ↔ protocol,
- protocol ↔ process,
- process ↔ visuals,
- visuals ↔ sources,
- walkthrough ↔ actual output.
