# 04 — Architecture: Zones, Conduits and Ground Truth

## Why this matters

A lab cannot evaluate “unexpected traffic” unless expected traffic is defined first.

## Visual tour

Compare:

- K-Chief distributed automation: https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/k-chief-600-marine-automation-system/
- Lee (2024) Figure 10, LNGC PMS-HIL network: https://www.mdpi.com/2077-1312/12/7/1236

## Memory hook

```text
ZONE = who belongs together
CONDUIT = who has a justified reason to talk
GROUND TRUTH = exactly which path is expected
```

## Reference control conduits

The single-server reference topology fixes identities so evidence is reproducible:

```text
Cargo PLC       → Cargo I/O        TCP/5020
PMS PLC         → PMS I/O          TCP/5021
Propulsion PLC  → Propulsion I/O   TCP/5022
```

The security policy in `security/conduits.json` is machine-readable and tested against Compose addressing.

## Why Docker Compose is the default

The project is designed to run continuously on one server. Docker Compose v2 + systemd keeps:

- fixed test identities,
- simple namespace-level captures,
- deterministic startup/recovery,
- lower orchestration noise.

k3s/Kubernetes is optional when the research question is Kubernetes itself.

## Worked example — unexpected Modbus source

Expected:

```text
172.28.20.10 → 172.28.20.20:5020
```

Observed:

```text
172.28.20.99 → 172.28.20.20:5020
```

The question is no longer “does this look suspicious?” The classifier compares observed evidence against declared ground truth.

## Lab action

```bash
./labctl config-check
./labctl capture cargo modbus
./labctl zeek cargo
```

Then use `security/conduit_classifier.py` on the generated Zeek connection evidence.

## Explain it in 60 seconds

Why does stable identity matter to an experiment about unexpected control sources?

## Go deeper

- [System design](../03-architecture/system-design.md)
- [Deployment decision](../03-architecture/deployment-decision.md)
- [Technology selection](../08-reference/technology-selection.md)
