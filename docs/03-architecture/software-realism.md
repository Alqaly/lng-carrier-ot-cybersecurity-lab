# Software Realism — What the Testbed Reproduces

This is a software-defined cyber-physical testbed.

That phrase is more accurate than calling the whole environment a single emulator.

## The process is simulated

OpenModelica/FMI calculates dynamic process state from equations.

Examples:
- tank level changes from conservation of volume,
- pressure follows the modelled liquid head,
- flow depends on pump/valve state and source head.

## The controller runtime is implemented

OpenPLC Runtime executes IEC 61131-3 control logic with scan-cycle semantics.

## The protocol is implemented

Modbus TCP packets are real protocol messages exchanged between software endpoints.

OPC UA is served by the PLC runtime and consumed by a real OPC UA client/collector.

## The I/O device is emulated

The virtual Remote I/O has a defined Modbus data model and translates the process-model state into a controller-facing I/O image.

## Navigation without hardware uses replay

Recorded NMEA 0183 streams can be replayed through GPSD tooling. Replay preserves real captured sentence data but is not a live GNSS sensor.

## Marine equipment remains a reference unless it has its own executable model

The project does not invent generator frequency, engine RPM, gas concentration or certified ship/shore-link state merely to fill a dashboard.

A subsystem enters the executable lab only when its behavior has:

1. an explicit state model,
2. defined control/measurement interfaces,
3. protocol mapping,
4. verification criteria,
5. documented limitations.


## Cross-system coupling is modelled, not painted onto dashboards

The Vessel Coordinator links selected model outputs to selected model inputs.

For the default profile:

```text
Cargo pump electrical demand → PMS load
PMS bus / Cargo shed state → Cargo power availability
Propulsion auxiliary electrical demand → PMS load
PMS bus → pre-lube auxiliary availability
```

The coupling is deliberately architecture-specific and is described in `vessel/profile.json`.
