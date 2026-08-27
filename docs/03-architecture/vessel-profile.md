# Vessel Profile — What Is Electrically Coupled?

A major source of bad maritime OT diagrams is treating every LNG carrier as if it used the same propulsion architecture.

It does not.

## Real LNG-carrier propulsion architectures vary

Public Wärtsilä material documents LNG carriers with electric propulsion and also gas-carrier arrangements where a main engine mechanically drives the propeller while auxiliary generation supplies electrical consumers.

That changes the cyber-physical dependency graph.

### Electric-propulsion concept

```text
Fuel / prime movers
      ↓
Generators
      ↓
Main electrical bus
      ├── hotel / auxiliaries
      ├── Cargo electrical loads
      └── propulsion drive / motor
```

A severe electrical event can directly affect propulsive power.

### Mechanical-propulsion concept

```text
Main engine ───────────────► shaft / propeller

Auxiliary generation
      ↓
Electrical bus
      ├── hotel / auxiliaries
      ├── Cargo pumps
      └── electrically driven machinery auxiliaries
```

Main shaft power is not simply another PMS electrical load.

## Default integrated teaching profile

The repository uses:

> **Mechanical main propulsion with electrically supplied Cargo and machinery auxiliary loads.**

The profile file is:

```text
vessel/profile.json
```

The cross-system coordinator implements only the selected dependencies:

```text
Cargo pump model
      │ pumpPowerKW
      ▼
PMS external Cargo load

PMS bus / Cargo shedding
      │
      ▼
Cargo powerAvailable

Propulsion auxiliaries
      │ auxiliaryElectricalLoadKW
      ▼
PMS external auxiliary load

PMS bus
      │
      ▼
Propulsion pre-lube auxiliary power
```

The running main engine's shaft output is **not** placed on the PMS bus.

## Why this matters for cybersecurity

An incident path depends on the vessel architecture.

For example:

```text
Generator trip
```

can mean:

- Cargo pump power lost,
- HMI/historian degradation,
- pre-lube unavailable before engine start,
- but not necessarily immediate loss of mechanical shaft propulsion.

The lab teaches the dependency explicitly instead of assuming every electrical fault stops every vessel function.
