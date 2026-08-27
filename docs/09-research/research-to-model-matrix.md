# Research-to-Model Matrix

This page prevents the lab from quietly turning public marine facts and private teaching assumptions into one indistinguishable story.

## Classification

Each design item is labelled as one of:

- **Public marine anchor** — supported by an authoritative public source.
- **Teaching assumption** — selected by this project to make an executable model.
- **Executable relationship** — a causal equation/logic implemented in the lab.
- **Not modelled** — deliberately left outside the executable scope.

## Cargo

| Item | Classification | Basis |
|---|---|---|
| Four membrane cargo tanks in the public 138,000 m³ example | Public marine anchor | Wärtsilä encyclopedia |
| Two 1700 m³/h electric submerged pumps per tank | Public marine anchor | Wärtsilä encyclopedia |
| Aggregate 13,600 m³/h software pump bank | Executable relationship derived from public anchor | 8 × 1700 m³/h |
| Pump head 100 m | Teaching assumption | not presented as vendor data |
| Pump efficiency 0.72 | Teaching assumption | not presented as vendor data |
| Cargo density 450 kg/m³ | Teaching approximation | representative liquid property only |
| Tank cross-sectional areas | Teaching assumption | chosen for useful dynamic time scale |
| BOG/reliquefaction thermodynamics | Not modelled | marine reference only |

Public source:
https://www.wartsila.com/encyclopedia/term/cargo-handling-equipment-of-a-typical-138-000m3-lng-tanker

## Power Management

| Item | Classification | Basis |
|---|---|---|
| Integrated marine power/energy management | Public marine anchor | ABB PEMS / Kongsberg K-Chief |
| Generator start/stop, breaker, reserve/load-shed concepts | Public marine anchor | marine PMS concept |
| Two 4500 kW teaching generators | Teaching assumption | selected for integrated exercises |
| 60 Hz bus | Teaching assumption/profile | not a universal LNG-carrier value |
| Frequency-dynamic equation | Executable relationship | teaching AC-bus balance |
| Full protection coordination / synchronizer | Not modelled | outside current scope |

Sources:
- https://new.abb.com/marine/systems-and-solutions/digital/control-and-monitoring/PEMS
- https://www.kongsberg.com/contentassets/8718109b78554cd0820b221c499a3442/k-chief-data-sheet.pdf

## Propulsion

| Item | Classification | Basis |
|---|---|---|
| Mechanical main-propulsion teaching profile | Architecture selection | real LNG/gas vessels have multiple propulsion architectures |
| Pre-lube / lube-pressure / cooling / speed protection concepts | Public marine-control concept | engine-control references |
| Max RPM / torque / inertia values | Teaching assumptions | not vendor ratings |
| Shaft torque balance | Executable relationship | rotational dynamics teaching equation |
| Main-shaft power placed on PMS bus | **Not modelled / deliberately false for this profile** | profile uses mechanical main propulsion |
| Auxiliary machinery electrical load on PMS | Executable cross-system relationship | selected profile dependency |

## HMI and alarms

| Item | Classification | Basis |
|---|---|---|
| Operator-centred Cargo HMI design | Public marine anchor | SIGTTO Cargo Control Room HMI guidance |
| Task-based loading display | Public marine anchor | SIGTTO example/process |
| Alarm-management philosophy | Public marine anchor | SIGTTO cargo alarm guidance |
| Exact priorities/thresholds/timers in `alarms/catalog.json` | Teaching assumptions | rationalized for this model only |

Sources:
- https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/
- https://www.sigtto.org/publications/recommendations-for-management-of-cargo-alarm-systems/

## Marine automation architecture

Kongsberg's public K-Chief material is used to teach that real marine automation can include:

- Distributed Processing Units,
- redundant process/network paths,
- CAN between distributed units,
- remote I/O,
- serial/vendor-system integration,
- centralized operator stations.

The repository does **not** clone K-Chief.

Source:
https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/k-chief-600-marine-automation-system/
## Network fidelity and cyber architecture

| Item | Classification | Basis |
|---|---|---|
| Segmentation into zones/tiers and controlled conduits | Public OT-security anchor | NIST SP 800-82 Rev. 3 |
| DMZ as an enforcement boundary | Public OT-security anchor | NIST SP 800-82 Rev. 3 |
| Secure integration of shipboard IT/OT across lifecycle | Public maritime cyber-resilience anchor | IACS UR E26; context only, no compliance claim |
| Current `172.28.x.0/24` subnets and endpoint IPs | Teaching/research ground truth | project-defined deterministic addresses, not vessel values |
| Docker bridge segmentation in canonical mode | Real software implementation with fidelity boundary | Docker networking; does not claim routed industrial-firewall behavior |
| Containerlab 0.77 explicit dataplane extension | Infrastructure implementation selected by research | optional and runtime-unvalidated until NF-A–NF-G |
| Linux static routing | Infrastructure implementation | chosen as simplest routed-zone mechanism |
| nftables default-deny conduit enforcement | Real software policy implementation | stateful filtering; not a vendor industrial-firewall claim |
| OVS mirror/SPAN sensor feed | Conditional implementation | only if an experiment requires passive mirrored traffic |
| FRR dynamic routing | Not modelled / not currently justified | add only for a routing-protocol research objective |
| Vendor firewall appliance behavior | Not modelled | requires a lawful vendor image/appliance and a vendor-specific research question |

Sources:
- https://csrc.nist.gov/pubs/sp/800/82/r3/final
- https://iacs.org.uk/resolutions/unified-requirements/ur-e/ur-e26-new
- https://containerlab.dev/manual/kinds/ext-container/
- https://wiki.nftables.org/wiki-nftables/index.php/Matching_connection_tracking_stateful_metainformation
- https://docs.openvswitch.org/en/stable/faq/configuration/

