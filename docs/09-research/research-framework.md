# Research Question and Test Method

## Plain-language version

This project tests one main idea:

> When a shipboard OT event is ambiguous, does looking at the physical process,
> controller state and network evidence together help a learner reconstruct what
> happened better than looking at network traffic alone?

The project does **not** yet say the answer is yes. That would require repeated
runs and a declared comparison. The repository currently provides the testbed,
ground-truth interventions, evidence format and scoring method needed to test it.

The motivating case is deliberately simple to say and difficult to diagnose:

> **The Cargo pump reports running, but flow is zero. Why?**

Possible explanations include a blocked transfer path, biased flow measurement,
loss of electrical power, a command failure or an evidence gap. The learner must
separate those explanations using observations that can contradict one another.

## Why the project is built this way

The exact paper-to-design translation is documented in
[What the Research Changed](research-to-model-matrix.md). In summary:

| Research result | Project choice it caused |
|---|---|
| Connected maritime systems must be studied as a system of systems | Couple Cargo and machinery availability to PMS state |
| Cyber-range scenarios should start from assets, functions and dependencies | Begin the integrated case with electrical supply, not a fictional attacker |
| Virtual maritime testbeds can be modular and protocol-visible | Use replaceable services and retain real Modbus evidence |
| LNG-carrier PMS validation exercises named operating functions | Make load sharing, generator start, blackout and shedding observable |
| Cyber-physical features may add information beyond network features | Compare network-only, process-only and cross-layer conditions |
| Expected process behavior can expose sensor inconsistency | Compare reported Cargo flow with tank mass balance |

These choices are enforced by
[`research-translation.json`](research-translation.json), not left as a citation
list.

## Research questions

### RQ1 — Can the software model produce a real causal dependency?

If generation is lost, does the PMS state change first and dependent Cargo or
machinery availability change afterward? A passing answer needs an ordered,
retained timeline—not a screenshot of two low values.

### RQ2 — Does the evidence condition change reconstruction quality?

Give the same event to a learner under three conditions:

1. network evidence only;
2. process/controller evidence only;
3. both evidence sets together.

Score correct event order, conclusions supported by evidence and uncertainty
identified. Do not score confidence, vocabulary or how polished the answer
sounds.

### RQ3 — Can an independent physical check expose a bad measurement?

For Cargo transfer, estimate flow from the source tank's level change:

\[
\hat{Q}_k = A\frac{h_{k-1}-h_k}{t_k-t_{k-1}}
\]

Compare that estimate with measured flow:

\[
r_k(\%) = 100\frac{Q_k-\hat{Q}_k}{\max(|\hat{Q}_k|,\epsilon)}
\]

The current 20% threshold is a teaching choice. It must not be described as a
validated vessel alarm limit.

### RQ4 — Can another person reproduce the conclusion?

A result is reproducible only when the run records its source commit, dirty-tree
state, intervention, required artifacts, timestamps, metric calculation and
artifact hashes. `run.json` flags and screenshots alone are not evidence.

## What each registered experiment tests

| Experiment | Question answered | Required causal observation | What would make the run fail |
|---|---|---|---|
| `EXP-CARGO-NORMAL` | Does a valid transfer produce a coherent baseline? | valve/pump feedback, flow rise, source-level fall and demand in the expected order | missing process or packet evidence; inconsistent order |
| `EXP-CARGO-BLOCKED-FLOW` | Can healthy command/feedback coexist with no flow? | running pump and open path command with collapsed physical flow | evaluator accepts only a command or packet |
| `EXP-CARGO-SENSOR-BIAS` | Can mass balance contradict a biased flow signal? | declared bias and a residual crossing the teaching threshold | no independent level-derived estimate |
| `EXP-PMS-GEN-TRIP` | Does a generation event propagate across domains? | trip → breaker loss → excursion → downstream consequence | any required step is absent or out of order |
| `EXP-PROP-COOLING-FAULT` | Does cooling impairment reach protective action? | high coolant temperature followed by PLC-visible engine inhibit | high temperature without later inhibit |
| `EXP-UNEXPECTED-MODBUS-SOURCE` | Can a connection be judged against declared policy? | observed endpoint tuple compared with `security/conduits.json` | classification has no retained network record |
| `EXP-OPCUA-STALE-CARGO` | Can supervisory loss be separated from control loss? | stale historian path while verified Cargo Modbus traffic continues | outage scope or control continuity is unproven |

## The comparison protocol

Use the same prepared run, task wording, time allowance and scoring rubric for
all evidence conditions. Randomize or counterbalance condition order when the
same learner performs more than one condition. Record prior OT experience.

For each response, score:

- initiating event identified;
- event order correct;
- each conclusion tied to an artifact;
- competing explanations eliminated with evidence;
- remaining uncertainty stated;
- time to a defensible conclusion.

At least three repeated runtime runs per experiment are required by the current
commissioning plan. That is enough to test repeatability of the apparatus; it is
not automatically a sufficient learner-study sample. Any public effectiveness
claim needs a separately justified sample and analysis plan.

## Run and preserve one experiment

Create the run before collecting evidence:

```bash
./labctl new-run EXP-CARGO-BLOCKED-FLOW
./labctl observe 60 evidence/runs/<run-dir>
./labctl capture cargo modbus evidence/runs/<run-dir> --duration 20
./labctl zeek cargo evidence/runs/<run-dir>/cargo-modbus.pcap evidence/runs/<run-dir>/zeek
./labctl conduit-check cargo evidence/runs/<run-dir>/zeek/conn.log evidence/runs/<run-dir>/conduit-classification.json
./labctl evaluate EXP-CARGO-BLOCKED-FLOW evidence/runs/<run-dir>
./labctl verify-run evidence/runs/<run-dir>
```

For the Cargo sensor-bias test:

```bash
./labctl cargo-residual evidence/runs/<run-dir>/cargo-state.jsonl
```

For the Cargo supervisory-path test:

```bash
./labctl hist-fresh cargo --threshold 5 --out evidence/runs/<run-dir>/freshness-before.json
./labctl opcua-outage cargo start --out evidence/runs/<run-dir>/opcua-outage.json
./labctl capture cargo modbus evidence/runs/<run-dir> --duration 8
./labctl hist-fresh cargo --threshold 5 --out evidence/runs/<run-dir>/freshness-after.json || true
./labctl opcua-outage cargo restore --out evidence/runs/<run-dir>/opcua-outage.json
./labctl evaluate EXP-OPCUA-STALE-CARGO evidence/runs/<run-dir>
./labctl verify-run evidence/runs/<run-dir>
```

## Evidence and timestamp rules

`./labctl new-run` records the Git commit, origin, dirty-tree state and hash of
the release manifest. The observer records when it received each state while
preserving the model's `time_s` or source timestamp separately. The evaluator
resolves real files, validates their formats and hashes required artifacts.
`./labctl verify-run` detects missing or modified evidence.

Do not silently treat observer time as PLC time, model time as packet time, or a
boolean in `run.json` as proof that an event occurred.

## Current claim boundary

The project may currently say:

- it implements a reproducible method for collecting process, controller and
  network evidence;
- it tests whether cross-layer evidence improves reconstruction;
- its source code and static checks pass when CI is green.

It may not yet say:

- cross-layer analysis improves or outperforms network-only monitoring;
- the lab proves root cause or prevents attacks;
- its detector has operational performance;
- it reproduces a specific LNG carrier, HIL facility or class-approved design.

Those statements remain blocked until target-machine commissioning, repeated
experiment evidence and the comparison study support them.
