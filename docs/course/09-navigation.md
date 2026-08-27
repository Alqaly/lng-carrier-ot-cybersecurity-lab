# 09 — Navigation Interfaces Without Pretending Replay Is a Sensor

## Why this matters

Navigation systems are cyber-physical too, but their protocols and trust model differ from machinery control.

## Visual tour

Use the official NMEA public descriptions:

- NMEA 0183: https://www.nmea.org/nmea-0183.html
- NMEA 2000: https://www.nmea.org/nmea-2000.html

For marine Ethernet security context, review IEC 61162-460:2024 via IEC: https://webstore.iec.ch/en/publication/82336

## Memory hook

```text
0183 = SERIAL TALKER
2000 = CAN NETWORK
450/460 = MARINE ETHERNET CONTEXT
```

## NMEA 0183 replay

Without physical GNSS, the lab uses:

```text
recorded NMEA data → gpsfake → gpsd → client
```

That is **recorded-data replay**. The transport/parser behavior is real software; the current position is not live sensor truth.

## Worked example

When a recorded position sentence is replayed, preserve the raw sentence first. Then compare parsed position/time/speed with the source record. This separates:

- source evidence,
- transport,
- parser interpretation.

## NMEA 2000 / CAN boundary

SocketCAN can teach arbitration, identifiers, frames and capture mechanics. It must not be labeled a complete NMEA 2000 implementation without real compliant devices/standard data definitions.

## Security lesson

Before calling navigation data “spoofed,” ask whether the evidence can distinguish:

- bad source,
- replay,
- parsing fault,
- timing/staleness,
- transport loss,
- malicious manipulation.

## Lab action

Use the GPSD replay workflow documented in `navigation/README.md`. Preserve the original capture, launch replay, connect a client, and save both the raw lines and parsed output. Then deliberately stop replay and observe how the client represents loss/staleness instead of inventing a position.

For the CAN extension, create a virtual CAN interface only as a mechanics exercise. Capture frames with standard Linux CAN tooling and explain arbitration/identifier/data fields before discussing any marine higher-layer meaning. The course should always say which layer is being demonstrated.

## Evidence

Keep three artifacts together: the source recording, the raw replay output and the normalized client output. That makes parser errors distinguishable from source-data anomalies. For CAN, retain the command used to create the virtual interface and the exact frame capture; do not label those frames NMEA 2000 unless they came from a legitimate NMEA 2000 source and licensing permits interpretation.

## Explain it in 60 seconds

Explain why replay is scientifically useful but must be labeled differently from live GNSS data.

## Go deeper

- [NMEA](../05-protocols/nmea.md)
- [IEC 61162-450/460](../05-protocols/iec-61162-450-460.md)
- [Navigation replay README](https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab/blob/main/navigation/README.md)
