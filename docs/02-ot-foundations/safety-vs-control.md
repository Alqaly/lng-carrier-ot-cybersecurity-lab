# Safety vs Control

## Visual tour

Read SIGTTO's ESD Systems guidance alongside this chapter: https://www.sigtto.org/publications/esd-systems/

**Notice:** emergency shutdown exists to move transfer toward a safe state and is not the same thing as ordinary sequence control. **Lab mapping:** the teaching safety state removes transfer permission. **Limitation:** the lab is not a certified ESD/SIS.

Normal control tries to operate the process.

Safety logic tries to move the process toward a safe condition when a hazardous condition exists.

## Ordinary control

```text
Operator requests transfer
→ PLC checks permissives
→ valve opens
→ pump starts
```

## Protective action

```text
hazard condition
→ safety logic
→ trip latched
→ pump stopped
→ valve commanded closed
```

In a real marine safety design, independence, redundancy, certification and cause-and-effect engineering can be much more sophisticated.

The software lab uses a logically independent safety service to teach separation, but it is **not** a functional-safety system.
