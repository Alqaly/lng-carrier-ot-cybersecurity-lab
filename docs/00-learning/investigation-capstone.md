# Capstone: defend the cause, not the dashboard

Your deliverable is a short engineering case report that another reader can
challenge and reproduce. Your question is: **what changed, through which path,
with which process consequence, and how certain are we?**

Prerequisites: [the learning journey](learning-journey.md), a commissioned lab
or an instructor-reviewed retained evidence set, and the
[cross-layer evidence workbook](../06-scenarios/cross-layer-evidence-workbook.md).
Never connect fault-injection exercises to real vessels or production OT.

## Worked example — an explanation, not runtime proof

Consider this **illustrative teaching case**, not a captured result:
the pump start command is present, pump and valve feedback are true, and measured
flow is zero. Network evidence can establish that a transaction occurred; it
cannot by itself establish that the cargo moved. Independent level change can
help distinguish a blocked hydraulic path from a biased flow measurement.

A defensible conclusion is “the retained observations contradict expected
transfer; compare independent inventory change before distinguishing blockage
from instrumentation error.” An unsupported conclusion is “the packet proves a
cyberattack.” Neither conclusion becomes a measured result by appearing here.

## Round 1 — guided Cargo investigation

1. On the commissioned stack, retain and verify `EXP-CARGO-NORMAL` first.
2. Write your prediction for `EXP-CARGO-BLOCKED-FLOW` before applying the declared
   fault. Use the existing [Cargo walkthrough](../course/06-cargo.md) and
   [process-integrity scenario](../06-scenarios/process-integrity.md).
3. Preserve the PCAP, state timeline and alarm timeline in the experiment run.
   Do not edit the raw evidence to fit your prediction.
4. Use `./labctl evaluate <run-dir>`, followed by `./labctl verify-run <run-dir>`.
   Read the semantic checks and unavailable metrics, not only the exit status.
5. Explain the command → feedback → flow contradiction. Give one alternative
   cause and identify the measurement needed to rule it out.

The run directory is the one printed by `./labctl new-run EXP-CARGO-BLOCKED-FLOW`.
Angle-bracket paths in this guide are placeholders, not literal shell commands.
Consult the workbook for capture and observer commands and retain their outputs.

## Round 2 — fade the guidance

Choose the registered PMS generator-trip or propulsion cooling-fault experiment.
This time prepare your own expected event sequence before opening the evaluator.
Use the existing [PMS](../04-build/pms-module.md) and
[propulsion](../04-build/propulsion-module.md) references to find the symbols,
fault controls and required observations.

For PMS, locate a generator-online baseline, trip intervention, breaker loss,
frequency/blackout excursion and cross-system consequence. For propulsion,
locate enabled operation, cooling impairment, high coolant condition and the
later engine inhibit. Do not substitute an alarm screenshot for the full sequence.

Compare timestamps by their declared clock. Model time, observer-receive time,
alarm-source time, packet time and historian time are not interchangeable.
If alignment is unavailable, state the uncertain ordering rather than inventing latency.

## Round 3 — independent reconstruction

Have an instructor or peer prepare three views of the **same** retained run:

| View | Evidence available | Question |
|---|---|---|
| Network-only | PCAP, decode, expected-conduit classification | What messages crossed the observed conduit? |
| Process-only | Model/I/O state, independent residual, alarm and historian chronology | What physical behavior changed? |
| Cross-layer | Both views with source paths and clock declarations | Which causal explanation survives both views? |

Write a conclusion for each view before revealing the next. Keep the earlier
conclusions intact. If testing learning or investigation performance across
people, counterbalance reveal order: seeing the full answer first contaminates
a later network-only comparison. Use the same task, time allowance and scoring
rules across views. This exercise design does not itself establish effectiveness.

## Scoring rubric

Each criterion receives 0, 1 or 2 points. A peer should cite a sentence or artifact
for every awarded point. This is an instructional rubric, not a validated exam.

| Criterion | 0 — unsupported | 1 — partial | 2 — defensible |
|---|---|---|---|
| Provenance | No traceable sources | Paths without verified identity | Run/commit, evidence paths and integrity result retained |
| Causal chain | Names symptoms only | Links some states | Orders intervention, control response and consequence |
| Protocol meaning | Treats ports as explanation | Decodes message only | Maps source/function/address to a symbol and process meaning |
| Alternative causes | Declares one cause as certain | Names another cause | Gives a falsification test and missing observation |
| Claim boundaries | Claims attack, safety or novelty without proof | Mentions a limitation vaguely | Separates observed, inferred and unknown, including clocks |

Suggested course checkpoint: **8/10 with no zero in provenance or claim
boundaries**. This threshold is a teaching choice, not professional certification.
Preserve disagreements between reviewers instead of averaging them away silently.

## Case-report template

- **Question and prediction:** written before the intervention.
- **Source:** exact clean commit, experiment ID and commissioning context.
- **Initial conditions:** normal baseline and what changed intentionally.
- **Timeline:** event, clock, artifact path, field/packet reference and uncertainty.
- **Three explanations:** network-only, process-only and cross-layer.
- **Alternative causes:** one test that could disprove the preferred explanation.
- **Integrity:** evaluator and verifier output; unavailable metrics with reasons.
- **Score:** rubric points, reviewer rationale and unresolved disagreement.
- **Transfer:** how the lesson relates to a real marine system, and where it does not.

Keep private evidence and reports under `evidence/`; review and redact before
publishing any artifact. A file hash detects changes relative to a known record.
It does not prove that observations were authentic, independent, or collected on
an approved system.

For a research/release claim, complete **all seven experiments at least three
times from the same clean commit**, not three copies of one run. Then perform
the full [Gates A–G acceptance](../04-build/server-acceptance-test.md) and follow
the [experimental claim boundaries](../09-research/experimental-claim-boundaries.md).

## Explain-back and transfer

Close the report. Explain in 60 seconds what you initially believed, which
observation changed your mind, and what remains unknown. Revisit the explanation
on days 1, 7 and 21, mixing Cargo with a PMS or OPC UA case. Use the
[source registry](../09-research/source-registry.md) for marine references and
the [learning method](how-to-use-this-course.md) for the teaching rationale.
