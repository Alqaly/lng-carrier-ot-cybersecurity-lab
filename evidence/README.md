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
