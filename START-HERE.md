# Start Here

Start with the [visual process/signal/packet guide](docs/00-learning/visual-guide.md).
Then use [setup](docs/04-build/first-run.md) and the
[first Cargo investigation](docs/06-scenarios/first-cargo-investigation.md).
Those pages give you the initial state, commands, observations and recovery steps.

This project is a **course, lab, research notebook and reproducible engineering build**.

Do not begin with packet captures.

Begin by understanding what the process is supposed to do.

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

## Learning order

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
Verify a normal loading sequence.

### 8. Cybersecurity
Investigate inconsistencies and unauthorized control-path behavior.

### 9. Marine mapping
Compare the learning model with public marine automation references.

## Definition of done for every chapter

You should be able to explain the chapter to another engineer **without reading the page**.


## After Cargo works

Continue in this order:

1. commission the operator HMI and alarm philosophy,
2. run the packet labs,
3. build the Power Management module,
4. build the Propulsion & Machinery module,
5. run troubleshooting cases that require cross-layer evidence.

The target skill is not “Docker started.” It is the ability to explain a state transition from model equation to packet to operator consequence.
