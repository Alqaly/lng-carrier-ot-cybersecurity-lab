# Deployment Decision — Always-on Single-Server Lab

## Decision

The reference deployment is **Docker Compose v2 managed by systemd on one Linux server**.

Kubernetes/k3s is an optional scale-out exercise, not the default runtime.

## Why

The lab is not a stateless web application. It intentionally teaches fixed OT conduits, protocol captures, stable source/destination identities, service-side network namespaces and reproducible failure injection. A single-host Compose topology preserves those properties with less infrastructure noise.

Docker's production guidance explicitly supports Compose on a single server and recommends production overrides plus restart policies. K3s is a strong lightweight Kubernetes distribution for edge/homelab/IoT use, but a CNI/overlay network adds an additional networking abstraction that is unnecessary for the reference experiment and makes packet attribution harder.

## When to choose k3s

Use k3s when the research question is itself about:

- orchestration resilience,
- multi-node scheduling,
- Kubernetes NetworkPolicy,
- container runtime isolation,
- distributed observability.

Do not migrate merely to make the architecture look more sophisticated.

## Daemon operation

```bash
cp .env.example .env
# change every credential/token
sudo ./deploy/install-systemd.sh
```

Then:

```bash
systemctl status lng-ot-lab
journalctl -u lng-ot-lab -f
```

## Upgrade policy

Dependencies are pinned. Upgrade only after:

1. checking upstream release/security notes,
2. updating `DEPENDENCIES.md`,
3. running the entire static test suite,
4. running a Docker commissioning suite on a test server,
5. comparing baseline PCAP/state behavior.
