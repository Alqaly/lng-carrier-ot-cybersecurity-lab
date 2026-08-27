# OPC UA Commissioning — Discover, Verify, Then Bind

## Visual rule

The canonical figure for this chapter is a screenshot from the live OPC UA browser showing the resolved NodeId/namespace/Quality, followed by the matching historian sample. Use the OPC Foundation architecture page only as the real-system reference: https://opcfoundation.org/about/opc-technologies/opc-ua/

The project deliberately does **not** treat example NodeIds as commissioned tags.

OpenPLC Runtime exposes the server; the engineering workflow must discover the deployed address space and prove the mapping before FUXA or Telegraf is trusted.

## Why this step exists

A value such as:

```text
Cargo.Flow
```

has two separate questions:

1. Is the controller calculating the correct value?
2. Is the OPC UA node you selected actually that controller value?

A dashboard can be wrong even when the PLC is correct if the binding points at the wrong node.

## 1 — Deploy the PLC project

Complete the OpenPLC Editor commissioning for the selected domain.

Runtime endpoints on the host:

| Domain | Runtime management | OPC UA host port |
|---|---:|---:|
| Cargo | `https://127.0.0.1:8443` | `4840` |
| PMS | `https://127.0.0.1:8444` | `4841` |
| Propulsion | `https://127.0.0.1:8445` | `4842` |

Inside the Compose operations network, all runtimes expose OPC UA on their container port `4840`.

## 2 — Browse the live address space

Cargo:

```bash
./labctl opcua cargo
```

PMS:

```bash
./labctl opcua pms
```

Propulsion:

```bash
./labctl opcua propulsion
```

The tool uses `asyncua` to browse the **live server** and stores:

```text
evidence/opcua/
├── cargo-opcua-discovery.json
├── cargo-opcua-discovery.md
├── pms-opcua-discovery.json
└── ...
```

For variables it records, where available:

- NodeId,
- BrowseName,
- node class,
- data type,
- current value,
- status code / Quality,
- source timestamp,
- server timestamp.

## 3 — Compare with PLC online values

Pick one value, for example Cargo measured flow.

Verify the chain:

```text
PLC online variable
      ↓
OPC UA BrowseName / NodeId
      ↓
OPC UA current value
```

Do not continue if the meanings disagree.

## 4 — Record the namespace

The discovery output includes the namespace array.

This matters because a numeric namespace index may change when server configuration changes. Preserve the namespace identity as commissioning evidence.

## 5 — Configure historian and HMI

Only after discovery should you update:

```text
historian/telegraf.conf
```

and the FUXA OPC UA device/tag bindings.

## 6 — Failure test

Stop the selected runtime:

```bash
docker compose stop openplc-cargo
```

Expected:

- OPC UA browse/read fails,
- Telegraf cannot obtain fresh samples,
- operator/historian visibility becomes stale or disconnected,
- **no new fabricated process value appears to hide the outage**.

Restart and prove recovery.

## What you learned

OPC UA commissioning is not “port 4840 is open.” It is proving:

```text
controller variable
↔ information-model node
↔ status / timestamp
↔ consumer binding
```

That distinction becomes important during both troubleshooting and incident response.

## 7 — Generate a binding plan from discovery evidence

After discovery succeeds:

```bash
./labctl bind-plan cargo
```

The resolver compares the **live discovered BrowseNames/NodeIds** with the documented PLC symbol intent and refuses to silently choose when a tag is missing or ambiguous.

Outputs:

```text
evidence/opcua/cargo-binding-plan.json
evidence/opcua/cargo-binding-plan.md
evidence/opcua/cargo-telegraf-fragment.conf
```

A plan is considered clean only when:

```text
missing = 0
ambiguous = 0
```

This creates an explicit commissioning gate between PLC deployment and historian/HMI binding.
