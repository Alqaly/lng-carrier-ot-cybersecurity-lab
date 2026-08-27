# NMEA 0183 and NMEA 2000

## Visual tour

Compare the official public NMEA descriptions:

- NMEA 0183: https://www.nmea.org/nmea-0183.html
- NMEA 2000: https://www.nmea.org/nmea-2000.html

**Notice:** 0183 is a serial talker/listener interface while NMEA 2000 is CAN-based and multi-device. The lab deliberately does not flatten both into “UDP navigation data.”

These are different technologies.

## NMEA 0183

NMEA describes NMEA 0183 as a one-way serial interface from a single talker to one or more listeners.

Software-only path:

```text
recorded NMEA log
→ gpsfake
→ gpsd
→ navigation client
```

The data source is a recorded NMEA stream, not newly generated coordinates.

This is a **replay exercise**.

With hardware later:

```text
GNSS receiver
→ serial interface
→ gpsd
```

## NMEA 2000

NMEA describes NMEA 2000 as a CAN-based, bidirectional, multi-device marine network.

A pure software exercise can teach CAN mechanics using SocketCAN, but that is not the same as owning a certified NMEA 2000 device or reproducing the licensed standard.

The course therefore treats NMEA 2000 as:
- architectural reference,
- CAN/networking lesson,
- optional hardware extension.

## Remember it

**0183 = serial talker/listener. NMEA 2000 = CAN-based multi-device network.** Similar marine purpose does not mean same protocol model.

## Explain it in 60 seconds

Explain why replaying a recorded NMEA 0183 log is useful but is not a live GNSS sensor.
