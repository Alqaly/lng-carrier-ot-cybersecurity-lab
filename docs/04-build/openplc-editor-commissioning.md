# OpenPLC Editor Commissioning

OpenPLC Runtime is headless and OpenPLC Editor is the engineering workstation used to create, map and deploy the controller projects.

The current dependency notes are kept in `DEPENDENCIES.md`.

## Source-of-truth mapping

Before creating I/O groups, keep these two files open:

```text
docs/08-reference/generated-io-map.md
openplc/mapping_contract.json
```

The generated map gives the process variable, Modbus object/address/scaling and corresponding PLC symbol. The mapping contract is machine-checked so a normal I/O point cannot silently exist in the process model without a documented PLC symbol.

## Cargo runtime

Start:

```bash
docker compose up -d openplc-cargo cargo-io cargo-plant
```

Editor target:

```text
https://127.0.0.1:8443
```

Remote I/O:

```text
Host: cargo-io
Port: 5020
Unit ID: 1
```

### Cargo I/O groups

| Area | Address | Raw representation | Meaning | Direction |
|---|---:|---|---|---|
| Coil | 0 | BOOL | cargo pump-bank command | PLC → I/O |
| Holding | 0 | 0–1000 | valve command permille | PLC → I/O |
| Discrete | 0 | BOOL | valve-open feedback | I/O → PLC |
| Discrete | 1 | BOOL | pump-run feedback | I/O → PLC |
| Discrete | 2 | BOOL | destination high-high | I/O → PLC |
| Discrete | 3 | BOOL | source low-low | I/O → PLC |
| Input Reg | 0 | mm | source level | I/O → PLC |
| Input Reg | 1 | mm | destination level | I/O → PLC |
| Input Reg | 2 | m³/h | measured cargo flow | I/O → PLC |
| Input Reg | 3 | kPa ×10 | source hydrostatic pressure | I/O → PLC |
| Input Reg | 4 | 0–1000 | actual valve position | I/O → PLC |
| Input Reg | 5 | 0–1000 | actual pump-bank speed | I/O → PLC |
| Input Reg | 6 | kW | calculated pump-bank electrical load | I/O → PLC |

Addresses 20+ are instructor-fault channels and should not be exposed as ordinary operator controls.

## Power Management runtime

Editor target:

```text
https://127.0.0.1:8444
```

Remote I/O:

```text
Host: pms-io
Port: 5021
Unit ID: 1
```

Core mapping:

- Coils 0–3: generator start/breaker commands
- Coils 4–5: load-shed commands
- Holding 0–2: standalone training load-demand flags
- Input 0: frequency ×100
- Input 1: voltage p.u. ×1000
- Input 2–5: generator power, load and reserve in kW
- Input 6–7: generator speed p.u. ×1000
- Input 8: coupled Cargo electrical load in kW
- Input 9: coupled propulsion auxiliary load in kW
- Discrete 0–8: readiness, breakers, under-frequency, blackout, sync permissives and bus state

The cross-system kW inputs are written into the PMS **process model** by the Vessel Coordinator. They are not instructor dashboard values.

## Propulsion runtime

Editor target:

```text
https://127.0.0.1:8445
```

Remote I/O:

```text
Host: propulsion-io
Port: 5022
Unit ID: 1
```

Core mapping:

- Coil 0: pre-lube command
- Coil 1: engine enable
- Holding 0: fuel command permille
- Holding 1: propeller-pitch command permille
- Input 0: RPM ×10
- Input 1: lube pressure bar ×100
- Input 2: coolant °C ×10
- Input 3: vessel speed kn ×100
- Input 4: engine load % ×10
- Input 5: propeller torque, 10 N·m per count
- Input 6: electrical auxiliary load kW
- Discrete 0–3: running / low lube / high coolant / overspeed

## OPC UA

For each PLC project:

1. add an OPC UA server in the Editor,
2. choose endpoint / namespace settings,
3. select the variables required by the HMI and historian,
4. choose and document the security policy/mode,
5. deploy,
6. browse the address space with an OPC UA client,
7. record exact NodeIds, data types, Quality and timestamp behavior,
8. only then configure FUXA and Telegraf.

Do not treat sample NodeIds in the repository as commissioned truth.

## Failure test

Stop one controller while the process model remains running.

Expected:

- controller-to-I/O polling stops,
- OPC UA freshness stops,
- underlying process-model state remains observable through the Learning Portal,
- alarm stale-data logic activates after its configured delay,
- the learner can distinguish **controller failure**, **process failure** and **visibility failure**.
