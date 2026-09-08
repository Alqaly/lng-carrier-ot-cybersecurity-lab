# Commissioning Orchestrator

The commissioning orchestrator turns the target-server acceptance test into a resumable evidence run. It executes every machine-verifiable step, stops at observations that require the live OpenPLC or HMI, copies the supplied evidence into the run, hashes it, and refuses final acceptance until every Gate A–G artifact is valid.

It does **not** make OpenPLC Editor actions, screenshots, reboots or restore tests disappear. Those are real commissioning work. It makes the remaining work explicit and prevents a service-health check or handwritten `PASS` from being promoted into evidence.

## Before starting

Use a clean clone of the intended Git commit. Configure `.env`, set its mode to `0600`, and keep the services on their loopback/private-management bindings.

```bash
git status --short
./labctl setup
```

The orchestrator refuses a dirty Git tree. Each run snapshots the Git commit/tree, release manifest, commissioning plan and dossier contract. Later commands stop if any of those inputs change.

Setup preserves existing credentials and validates the private file. For a new
host or a checkout with local edits, complete [safe first run](first-run.md) first.

## Start Gates A and B

```bash
./labctl commission start
```

This creates `evidence/commissioning/<timestamp>-gates-a-g/` and runs:

- Gate A: preflight, complete static/research gates, rendered Compose validation without interpolating secrets;
- Gate B: FMU/container build, runtime smoke, **PMS first to establish power**, Cargo, Propulsion, and the cross-domain demo. A failed step stops this sequence.

The command prints the run directory. Preserve that exact path for every following command:

```bash
RUN=evidence/commissioning/<timestamp>-gates-a-g
./labctl commission status "$RUN"
```

Exit status `0` means the invoked automatic step completed, `2` means a validation failed, and `3` means the next gate requires live/manual evidence.

## Preserve and diagnose a partial run

Do not select a run merely because its directory is newest. Use the exact path
printed when you started that acceptance session. `status` is read-only and
reports retained evidence; it is not a new live health check. Its exit code is
not the acceptance decision—read the gate lines and final result.

Before CLI `run`, `resume`, `record` or `finalize` changes an existing run, it
copies that entire run to `evidence/commissioning/history/<run-name>/before-*/run`.
This preserves previous logs, hashes and attachments before a retry or deliberate
replacement. These are independent copies, not hard links. Allow disk space for
each copy; a failed copy aborts the operation. Keep one operator per run—concurrent
commissioning commands are not supported. History is private, ignored by Git,
and must be included in your evidence-retention/backup policy.

If a checkpoint fails:

```bash
./labctl commission status "$RUN"
```

Inspect the failed artifact's `commands` list for the nonzero `exit_code` and its
run-relative `log` path. Review logs locally and redact credentials before sharing.
Fix the cause, then `./labctl commission resume "$RUN"`. Failed resource profiles
are retried; invalid manual evidence is reported instead of silently skipped.
No recorder can determine whether your screenshot observation is truthful:
the operator must inspect it, and should not copy the example observation text
unless it describes what actually happened.

Do not pull or change source during a run. `finalize` and `resume` now explicitly
check the current clean source against the frozen snapshot, including when every
stored gate already says PASS. A source change needs a new commissioning run;
never edit the old run's provenance to make it match.

## Gate C — record live PLC evidence

Deploy and run the three OpenPLC projects using the generated I/O map. Retain online-state exports/screenshots and a normal Modbus packet capture. Then record the evidence with labels enforced by `commissioning/commissioning-plan.json`:

```bash
./labctl commission record "$RUN" plc-commissioning.json \
  --evidence cargo-online=/path/cargo-online.png \
  --evidence pms-online=/path/pms-online.png \
  --evidence propulsion-online=/path/propulsion-online.png \
  --evidence normal-modbus-pcap=evidence/live/cargo/modbus.pcap \
  --operator "$USER" \
  --note "All three PLCs were online; the retained Cargo transaction matched command, feedback and process response."

./labctl commission record "$RUN" plc-io-map-review.json \
  --evidence cargo-map=/path/cargo-map.txt \
  --evidence pms-map=/path/pms-map.txt \
  --evidence propulsion-map=/path/propulsion-map.txt \
  --operator "$USER" \
  --note "Every commissioned Editor address was compared with the generated map and no address drift remained."
```

