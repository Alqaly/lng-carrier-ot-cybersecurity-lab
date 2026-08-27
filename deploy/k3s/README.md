# Optional k3s Research Deployment

The reference deployment remains **Docker Compose v2 + systemd** on one Linux server.

Use k3s only when Kubernetes itself is part of the research question: multi-node resilience, NetworkPolicy, orchestration recovery, CNI observability or distributed scheduling.

## Why no default Kubernetes manifests?

Blindly translating the Compose file would weaken the experiment by changing network identity/capture semantics without validating them. The core testbed depends on:

- fixed control-plane identities,
- protocol attribution,
- namespace-level capture,
- deterministic service topology.

A k3s port must define and test equivalent ground truth before it is accepted.

## Acceptance criteria for a future k3s profile

1. Each PLC→I/O conduit has stable evidence identity.
2. NetworkPolicy is deny-by-default with explicit operational conduits.
3. Packet capture can attribute the original pod/workload endpoint.
4. Persistent data survives pod rescheduling.
5. All seven registered experiments produce equivalent event ordering/metrics within documented tolerance.
6. `research_gate.py` and a dedicated k3s integration suite pass.

Do not deploy Kubernetes merely because it is more fashionable than Compose.
