# Historian Commissioning

The repository ships **no guessed OPC UA input NodeIds** in the active Telegraf configuration.

The correct workflow is:

```text
OpenPLC deployment
→ live OPC UA discovery
→ binding-plan resolution
→ install verified Telegraf fragment
→ restart Telegraf
→ verify InfluxDB
```

## 1 — Discover the live server

```bash
./labctl opcua cargo
```

## 2 — Resolve teaching tags

```bash
./labctl bind-plan cargo
```

The binding plan fails closed if required tags are missing or ambiguous.

## 3 — Install the verified input fragment

```bash
./labctl hist-install cargo
```

The command copies:

```text
evidence/opcua/cargo-telegraf-fragment.conf
```

to:

```text
historian/generated/cargo.conf
```

and restarts Telegraf.

Repeat for `pms` and `propulsion`.

## 4 — Verify the sample

Compare the same value in:

```text
OpenPLC online state
OPC UA discovery/client
InfluxDB
Grafana
```

## Failure behavior

If an OPC UA endpoint is unavailable, the historian receives no new samples from that input. The stack must not manufacture substitute process values.

## Domain endpoints inside the operations network

```text
Cargo      opc.tcp://openplc-cargo:4840/openplc/opcua
PMS        opc.tcp://openplc-pms:4840/openplc/opcua
Propulsion opc.tcp://openplc-propulsion:4840/openplc/opcua
```
