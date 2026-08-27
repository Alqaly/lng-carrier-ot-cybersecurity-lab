# Network Fidelity Extension

This directory is intentionally **not** a second runtime stack.

The canonical lab remains Docker Compose + systemd. Network-fidelity work is governed by `fidelity-contract.json` and the architecture decision in `docs/03-architecture/network-fidelity-decision.md`.

## Current status

`design_accepted_runtime_unvalidated`

No active Containerlab topology or nftables ruleset is published as production-ready yet because this build environment cannot execute the Docker/server acceptance sequence.

## First target-server vertical slice

1. Start and commission the canonical Compose baseline.
2. Preserve baseline PCAP/state evidence.
3. Attach one explicit extension dataplane interface to one Compose-owned service.
4. Route that test path through one Linux policy-enforcement node.
5. Install one explicit allow rule derived from `security/conduits.json`; keep default deny for everything else.
6. Prove the allowed path with PCAP and policy counters.
7. Prove an undeclared path is denied.
8. Restart the selected Compose service.
9. Reconcile the extension and prove the original interface/path identity returns.
10. Preserve the run as evidence before expanding the topology.

Do not expand to full DMZ/vendor/OT segmentation until this vertical slice survives restart and failure/recovery testing.
