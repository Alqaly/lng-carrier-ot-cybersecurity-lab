# Software-Defined Testbed

Because hardware is optional, the executable environment uses a high-fidelity software approach.

## Layer 1 — Process physics

OpenModelica compiles a dynamic Cargo transfer model to an FMI Co-Simulation FMU.

The model calculates:

- source tank level,
- destination tank level,
- flow,
- hydrostatic pressure,
- valve/pump effect.

## Layer 2 — I/O device

A Modbus TCP service represents a remote-I/O station.

It exposes:

- process measurements as input registers,
- equipment feedback as discrete inputs,
- pump/valve commands as coils.

The values come from the process model.

## Layer 3 — PLC

OpenPLC Runtime executes IEC 61131-3 control logic.

## Layer 4 — Information integration

OpenPLC's OPC UA server exposes process/controller variables.

## Layer 5 — Historian

Telegraf reads OPC UA and writes to InfluxDB.

## Layer 6 — Visualization

Grafana renders current and historical trends.

## Layer 7 — Security evidence

Packet capture is performed on the controller/I/O and OPC-UA conduits.

## Data provenance

Every value should have an entry in `docs/08-reference/data-provenance.md`.
