# Source Registry

The public research layer prioritizes official manufacturers, standards organizations and industry bodies.

## Kongsberg Maritime — K-Chief

Used for:
- distributed marine automation architecture,
- cargo/power/propulsion monitoring context,
- redundant process/network concepts,
- remote I/O and CAN/Ethernet gateway examples.

Official product material:
https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/k-chief-600-marine-automation-system/

Current product/class material also lists K-Chief/K-Safe/AutoChief systems with IACS UR E27:
https://www.kongsberg.com/maritime/contact/certificates/product-certificates/lloyds-register-lr2607820sc-02/

## ABB — Marine PEMS

Used for:
- marine power management reference.

https://new.abb.com/marine/systems-and-solutions/digital/control-and-monitoring/PEMS

## Wärtsilä — Gas Solutions

Used for:
- LNG/gas handling,
- BOG/reliquefaction context.

https://www.wartsila.com/marine/products/gas-solutions

## SIGTTO — ESD Systems

Used for:
- ESD philosophy,
- ship-shore link,
- pre-transfer testing context.

https://www.sigtto.org/publications/esd-systems/

## NMEA

Used for:
- NMEA 0183 public interface description,
- NMEA 2000 public interface description.

https://www.nmea.org/

## IEC 61162-460

Used for:
- secure/redundant marine navigation Ethernet context.

https://webstore.iec.ch/

## OpenPLC Runtime

Used for:
- IEC 61131-3 PLC runtime,
- Modbus integration,
- OPC UA integration.

https://github.com/Autonomy-Logic/openplc-runtime

## OpenModelica

Used for:
- dynamic physical process modelling,
- FMI export/co-simulation.

https://openmodelica.org/

## PyModbus

Used for:
- software I/O device implementing Modbus TCP.

https://pymodbus.readthedocs.io/

## Current implementation references

### OpenPLC Runtime
Current stable release used by the compose file: `v4.1.9`.

Official releases:
https://github.com/Autonomy-Logic/openplc-runtime/releases

The Runtime documentation describes the headless Editor → HTTPS API → program bundle → runtime compilation/deployment flow and its plugin system for Modbus and OPC UA.

### STruC++
Used as an independent way to compile/test Structured Text logic in CI or a developer workstation without requiring the complete PLC runtime.

https://github.com/Autonomy-Logic/STruCpp

### OpenModelica
The project uses the official `openmodelica/openmodelica:v1.27.0-minimal` image. OpenModelica documents FMI 2.0 Co-Simulation support.

https://openmodelica.org/download/docker/
https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/fmitlm.html

### FMPy
Pinned Python FMI runtime library used to load and step the Cargo FMU.

https://github.com/CATIA-Systems/FMPy

### PyModbus
The virtual Remote I/O uses PyModbus and its asynchronous server interface. The dependency is pinned so API changes do not silently alter the lab.

https://github.com/pymodbus-dev/pymodbus

## FUXA — Open-source SCADA/HMI

Used for:
- web SCADA/HMI engineering,
- OPC UA / Modbus connectivity,
- alarms, acknowledgement and alarm history,
- SVG-based operator displays.

https://github.com/frangoteam/FUXA

FUXA's current public API documents endpoints for current alarms, alarm history and acknowledgement. Its project alarm engine maintains active/acknowledged/history state.

## ISA — HMI and alarm-management public guidance

Used for design philosophy only; the project does not reproduce licensed standards or claim compliance.

- ISA101 committee / HMI scope: https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa101
- ISA-18 series overview: https://www.isa.org/standards-and-publications/isa-standards/isa-18-series-of-standards

## EEMUA 191

Used as a public alarm-management reference. Edition 4 material describes alarm-system lifecycle, alarm philosophy, alarm database and operator response topics.

https://www.eemua.org/Products/Publications/Digital/EEMUA-Publication-191.aspx


## SIGTTO — Cargo Control Room HMI

Used for the human-centred, task-based HMI design method.

https://www.sigtto.org/publications/recommendations-for-cargo-control-room-hmi/

The guidance explicitly focuses on operator needs, information/control functions, prototyping/testing and verification/validation.

## SIGTTO — Cargo Alarm Management

Used for alarm philosophy, rationalization, lifecycle and alarm-flood/nuisance-alarm concepts on gas carriers.

https://www.sigtto.org/publications/recommendations-for-management-of-cargo-alarm-systems/

## Kongsberg — AutoChief 600

Used as a public real-vessel propulsion-control reference. Current public material describes a low-speed propulsion remote-control system with control panel, engine telegraph, engine safety, processing system and optional governor/remote connection.

https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/366198-f---autochief-600-product-sheet.pdf

## Wärtsilä — UNIC engine automation

Used as a real marine engine-control reference. Public material describes start/stop management, engine safety, fuel management, speed/load control and conditions including overspeed, low lube-oil pressure and high coolant-water temperature.

https://www.wartsila.com/services-catalogue/engine-services-4-stroke/control-system-upgrades

## Wärtsilä — Main engine lubricating-oil system

Used to explain the physical lube-oil subsystem behind the propulsion permissive/safety lesson.

https://www.wartsila.com/encyclopedia/term/main-engine-lubricating-oil-system


## Zeek — offline protocol analysis

