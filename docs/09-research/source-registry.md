# Source Registry

This page answers **where a statement came from**. It does not claim that every
source was implemented.

Use the source labels consistently:

- **decision source** — changed the architecture, experiment or evaluation;
- **engineering anchor** — constrains terminology or a public equipment concept;
- **implementation documentation** — explains a software interface or version;
- **context only** — helps compare scope but supplies no implemented result.

For the exact decision → code → learner action → evidence chain, read
[What the Research Changed](research-to-model-matrix.md).

## Research decision sources

| ID | Source | What was adopted | What was not imported |
|---|---|---|---|
| `RT-CYBERSHIP-2019` | Tam, Forshaw & Jones, [Cyber-SHIP](https://pearl.plymouth.ac.uk/secam-research/1531/), DOI `10.24868/icmet.oman.2019.005` | system-of-systems scope and explicit realism classification | bridge hardware or physical-twin fidelity |
| `RT-CYBERMAR-2021` | Jacq et al., [Cyber-MAR hybrid range](https://www.cyber-mar.eu/wp-content/uploads/2021/09/Hybrid_cyber_range_use_for_port_risk_assessment.pdf), DOI `10.1109/CSR51186.2021.9527968` | dependency-first scenario design | port topology, econometric layer or physical range |
| `RT-MACYSTE-2023` | Longo et al., [MaCySTe](https://crack-mcr.github.io/MaCySTe/), DOI `10.1016/j.softx.2023.101426` | modular virtual maritime testbed and inspectable protocol components | navigation/RADAR/NMEA scope or codebase |
| `RT-LEE-PMS-2024` | Lee, [LNG-carrier PMS HIL test bed](https://www.mdpi.com/2077-1312/12/7/1236), DOI `10.3390/jmse12071236` | named PMS test functions and scenario-based verification | HIL apparatus, vessel parameters or FAT-replacement claim |
| `RT-MULLER-2022` | Mueller, Ziras & Heussen, [cyber-physical detection assessment](https://arxiv.org/abs/2202.09352), DOI `10.1109/SmartGridComm52983.2022.9961010` | network-only/process-only/cross-layer comparison | the paper's dataset, ML models or performance result |
| `RT-GHAEINI-2018` | Ghaeini et al., [state-aware anomaly detection](https://tippenhauer.de/publication/ghaeini-18-stateaware/ghaeini-18-stateaware.pdf), DOI `10.1145/3167132.3167305` | physical expectation and residual as independent evidence | CUSUM implementation, trained model or validated threshold |

## Marine engineering anchors

| Source | Used for | Claim boundary |
|---|---|---|
| [Wärtsilä: typical 138,000 m³ LNG tanker Cargo equipment](https://www.wartsila.com/encyclopedia/term/cargo-handling-equipment-of-a-typical-138-000m3-lng-tanker) | public example with four membrane tanks and two 1700 m³/h electric submerged pumps per tank | the software aggregates eight pumps; head, efficiency, density and geometry remain teaching assumptions |
| [ABB Marine PEMS](https://new.abb.com/marine/systems-and-solutions/digital/control-and-monitoring/PEMS) | marine power-management role | no ABB configuration or compliance claim |
| [Kongsberg K-Chief 600](https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/k-chief-600-marine-automation-system/) | distributed process units, remote I/O, centralized operators and mixed interfaces | the repository does not clone K-Chief |
| [Kongsberg AutoChief 600](https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/366198-f---autochief-600-product-sheet.pdf) | propulsion remote-control and engine-safety context | no vendor control logic or engine model |
| [Wärtsilä UNIC control-system upgrades](https://www.wartsila.com/services-catalogue/engine-services-4-stroke/control-system-upgrades) | start/stop, speed/load and safety concepts | no vendor thresholds or certification |
| [Wärtsilä main-engine lubricating-oil system](https://www.wartsila.com/encyclopedia/term/main-engine-lubricating-oil-system) | physical context for the pre-lube permissive | simplified teaching dynamics only |
| [SIGTTO Cargo Control Room HMI](https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/) | task-centred display and operator mental-model method | no licensed text reproduced and no compliance claim |
| [SIGTTO Cargo Alarm Management](https://www.sigtto.org/publications/recommendations-for-management-of-cargo-alarm-systems/) | alarm philosophy, rationalization, flooding and response | exact catalog values are project choices |
| [SIGTTO ESD Systems](https://www.sigtto.org/publications/esd-systems/) | ESD and ship/shore-link context | ESD is not implemented as a class-approved safety system |

The default vessel profile uses **mechanical main propulsion** with electrically
supplied Cargo and machinery auxiliaries. It does not place main-shaft power on
the PMS bus. Public propulsion alternatives are described by Wärtsilä's
[dual-fuel electric concept](https://www.wartsila.com/encyclopedia/term/df-electric-concept-also-dual-fuel-diesel-eletric-propulsion),
[hybrid electric LNG-carrier material](https://www.wartsila.com/marine/products/ship-electrification-solutions/hybrid-electric-lng-carrier)
and [gas-carrier segment material](https://www.wartsila.com/marine/customer-segments/merchant/small-and-medium-gas-carriers).

## Security and network anchors

| Source | Used for | Claim boundary |
|---|---|---|
| [NIST SP 800-82 Rev. 3](https://csrc.nist.gov/pubs/sp/800/82/r3/final) | zones, controlled conduits, DMZ and explicit authorized flows | does not define the lab's subnets or certify the design |
| [IACS UR E26](https://iacs.org.uk/resolutions/unified-requirements/ur-e/ur-e26-new) | maritime cyber-resilience lifecycle context | no IACS compliance claim |
| [IEC 61162-460](https://webstore.iec.ch/) | secure/redundant navigation-Ethernet context | no IEC 61162-460 network is implemented |
| [NMEA](https://www.nmea.org/) | public NMEA 0183/2000 interface context | no current navigation scenario |
| [ISA101](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa101) and [ISA-18](https://www.isa.org/standards-and-publications/isa-standards/isa-18-series-of-standards) | public HMI/alarm lifecycle context | design philosophy only; licensed standards are not reproduced |
| [EEMUA 191](https://www.eemua.org/Products/Publications/Digital/EEMUA-Publication-191.aspx) | alarm philosophy/database/operator-response context | no EEMUA compliance claim |

## Software implementation documentation

Versions are pinned in `DEPENDENCIES.md`; documentation here explains why each
interface is used.

| Software | Project use | Primary documentation |
|---|---|---|
| OpenPLC Runtime `4.1.9` | IEC 61131-3 controller runtime, Modbus and OPC UA | [official repository/releases](https://github.com/Autonomy-Logic/openplc-runtime/releases) |
| STruC++ | independent Structured Text compilation in CI | [official repository](https://github.com/Autonomy-Logic/STruCpp) |
| OpenModelica `1.27.0` | physical models and FMI 2.0 co-simulation export | [Docker](https://openmodelica.org/download/docker/) · [FMI guide](https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/fmitlm.html) |
| FMPy | step the exported FMUs | [official repository](https://github.com/CATIA-Systems/FMPy) |
| PyModbus | asynchronous Modbus TCP software I/O | [official repository](https://github.com/pymodbus-dev/pymodbus) |
| FUXA `1.3.4` | web HMI/SCADA and project import/export | [official repository](https://github.com/frangoteam/FUXA) · [project API](https://github.com/frangoteam/FUXA/blob/master/server/docs/openapi.yaml) |
| asyncua | live OPC UA namespace discovery during commissioning | [package documentation](https://pypi.org/project/asyncua/) |
| Zeek `8.0.10` | offline PCAP and Modbus analysis | [Modbus analyzer](https://docs.zeek.org/en/current/scripts/base/protocols/modbus/main.zeek.html) |

## Optional network-fidelity tooling

The canonical Compose baseline must remain runnable without this extension.

| Tool | Recorded decision |
|---|---|
| [Containerlab `0.77.0`](https://github.com/srl-labs/containerlab/releases/tag/v0.77.0) | selected as the optional topology orchestrator; [`ext-container`](https://containerlab.dev/manual/kinds/ext-container/) can attach links to Compose-managed containers |
| [nftables](https://wiki.nftables.org/wiki-nftables/index.php/Matching_connection_tracking_stateful_metainformation) | selected candidate for stateful default-deny software enforcement; not a vendor firewall |
| [Open vSwitch](https://docs.openvswitch.org/en/stable/faq/configuration/) | conditional passive mirror only when an experiment requires it |
| [GNS3 Docker support](https://docs.gns3.com/docs/emulators/docker-support-in-gns3) | reviewed, not selected for the current extension |
| [EVE-NG](https://www.eve-ng.net/index.php/documentation/howtos/) | reviewed, not selected; vendor images would require separate lawful sourcing |

## Registry rule

Adding a URL here is not enough. A new source may be called “used by the
project” only after its specific finding, decision, implementation path,
learner action, evidence and excluded claims are added to
`research-translation.json` and pass the research gate.
