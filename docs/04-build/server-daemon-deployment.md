# Server Daemon Deployment

The reference target is a Linux server that runs the lab continuously under systemd.

## 1. Server prerequisites

- modern x86-64/ARM64 Linux,
- Docker Engine,
- Docker Compose v2,
- enough RAM for the commissioned stack; **no fixed RAM requirement is published before target-server measurement**,
- enough disk for images, retained evidence and at least one tested backup; measure actual usage on the target server,
- NTP/chrony synchronized host time.

## 2. Configure secrets

```bash
cp .env.example .env
```

Replace every placeholder, then `chmod 600 .env`. The preflight and systemd installer fail closed when secrets are missing, placeholder-valued or too broadly readable. Never publish `.env`.

## 3. Validate before daemon install

```bash
./labctl commission start
```

Keep the printed commissioning run directory. `commission start` runs the prerequisite, static and pre-PLC layers while preserving logs and source provenance. Use `./labctl commission resume <run-dir>` after the live PLC/HMI steps.

## 4. Install service

```bash
sudo ./deploy/install-systemd.sh
```

## 5. Verify

```bash
systemctl status lng-ot-lab
./labctl status
journalctl -u lng-ot-lab -f
```

## Remote access

The default Compose ports bind to `127.0.0.1`. Keep them that way on an Internet-accessible server. Use SSH port forwarding or a hardened authenticated reverse proxy/VPN rather than exposing OpenPLC/FUXA/InfluxDB directly.

Example:

```bash
ssh -L 8500:127.0.0.1:8500 -L 3000:127.0.0.1:3000 user@server
```

## Resource sizing evidence

Do not turn a laptop/server guess into a published requirement. After commissioning, collect steady-state and representative experiment evidence:

```bash
./labctl profile-resources --samples 24 --interval 5
```

The profiler records Docker CPU/memory/network/block-I/O/PID observations with the Git commit and release-manifest hash. It deliberately does **not** synthesize limits. Resource limits are admitted only after repeated baseline and experiment measurements on the target server.

Inside a Gates A–G run, use `./labctl commission run <run-dir> --gate G --samples 24 --interval 5` so the resource data is retained and indexed by the final dossier.

## Readiness levels

`config/readiness-contract.json` separates **process alive → reachable → commissioned → semantic ready**. A green container or open TCP port is never used as proof that PLC logic, OPC UA identities, historian timestamps, or operator semantics are correct.
