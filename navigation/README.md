# Navigation Replay Lab

Without GNSS hardware, navigation is taught using **recorded NMEA data replay**.

The recommended tool is GPSD's `gpsfake`.

Architecture:

```text
recorded NMEA log
→ gpsfake
→ gpsd
→ client / parser
```

This lets the learner study:
- NMEA sentences,
- fix status,
- position,
- time,
- speed/course,
- parser behavior.

The course does not generate a fictional route and call it a live sensor.

## Add your own capture later

With a USB/serial GNSS receiver:

```bash
gpsd /dev/ttyUSB0
```

The software clients do not need to change.
