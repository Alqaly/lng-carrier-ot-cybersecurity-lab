# Learner experience: what still needs work

## Review correction — 6 September 2026

The earlier publication assessment was too broad. The automated gates checked
file/link presence, declared chapter sections and source contracts. They did not
establish that a newcomer could understand the diagrams, install the lab or
complete a useful investigation. Test count is not a measure of teaching quality.

This pass repairs the entry experience: an illustrated README/home, a visual
process/signal/packet guide, fresh and existing checkout setup, a worked Cargo
register lesson, and a first investigation with expected observations and recovery.
These changes have not yet undergone an independent learner trial or target-machine execution.

## Remaining work and acceptance criteria

| Priority | Deliverable | It is finished when |
|---|---|---|
| P0 | Walk through setup on a clean reference Linux target | Every command is executed in order; OS, resources, image digests, errors and resolutions are retained; someone reaches their first explained signal |
| P0 | Annotated OpenPLC commissioning screenshots | Cargo, PMS and Propulsion each show the actual project import, I/O mapping, deployment and online state, with verified runtime/editor versions |
| P0 | FUXA and historian walkthrough | An operator can follow actual screenshots from live NodeId discovery to a bound HMI signal and matching Grafana trend, including stale-data recovery |
| P0 | Complete published example investigation | An accepted run has redacted PCAP, model/controller timeline, alarms, trend and a reasoned conclusion; source commit and capture provenance accompany every runtime image |
| P1 | Full chapter-by-chapter teaching review | Every chapter has an actual readable visual, a worked example with explanation, meaningful practice and an answer rationale; a link to an external figure alone is insufficient |
| P1 | Interactive signal and PLC scan lessons | Learners predict effects of scaling, lag and scan order, change one input and receive explanatory feedback; illustrative calculations are labelled |
| P1 | PMS and Propulsion first investigations | Each has prerequisites, exact actions, named observations, a packet/signal example, recovery and troubleshooting matching the depth of the Cargo entry exercise |
| P1 | Real marine visual context | Licensed embedded vessel/equipment photographs or figures have attribution and explain their relation to the teaching model; link-only permissions remain links |
| P1 | Desktop/mobile usability review | Screenshots show legible diagrams, working navigation/code copy/search and no horizontal page overflow; newcomers can find setup from the first screen |
| P1 | Independent learner trial | A learner unfamiliar with the repo performs the first exercise without undocumented assistance; their points of confusion become fixes |

## Visual evidence rules

The new process, signal and packet SVGs are original explanatory figures under
the repository license. Numeric packet/flow examples are constructed, not collected
from a running target. They can teach protocol meaning but cannot prove commissioning.

Runtime images must state the source service/tool, capture time, run and source
commit, plus a redaction review. Keep raw captures private until reviewed.
See the [image provenance policy](../09-research/visual-source-registry.md) and
[experimental boundaries](../09-research/experimental-claim-boundaries.md).

An illustrated course preview may be shared for review. Calling the full course
complete or the lab commissioned requires the unfinished work above and the
[server acceptance process](../04-build/server-acceptance-test.md).
