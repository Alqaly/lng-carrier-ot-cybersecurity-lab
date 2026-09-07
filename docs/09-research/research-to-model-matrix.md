# What the Research Changed

This is the page to read when someone asks: **“What did the papers actually add to this project?”**

The short answer is that the papers did not supply a finished LNG-carrier model. They changed six design decisions: couple the vessel domains, start scenarios from operational dependencies, keep the testbed modular, exercise named PMS functions, compare three evidence conditions, and test sensor claims against a physical residual.

A citation counts as used only when the project can show this chain:

> **published result → engineering decision → implementation → learner action → retained evidence → claim limit**

The machine-readable version of that chain is
[`research-translation.json`](research-translation.json). `tools/research_gate.py`
checks that every listed path and experiment exists.

## The project in one minute

The lab asks a practical incident question:

> A Cargo pump reports **running**, but transfer flow is **zero**. Is the command wrong, the flow path blocked, the measurement biased, or electrical power unavailable?

One screen cannot answer that. The learner must compare the dynamic process, PLC
state, Modbus traffic, alarm chronology and an independent physical check. The
papers below explain why the project was built that way. They do **not** prove
that this implementation works; the project's own experiments must do that.

## RT-CYBERSHIP-2019 — Couple the domains and label realism

**Source.** Tam, Forshaw and Jones, *Cyber-SHIP: Developing Next Generation
Maritime Cyber Research Capabilities* (2019),
[DOI 10.24868/icmet.oman.2019.005](https://pearl.plymouth.ac.uk/secam-research/1531/).

**Result used.** Maritime cyber research must consider connected ship systems
and make a deliberate choice among simulation, emulation and live equipment.

**Decision made here.** Cargo, PMS and propulsion auxiliaries are not three
unrelated demos. `vessel/coordinator.py` couples their power dependency. The
architecture contract also labels what is a dynamic simulation, protocol
emulation or real software implementation.

**Learner test.** In `EXP-PMS-GEN-TRIP`, show the order
generator trip → breaker loss → frequency/blackout excursion → vessel
consequence. Retain the PMS state, vessel state, alarms and Modbus capture.

**Limit.** This lab contains no bridge hardware and is not a physical twin. It
does not inherit Cyber-SHIP's live-equipment realism.

## RT-CYBERMAR-2021 — Start from a dependency, not an attack story

**Source.** Jacq et al., *The Cyber-MAR Project: First Results and Perspectives
on the Use of Hybrid Cyber Ranges for Port Risk Assessment* (2021),
[paper](https://www.cyber-mar.eu/wp-content/uploads/2021/09/Hybrid_cyber_range_use_for_port_risk_assessment.pdf).

**Result used.** Cyber-MAR derives scenarios by studying incidents, assets,
functions and dependencies. Its port scenario treats electrical supply as a
driver because other operations depend on it.

**Decision made here.** The integrated vessel scenario starts with power
availability. The PMS receives Cargo-pump and machinery-auxiliary demand, and
the Vessel Coordinator returns bus availability to those processes.

**Learner test.** When Cargo or machinery stops, check whether the initiating
event was electrical before calling it a controller fault or cyberattack.

**Limit.** This project does not reproduce a port, Cyber-MAR's econometric
layer, or its hybrid physical range.

## RT-MACYSTE-2023 — Use replaceable services and inspectable protocols

**Source.** Longo et al., *MaCySTe: A virtual testbed for maritime
cybersecurity* (2023),
[DOI 10.1016/j.softx.2023.101426](https://crack-mcr.github.io/MaCySTe/).

**Result used.** MaCySTe demonstrates that a virtual maritime testbed can be
assembled from modular network, scenario, software-PLC, Modbus, attack and
monitoring components.

**Decision made here.** The Compose architecture uses replaceable open-source
services and produces real Modbus traffic. This project adds its own dynamic
Cargo, PMS and propulsion models and evidence rules rather than copying
MaCySTe's navigation scope.

**Learner test.** Follow one value across Modelica → I/O mapping → Modbus → PLC
variable → packet analysis. Then use `EXP-UNEXPECTED-MODBUS-SOURCE` to classify
an observed connection against the declared conduit policy.

**Limit.** This is not a fork of MaCySTe and does not claim its RADAR, NMEA or
integrated-navigation coverage. A group of containers is not, by itself, a
research contribution.

## RT-LEE-PMS-2024 — Turn PMS functions into observable scenarios

**Source.** Lee, *Development of Hardware-in-the-Loop Simulation Test Bed to
Verify and Validate Power Management System for LNG Carriers* (2024),
[DOI 10.3390/jmse12071236](https://www.mdpi.com/2077-1312/12/7/1236).

**Result used.** The study evaluates an LNG-carrier PMS with scenario tests for
load sharing, load-dependent start, blackout prevention and preferential load
behavior.

**Decision made here.** `PowerManagementPlant.mo` exposes generator loading,
reserve, frequency and blackout state. `PowerManagement.st` implements a
reserve-based second-generator start and staged Cargo/hotel load shedding.

**Learner test.** Establish the bus, add demand, trip one generator and explain
the event order from retained state and alarm evidence. `experiments/evaluate.py`
must reject a run that lacks the intervention, breaker loss, excursion or
downstream effect.

**Limit.** This is software-in-the-loop, not Lee's HIL apparatus. The 4500 kW
ratings, 60 Hz profile and thresholds are project teaching assumptions, not
paper values. The project does not claim to replace a factory acceptance test.

## RT-MULLER-2022 — Compare evidence conditions before claiming improvement

**Source.** Mueller, Ziras and Heussen, *Assessment of Cyber-Physical Intrusion
Detection and Classification for Industrial Control Systems* (2022),
[DOI 10.1109/SmartGridComm52983.2022.9961010](https://arxiv.org/abs/2202.09352).

**Result used.** On the paper's dataset, combining physical-process and network
features improved classification over a network-only counterpart and supported
joint analysis of attacks and faults.

**Decision made here.** The capstone requires three separate conditions:
network-only, process-only and cross-layer. `config/detection-claims.json`
forbids saying this project “outperforms network-only monitoring” until repeated
controlled runs support that statement.

**Learner test.** Investigate the same event under all three evidence
conditions. Score correct event order, supported conclusions and unresolved
uncertainty; do not score confidence or writing style.

**Limit.** The published performance result belongs to the paper's dataset and
detectors. This project currently has a hypothesis and comparison protocol—not
a positive result.

## RT-GHAEINI-2018 — Check a sensor against expected physical behavior

**Source.** Ghaeini et al., *State-Aware Anomaly Detection for Industrial
Control Systems* (2018),
[DOI 10.1145/3167132.3167305](https://tippenhauer.de/publication/ghaeini-18-stateaware/ghaeini-18-stateaware.pdf).

**Result used.** The paper shows how expected process behavior and
state-dependent residuals can detect deviations that a single sensor or traffic
view cannot explain.

**Decision made here.** `security/process_residual.py` independently estimates
Cargo flow from source-tank level change and compares it with the reported flow.
The resulting residual is stored separately from the Modbus capture.

**Learner test.** In `EXP-CARGO-SENSOR-BIAS`, inject a deterministic flow bias
and decide whether command, equipment feedback, tank inventory and measured flow
still agree.

**Limit.** The project implements a simple mass-balance residual with a fixed
teaching threshold. It is not the paper's state-aware CUSUM detector, uses no
trained model, and has not validated an operational alarm limit.

## What came from engineering references instead of papers?

Research papers shape the experiment and architecture. Public engineering
references constrain domain vocabulary and selected equipment relationships:

| Reference | What it anchors | What remains a project assumption |
|---|---|---|
| Wärtsilä typical 138,000 m³ LNG tanker example | Four membrane tanks and two 1700 m³/h submerged pumps per tank | Aggregate pump-bank head, efficiency, density and tank geometry |
| ABB PEMS and Kongsberg K-Chief material | Marine PMS/automation roles and distributed architecture concepts | Two 4500 kW generators, the 60 Hz profile and simplified dynamics |
| SIGTTO Cargo HMI/alarm guidance | Task-centred displays, alarm rationalization and operator mental model | Exact priorities, delays, thresholds and screen implementation |
| NIST SP 800-82 Rev. 3 and IACS UR E26 | Segmentation, controlled conduits and maritime cyber-resilience context | Lab subnets, policy rules and all compliance status |

See the [source registry](source-registry.md) for exact links. None of those
references turns a teaching parameter into vessel data.

## Model facts, assumptions and exclusions

| Domain | Public anchor | Implemented teaching relationship | Deliberately not claimed |
|---|---|---|---|
| Cargo | Eight 1700 m³/h pumps in one public vessel example | One aggregate pump bank, valve/flow dynamics and tank mass balance | Vendor P&ID, cryogenic thermodynamics or a specific ship |
| PMS | Marine generator, breaker, reserve and load-management functions | Simplified two-generator frequency/load balance and staged shedding | Protection coordination, phase-angle/AVR detail or HIL fidelity |
| Propulsion | Marine pre-lube, cooling and engine-safety concepts | Mechanical main shaft plus electrically supplied auxiliaries | Main shaft on the PMS bus, vendor ratings or full engine thermodynamics |
| Network | OT zones, conduits and enforcement principles | Deterministic private subnets and declared Modbus paths | Vessel network survey, vendor firewall behavior or IACS compliance |

## What would disprove the project's research story?

The project should not claim a contribution if any of these remain true after
commissioning:

1. the coupled domains do not produce a repeatable downstream consequence;
2. an evaluator passes without the evidence required by its hypothesis;
3. the cross-layer condition does not improve the predeclared reconstruction
   measure over the network-only condition;
4. the Cargo residual cannot distinguish the declared bias from healthy runs;
5. another learner cannot reproduce the result from the retained run record.

That is the difference between a research question and marketing language.
