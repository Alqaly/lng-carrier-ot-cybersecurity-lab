# Historian — Commission Live OPC UA Data

## Visual rule

Use a live OPC UA browser screenshot and a matching Grafana/Influx sample captured during commissioning. The project refuses to ship a fabricated “healthy historian” screenshot.

The historian is deliberately **empty of OPC UA inputs at repository checkout**.

That is a design decision. A NodeId belongs to the deployed PLC address space, so the lab refuses to pretend an example NodeId is a commissioned tag.

## Architecture

```text
OpenPLC project deployed
        ↓
live OPC UA address space
        ↓
asyncua discovery
        ↓
verified binding plan
        ↓
Telegraf input fragment
        ↓
InfluxDB
        ↓
Grafana
```

## Step 1 — discover Cargo OPC UA

```bash
./labctl opcua cargo
```

This browses the **running** OpenPLC server and records:

- NodeId,
- BrowseName / DisplayName,
- data type,
- StatusCode / Quality,
- source timestamp,
- server timestamp.

Evidence is written to:

```text
evidence/opcua/cargo-opcua-discovery.json
evidence/opcua/cargo-opcua-discovery.md
```

Repeat with `pms` and `propulsion`.

## Step 2 — resolve the teaching tags

```bash
./labctl bind-plan cargo
```

The resolver compares the **documented PLC symbol intent** against discovered live variables.

It passes only when each required teaching tag resolves to exactly one node.

It fails if a tag is:

- missing,
- ambiguous,
- or the discovery contains no matching live variable.

Outputs:

```text
evidence/opcua/cargo-binding-plan.json
evidence/opcua/cargo-binding-plan.md
evidence/opcua/cargo-telegraf-fragment.conf
```

## Step 3 — install the verified fragment

```bash
./labctl hist-install cargo
```

The command refuses to install an incomplete binding plan.

On success it copies the generated fragment to:

```text
historian/generated/cargo.conf
```

and restarts the historian services when Docker is available.

The generated file is ignored by Git because it belongs to **your deployed PLC namespace**, not to the generic repository.

Repeat:

```bash
./labctl opcua pms
./labctl bind-plan pms
./labctl hist-install pms

./labctl opcua propulsion
./labctl bind-plan propulsion
./labctl hist-install propulsion
```

## Step 4 — verify one value end-to-end

Pick one tag, for example Cargo measured flow.

Compare it at the same operating moment in:

```text
OpenPLC online variable
      ↓
OPC UA client / discovery evidence
      ↓
Telegraf input
      ↓
InfluxDB sample
      ↓
Grafana trend
```

Record the NodeId and timestamps in your evidence notes.

## Step 5 — supervisory-path failure test

Do **not** stop the Cargo PLC. That would mix controller/control loss with the supervisory failure we are trying to measure. First prove the historian is fresh, then isolate only the PLC operations-network attachment:

```bash
./labctl hist-fresh cargo --threshold 5 --out evidence/runtime/freshness-before.json
./labctl opcua-outage cargo start
# wait longer than the declared freshness threshold
./labctl hist-fresh cargo --threshold 5 --out evidence/runtime/freshness-after.json || true
./labctl opcua-outage cargo restore
```

Expected:

- the Cargo PLC remains attached to the fixed `cargo_control` Modbus conduit,
- the operations-side OPC UA path becomes unreachable,
- Telegraf cannot obtain new Cargo samples and the historian becomes stale,
- no service manufactures replacement fresh values,
- restore reconnects the recorded operations network with the same fixed IP.

The outage helper refuses to proceed if the control path is already absent, because that would invalidate the experiment.

## Why this matters

`LevelSource_m` is a human concept.

`ns=...;s=...` is the concrete identity exposed by a particular running server.

Commissioning is the engineering act that proves those two refer to the same thing.