The repository uses the official Zeek Docker release image for offline PCAP analysis. Zeek includes a Modbus analyzer and `modbus.log`; the lab redefines the Modbus port set because each teaching domain uses a separate non-default TCP port.

https://hub.docker.com/r/zeek/zeek
https://docs.zeek.org/en/current/scripts/base/protocols/modbus/main.zeek.html


## Wärtsilä — Typical LNG carrier cargo handling equipment

Used to anchor the Cargo process model to a real public LNG-carrier equipment example.

The public reference for a typical 138,000 m³ LNG tanker describes four membrane cargo tanks with **two 1700 m³/h electric submerged cargo pumps per tank**. The software Cargo model collapses those eight pumps into one aggregate pump-bank model for teaching.

https://www.wartsila.com/encyclopedia/term/cargo-handling-equipment-of-a-typical-138-000m3-lng-tanker

The model does not claim the teaching pump head, efficiency or tank geometry are vendor design values.

## Wärtsilä — LNG carrier propulsion architecture references

Used to keep electrical and mechanical propulsion assumptions explicit.

Wärtsilä documents both:

- dual-fuel/electric LNG-carrier propulsion concepts, where generators feed the ship electrical system and propulsion motors,
- mechanical gas-carrier concepts where the main engine drives the propeller and auxiliary generation supplies hotel/cargo electrical loads.

https://www.wartsila.com/encyclopedia/term/df-electric-concept-also-dual-fuel-diesel-eletric-propulsion

https://www.wartsila.com/marine/products/ship-electrification-solutions/hybrid-electric-lng-carrier

https://www.wartsila.com/marine/customer-segments/merchant/small-and-medium-gas-carriers

The default integrated lab profile uses **mechanical main propulsion with electrically supplied Cargo and machinery auxiliary loads**. It does not place main shaft power on the PMS bus.

## FUXA current release / project API

The Compose file pins FUXA `1.3.4`.

Official release list:
https://github.com/frangoteam/FUXA/releases

FUXA documents a full-project REST API (`GET/POST /api/project`) and authenticated API-key/JWT access for administrative writes:
https://github.com/frangoteam/FUXA/blob/master/server/docs/openapi.yaml

The repository intentionally does not generate guessed OPC UA bindings before the OpenPLC address space is commissioned.

## SIGTTO — Cargo Control Room HMI

Used for:
- human-centred HMI design,
- task-oriented operator information,
- maintaining an operator mental model of system behaviour.

https://sigtto.org/media/3459/sigtto-2021-recommendations-for-cargo-control-room-hmi.pdf

## SIGTTO — Cargo Alarm Management

Used for:
- nuisance-alarm reduction,
- alarm flooding/chattering context,
- master alarm database / rationalization concepts,
- operator Detect → Diagnose → Respond reasoning.

https://www.sigtto.org/publications/recommendations-for-management-of-cargo-alarm-systems/

## FUXA

Used for:
- operator HMI/SCADA implementation,
- whole-project export/import workflow through the current project API.

https://github.com/frangoteam/FUXA

The course pins FUXA in Compose and treats its project JSON as engineering configuration that must be backed up and reviewed.

## asyncua

Used for:
- live OPC UA address-space discovery during commissioning.

https://pypi.org/project/asyncua/

The discovery helper records the live NodeIds, namespaces, data types, status and timestamps rather than trusting example identifiers.
## Network-fidelity architecture and tooling

### NIST SP 800-82 Rev. 3

Used for the OT segmentation principle: zones/tiers, DMZ enforcement boundaries, mapped authorized flows and policy enforcement. It does not define the lab's exact subnets.

https://csrc.nist.gov/pubs/sp/800/82/r3/final

### IACS UR E26 — Cyber resilience of ships

Used as maritime context for secure shipboard IT/OT integration across design, construction, commissioning and operation. The project does **not** claim IACS compliance.

https://iacs.org.uk/resolutions/unified-requirements/ur-e/ur-e26-new

### Containerlab

Used for the researched optional network-fidelity extension. Version **0.77.0** is the reviewed release. The `ext-container` kind is important because it can add links to containers managed by Docker Compose without owning their lifecycle.

- https://github.com/srl-labs/containerlab/releases/tag/v0.77.0
- https://containerlab.dev/manual/kinds/ext-container/
- https://containerlab.dev/rn/0.77/
- https://containerlab.dev/manual/kinds/linux/

### nftables

Used as the candidate default-deny/stateful software policy-enforcement mechanism for the routed extension. It is not labelled as a vendor industrial firewall.

https://wiki.nftables.org/wiki-nftables/index.php/Matching_connection_tracking_stateful_metainformation

### Open vSwitch

Used only as a candidate for a passive mirror/SPAN observation point when an experiment requires that property.

- https://docs.openvswitch.org/en/stable/faq/configuration/
- https://containerlab.dev/manual/kinds/ovs-bridge/

### GNS3 and EVE-NG comparison

Reviewed but not selected as reference dependencies for the current extension. GNS3 is appliance/topology oriented and explicitly does not use Docker to control real container infrastructure; EVE-NG requires users to provide legally obtained vendor images.

- https://docs.gns3.com/docs/emulators/docker-support-in-gns3
- https://www.eve-ng.net/index.php/documentation/howtos/

