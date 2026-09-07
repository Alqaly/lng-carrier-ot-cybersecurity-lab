# 01 — What Are We Building?

## Why this matters

A cyber range can be impressive while teaching very little. This project has a stricter goal: build a reproducible LNG-carrier-oriented **software-defined cyber-physical OT testbed** where an engineer can trace an event from process dynamics to controller state, protocol traffic, operator visibility and investigation evidence.

## Explain the project before naming the tools

Use this explanation:

> The lab models a Cargo transfer whose pump depends on the vessel's electrical
> system. It then creates controlled faults and preserves process, PLC, packet,
> alarm and historian evidence. The learner has to explain what physically
> happened and which observations support that conclusion. It is a teaching and
> research testbed, not a replica of a particular ship.

If that statement is unclear, do not start with Docker, Modelica or OPC UA. Start
with the Cargo question below.

## Visual tour — start from the incident

![The lab's Cargo process, electrical supply and independent control signals](../assets/visuals/cargo-system.svg)

This original schematic shows the model you will operate: ship inventory, pump,
valve and shore receiving boundary. Follow the liquid path, then ask what changes
if PMS stops supplying pump power. Read the [visual guide](../00-learning/visual-guide.md)
to trace the same process into a signal and packet before installing anything.

## What one paper changed

Lee (2024), [*Development of Hardware-in-the-Loop Simulation Test Bed to Verify
and Validate Power Management System for LNG Carriers*](https://www.mdpi.com/2077-1312/12/7/1236),
tests load sharing, load-dependent generator start, blackout prevention and
preferential load behavior.

That led to four observable PMS behaviors in this lab:

- two online generators share demand;
- low reserve can start the second generator;
- the model exposes under-frequency and blackout state;
- the PLC sheds Cargo before hotel load as frequency falls.

You test those behaviors with `EXP-PMS-GEN-TRIP`; the evaluator requires trip,
breaker loss, frequency/blackout excursion and downstream vessel consequence in
that order. The paper did **not** supply the project's generator ratings,
thresholds or equations. This implementation is software-in-the-loop, not Lee's
physical HIL test bed.

The other paper-to-code decisions are listed in
[What the Research Changed](../09-research/research-to-model-matrix.md).

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
