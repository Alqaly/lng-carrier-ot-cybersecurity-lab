# Full-Vessel Operational Event — Power, Cargo and Propulsion Auxiliaries

## Primary visual

Use the actual synchronized Cargo/PMS/Propulsion event timeline and packet evidence from the experiment. A static architecture figure is not evidence of cross-system behavior.

This exercise is the first scenario where the three executable domains influence one another.

## Selected vessel profile

The training profile represents **mechanical main propulsion**.

Therefore:

```text
Main shaft propulsion ≠ main PMS propulsion load
```

The PMS supplies:

- Cargo pump electrical demand,
- propulsion/machinery auxiliary electrical demand,
- hotel/auxiliary vessel load.

This avoids incorrectly modelling a mechanically propelled ship as an electric-propulsion vessel.

## Cross-system dependency

```text
Cargo pump power ─────────────┐
                              ▼
Propulsion auxiliary load → PMS bus
                              │
                              ├── Cargo power available
                              └── Propulsion auxiliary power available
```

## First run: process/I/O commissioning path

Start the model/I/O layer:

```bash
./labctl build
```

Capture at least Cargo and PMS Modbus traffic in separate terminals if desired:

```bash
./labctl capture cargo modbus
./labctl capture pms modbus
```

Run:

```bash
./labctl demo vessel
```

This intentionally bypasses OpenPLC. Its purpose is to validate physics, I/O and cross-system dependencies before adding controller behavior.

The scenario writes a structured timeline to:

```text
evidence/live/vessel/commissioning-timeline.jsonl
```

Each phase records:

- Cargo registers/feedback,
- PMS registers/feedback,
- Propulsion registers/feedback,
- Vessel Coordinator links,
- current alarm state.

## Phase 0 — known neutral state

Expected:

- no generators connected,
- no Cargo transfer,
- engine stopped,
- process values at their initial dynamic state.

## Phase 1 — establish electrical bus

```text
Gen 1 start
→ speed rises
→ ready
→ breaker closes
→ bus at nominal region
→ hotel load applied
```

Verify the PMS measurements and breaker feedback.

## Phase 2 — propulsion pre-lube

```text
PMS bus
→ auxiliary power available
→ pre-lube command
→ lube-oil pressure rises
→ propulsion auxiliary kW rises
→ PMS external auxiliary load rises
```

The main shaft is still mechanical; only the auxiliary load is coupled electrically.

## Phase 3 — engine and Cargo operation

Propulsion:

```text
pre-lube healthy
→ engine enable
→ fuel + pitch
→ RPM / torque / vessel-speed response
```

Cargo:

```text
valve command
→ valve feedback
→ pump command
→ pump feedback
→ flow
→ pump electrical kW
→ PMS external Cargo load
```

At this point the electrical system should carry hotel + Cargo + machinery auxiliary demand.

## Phase 4 — loss of Generator 1 before standby redundancy

Generator 2 has been started but its breaker is not yet closed.

Trip Generator 1.

Expected dependency propagation:

```text
Gen 1 trip
→ bus unavailable / frequency collapse
→ Cargo powerAvailable = false
→ Cargo pump speed decays
→ flow decays

and

→ propulsion auxPowerAvailable = false
```

The engine-driven lube contribution may preserve lubrication once the engine is already turning; the pre-lube electric dependency is still visible in the machinery model. This is a modelling choice documented in `model-assumptions.md`.

## Phase 5 — Generator 2 recovery

Wait until Gen 2 is ready and the model's simplified sync permissive is true.

Close its breaker.

Expected:

```text
bus restored
→ dependent auxiliary power restored
→ Cargo pump may recover if its command remains active
→ process state stabilizes
```

## Second run: final PLC-controlled exercise

After all three OpenPLC projects are commissioned, repeat the event through controller logic instead of the commissioning client.

Now compare:

```text
controller decision
↔ Modbus traffic
↔ process state
↔ alarm chronology
↔ OPC UA
↔ historian
```

## Investigation questions

1. Which subsystem is the initiating cause?
2. Which subsystem is merely showing a consequence?
3. Which Modbus messages were commands versus measurements?
4. Did the alarm chronology preserve the causal order?
5. Did historical visibility remain available during the power event?
6. What would be different on a diesel-electric / electric-propulsion vessel profile?

## Evidence workbook

Complete `cross-layer-evidence-workbook.md` using the generated timeline and PCAPs.
