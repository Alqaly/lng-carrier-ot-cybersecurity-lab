# Canonical Reconciliation — 27 August 2026

## Why this pass was required

The canonical Notion handoff described a newer post-audit state than the latest packaged release. The package still passed its own gates, but those gates reported 46 tests and several documented runtime-evidence commands were absent from `labctl`. That meant repository, release manifest and Notion were not yet one reproducible state.

## Drift found and repaired

- Restored the documented **49-test** static contract by adding three runtime-evidence contract tests and executing all 49 tests.
- Added `./labctl observe` with explicit timestamp provenance: process/vessel state uses observer receive time while preserving source clocks; alarm transitions preserve the alarm-engine source timestamp.
- Added `./labctl conduit-check` against `security/conduits.json`.
- Extended Cargo process residual analysis to accept observer JSONL as well as CSV.
- Added `./labctl hist-fresh` with evidence output and project `.env` loading.
- Added `./labctl opcua-outage <domain> start|restore`, which isolates only the OpenPLC operations network and refuses to proceed if the fixed control conduit is already absent.
- Added `timestamp = "source"` to generated Telegraf OPC UA bindings so commissioned historian data preserves OPC UA source timestamps.
- Corrected documented Modbus conduit identities to Cargo `172.28.20.10 → 172.28.20.20`, PMS `172.28.40.10 → 172.28.40.20`, Propulsion `172.28.60.10 → 172.28.60.20`.
- Corrected the blocked-flow experiment identifier to `EXP-CARGO-BLOCKED-FLOW`.
- Updated InfluxDB OSS from 2.7.12 to reviewed 2.9.1 after upstream release/Docker verification; documented the 2.9 token-hashing migration implication.

## Validation executed after repair

```text
pytest                         49 passed
plant ↔ I/O traceability      PASS
generated I/O drift check     PASS
quality gate                   PASS
deep review                    PASS
research/publication gate      PASS
pedagogy gate                  PASS
release gate                   PASS
```

## Runtime boundary

This reconciliation does **not** claim Docker/OpenPLC/OPC UA/FUXA/Influx runtime commissioning. Gates A–G in `docs/04-build/server-acceptance-test.md` still require a Docker-capable target server and retained runtime evidence.

## Next decision boundary

The network-fidelity design decision is now complete but remains runtime-unvalidated. The next network step is **not** a full topology build: after canonical Gates A–G pass on the target server, execute one minimal Containerlab + Linux routing + nftables vertical slice and collect NF-A–NF-G evidence before expanding to DMZ/vendor/full-OT routing.

## 61-test hardening checkpoint

After the 49-test reconciliation, the recursive audit found three publication/runtime-quality gaps: evidence evaluation could be satisfied by metadata booleans, secrets had runnable placeholder fallbacks, and backup lacked a guarded restore contract. The current checkpoint adds artifact SHA-256 verification and semantic experiment checks, fail-closed secret handling, cold backup/guarded restore, explicit readiness levels, evidence-based resource profiling, and GitHub supply-chain controls. The current static suite collects and passes **61 tests**; runtime Docker acceptance remains pending the target server.
