# Backup and Recovery

An always-on research lab must be recoverable, not merely restartable.

## Cold reference backup

```bash
./labctl backup
```

The reference backup quiesces the Compose stack before exporting persistent Docker volumes, captures repository/configuration without `.env`, creates `SHA256SUMS`, then restores the prior running state. The secret file is intentionally excluded and must be recovered through a separate secret-management process.

Preserved runtime state includes FMUs, three OpenPLC data volumes, alarm data and InfluxDB state. Retained PCAPs/experiment evidence should be archived separately according to the study protocol.

## Guarded restore

```bash
./labctl restore backups/<timestamp> --yes
# only when intentionally replacing non-empty runtime state:
./labctl restore backups/<timestamp> --yes --force
```

Restore verifies every SHA-256 entry before touching runtime state and refuses to overwrite non-empty volumes unless `--force` is explicit. A successful file restore is **not** a recovery PASS.

## Recovery acceptance

On a clean target server, repeat Gates A–G from the Server Acceptance Test, then rerun at least one Cargo baseline and one cross-system experiment. Preserve restoration time, Git commit, backup checksum manifest, runtime evidence and any drift.
