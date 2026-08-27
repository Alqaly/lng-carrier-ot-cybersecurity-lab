# Pre-PLC Commissioning

Before configuring OpenPLC, prove that each process model and Modbus I/O endpoint behaves causally.

This is the software equivalent of commissioning field I/O before trusting a controller program.

## Important boundary

The commissioning client writes directly to the software I/O endpoint:

```text
commissioning client
→ Modbus TCP
→ software remote I/O
→ physics model
```

It deliberately bypasses OpenPLC.

Use this only to verify the process, I/O contract and protocol path. Final end-to-end exercises must use the PLC.

## Cargo

Terminal 1:

```bash
./labctl build
./labctl capture cargo modbus
```

Terminal 2:

```bash
./labctl demo cargo
```

Observe valve travel, pump run-up, measured-flow response, source-level fall and destination-level rise.

## Power Management

```bash
./labctl demo pms
```

Observe Generator 1 run-up, first breaker connection, load steps, reserve reduction, Generator 2 run-up, sync permissive and second breaker connection.

## Propulsion

```bash
./labctl demo propulsion
```

Observe pre-lube pressure, engine enable, RPM acceleration, shaft loading, coolant response and vessel-speed response.

## Why this step exists

If the process/I/O behavior is wrong, debugging the PLC first wastes time.

The engineering sequence is:

```text
process model
→ I/O mapping
→ protocol
→ PLC
→ HMI/historian
→ alarms
```
