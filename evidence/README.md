# Evidence

Create one directory per exercise.

Recommended structure:

```text
evidence/
  2026-08-26-cargo-normal-transfer/
    notes.md
    modbus.pcap
    opcua.pcap
    openplc.log
    io.log
    plant.log
    alarm-history.json
    grafana.png
```

For every investigation, annotate the sequence:

```text
operator/controller intent
→ protocol evidence
→ I/O state
→ process response
→ alarm/event state
→ historian timeline
```

Do not commit packet captures or logs containing sensitive real-world information.

## Target-server acceptance runs

Use the resumable orchestrator rather than assembling Gates A–G filenames manually:

```bash
./labctl commission start
./labctl commission status evidence/commissioning/<run>
./labctl commission resume evidence/commissioning/<run>
./labctl commission finalize evidence/commissioning/<run>
```

Each commissioning run snapshots the clean Git commit/tree and the governing contracts. Automatic outputs are written into that run. Live PLC/HMI/reboot/restore evidence is accepted only through `commission record`, which copies the files into `attachments/` and records their SHA-256 hashes. `acceptance-dossier.json` is written only by finalization and remains failed while any required artifact, semantic PASS, commit binding or retained hash is missing.

See `docs/04-build/commissioning-orchestrator.md` for the complete target-machine sequence.
