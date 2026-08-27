# Scenario — Safety Event

The software testbed includes a separate safety state.

A process-high condition can latch a shutdown request.

## Expected action

```text
process high-high
→ safety condition
→ transfer permit removed
→ pump output removed
→ valve closes
```

The exercise teaches cause-and-effect and separation.

It must not be confused with a class-approved or SIL-rated safety system.
