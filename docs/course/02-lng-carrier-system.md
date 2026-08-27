# 02 — Understand the LNG Carrier Before Cybersecurity

## Why this matters

A packet is operationally meaningless until you know what system it belongs to. An LNG carrier is a **system of systems**, not one flat “OT network”.

## Visual tour — real marine automation

Use Kongsberg K-Chief 600 public material: https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/k-chief-600-marine-automation-system/

Also review Wärtsilä Gas Solutions: https://www.wartsila.com/marine/products/gas-solutions

**What to notice**

- operator stations are separate from distributed control and I/O,
- marine automation integrates multiple functions,
- different equipment vendors/interfaces coexist,
- alarms, process views and engineering access are distinct concerns.

## Memory hook

```text
CARGO — POWER — MACHINERY — SAFETY — NAVIGATION
             \       |       /
              AUTOMATION
```

Then add **people/interfaces**: operator, engineer, vendor, terminal/shore.

## Core concepts

### Cargo
Tank state, pumps, valves, transfer sequence, gauging, BOG-related context and ship/shore safety.

### Power
Generators, switchboards, bus availability, load sharing, reserve, shedding and blackout recovery.

### Machinery / propulsion
Start permissives, lubrication, cooling, engine/shaft state and dependent auxiliaries.

### Safety
Protective functions such as F&G/ESD must not be collapsed into ordinary process control.

### Navigation
GNSS and marine data interfaces have different trust, timing and network models from machinery control.

## Worked example — why domain context matters

You see TCP traffic to a PLC followed by a frequency drop.

Without vessel context, you might report “PLC network anomaly.”

With context:

```text
Generator trip
→ available generation falls
→ bus frequency/reserve changes
→ load-shedding decision
→ Cargo/Propulsion consequence
```

Now the same traffic has an operational story.

## Lab mapping

The executable core currently models three coupled domains:

- Cargo unloading profile,
- Power Management,
- Propulsion/Machinery.

Navigation and real ship/shore systems are taught with replay/reference boundaries where full implementation would be dishonest.

## Explain it in 60 seconds

Why is “the ship OT network” an oversimplification? Name five operational domains and one interface between them.

## Go deeper

- [LNG Carrier 101](../01-vessel/lng-carrier-101.md)
- [Marine automation reference](../01-vessel/marine-automation-reference.md)
- [Cargo system](../01-vessel/cargo-system.md)
