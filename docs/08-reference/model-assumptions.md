# Model Assumptions and Realism Boundaries

The models are designed for control and cybersecurity education, not naval architecture, class approval or equipment sizing.

## Cargo

The Cargo model includes:

- two tank states,
- pump run-up/run-down,
- motorized valve travel,
- hydraulic-head influence,
- flow-transmitter lag,
- tank level and hydrostatic pressure,
- deterministic instructor faults.

It does not claim fidelity for cryogenic LNG thermodynamics, membrane containment heat transfer, BOG generation/reliquefaction, real cargo-pump curves, surge calculations, terminal loading-arm dynamics or certified ESD timing.

## Power Management

The PMS model is a simplified two-generator AC bus with:

- prime-mover run-up,
- generator ready state,
- breaker state,
- three load groups,
- simplified governor/power response,
- frequency inertia and damping,
- reserve calculation,
- progressive load shedding,
- deterministic generator-trip faults.

It teaches:

```text
generation capacity
↔ load demand
↔ frequency
↔ reserve
↔ breaker state
↔ load shedding
```

It does not model short-circuit current, relay curves, AVR/excitation in detail, full synchronizer phase-angle logic, harmonic studies or proprietary marine PMS algorithms.

## Propulsion

The propulsion model includes:

- pre-lube permissive,
- engine enable,
- fuel command,
- pitch command,
- shaft inertia,
- speed-dependent propeller load,
- lube-oil pressure,
- coolant temperature,
- vessel-speed response,
- deterministic lube-pump failure,
- deterministic cooling impairment with a statically checked reachable trip.

The cooling-fault coefficient is a transparent teaching calibration, not a
manufacturer or vessel measurement. The [reachability record](../09-research/propulsion-cooling-reachability.md)
derives the healthy and impaired steady-state bounds and states what the demo
does and does not prove.

It does not reproduce a specific MAN, WinGD or Wärtsilä engine controller and does not model cylinder combustion, turbocharger dynamics, gas admission, shaft torsional vibration, detailed CPP servo dynamics or a validated hull-resistance curve.

## Faults

Fault inputs are explicit instructor commands and are never random:

```text
faultPumpFail
faultFlowPathBlocked
faultValveStuck
faultGen1Trip
faultGen2Trip
faultLubePumpFail
faultCoolingFail
```

The lab must never activate a fault simply because an uninitialized register has a non-neutral interpretation.

## Source philosophy

A marine source supports the *real system concept*.

A software equation implements the *teaching model*.

The documentation keeps those statements separate.

## FMI integration method

The repository exports FMI 2.0 Co-Simulation FMUs using OpenModelica's standard Co-Simulation path and advances them at a 50 ms communication interval.

The models are intentionally kept low-order enough that the portable default integration path is preferred over adding a CVODE runtime dependency to every FMU. If a future subsystem becomes numerically stiff or requires a higher-fidelity solver, that choice must be validated and documented rather than changed silently.
