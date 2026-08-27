# Power Management System — Dynamic Electrical Dependency

## Visual tour — real LNGC PMS test bed

Use Lee (2024), especially Figures 3, 9, 10 and 11: https://www.mdpi.com/2077-1312/12/7/1236

**Notice:** generator/consumer simulation, target PMS/MSBD, network configuration and condition-monitoring GUI. **Lab mapping:** our PMS plant, OpenPLC controller, Modbus I/O and FUXA/historian separate the same teaching roles. **Limitation:** ours is software-defined, not hardware HIL.

The PMS module exists because Cargo, automation and machinery auxiliaries depend on electrical availability. It is not a decorative `frequency = 59.8` tag.

## Real marine reference

ABB describes marine PEMS as an integrated vessel power/energy management layer connected with switchboards, protection devices and controllers. Kongsberg's public K-Chief material likewise shows integration with vessel electric-plant control.

Official references:
- https://new.abb.com/marine/systems-and-solutions/digital/control-and-monitoring/PEMS
- https://www.kongsberg.com/contentassets/8718109b78554cd0820b221c499a3442/k-chief-data-sheet.pdf

The executable model is vendor-neutral and does not reproduce ABB/Kongsberg proprietary logic.

## What is modelled

```text
Gen 1 prime mover ─► breaker ─┐
                              ├──► AC bus ─► hotel/aux load
Gen 2 prime mover ─► breaker ─┘          ├──► Cargo electrical load
                                         └──► machinery auxiliary load
```

Dynamic state includes:

- generator prime-mover run-up,
- ready feedback,
- simplified synchronizing permissive,
- breaker command/feedback,
- generator kW response,
- total load,
- bus frequency,
- simplified voltage,
- spinning reserve,
- under-frequency,
- blackout,
- load shedding.

## Power balance

The central teaching relationship is:

```text
generation - demand - frequency damping
                    ↓
              d(frequency)/dt
```

If load exceeds the online generation response, frequency falls. Bringing additional generation online increases available capacity/reserve.

## Why the Cargo model matters here

The PMS does not need a hard-coded `Cargo = 2500 kW` in the integrated vessel exercise.

The Vessel Coordinator writes the **calculated Cargo pump load** into:

```text
externalCargoLoadKW
```

The PMS then computes:

```text
cargoLoadActualKW
TotalLoadKW
spinningReserveKW
frequencyHz
```

If Cargo shedding is commanded, `cargoLoadActualKW` becomes zero and the coordinator removes Cargo power availability.

## First-generator / second-generator sequence

The supplied IEC 61131-3 teaching logic uses:

```text
Plant Enable
   ↓
Gen 1 start
   ↓
Gen 1 ready + sync permissive
   ↓
Gen 1 breaker
   ↓
live bus established
   ↓
load / reserve evaluated
   ↓
Gen 2 starts only when required
```

This avoids the common lab error where `reserve = 0` on a dead bus immediately starts every generator.

## Synchronizing boundary

The model exposes a **simplified frequency-match permissive**. It does not implement a full generator synchronizer with:

- phase-angle matching,
- detailed voltage matching,
- AVR dynamics,
- synchronism-check relay behavior.

The PLC must see the simplified permissive before closing the second generator breaker.

## Load shedding

The teaching controller uses staged frequency thresholds:

```text
frequency < 57.5 Hz → shed Cargo
frequency < 57.0 Hz → shed hotel/auxiliary load
```

These are **lab thresholds**, not real vessel settings.

## Pre-PLC commissioning walkthrough

Run:

```bash
./labctl build
./labctl demo pms
```

Trace this sequence:

1. Generator 1 start command.
2. Prime-mover speed rises rather than switching instantly.
3. `gen1Ready` becomes true.
4. Breaker command is applied.
5. Bus becomes energized at the teaching reference frequency.
6. Hotel load is applied.
7. Cargo demand is added.
8. Total load rises and spinning reserve falls.
9. Generator 2 starts.
10. Generator 2 reaches ready/sync state.
11. Second breaker closes.
12. Available capacity/reserve increases.

Capture:

```bash
./labctl capture pms modbus
```

Then inspect register meaning in `docs/08-reference/generated-io-map.md`.

## Integrated power-loss exercise

After the standalone sequence, run:

```bash
./labctl demo vessel
```

The key lesson is cross-system diagnosis:

```text
Cargo flow disappears
```

may be explained by:

```text
PMS bus lost / Cargo load shed
```

rather than a Cargo PLC or pump fault.

## Explicit limitations

The model does not perform:

- short-circuit studies,
- protection-relay coordination,
- electromagnetic machine transients,
- harmonic/power-quality studies,
- real synchronizer/AVR control,
- proprietary load-sharing algorithms.

It is a dynamic operations/cybersecurity teaching model.
