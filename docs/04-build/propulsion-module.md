# Propulsion and Machinery — Permissives, Shaft Dynamics and Protective State

## Visual tour

Use a real marine engine-control reference before the teaching model. Wärtsilä's control-system/engine material is the system reference; your actual OpenPLC/FUXA traces are the executable visual evidence. Do not interpret the Modelica model as a WinGD/MAN/Wärtsilä digital twin.

The default vessel profile uses a **mechanical main-propulsion teaching model**. Main shaft power is not falsely placed on the electrical PMS bus; only machinery auxiliary electrical demand is coupled to PMS.

## Why build this module?

A propulsion cybersecurity exercise is weak if it consists only of writing `RPM = 80` to a dashboard.

The module instead connects:

```text
auxiliary electrical power
→ pre-lube
→ lube pressure
→ engine enable permissive
→ fuel command
→ engine torque
→ shaft acceleration
→ propeller load
→ vessel-speed response
→ thermal/protective conditions
```

## Real-system reference

Real marine engine-control systems monitor/control concepts such as start/stop, engine speed/load and protective conditions including lubrication and cooling. Actual LNG carriers may use different main-engine and propulsion architectures.

The software model is vendor-neutral and does not claim to reproduce a MAN, WinGD, Wärtsilä or propulsion-drive proprietary controller.

## Pre-lube dependency

Before the engine turns, the model requires auxiliary electrical availability for the pre-lube pump:

```text
PMS bus available
      ↓
pre-lube command
      ↓
lube pressure rises
      ↓
engine enable permitted
```

Once the engine is rotating, the teaching model adds an engine-driven main-lube contribution.

This creates a useful cross-system distinction:

- loss of the PMS bus can block **starting/pre-lube**,
- but the selected mechanical-profile model does not pretend the running shaft itself is an electrical load.

## Shaft dynamics

The simplified mechanical relationship is:

```text
J dω/dt = engine torque - propeller load torque - friction
```

Engine torque depends on fuel command, engine-enable state, lube permissive and speed.

Propeller load rises strongly with shaft speed and pitch:

```text
Tprop ∝ pitch × ω²
```

The result is an equilibrium speed rather than an arbitrary RPM tag.

## Cooling and machinery state

Coolant temperature follows modeled engine load with a slower time constant. Lube pressure follows pre-lube/engine-running state and can be deliberately failed with an instructor fault.

Protective outputs include:

- low lube pressure,
- high coolant temperature,
- overspeed.

## PLC sequence

The teaching PLC should make the causal order obvious:

```text
Propulsion enable request
      ↓
pre-lube command
      ↓
pressure permissive
      ↓
engine enable
      ↓
fuel / pitch control
```

If a protective condition becomes active, fuel/engine enable is removed through the teaching control path.

## Pre-PLC commissioning

Run:

```bash
./labctl build
./labctl demo propulsion
```

Observe:

1. pre-lube command,
2. lube pressure rise,
3. engine enable,
4. fuel and pitch command,
5. engine RPM acceleration,
6. propeller torque,
7. machinery auxiliary kW,
8. coolant response,
9. vessel-speed response.

Capture:

```bash
./labctl capture propulsion modbus
```

Then compare packet values with `docs/08-reference/generated-io-map.md`.

## Fault investigation

The instructor fault `faultLubePumpFail` does not randomly appear.

When deliberately asserted, investigate:

```text
fault command
→ lube-pressure decay
→ low-lube condition
→ PLC protective response
→ RPM/load response
→ alarm chronology
```

The lesson is not merely “an alarm appeared”; it is to explain every transition on one timeline.

## Explicit limitations

The model does not represent:

- individual cylinders/combustion,
- turbocharger dynamics,
- detailed gas admission,
- torsional vibration,
- controllable-pitch hydraulic servo internals,
- actual propeller/hull performance curves,
- a manufacturer engine-safety system.
