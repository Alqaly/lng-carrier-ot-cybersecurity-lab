# Reader-first audit — 7 September 2026

## Decision and scope

Publish and teach from the existing GitHub repository. Do not build another
website or duplicate the Notion course. Optional local documentation rendering
is retained for existing users, but is not a prerequisite for learning or running
the lab.

Baseline: `e991c37d27d20a5c8732de0502d8419354d8c70f` (PR #15).
The baseline's 134 Python tests pass in this review environment. That did not
prevent the defects below. Test count and document presence are not equivalent
to correct behavior, teaching clarity or a working target deployment.

This is a **source/setup/evidence repair pass**, not a completed whole-project
certification. No Docker executable/daemon is available in the review environment.
No target dossier or runtime screenshots were supplied for this pass.

## Findings and implemented repairs

| Finding | Consequence | Repair / regression coverage |
|---|---|---|
| README leads with research and optional course hosting | Reader meets unfamiliar names before understanding the process | Introduce unloading, power dependency, five terms and command/feedback/flow first; mark hosting optional |
| Learning Portal opens as nine equally weighted reference panels | A first-time learner sees data but no connected task, sequence or stopping point | Open on a seven-step Guided start; move reference panels behind progressive disclosure; test default route, navigation and offline fallback |
| Missing model telemetry is formatted as zero or OFF | A transport/service failure can look like a real process state | Preserve `UNKNOWN`, `unavailable` and em-dash states; clear stale live-dashboard values after a failed snapshot |
| Competing start documents say loading/unloading and give different build orders | Reader cannot tell which physical direction or dependency is intended | Correct root START-HERE to unloading and align acceptance order |
| Doctor/preflight check Docker installation but not daemon access | Setup appears valid although build cannot contact Docker | Check `docker info`; test unreachable daemon with a fake CLI |
| Build starts services without a bounded health wait | Immediate smoke can race startup | Request Compose health wait with a 180-second timeout |
| Modbus exception reads become empty lists; writes are unchecked | A failed protocol operation can exit as a successful demo | Checked client rejects exception responses; short reads fail; behavioral protocol fixtures |
| Cargo demo does not require flow or feedback | Printed values can be mistaken for demonstrated transfer | Require positive measured flow plus valve/pump feedback; attempt neutral commands on failure |
| Gate B runs Cargo before PMS and continues after failures | A cold-start Cargo test lacks its power prerequisite | Establish PMS first; verify energized bus; stop at first failed Gate B step |
| Retry commands overwrite earlier run artifacts/logs | The initiating failure can be lost | CLI preserves a complete independent pre-mutation copy before run/resume/record/finalize |
| Finalize does not check current source | Stored evidence can be accepted from a changed checkout | Check clean frozen source before any finalization write; regression refuses dirty source |
| Gate G resume tests resource file existence, not validity | A failed profile can become a permanent manual-evidence pause | Retry invalid resource artifact; report invalid recorded artifacts |
| Daemon instructions say after full commissioning | Circular dependency: Gate G needs daemon reboot proof before completion | Install after healthy runtime and before Gate G reboot test |

Regression fixtures live in `tests/test_reader_first_audit.py`. They simulate
failures; they are not collected evidence from a PLC or vessel.

Local verification after repairs: **148 Python test cases passed**, all
`./labctl review` source gates passed, strict MkDocs build passed, fifteen JavaScript
behavior tests passed, changed shell scripts passed `bash -n`, and
`git diff --check` passed. The manifest counts **146 test functions**; two
parameterized functions produce the additional cases. The manifest regression
now derives that count rather than asserting a stale hard-coded total.

## What was reviewed, and what remains open

| Area | Coverage in this pass | Still required |
|---|---|---|
| Reader entry/setup | README, START-HERE, first-run, seven-step portal guide, Cargo exercise, gate guide, acceptance checklist | Independent learner follows the revised path and explains the first observation without help |
| Runtime launch | labctl, preflight, secrets entry, Compose process health/dependency definitions | Fresh Docker-host build, FMU execution and state sanity |
| Protocol demos | Connection/read/write error handling, Cargo observation, PMS prerequisite, Gate B sequencing | Actual device behavior, timing and all fault cleanup paths |
| Acceptance evidence | Resume/finalize, prior-attempt retention, resource retry, dossier command order | Complete Gates A–G; independent verification of manual observations |
| Research teaching | Existing paper-to-code matrix, residual implementation, claim boundary; one worked mass-balance example | Independent review of every source attribution and measured three-condition comparison |
| Notion | Root, canonical handoff and build entry compared with GitHub | Full chapter-by-chapter rewrite/review remains open; no claim that all pages were re-audited |
| Security/deployment | Relevant startup/credential/evidence paths inspected | Threat-model review of every service, dependency advisories, restore/reboot/network-fidelity tests |

## Research, explained as a calculation

The residual implementation uses `tank_area × level_drop / elapsed_model_time`
to estimate flow. The README's 1250 m² × 0.004 m / 10 s = 0.5 m³/s example
explains why a 0.6 m³/s transmitter value deserves investigation. These are
constructed teaching numbers, not new experimental results.

The network/process comparison is motivated by
[Müller, Ziras and Heussen](https://arxiv.org/abs/2202.09352), who evaluated
combined data on their dataset. This project does not inherit their performance
result. Comparing learner investigations also does not reproduce their trained
classifier evaluation. A three-repeat minimum is an acceptance floor, not a
statistical power calculation or proof of novelty.

## Next execution boundary

1. Review this repair branch and its checks before adopting it. Do not change
   the source of an in-progress target commissioning run.
2. On a clean checkout, follow [first run](../04-build/first-run.md), using PMS
   before Cargo. Preserve errors and state; do not remove volumes to retry.
3. Complete live PLC maps, OPC UA identity, historian freshness and HMI bindings.
4. Retain 21 verified experiment runs and reboot/restore/resource evidence.
5. Finalize the dossier. Keep claims at release-candidate level until it passes.

Compose wait behavior is based on the
[official CLI reference](https://docs.docker.com/reference/cli/docker/compose/up/).
Healthy containers establish availability, not process fidelity or a safe PLC program.
