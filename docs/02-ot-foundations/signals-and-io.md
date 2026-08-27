# Signals and I/O

The software lab emulates I/O behavior, but the concepts correspond to real field instrumentation.

## Digital input

Represents a discrete state:

```text
0 / 1
OFF / ON
OPEN / CLOSED
FAULT / HEALTHY
```

## Digital output

Represents a commanded discrete state.

## Analog measurement

A physical transmitter may use standards such as 4–20 mA.

The software lab represents the engineering-unit value and its raw I/O representation separately so the reader can learn scaling.

## Scaling

For a linear 4–20 mA transmitter:

```text
EU = (mA - 4) / 16 × span + low_limit
```

Example for a 0–2000 m³/h flow transmitter:

```text
4 mA  → 0
12 mA → 1000
20 mA → 2000
```

The important lesson is the chain:

```text
physical property
→ transmitter
→ I/O conversion
→ raw value
→ engineering-unit scaling
→ PLC logic
```
