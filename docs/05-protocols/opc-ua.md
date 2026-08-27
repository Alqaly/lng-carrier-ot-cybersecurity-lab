# OPC UA

## Visual tour

Use the OPC Foundation's OPC UA architecture overview: https://opcfoundation.org/about/opc-technologies/opc-ua/

Then browse the running OpenPLC server. The teaching visual is the live address space: NodeId, namespace, DataType, value, status/Quality and timestamp — not a decorative pipeline.

OpenPLC Runtime includes an OPC UA plugin and current public documentation describes support for server-side variables, authentication, security profiles and PLC value synchronization.

## Key concepts

### Address space
The hierarchical information model exposed by the server.

### Node
An object or variable in the address space.

### NodeId
The identifier for a node.

### Namespace
A mechanism for avoiding naming collisions.

### Data type
Examples:
- Boolean
- Int16
- Float
- String

### Quality / status
An OPC UA value is more than a number. Status can tell the consumer whether the data is trustworthy.

### Timestamp
A value can include source/server timing information.

## Security

OPC UA can use:
- certificates,
- username/password,
- security policies,
- signing,
- encryption.

The teaching lab should progress from simple connectivity to certificate-based trust rather than permanently leaving the server in the least-secure mode.


## Practical observation workflow

### 1 — Browse the server

After deploying the OpenPLC project, use an OPC UA browser/client to inspect the actual server.

Record:

```text
Endpoint
Security policy
Security mode
Namespace
NodeId
DataType
Current Value
Status / Quality
Timestamp
```

Do not treat the sample names in `historian/telegraf.conf` as commissioned until they match the deployed server.

### 2 — Compare controller and OPC UA state

Select one point such as flow.

Verify:

```text
PLC online value
=
OPC UA value
```

If they disagree, stop and identify which mapping is wrong before starting the historian.

### 3 — Observe the network session

Capture the PLC/historian conduit:

```bash
./labctl capture cargo opcua
```

This starts a packet-capture sidecar that **shares the Cargo PLC network namespace**. That detail matters: a normal container attached to the same Docker bridge would not be a reliable passive tap for unicast traffic between other containers.

Open the capture in Wireshark and identify the OPC UA TCP conversation.

### 4 — Historian test

Start Telegraf only after the NodeIds have been verified.

Then stop OpenPLC temporarily.

Expected:

```text
no fresh OPC UA samples
→ historian gap / stale trend
→ no substitute process values
```

The failure behavior is part of the lesson.

## Worked example — discover, do not guess

1. Deploy the Cargo PLC project.
2. Browse its live OPC UA server.
3. Find the `Flow_m3h` node by BrowseName.
4. Record NodeId, namespace, DataType, Status/Quality and timestamps.
5. Generate the verified historian binding plan.
6. Stop the operations-side OPC UA path and prove fresh historian samples stop while the Cargo Modbus control conduit remains available.

The important lesson is that a number without provenance, quality and freshness is not sufficient supervisory evidence.

## 60-second explain-back

Explain why OPC UA is more than “Modbus with security”: it provides discovery, an address space/information model, typed nodes, services, subscriptions/events and security mechanisms.

## Remember it

**OPC UA publishes an information model, not just register numbers.** Keep NodeId, type, status/Quality and time together.

## Explain it in 60 seconds

Explain why live discovery must happen before configuring the historian.
