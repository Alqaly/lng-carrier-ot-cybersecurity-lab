# Evidence-first learning and delivery audit — 5 September 2026

## Scope and baseline

Baseline: `9ca3e306c1dc1ca64b510c3f58e44f69d6ccace0`. The canonical Notion
handoff, root and teaching contract were compared with this checkout. Its
103 Python tests and recursive gates passed locally before editing.

This is a **focused engineering audit** of evidence verification, aggregation,
commissioning retention, setup, learning and website delivery. It is not an
independent whole-project security audit, a marine-controls assessment, an image
vulnerability attestation or proof of research novelty.

## Findings and repairs

| Finding | Consequence | Repair |
|---|---|---|
| Empty indexes could verify | No evidence could be called verified | Exact required artifact set and fail-closed parsing |
| Metadata and evaluation semantics were not rechecked | Edited results could escape hash checks | Metadata hash plus read-only causal re-evaluation |
| Nested paths reduced to filenames | Valid custom paths could fail verification | Preserve run-relative evidence paths |
| Zero flow fell through a missing-value default | True no-flow observation could fail | Preserve zero as a valid observation |
| Aggregation trusted pass flags and duplicate runs | Inflated repetition counts | Verify inputs; deduplicate paths and metadata identities |
| Generic proof files satisfied manual dossier checks | Hashing confused with evidence coverage | Exact labels, operator/observation and automatic command checks |
| Full experimental evidence remained external to the dossier | Later acceptance depended on mutable external paths | Retain full verified baseline/repeated-run directories |
| Copy-and-edit secrets setup | Existing credentials could be overwritten | Private exclusive creation; preserve existing files |
| No shared learning-journey contract | Little guidance beyond chapter order | Prerequisites, practice, checkpoints and three learner paths |
| No standalone website container | Public course and private lab could be conflated | Static-only image with allowlisted context and isolated Compose project |
| Start page said loading | Drift from the ship-unloading profile | Align the operational description |

## Evidence compatibility

Experiment index schema 2 binds `run.json`. Verification does not silently
upgrade legacy indexes. Preserve old evidence and its original source; explicitly
re-evaluate a copy if needed, recording that this is re-analysis, not a new run.

Commissioning plan schema 2 uses the `baseline-run` label for the full normal
experiment directory. New source requires a new commissioning run. Do not
relabel old acceptance artifacts. Keeping 21 complete experiment copies inside
acceptance evidence requires additional disk space.

## Verification

The upgrade PR and its CI runs identify the final tested commit. Verification
covers Python regressions, JavaScript DOM-adapter tests, strict MkDocs build,
the learning contract, existing recursive gates and a separate course-container
build/HTTP smoke job.

The editing environment has no Docker executable or daemon: **no local container
run or full OT acceptance is claimed**. Real browser/keyboard/mobile visual and
accessibility checks have not been performed; DOM-adapter tests are not those checks.

## Remaining acceptance work

- Run live PLC, Modbus, OPC UA, FUXA, historian, reboot/restore and resource gates.
- Retain seven experiments at least three times each from one clean commit;
  preserve clock distinctions and unavailable metrics, then seek independent reproduction.
- Review manual observations: hashes detect changes, not observation authenticity.
- Resolve image digests, inventory dependencies and scan the actual release images.
  Base tags and transitive Python dependencies are not completely immutable.
- Check real browser accessibility and visual/reference reuse before website release.
- Collect learner/comparator data before claiming effectiveness, superiority or novelty.

See the [journey](../00-learning/learning-journey.md),
[capstone](../00-learning/investigation-capstone.md),
[first run](../04-build/first-run.md) and
[website/Docker guide](../04-build/website-and-docker.md).

Implementation references: [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/),
[Docker build-context exclusions](https://docs.docker.com/build/concepts/context/)
and the [official nginx image](https://hub.docker.com/_/nginx).
These support implementation choices, not runtime validation.
