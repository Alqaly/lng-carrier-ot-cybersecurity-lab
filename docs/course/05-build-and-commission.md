# 05 — Build and Commission the Lab Like an Engineer

## Why this matters

Starting containers is deployment. **Commissioning** proves that interfaces mean what you think they mean.

## Visual tour — test object vs simulator

Use Lee (2024) Figure 9, the integrated LNGC PMS-HIL test bed: https://www.mdpi.com/2077-1312/12/7/1236

**Notice:** the target PMS/MSBD and the simulation/control side are distinct. That separation is the mindset we preserve in software.

## Memory hook

```text
MODEL FIRST → I/O SECOND → PLC THIRD → SUPERVISION FOURTH
```

Do not debug all four at once.

## Lab action — staged commissioning

New to the repository? Complete [safe first run](../04-build/first-run.md) first.
It includes cloning, prerequisites, credentials, expected pages and troubleshooting.
For one guided learning session, use the [first Cargo investigation](../06-scenarios/first-cargo-investigation.md).
For retained acceptance, the orchestrator below already runs the build/demo stages;
the later phases explain those layers rather than requiring a duplicate run.

### Phase 1 — server

```bash
./labctl commission start
```

This freezes source provenance, preserves logs and executes the server plus pre-PLC gates as one resumable acceptance run.

### Phase 2 — prove model + I/O before PLC

```bash
./labctl build
./labctl demo pms
./labctl demo cargo
./labctl demo propulsion
```

These commissioning demos intentionally drive the software I/O directly. They answer: *does process + I/O + Modbus work before PLC logic is introduced?*

Then prove that the propulsion cooling alarm is physically reachable rather
than merely declared in code:

```bash
./labctl demo propulsion-cooling
```

The command fails if the deterministic temperature threshold is not reached and
saves a named pre-PLC timeline. It does not claim the PLC protective shutdown;
that requires the later commissioned experiment.

### Phase 3 — commission OpenPLC

For each domain:

1. import/use the Structured Text,
2. configure the documented Modbus remote I/O endpoint,
3. map symbols to the register/data contract,
4. deploy to the correct runtime,
5. verify online values.

### Phase 4 — OPC UA binding gate

```bash
./labctl commission resume evidence/commissioning/<run>
```

After the required live PLC evidence is recorded, `resume` performs run-scoped discovery, binding and historian freshness checks for all three domains. The historian is not allowed to trust guessed NodeIds.

### Phase 5 — HMI

```bash
./labctl fuxa bootstrap
# bind verified OPC UA tags
./labctl fuxa export
./labctl fuxa validate
```

### Phase 6 — daemon

```bash
sudo ./deploy/install-systemd.sh
systemctl status lng-ot-lab
```

Retain the reboot, restore and resource evidence, then require:

```bash
./labctl commission finalize evidence/commissioning/<run>
```

## What you should see

If a layer fails, stop and fix it. Do not hide the gap with substitute data.

## Explain it in 60 seconds

Why is pre-PLC commissioning useful, and why does it *not* prove the final control loop yet?

## Go deeper

- [Full walkthrough](../04-build/software-lab-walkthrough.md)
- [Commissioning orchestrator](../04-build/commissioning-orchestrator.md)
- [OpenPLC commissioning](../04-build/openplc-editor-commissioning.md)
- [OPC UA commissioning](../04-build/opcua-commissioning.md)
- [Server daemon](../04-build/server-daemon-deployment.md)
