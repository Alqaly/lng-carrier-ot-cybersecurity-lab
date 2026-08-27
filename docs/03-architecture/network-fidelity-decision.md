# Network Fidelity Decision — Preserve the Baseline, Add an Auditable Dataplane Extension

## Decision

The canonical runtime remains **Docker Compose v2 + systemd**.

The next network-fidelity phase is an **optional extension**, not a replacement runtime:

- **Containerlab 0.77.0** for explicit veth/link topology when Docker bridge membership is no longer enough to teach the path;
- **Linux kernel static routing** for routed zones;
- **nftables** for default-deny, stateful conduit enforcement;
- **Open vSwitch mirroring** only if an experiment genuinely requires a passive SPAN/TAP-style observation point;
- **FRRouting is not selected** unless dynamic routing itself becomes a documented learning/research objective.

This decision is encoded in `network/fidelity-contract.json` and is **runtime-unvalidated** until the NF-A through NF-G acceptance gates are executed on the target server.

## Why change anything?

The current Compose topology gives the project deterministic endpoint identities, isolated Docker bridges, protocol captures and stable cross-layer experiments. It does **not** prove a real routed/default-deny path between OT zones. Docker network membership is useful segmentation for a software lab, but it is not the same thing as forcing an inter-zone flow through a policy-enforcement point.

The fidelity gap is therefore specific:

> preserve the existing process/control experiment ground truth while making selected inter-zone paths explicit, routable, deny-by-default, observable and recoverable.

NIST SP 800-82 Rev. 3 describes segmentation using levels/tiers/zones, the use of DMZs as enforcement boundaries, and policy engines that permit only mapped/authorized communications. That supports the **architecture principle**, not the exact lab subnet or firewall implementation.

IACS UR E26 is also relevant maritime context because it targets secure integration of shipboard IT and OT across design, construction, commissioning and operation. The lab uses that as a design motivation only. **Nothing in this extension is an IACS compliance claim.**

## Why Containerlab, but only as an extension?

Containerlab fits one requirement unusually well: its `ext-container` kind can attach links to containers that are created and owned by another orchestrator. That means Compose can remain responsible for OpenPLC, I/O, process, historian and HMI lifecycle while Containerlab is used only to add explicit dataplane interfaces.

Containerlab 0.77 also introduced `apply`, which can reconcile supported topology changes against a running lab instead of always destroying and redeploying it.

That does **not** make Containerlab the daemon baseline. Additional interfaces are tied to container/network-namespace lifetime. Containerlab's own Linux-container documentation warns that non-`eth0` interfaces can be lost when a container restarts. A 24/7 research platform therefore must prove restart reconciliation before this extension is accepted.

This is exactly why the project keeps the existing Compose mode independently runnable.

## Why not GNS3 as the reference extension?

GNS3 is valuable when the learning target is an emulated network appliance or a topology built around QEMU/VM/network nodes. Its own Docker documentation explains that Docker containers are treated as lightweight virtual machines and that GNS3 is **not designed to control real container infrastructure**.

That is a poor fit for a project whose executable OT system already exists as a Compose application and whose experiment evidence depends on those exact containers.

GNS3 remains useful later if a specific network appliance or vendor behavior becomes the object of study.

## Why not EVE-NG as the reference extension?

EVE-NG is similarly useful for appliance-centric network labs. Its documentation explicitly states that it does not provide copyrighted vendor images; users must prepare their own legally obtained images.

The core LNG lab is intended to be reproducible from public/open components. Requiring vendor firewall/router images would add a licensing and distribution burden without solving a current research requirement.

EVE-NG can still be an optional **vendor-appliance comparison environment** when the user has a lawful image and the experiment asks a vendor-specific question.

## Policy enforcement: nftables, not a fake "industrial firewall"

The first enforcement implementation should use Linux **nftables** because the question we need to answer is simple and testable:

> Did a declared flow pass, and did an undeclared flow fail, at the intended boundary?

nftables supports stateful filtering through connection tracking and default-drop policies. It lets the lab implement policy semantics without pretending a generic Linux node is a FortiGate, Hirschmann, Tofino, Cisco Secure Firewall or another industrial appliance.

The published label must therefore be **software policy-enforcement point** or **nftables firewall**, not "industrial firewall" unless a real vendor appliance is actually under test.

