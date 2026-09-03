# Full Software Lab Walkthrough

## Visual rule for this walkthrough

At each stage, capture the **actual running evidence**: process state → Modbus packet → PLC online tag → OPC UA browser → FUXA → Grafana/Influx → Zeek. Those screenshots become the course visuals for this chapter.

This is the main practical build path.

Do not jump from `docker compose up` directly to cybersecurity scenarios. Commission one layer at a time.

## 0 — Prerequisites

Install:

- Docker Engine / Docker Desktop
- Docker Compose v2
- OpenPLC Editor
- Wireshark
- Python 3.10+

Check the local requirements:

```bash
./labctl doctor
```

## 1 — Compile the dynamic models

```bash
docker compose run --rm modelica-builder
```

The shared FMU volume receives:

```text
cargo_plant.fmu
pms_plant.fmu
propulsion_plant.fmu
```

OpenModelica exports FMI Co-Simulation models. The model equations remain visible under `plant/modelica/`.

## 2 — Start process models, I/O and cross-system coupling

```bash
./labctl build
```

Open:

```text
http://127.0.0.1:8500
```

Check:

```bash
curl http://127.0.0.1:8100/state
curl http://127.0.0.1:8200/state
curl http://127.0.0.1:8300/state
curl http://127.0.0.1:8600/state
```

At this point the environment is:

```text
physics models
+ Modbus software I/O
+ explicit cross-system coupling
+ alarm chronology
```

The PLC loop is not yet commissioned.

## 3 — Prove the process/I/O layer first

Run each direct commissioning exercise:

```bash
./labctl demo cargo
./labctl demo pms
./labctl demo propulsion
```

These exercises intentionally bypass OpenPLC.

Then run the cross-system exercise:

```bash
./labctl demo vessel
```

The integrated exercise should prove:

```text
Cargo pump kW
→ PMS load
→ electrical bus state
→ Cargo power availability
→ Cargo flow
```

See `docs/06-scenarios/integrated-power-cargo-event.md`.

## 4 — Capture the protocol

In one terminal:

```bash
./labctl capture cargo modbus
```

In another:

```bash
./labctl demo cargo
```

Open the PCAP and trace:

```text
Modbus function
→ address
→ I/O contract
→ model variable
→ process result
```

Repeat for PMS and propulsion.

## 5 — Commission Cargo OpenPLC

Start:

```bash
docker compose up -d openplc-cargo
```

Connect OpenPLC Editor to:

```text
https://127.0.0.1:8443
```

Import/create the program from:

```text
openplc/cargo/CargoControl.st
```

Configure the Remote I/O:

```text
Host: cargo-io
Port: 5020
Unit ID: 1
```

Use `docs/08-reference/tag-registers.md` as the mapping source.

## 6 — Verify the Cargo control sequence

Expected:

```text
Transfer_Enable
→ valve command
→ dynamic valve travel
→ valve-open feedback
→ pump command
→ dynamic pump run-up
→ pump feedback
→ measured flow
→ pumpPowerKW
→ source/destination level response
```

Command and feedback must not change at the same instant.

## 7 — Commission PMS OpenPLC

Runtime:

```text
https://127.0.0.1:8444
```

Remote I/O:

```text
pms-io:5021
```

Verify:

```text
Plant_Enable
→ Gen 1 start
→ Gen 1 ready
→ sync permissive
→ breaker close
→ bus energized
→ load applied
→ reserve evaluated
→ Gen 2 start when required
```

Do not close the second generator merely because it is running; check the sync permissive exposed by the process model.

## 8 — Commission propulsion OpenPLC

Runtime:

```text
https://127.0.0.1:8445
```

Remote I/O:

```text
propulsion-io:5022
```

Verify:

```text
Propulsion_Enable
→ pre-lube
→ lube pressure permissive
→ engine enable
→ fuel / pitch command
→ RPM / propeller torque / vessel response
```

The default vessel profile does not put mechanical shaft power on the PMS bus. It does place machinery auxiliary electrical demand on the bus.

## 9 — OPC UA

For each OpenPLC project:

1. add/enable the OPC UA server,
2. expose the required controller variables,
3. browse the **live** server,
4. record exact NodeIds / namespace / data types,
5. record Quality and timestamp behavior,
6. apply the selected security mode,
7. only then configure HMI/historian clients.

Use the built-in commissioning helper:

```bash
./labctl opcua cargo
./labctl opcua pms
./labctl opcua propulsion
```

The evidence is saved under `evidence/opcua/`.

See `docs/04-build/opcua-commissioning.md`.

## 10 — Operator HMI

Start FUXA:

```bash
docker compose up -d fuxa
```

Open:

```text
http://127.0.0.1:1881
```

Use the task-based SVGs and design method documented in:

```text
docs/04-build/task-based-hmi-design.md
docs/04-build/fuxa-commissioning.md
docs/04-build/fuxa-project-workflow.md
```

The primary operator display answers operational questions. Protocol addresses belong on engineering diagnostics, not the top-level operator screen.

After the live OPC UA bindings are commissioned, export the exact HMI project as engineering evidence:

```bash
export FUXA_TOKEN='...'
./labctl fuxa export
```

## 11 — Alarm engineering

Open:

```text
http://127.0.0.1:8400/catalog
http://127.0.0.1:8400/alarms
http://127.0.0.1:8400/history
http://127.0.0.1:8400/metrics
```

Verify:

- activation delay,
- clear delay,
- hysteresis / return threshold where configured,
- acknowledgement state,
- stale-data alarms,
- chronology.

## 12 — Commission historian bindings from the live PLCs

Do **not** edit guessed NodeIds into the base Telegraf config.

For each domain:

```bash
./labctl opcua cargo
./labctl bind-plan cargo
./labctl hist-install cargo

./labctl opcua pms
./labctl bind-plan pms
./labctl hist-install pms

./labctl opcua propulsion
./labctl bind-plan propulsion
./labctl hist-install propulsion
```

Then compare one live OpenPLC value with the exact OPC UA NodeId, its InfluxDB sample and its Grafana trend.

Failure test:

1. stop one PLC runtime,
2. confirm its samples stop,
3. confirm the other domains remain available,
4. restart it and document the recovery interval.

## 13 — Zeek / packet evidence

After collecting a Modbus capture:

```bash
./labctl zeek cargo
```

Use Zeek logs for connection/protocol chronology and Wireshark for packet-level inspection.

## 14 — Repeat the integrated event through the PLCs

After Cargo, PMS and Propulsion PLC commissioning, repeat the generator-loss/cross-domain story through normal operator/controller paths.

Collect:

```text
Cargo Modbus PCAP
PMS Modbus PCAP
PLC online state
alarm chronicle
Vessel Coordinator state
historian trends
operator screenshots
written timeline
```

## 15 — Explain one value and one event

A build is not complete until you can explain a value:

```text
model equation
→ FMU output
→ I/O register
→ Modbus message
→ PLC symbol
→ OPC UA node
→ HMI / historian
```

and explain an event:

```text
root cause
→ controller / process transition
→ cross-system consequence
→ alarm transition
→ packet evidence
→ recovery
```

If any arrow is hand-waved, the walkthrough is not finished.

## Remember it

**Equation → I/O → PLC → protocol → operator/history → evidence.** If you cannot trace a point both directions, commissioning is incomplete.

## Explain it in 60 seconds

Trace one Cargo flow sample from its process equation to its packet and historian point.
