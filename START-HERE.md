# Start Here

This is a software-only lab for learning how a physical process, controller and
network explain the same event. Read the notes directly on GitHub; no website is required.

Your first session has one route:

1. Read the [visual process/signal/packet guide](docs/00-learning/visual-guide.md).
2. Follow [setup](docs/04-build/first-run.md) and run `./labctl build`.
3. Open **http://127.0.0.1:8500** and complete the seven-step **Guided start**.
4. Use the [first Cargo investigation](docs/06-scenarios/first-cargo-investigation.md)
   to collect and interpret your own observations.

Each step tells you what to do, what should happen and what to inspect if it
does not. Do not begin with packet captures. Begin by understanding what the
process is supposed to do.


## The central question

> If an engineer sees a network packet or an alarm, can they trace it all the way to the physical or operational meaning?

For Cargo, the trace should look like:

```text
Operator intent
    ↓
PLC logic
    ↓
Modbus command
    ↓
I/O state
    ↓
process equation
    ↓
flow / level / pressure response
    ↓
feedback
    ↓
OPC UA
    ↓
historian
    ↓
security evidence
```

## What counts as a valid data point in the software lab?

Every value must have a defined provenance.

Example:

```text
Cargo.Flow_m3h
```

must be traceable to:

```text
OpenModelica equation
→ FMU output
→ virtual I/O input register
→ PLC variable
→ OPC UA node
→ historian field
```

Nothing should appear in Grafana simply because it “looks realistic.”

## Longer roadmap — after the first session

### 1. Vessel
Understand Cargo, PMS, propulsion, safety, bridge, engineering and ship/shore relationships.

### 2. OT fundamentals
Understand PLC scan cycle, sensor, actuator, command, feedback, interlock, alarm and trip.

### 3. Architecture
Understand zones, conduits, interfaces and trust boundaries.

### 4. Process physics
Understand how the Cargo process state evolves.

### 5. PLC
Write control logic and map I/O.

### 6. Protocols
Inspect Modbus, OPC UA and navigation data at message level.

### 7. Operations
Verify a normal ship-unloading sequence: liquid leaves the source inventory.

### 8. Cybersecurity
Investigate inconsistencies and unauthorized control-path behavior.

### 9. Marine mapping
Compare the learning model with public marine automation references.

## Definition of done for every chapter

You should be able to explain the chapter to another engineer **without reading the page**.


## After Cargo works

Continue in this order:

1. establish PMS power and complete the pre-PLC Cargo exercise,
2. commission the three OpenPLC controllers and their I/O maps,
3. discover OPC UA values and commission historian/HMI bindings,
4. collect the normal baseline and run registered experiments,
5. retain recovery evidence and finalize Gates A–G.

The [commissioning guide](docs/04-build/commissioning-orchestrator.md) is the
execution authority. A gate is a checkpoint with required evidence, not an
extra software component. Starting containers is only an early step.

The target skill is not “Docker started.” It is the ability to explain a state transition from model equation to packet to operator consequence.
