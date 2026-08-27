# LNG Carrier 101

An LNG carrier is a floating industrial system whose mission depends on several interacting domains.

## Visual tour

Use the official Kongsberg K-Chief 600 material to inspect a real distributed marine automation reference: https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/k-chief-600-marine-automation-system/

**Notice:** Operator Stations, Distributed Processing Units, remote I/O, process/network separation and alarm handling. **Lab mapping:** our domains are separate teaching models connected through explicit conduits. **Limitation:** actual vessel/vendor topology varies.

## Cargo

The cargo system handles LNG transfer and monitors containment-related conditions.

Teaching concerns:
- tank level,
- pressure,
- temperature,
- cargo pumps,
- valves,
- boil-off gas,
- loading/unloading sequence,
- emergency shutdown.

## Power

The vessel generates and distributes its own electrical power.

Teaching concerns:
- generators,
- switchboards,
- bus state,
- protection,
- load shedding,
- blackout recovery.

## Machinery and propulsion

The main engine or propulsion system depends on supporting machinery.

Teaching concerns:
- lube oil,
- cooling,
- fuel-gas supply,
- RPM,
- availability,
- permissives.

## Safety

Safety functions react to hazardous conditions and should not be confused with ordinary process control.

Teaching concerns:
- Fire & Gas,
- emergency shutdown,
- independent protective paths,
- trip reset conditions.

## Bridge and navigation

Navigation systems produce position, heading, speed, course, depth and other data.

Teaching concerns:
- NMEA 0183,
- NMEA 2000,
- IEC 61162 Ethernet interfaces,
- data plausibility,
- trusted time.

## Ship/shore

Cargo transfer depends on coordination between the vessel and the terminal.

SIGTTO guidance describes linked ESD systems and ship-shore link testing for liquefied-gas transfer.

## Cybersecurity consequence

A network event matters because of the operational function behind it.

The correct question is not only:

> Which IP address changed?

It is also:

> Which vessel function can this data or command influence?

## Remember it

**SHIP = Cargo + Power + Machinery + Safety + Navigation + Human/Engineering interfaces.** A cyber event matters only when you can say which operational function it can influence.

## Explain it in 60 seconds

Explain why an LNG carrier should be treated as a system of systems rather than one “OT network”.
