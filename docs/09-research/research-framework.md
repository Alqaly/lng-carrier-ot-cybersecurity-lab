# Research Framework

## Problem statement

Maritime cyber ranges frequently emphasize bridge/navigation systems or generic virtualized ship networks. This project investigates whether a reproducible software-defined LNG-carrier OT testbed can connect **process dynamics, controller state, industrial protocol evidence and cross-system operational consequences** in a way that improves both training and incident reconstruction.

## Research questions

- **RQ1:** Can a software-defined LNG-carrier testbed reproduce meaningful causal dependencies among Cargo, PMS and propulsion/machinery domains?
- **RQ2:** Does combining network evidence with process/controller state improve event classification and root-cause reconstruction compared with network-only evidence?
- **RQ3:** Can explicit data provenance reduce ambiguity when investigating sensor, command and communication faults?
- **RQ4:** How accurately can alarm/event chronology reconstruct the causal order of cross-domain incidents?
- **RQ5:** Can the build methodology transfer to a second OT domain without redesigning the entire teaching/research framework?

## Related-work position

Relevant maritime work includes Cyber-SHIP, Cyber-MAR/maritime cyber-range research, bridge-focused cyber environments and recent marine integrated-platform cyber trainers. The project therefore does **not** claim novelty merely for virtualizing ship systems.

The candidate contribution is narrower and testable: a reproducible LNG-carrier-oriented, cross-layer evidence chain that maps dynamic process state ↔ PLC/I/O ↔ protocol ↔ operator/history ↔ defensive investigation across coupled vessel domains.

## Evaluation

Experiments must define ground truth before execution and report, where meaningful:

- detection latency,
- process response time,
- alarm latency,
- event-order accuracy,
- reconstruction completeness,
- false positives/negatives for a defined detection rule,
- runtime overhead.

No metric is reported without retained evidence and a reproducible calculation method.


## Reproducible runtime evidence workflow

Create the run first, then let the observer timestamp what it actually receives. Alarm transitions retain the alarm-engine source timestamp. Process and vessel snapshots are timestamped at observer receipt while preserving `time_s` or `last_update` separately, so the evidence never pretends the observer clock is a PLC/process source clock.

```bash
./labctl new-run EXP-CARGO-BLOCKED-FLOW
./labctl observe 60 evidence/runs/<run-dir>
./labctl capture cargo modbus
./labctl zeek cargo
./labctl conduit-check cargo
./labctl evaluate EXP-CARGO-BLOCKED-FLOW evidence/runs/<run-dir>
```

For Cargo sensor-integrity work, the mass-balance analyzer accepts either CSV or the observer JSONL timeline:

```bash
./labctl cargo-residual evidence/runs/<run-dir>/cargo-state.jsonl
```

For a Cargo supervisory outage, preserve the Modbus controller path and isolate only the PLC operations-network attachment:

```bash
./labctl hist-fresh cargo --threshold 5 --out evidence/runs/<run-dir>/freshness-before.json
./labctl opcua-outage cargo start
# wait beyond the declared freshness threshold
./labctl hist-fresh cargo --threshold 5 --out evidence/runs/<run-dir>/freshness-after.json || true
./labctl opcua-outage cargo restore
```

`conduit-check` compares Zeek connection evidence against `security/conduits.json`; `cargo-residual` compares measured flow with source-tank mass balance; `hist-fresh` uses the commissioned OPC UA group/Influx measurement name rather than a guessed tag identity.

## Evidence integrity and repository provenance

`./labctl new-run` records the Git commit, origin URL when configured, dirty-tree state and SHA-256 of `release-manifest.json`. `./labctl evaluate` resolves concrete files inside the run directory, validates their formats, hashes every required artifact and applies experiment-specific checks. `run.json` boolean flags are not accepted as evidence. After evaluation, `./labctl verify-run <run-dir>` detects missing or modified artifacts by SHA-256.
