# Modbus TCP

## Visual tour

Open the Modbus Organization specifications while reading this chapter: https://www.modbus.org/modbus-specifications

Then capture a transaction from this lab and decode it in Wireshark. The actual packet is the primary visual: Ethernet → IP → TCP → MBAP → function → address → data → process meaning.

Official specifications are published by the Modbus Organization.

## What Modbus solves

It gives clients and servers a simple data model for:

- coils,
- discrete inputs,
- input registers,
- holding registers.

## Modbus TCP structure

```text
Ethernet
  ↓
IP
  ↓
TCP
  ↓
MBAP header
  ↓
Function code + data
```

## MBAP header

Contains:
- Transaction Identifier
- Protocol Identifier
- Length
- Unit Identifier

## Functions used in the lab

- FC01 — Read Coils
- FC02 — Read Discrete Inputs
- FC03 — Read Holding Registers
- FC04 — Read Input Registers
- FC05 — Write Single Coil
- FC06 — Write Single Register

## Why the device map matters

Address `0` has no universal meaning.

In our virtual I/O device:

```text
Input Register 0 = source level
```

because **we define and document that I/O map**.

On a real device, the manufacturer manual is the source of truth.

## Wireshark walkthrough

Capture:

```bash
tcpdump -nn -s0 -w evidence/modbus.pcap tcp port 5020
```

Open in Wireshark:

```text
modbus
```

Correlate one write and one read with the process model.

## Worked example — read Cargo flow

In this lab, Cargo Input Register 2 represents the lagged measured transfer flow. The I/O configuration defines the raw scaling.

The reader should trace:

```text
Modelica flowMeasured
→ Cargo I/O Input Register 2
→ Modbus FC04 response
→ OpenPLC AI_Flow_m3h
→ Flow_m3h engineering value
→ OPC UA/HMI/historian
```

Capture the packet, locate function code 04 and the returned register bytes, then compare the decoded value with `curl http://127.0.0.1:8100/state`.

## 60-second explain-back

Explain why `Input Register 2` means Cargo flow **only in this I/O contract**, not in Modbus generally.

## Remember it

**Modbus carries an operation on a data object; the device map gives it physical meaning.**

## Explain it in 60 seconds

Explain one captured FC04 response from Ethernet through the register value to the process variable.
