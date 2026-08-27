# 07 — Protocol Academy: Message to Process Consequence

## Why this matters

A protocol is not a port number. You should be able to point to a captured message and explain what it means operationally.

## Memory hook

```text
WHERE → WHO TALKS → MESSAGE → MEANING → PROOF
```

## Visual tour

Keep the official Modbus, OPC Foundation, NMEA and IEC pages open while you work. After commissioning, replace conceptual visuals with your own Wireshark, OPC UA browser and replay/capture screenshots from the running testbed.

## Modbus TCP

Official source: https://www.modbus.org/modbus-specifications

```text
Ethernet → IP → TCP → MBAP → Function → Address → Data
```

The **device map** turns address/data into I/O meaning.

Worked example: an FC04 response contains the raw Cargo flow register; the I/O map tells you its scaling; the PLC tag tells you how control logic sees it.

## OPC UA

Official source: https://opcfoundation.org/about/opc-technologies/opc-ua/

Think:

```text
NodeId + DataType + Value + Quality + Time
```

The lab performs live discovery before historian installation so a guessed identifier cannot silently become “truth.”

## NMEA 0183

Official source: https://www.nmea.org/nmea-0183.html

Legacy serial talker/listener model. Without GNSS hardware, the lab replays a recorded real NMEA stream through GPSD tooling and labels it replay.

## NMEA 2000 / CAN

Official source: https://www.nmea.org/nmea-2000.html

CAN-based multi-device marine network. The software extension can teach CAN mechanics with SocketCAN, but it does not redistribute licensed PGN definitions or claim NMEA 2000 certification.

## CAN / J1939

J1939 is taught as a machinery-network concept only where equipment/vendor context makes it relevant. It is not asserted as the universal LNG-carrier engine protocol.

## IEC 61162-450 / 460

IEC 61162-460:2024 is a marine Ethernet safety/security reference layered on the 61162-450 environment. The lab teaches the architecture and security context but does not claim compliance.

## Lab action — prove one Modbus message

```bash
./labctl capture cargo modbus
# perform a controlled Cargo operation
./labctl zeek cargo
```

In Wireshark identify one transaction and explain it from L2 through process meaning.

## Explain it in 60 seconds

Why is “Modbus = TCP/502” an inadequate explanation? What extra information gives a register physical meaning?

## Go deeper

- [Ethernet/IP/TCP](../05-protocols/ethernet-ip-stack.md)
- [Modbus TCP](../05-protocols/modbus-tcp.md)
- [OPC UA](../05-protocols/opc-ua.md)
- [NMEA](../05-protocols/nmea.md)
- [CAN/J1939](../05-protocols/can-j1939.md)
- [Packet labs](../05-protocols/packet-labs.md)
