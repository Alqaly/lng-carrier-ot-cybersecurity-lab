# Scenario — Process Integrity Investigation

The point is not to create an “attack.”

The point is to investigate disagreement.

Examples:

```text
pump command ON
pump feedback ON
flow remains zero
```

or:

```text
valve command OPEN
valve feedback CLOSED
```

Questions:

1. Is the PLC command correct?
2. Did Modbus carry the command?
3. Did the I/O state change?
4. Did the process model receive the input?
5. Is the feedback path correct?
6. Did OPC UA expose the same state?
7. Does the historian timeline match?

This investigation method transfers directly to hardware labs later.
