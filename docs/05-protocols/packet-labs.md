# Packet Labs — From Protocol Message to Process Consequence

A packet capture is useful only when it can be connected to a controller tag and a process consequence.

## Why capture uses namespace sidecars

A container attached to the same Docker bridge is **not automatically a passive TAP** for unicast traffic between other containers.

The lab therefore uses capture sidecars that share the network namespace of the actual I/O or PLC service:

```text
capture-cargo-io  ↔ network namespace of cargo-io
capture-cargo-plc ↔ network namespace of openplc-cargo
```

That makes the packet evidence representative of the software conduit being studied.

## Wireshark display filters

Useful starting filters:

```text
modbus
```

```text
tcp.port == 5020
```

```text
opcua
```

Do not stop at the filter. Decode the operation and map it to the I/O contract.

## Lab 1 — Cargo Modbus commissioning

Terminal A:

```bash
./labctl build
./labctl capture cargo modbus
```

Terminal B:

```bash
./labctl demo cargo
```

Open:

```text
evidence/live/cargo/modbus.pcap
```

Build a packet worksheet:

```text
packet timestamp
→ source/destination
→ Modbus function
→ object/address
→ raw value
→ generated I/O map
→ plant variable
→ process response
```

The generated contract is:

```text
docs/08-reference/generated-io-map.md
```

## Lab 2 — Measurement fault versus equipment fault

Capture Cargo Modbus, then run:

```bash
./labctl demo cargo-fault
```

The scenario performs two deliberately different abnormalities:

### Flow-transmitter bias

```text
true modeled flow remains physically consistent
but
reported measured flow is biased
```

Use tank-level rate-of-change and process API state to distinguish measurement integrity from pump performance.

### Pump-bank failure

```text
pump target → zero
pump speed decays
actual flow decays
measured flow follows
```

Compare the network command with the physical-model response.

## Lab 3 — Final PLC Cargo control path

After OpenPLC is commissioned, repeat the capture while the **PLC** starts transfer.

Now annotate:

```text
PLC control decision
→ Modbus request
→ I/O state
→ process response
→ feedback read
→ next PLC scan/state
```

Compare this with pre-PLC commissioning. The client/source and command sequence should change because the PLC now owns the control path.

## Lab 4 — OPC UA

Start:

```bash
./labctl capture cargo opcua
```

Connect FUXA, Telegraf or an OPC UA browser to the Cargo PLC.

Study:

- TCP session,
- SecureChannel/session establishment,
- security policy/mode,
- certificate/authentication behavior,
- publish/read timing,
- the difference between protocol metadata and encrypted payload visibility.

If OPC UA encryption is enabled, you should **not** expect Wireshark to reveal every process value. The lesson becomes trust policy, certificates, endpoint metadata and server/client logs.

## Lab 5 — PMS generator trip

Capture:

```bash
./labctl capture pms modbus
```

Pre-PLC process/I/O fault:

```bash
./labctl demo pms-trip
```

Then repeat after PMS PLC commissioning so the controller can perform generator-start and load-shed logic.

Correlate:

```text
generator trip
→ breaker/ready state
→ frequency response
→ PLC under-frequency logic
→ load-shed write
→ process recovery
```

## Lab 6 — Propulsion lube-oil event

```bash
./labctl capture propulsion modbus
./labctl demo propulsion-lube
```

Pre-PLC commissioning proves the plant state transition. After OpenPLC commissioning, repeat through the PLC and identify the protective output transition.

## Lab 7 — Propulsion cooling impairment

Terminal A:

```bash
./labctl capture propulsion modbus
```

Terminal B:

```bash
./labctl demo propulsion-cooling
```

The deterministic pre-PLC scenario establishes sustained load, asserts
instructor-only coil 21 and fails unless discrete input 2 (`highCoolantTemp`)
becomes true. Correlate the coil write, register trend and threshold transition
with `evidence/live/propulsion/pre-plc-cooling-timeline.jsonl`.

This direct-I/O demonstration does not prove protective shutdown. After OpenPLC
commissioning, repeat the registered `EXP-PROP-COOLING-FAULT` intervention while
the PLC owns `engineEnable`; the accepted causal chain ends only when the later
PLC-visible enable state becomes false.

## Zeek offline analysis

After a Modbus PCAP exists:

```bash
./labctl zeek cargo
```

The project loads Zeek's Modbus analyzer plus:

```text
known-masters-slaves
track-memmap
```

Useful outputs can include:

```text
conn.log
modbus.log
known_modbus.log
modbus_register_change.log
```

`modbus.log` includes request time, connection identifier, transaction ID, unit, function name, request/response direction and exception status. `modbus_register_change.log` helps examine holding-register changes when the policy script can track them.

Official Zeek references:
- https://docs.zeek.org/en/current/scripts/base/protocols/modbus/main.zeek.html
- https://docs.zeek.org/en/lts/scripts/policy/protocols/modbus/known-masters-slaves.zeek.html

Zeek is an **analysis layer**, not the source of process truth.

## Packet worksheet

| Field | Value |
|---|---|
| Timestamp | |
| Source / destination | |
| TCP ports | |
| Transaction ID | |
| Unit ID | |
| Function | |
| Request / response | |
| Address/object | |
| Raw value | |
| Engineering value | |
| PLC tag | |
| Operational meaning | |
| Expected process response | |
| Observed process response | |

A packet lab is complete when the learner can explain why the message matters without saying only “it is a Modbus write.”
