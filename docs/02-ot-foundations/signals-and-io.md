# Signals and I/O: follow one value all the way through

A **command** is what the controller requests. **Feedback** describes equipment
state. A **measurement** describes a process quantity. Confusing those three
makes both commissioning and incident investigation harder.

## Start with the Cargo valve

| Quantity | Lab object | Meaning |
|---|---|---|
| Requested opening | Holding register 0 → `valveCommand` | Raw 1000 requests a normalized opening of 1.0 |
| Actual opening | Input register 4 ← `valvePosition` | Physical teaching-model response; it takes time to move |
| Fully-open indication | Discrete input 0 ← `valveFeedback` | A Boolean feedback condition |
| Pump run request | Coil 0 → `pumpCmd` | A command, not proof of rotation or liquid movement |
| Pump running indication | Discrete input 1 ← `pumpFeedback` | Equipment feedback, not an independent flow measurement |

Input and output are named relative to the controller: it reads measurements and
feedback, and writes commands. The software I/O service exposes those objects to
the Modbus client. Its HTTP connection exchanges commands/state with the FMU runtime.

In the commissioned Cargo program, `DO_Pump` requires `Permit_Transfer` and
`DI_ValveOpenFB`. The direct commissioning demo uses timed actions and bypasses
that logic. A successful demo therefore does not establish that the PLC permissive works.

## Worked signal: 0.5 m³/s becomes register value 1800

![Cargo flow unit conversion through software I/O, PLC and supervision](../assets/visuals/flow-signal.svg)

This is a worked numeric example, not a runtime sample.

1. The Cargo FMU exposes `flowMeasured` in **m³/s**.
2. The I/O configuration maps it to **input register 2**, with scale **1/3600**.
3. The emulator encodes `raw = round(model_value / scale)`: 0.5 × 3600 = **1800**.
4. The PLC reads `AI_Flow_m3h = 1800` and applies `INT_TO_REAL`.
5. `Flow_m3h = 1800.0` is published through the commissioned OPC UA identity.

The PLC does **not** multiply by 3600 again. Its input is already in whole m³/h.
The model-to-register conversion rounds to an integer, so small differences below
one register step can be quantization rather than a faulty sensor.
Do not expect samples obtained at different times to agree during a transient.

**Source check:** the implementation is in
[Cargo I/O configuration](https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab/blob/main/io_emulator/configs/cargo.json),
the [I/O encoder](https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab/blob/main/io_emulator/server.py)
and [CargoControl.st](https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab/blob/main/openplc/cargo/CargoControl.st).
Use the [generated map](../08-reference/generated-io-map.md) when configuring addresses.

## Do not confuse the four Modbus object spaces

| Object | This lab's use | Example function |
|---|---|---|
| Coil | Boolean command/fault input | FC05 writes one coil |
| Discrete input | Boolean feedback/condition | FC02 reads discrete inputs |
| Holding register | Numeric command/fault input | FC06 writes one register |
| Input register | Numeric measurement | FC04 reads input registers |

Address zero can exist in all four spaces with different meanings. This repository
uses **zero-based protocol addresses**. Some engineering tools display one-based
references such as 30001/40001; confirm the tool's convention before entering a map.
Do not put a display reference into a field expecting the raw protocol offset.

![Constructed Modbus FC04 read of input register 2](../assets/visuals/modbus-flow-read.svg)

The Modbus response contains a numeric value, not its engineering units.
`07 08` is hexadecimal 0x0708 = 1800. In this Cargo mapping it represents m³/h.
In another installation that same raw integer might mean something completely different.

## Where does 4–20 mA fit?

A physical analog transmitter can convert a measured quantity into current.
An analog input module converts that current into a digital value. This software
lab does not generate an electrical current loop; it models the process value
and its digital encoding.

For a hypothetical linear 0–2000 m³/h transmitter:

```text
flow = (current_mA - 4) / 16 × 2000 m³/h
```

| Current | Fraction of span | Flow |
|---|---:|---:|
| 4 mA | 0% | 0 m³/h |
| 8 mA | 25% | 500 m³/h |
| 12 mA | 50% | 1000 m³/h |
| 16 mA | 75% | 1500 m³/h |
| 20 mA | 100% | 2000 m³/h |

That illustrative transmitter span is **not** the Cargo register's configured
full-scale range. The two examples teach different conversions: physical current
scaling versus this project's digital unit mapping.

## Diagnose a disagreement

Suppose the process API shows `flowMeasured=0.5`, the PLC shows
`Flow_m3h=1800`, and the HMI shows zero.

The first two agree after conversion. Next inspect the HMI's live-discovered OPC UA
NodeId, Quality, timestamp and displayed units. Do not change the process equation
to make an incorrectly bound display look right.

If the model's `flow` and `flowMeasured` disagree, inspect measurement lag and
sensor bias. The former is the teaching model's actual-flow reference; the latter
is the measured channel passed to the register. In a real plant, independent flow
truth is not automatically available.

## Practise before proceeding

- A Cargo flow register reads 900. What should you compare with the model API?
- Valve command is 1000 but position is 300. What is requested and what is observed?
- Why can pump feedback be true while flow remains low?

**Answers:** 900 m³/h = 0.25 m³/s. The valve is requested fully open but is currently
at 0.3 normalized opening; travel, a fault or stale data needs investigation.
Pump feedback alone does not establish an open hydraulic path or a truthful flow
measurement. Compare independent process evidence.

Next, collect those observations in the
[first Cargo investigation](../06-scenarios/first-cargo-investigation.md).
