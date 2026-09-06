# Release Readiness

This repository is a **release candidate for target-server commissioning**.

The [evidence-first upgrade audit](docs/09-research/upgrade-audit-2026-09-05.md)
records the learning journey, verification repairs, evidence compatibility and
standalone course delivery. A course-container healthcheck is not OT acceptance.

## What has been validated in the current build environment

- Python/test source imports and syntax
- Docker Compose / production override YAML parsing
- GitHub Actions workflow YAML parsing
- MkDocs navigation YAML parsing
- process ↔ I/O ↔ PLC mapping traceability
- alarm-to-domain contract resolution
- generated I/O documentation consistency
- research experiment contracts
- Chapters 01–10 pedagogy contract
- Chapters 01–10 real visual-source manifest
- local Markdown links / documentation structure
- dependency pin policy / no `latest` runtime images
- deployment script shell syntax
- deterministic fault presence and alarm reachability contracts
- control-vs-supervisory path separation contracts
- normalized runtime observer timestamp/provenance contract
- expected-conduit, process-residual and historian-freshness evidence helpers
- supervisory-only OPC UA operations-network outage/restore contract
- machine-readable project scope, vessel coverage and architecture boundaries
- data-semantics, timebase, image-provenance and detection-claim contracts
- repeated-run aggregation that preserves unavailable metrics
- checksum-indexed Gates A–G acceptance dossier tooling
- resumable commissioning orchestration with commit pinning, run-scoped outputs and hashed manual evidence

## What is intentionally NOT claimed yet

This build environment has no Docker daemon and cannot execute the integrated Compose stack. Therefore this document does **not** claim:

- all containers started successfully together,
- FMUs compiled on the target image,
- three OpenPLC projects were deployed,
- live OPC UA NodeIds were discovered,
- historian values were ingested,
- FUXA was bound to live tags,
- target-server reboot persistence was proven,
- all seven experiments produced runtime evidence,
- backup restore was demonstrated on a clean host.

Those claims become valid only after `docs/04-build/server-acceptance-test.md` Gates A–G pass on the target server.

## First target-server sequence

```bash
./labctl setup
./labctl commission start
```

Preserve the printed run directory and use `./labctl commission resume <run-dir>`. The orchestrator completes the automatable gates and prints the exact evidence labels required for OpenPLC, HMI, reboot and restore checkpoints. It refuses source drift, dirty runs, unverified experiment indexes and evidence hash mismatches.

After full commissioning:

```bash
./labctl runtime-verify
sudo ./deploy/install-systemd.sh
```

Finally run all experiments, preserve their required evidence, reboot-test the daemon and perform a restore test.

Gate F aggregates comparable repetitions from the same clean commit. Finish with `./labctl commission finalize <run-dir>`. Neither the orchestrator nor the dossier builder converts missing evidence into a pass.

Only after the canonical runtime is healthy should the optional network-fidelity vertical slice be attempted; its NF-A–NF-G evidence is separate from the base Gates A–G.

## Publication rule

Do not change this document to “fully tested” based on screenshots or service startup alone. Publication acceptance requires traceable process/protocol/controller/operator evidence.

The repository may be published as a **release candidate for target-server commissioning** after its static CI gate passes. It must not be announced as a fully commissioned or experimentally validated platform until the retained dossier passes.
