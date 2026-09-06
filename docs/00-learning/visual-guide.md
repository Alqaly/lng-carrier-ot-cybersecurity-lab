# Visual guide: process, signal, packet

Start with one question: **a pump says it is running, but the cargo flow is zero.
What observation would separate a blocked pipe from a bad flow measurement?**
You do not need Docker for this guide. The illustrations are original teaching
material based on the repository's model and I/O mapping. They are not captured runtime results.

## 1. Understand what is moving

![Cargo liquid path, electrical power dependency and independent command/feedback signals](../assets/visuals/cargo-system.svg)

Read the solid path from the ship inventory through the pump and valve to the
receiving boundary. During unloading, the source level should fall and the
receiving level should rise. The electrical supply above the path is necessary
for pump operation. The blue signal paths represent control information, not liquid.

The lab represents a pump bank and aggregate inventories. It does not reproduce
all ship piping, cryogenic thermodynamics or terminal equipment. The shore receiver
is a mass-balance proxy; it is not another onboard cargo tank.

**Predict:** if the flow transmitter alone develops a positive bias, should the
actual liquid transfer increase? No. A measurement fault changes what the control
system sees; it does not by itself supply more pump power or open a valve.

## 2. Follow a number through the layers

![Flow signal conversion and publication through model, input register, PLC and OPC UA](../assets/visuals/flow-signal.svg)

Here, 0.5 and 1800 represent the same flow in different units. The model uses m³/s;
the Cargo register stores whole m³/h. Multiplying by 3600 again in the PLC would
create an error. The PLC source intentionally converts the integer type without
another unit conversion.

Read the [full signals lesson](../02-ot-foundations/signals-and-io.md) for digital
I/O, analog scaling, quantization and Modbus address spaces.

## 3. Read the protocol representation

![Constructed Modbus request and response for reading Cargo input register two](../assets/visuals/modbus-flow-read.svg)

These bytes are a constructed example. Your capture may read several registers
in one transaction and use a different transaction identifier. Locate the
requested start address and count before deciding which returned value is flow.

Modbus does not encode the words “Cargo flow in m³/h” in that response. You obtain
the meaning from the [generated I/O map](../08-reference/generated-io-map.md).
An address without its object type is incomplete: input register 2 and holding
register 2 are different objects.

## 4. Make an investigation decision

| Observation after transients settle | What it suggests | What to check next |
|---|---|---|
| Command ON, pump feedback OFF, no flow | Actuation, supply or feedback problem | PMS supply, pump speed and injected equipment fault |
| Pump feedback ON, valve open, measured flow low | Hydraulic path problem or misleading measurement | Actual model flow and tank-level movement |
| Measured flow rises without matching actual flow or level-rate change | Measurement-path bias is a candidate | Compare `flow` with `flowMeasured` and the register encoding |
| PLC value is stale while model time advances | A communication/publication problem is a candidate | Modbus transactions, OPC UA Quality and timestamps |

These are hypotheses, not automatic diagnoses. In a real installation you do not
have a perfect `flow` truth API. The teaching model provides that comparison so
you can understand why independent measurements matter.

## Try it and explain it

Use [safe first run](../04-build/first-run.md), then the
[first Cargo investigation](../06-scenarios/first-cargo-investigation.md).
Before running a fault, write your prediction for command, feedback, actual flow
and measured flow. Afterward, explain which observation changed your diagnosis.

The next course chapter is [OT foundations](../course/03-ot-foundations.md).
For real hardware context, inspect the HIL simulator/target separation in
[Lee's LNG-carrier PMS study](https://www.mdpi.com/2077-1312/12/7/1236).
That external testbed includes physical equipment; our diagrams describe this software lab.
