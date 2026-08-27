# Detection Engineering

Detection should combine protocol evidence with process context.

## Example 1

```text
PLC writes pump ON
AND
pump feedback remains OFF
```

Possible causes:
- process/equipment failure,
- I/O mapping failure,
- communication failure,
- unauthorized or unexpected command.

## Example 2

```text
Modbus write occurs
FROM unexpected source
```

This is more directly cyber-relevant because the source violates the expected conduit.

## Detection layers

- network source/destination
- protocol operation
- controller variable
- equipment feedback
- process response
- historian sequence

A strong detection explains **why the event matters operationally**.

## Remember it

**Network tells you who/what communicated. Process tells you whether the operation made physical sense. Cross-layer evidence tells the story.**

## Explain it in 60 seconds

Explain why an unexpected Modbus source and a no-flow process residual answer different investigative questions.