The source files are copied under the run's `attachments/` directory. Their hashes—not the original paths—become acceptance evidence.

## Gate D — discover and bind live OPC UA

```bash
./labctl commission resume "$RUN"
```

After Gate C passes, `resume` runs live discovery, binding-plan generation, historian installation/recreation and freshness checks for Cargo, PMS and Propulsion. All discovery and binding outputs are written inside this commissioning run. A missing or ambiguous teaching tag blocks Gate D.

## Gate E — record HMI and normal baseline

Bind FUXA to the same discovered live nodes, export the project, and retain task-oriented screenshots plus a verified normal Cargo run:

```bash
./labctl commission record "$RUN" hmi-alarm-review.json \
  --evidence cargo-screen=/path/cargo.png \
  --evidence pms-screen=/path/pms.png \
  --evidence propulsion-screen=/path/propulsion.png \
  --evidence alarm-screen=/path/alarms.png \
  --evidence fuxa-export=evidence/fuxa/fuxa-project.json \
  --operator "$USER" \
  --note "Operator views showed the commissioned tags and the alarm view preserved the observed live chronology."

./labctl commission record "$RUN" normal-baseline-run.json \
  --evidence baseline-run=evidence/runs/<normal-run> \
  --operator "$USER" \
  --note "EXP-CARGO-NORMAL completed with file-backed evidence and passed semantic evaluation."
```

The normal-baseline recorder verifies the complete `EXP-CARGO-NORMAL` run,
checks that it came from this commissioning run's clean commit, and retains a
hashed copy of the entire directory. Three metadata files without their raw
evidence are not an accepted baseline. The repeated-run gate likewise retains
full verified run directories; allow disk space for these acceptance copies.

## Gate F — index repeated experiments

Run all seven registered experiments at least three times from the same clean Git commit. Evaluate and verify every run. Then:

```bash
./labctl commission run "$RUN" --gate F --experiment-root evidence/runs
```

The orchestrator rejects dirty runs, mixed commits, missing evidence indexes and failed evaluations. It re-runs integrity verification, aggregates each experiment separately, preserves unavailable metrics and requires the configured minimum repetition count. The minimum publication set is therefore 21 verified runs, not seven one-off demonstrations.

## Gate G — persistence, restore and resources

Install the daemon, retain the before/after reboot observations, run `runtime-verify`, perform a cold backup and verify a restore on a clean test host. Record the evidence:

```bash
./labctl commission record "$RUN" reboot-persistence.json \
  --evidence before-reboot=/path/before.txt \
  --evidence after-reboot=/path/after.txt \
  --evidence service-status=/path/systemctl-status.txt \
  --evidence runtime-verify=/path/runtime-verify.txt \
  --operator "$USER" \
  --note "The host boot ID changed and the commissioned services recovered before runtime verification passed."

./labctl commission record "$RUN" backup-restore.json \
  --evidence backup-checksums=/path/SHA256SUMS \
  --evidence restore-verification=/path/restore-verify.txt \
  --evidence restored-runtime=/path/restored-runtime-verify.txt \
  --operator "$USER" \
  --note "A checksum-verified cold backup was restored on a clean host and the commissioned runtime passed verification."

./labctl commission run "$RUN" --gate G --samples 24 --interval 5
```

Resource profiling records measurements only; it does not invent deployment limits.

## Finalize

```bash
./labctl commission finalize "$RUN"
```

Finalization validates every required JSON artifact, its Gate and filename identity, `pass=true`, the frozen Git commit, every retained evidence path and every SHA-256 hash. It writes `acceptance-dossier.json` and exits nonzero unless Gates A–G all pass.

If work is interrupted, use:

```bash
./labctl commission resume "$RUN"
```

`resume` executes the next safe automatic gate or prints the exact evidence labels required for the next live checkpoint.

## Claim boundary

A completed dossier supports the statement that this commit passed the documented target-server acceptance process with retained evidence. It does not make the models class-approved, validate production PKI, prove every cybersecurity claim or replace repeated experimental analysis.