## Routing: keep it boring until routing is the lesson

Static Linux routing is enough for the first routed-zone experiments. Adding BGP, OSPF or FRR merely to make the topology look advanced would add failure modes and configuration state without improving the Cargo/PMS/propulsion security experiments.

FRR becomes justified only when a research question requires, for example:

- route convergence/failure;
- dynamic path changes;
- routing-protocol attack/detection;
- redundant routed-path behavior.

Until then, **no FRR**.

## Passive monitoring: do not add OVS just because SPAN sounds realistic

The current lab can capture at known network namespaces/interfaces. That is already strong evidence for many experiments.

If a future experiment requires a sensor that is demonstrably passive and receives mirrored traffic from another path, Open vSwitch is the preferred candidate because its official configuration supports a mirror/SPAN output port. Containerlab can connect nodes to a pre-created OVS bridge.

However OVS becomes another stateful host component. It is therefore admitted only when the experiment requires this property:

> the monitoring sensor must observe a copy of traffic without being an inline forwarding dependency.

Until that requirement is exercised, namespace/interface capture remains the simpler baseline.

## Architecture boundary

```text
CANONICAL MODE
Compose + systemd
  ├─ process / I/O / PLC / OPC UA / historian / HMI
  ├─ deterministic Docker-network identities
  └─ existing packet/evidence tooling

OPTIONAL NETWORK-FIDELITY MODE
Compose still owns the OT services
  + Containerlab adds explicit dataplane links
  + Linux routing forces selected inter-zone paths
  + nftables enforces declared conduits
  + optional OVS mirror feeds a passive sensor
```

The extension is allowed to add **links and enforcement**, not to create a second authoritative inventory of PLC/I/O IP addresses. `docker-compose.yml` and `security/conduits.json` remain the current endpoint/conduit ground truth.

## Acceptance is evidence, not topology rendering

A topology screenshot is not a PASS. The extension is accepted only when NF-A through NF-G in `network/fidelity-contract.json` are tested on a Docker-capable target server.

Minimum evidence includes:

1. baseline still passes without the extension;
2. exact interface/link inventory after attachment;
3. allowed-flow packet capture;
4. denied-flow policy log/counter evidence;
5. expected Modbus and OPC UA path evidence;
6. service-restart reconciliation evidence;
7. gateway/policy failure and recovery evidence;
8. if enabled, proof that the mirrored sensor is passive rather than inline.

## What is deliberately not implemented yet

This repository does **not** yet ship an active Containerlab topology or nftables ruleset as part of the reference daemon. We have no Docker-capable target in the current build environment, so adding a topology that has never been attached, restarted and failure-tested would create false confidence.

The next implementation step on the target server is a minimal vertical slice:

```text
one existing Compose service
→ one explicit extension interface
→ one routed boundary
→ one allowed conduit
→ one denied control flow
→ PCAP + nftables evidence
→ restart the service
→ reconcile
→ repeat the evidence check
```

Only after that vertical slice passes should the pattern be expanded to the full DMZ/vendor/OT topology.

## Sources reviewed for this decision

- NIST SP 800-82 Rev. 3, *Guide to Operational Technology (OT) Security*: https://csrc.nist.gov/pubs/sp/800/82/r3/final
- IACS UR E26, *Cyber resilience of ships*: https://iacs.org.uk/resolutions/unified-requirements/ur-e/ur-e26-new
- Containerlab external-container kind: https://containerlab.dev/manual/kinds/ext-container/
- Containerlab 0.77 release / `apply`: https://containerlab.dev/rn/0.77/
- Containerlab Linux-container behavior: https://containerlab.dev/manual/kinds/linux/
- GNS3 Docker support: https://docs.gns3.com/docs/emulators/docker-support-in-gns3
- EVE-NG image-loading guidance: https://www.eve-ng.net/index.php/documentation/howtos/
- nftables stateful filtering: https://wiki.nftables.org/wiki-nftables/index.php/Matching_connection_tracking_stateful_metainformation
- Open vSwitch SPAN/mirroring: https://docs.openvswitch.org/en/stable/faq/configuration/
- Containerlab OVS bridge kind: https://containerlab.dev/manual/kinds/ovs-bridge/
