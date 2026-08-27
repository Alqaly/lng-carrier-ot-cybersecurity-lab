# OT From Zero

## The smallest useful OT model

```text
Human
  ↓
HMI / Engineering
  ↓
PLC
  ↓
I/O
  ↓
Physical process
  ↑
Measurement / feedback
```

## PLC scan cycle

A PLC repeatedly performs a scan:

1. read inputs,
2. execute logic,
3. write outputs,
4. repeat.

The cycle matters because OT logic is stateful and timing-dependent.

## Command

What the controller or operator requests.

## Output

What the controller drives toward the field.

## Feedback

Independent confirmation of equipment state.

## Measurement

A value representing the process itself.

These are not interchangeable.

Example:

```text
Pump command = ON
Pump output = ON
Pump feedback = OFF
Flow = 0
```

Possible causes include:
- failed motor/drive,
- failed feedback,
- wiring/configuration error,
- blocked process,
- incorrect command mapping.

A cyberattack is only one possible explanation.

## Remember it

**Command is intent. Output is drive. Feedback is equipment state. Measurement is process state.** Do not collapse them into one tag.

## Explain it in 60 seconds

Use a pump example to explain command vs output vs feedback vs flow measurement.
