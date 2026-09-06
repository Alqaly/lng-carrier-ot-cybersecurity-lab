# 01 — What Are We Building?

## Why this matters

A cyber range can be impressive while teaching very little. This project has a stricter goal: build a reproducible LNG-carrier-oriented **software-defined cyber-physical OT testbed** where an engineer can trace an event from process dynamics to controller state, protocol traffic, operator visibility and investigation evidence.

## Visual tour — start from a real test-bed concept

![The lab's Cargo process, electrical supply and independent control signals](../assets/visuals/cargo-system.svg)

This original schematic shows the model you will operate: ship inventory, pump,
valve and shore receiving boundary. Follow the liquid path, then ask what changes
if PMS stops supplying pump power. Read the [visual guide](../00-learning/visual-guide.md)
to trace the same process into a signal and packet before installing anything.

Open Lee (2024), *Development of Hardware-in-the-Loop Simulation Test Bed to Verify and Validate Power Management System for LNG Carriers*: https://www.mdpi.com/2077-1312/12/7/1236

Study **Figure 3** and **Figure 10**.

**What to notice**

- the system under test is separated from the simulator,
- power suppliers/consumers are modeled as interacting components,
- communications connect the test object and simulation environment,
- validation happens through scenarios, not “the UI loaded”.

**How it maps to this lab**

- Modelica/FMUs = dynamic process side,
- OpenPLC = controller under test,
- Modbus TCP = controller/I/O path,
- OPC UA = supervisory information path,
- FUXA = operator view,
- InfluxDB/Grafana = history,
- PCAP/Zeek = network evidence.

**Limitation:** the reference build is SIL/emulation, not the physical HIL shown in the paper.

## Memory hook

```text
MODEL → CONTROL → COMMUNICATE → OBSERVE → INVESTIGATE
```

If one of those five layers is missing, the lab is incomplete.

## Worked example

Suppose the model API shows `flowMeasured = 0.5 m³/s`, while the PLC shows
`Flow_m3h = 1800`. These agree: 0.5 × 3600 = 1800. Input register 2 stores whole
m³/h, so the PLC must not apply that conversion again.

The [signals lesson](../02-ot-foundations/signals-and-io.md) works through the
encoding and the [first Cargo investigation](../06-scenarios/first-cargo-investigation.md)
shows where to find the register in a real capture.

This project asks:

1. Which process equation produced the physical state?
2. Which virtual I/O register represents the measurement?
3. Which Modbus response carried the value?
4. Which PLC symbol consumed it?
5. Which OPC UA node published it?
6. Which historian sample stored it?
7. What independent evidence supports or contradicts it?

That chain is the research artifact.

## Lab action

Before starting containers:

```bash
./labctl preflight
./labctl test
./labctl config-check
```

Then read `docs/03-architecture/software-realism.md` and classify each major component as simulation, emulation, real software implementation, replay or reference.

## Evidence to collect

Create a run with:

```bash
./labctl new-run EXP-CARGO-NORMAL
```

The run directory is not “proof” yet. It is a checklist for evidence you still have to collect.

## Explain it in 60 seconds

Explain why this is **not** a digital replica of a specific LNG carrier, but can still be a defensible maritime OT research testbed.

## Go deeper

- [Research framework](../09-research/research-framework.md)
- [Software realism](../03-architecture/software-realism.md)
- [Engineering review](../08-reference/engineering-review.md)
