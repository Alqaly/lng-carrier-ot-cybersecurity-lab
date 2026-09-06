# Propulsion Cooling-Fault Reachability Record

## Decision

The registered `EXP-PROP-COOLING-FAULT` experiment must be physically reachable
in the executable teaching model. A declared alarm or evaluator branch is not
enough.

The earlier cooling-fault gain was `0.90 °C/% load`. At full fuel and full pitch,
the model's steady shaft equation settles near `58.5%` load. Its impaired
coolant target was therefore only about `87.7 °C`, below the `92 °C` trip. The
experiment could not reach its own protective condition during sustained
operation.

The corrected teaching gain is `1.20 °C/% load`. With the same executable
steady-state load:

```text
healthy target  = 35 + 0.48 × 58.5 ≈ 63.1 °C
impaired target = 35 + 1.20 × 58.5 ≈ 105.2 °C
trip threshold  = 92 °C
```

Healthy maximum operation remains below the threshold, while deterministic
cooling impairment now crosses it with margin. `tests/test_model_sanity.py`
derives the equilibrium from the actual torque, drag and speed parameters and
fails if a later parameter change breaks either boundary.

## Reproducible pre-PLC exercise

Run a packet capture and the controlled scenario in separate terminals:

```bash
./labctl capture propulsion modbus
./labctl demo propulsion-cooling
```

The scenario:

1. clears both propulsion instructor faults;
2. establishes pre-lube and sustained maximum teaching load;
3. verifies that `highCoolantTemp` is false before intervention;
4. asserts `faultCoolingFail` at Modbus coil 21;
5. records the temperature and discrete-state timeline;
6. exits nonzero unless the high-coolant input becomes true;
7. clears the fault and commands even after failure.

The timeline is saved as
`evidence/live/propulsion/pre-plc-cooling-timeline.jsonl`. It is explicitly
labelled `pre_plc_commissioning_not_experiment_evidence` so it cannot be mistaken
for an accepted research run.

## Evidence boundary

`./labctl demo` deliberately bypasses OpenPLC. It proves the plant, Modbus I/O,
fault intervention and alarm-input reachability. It does **not** prove the final
controller action.

An accepted `EXP-PROP-COOLING-FAULT` run still requires the commissioned PLC to
own `engineEnable` and must retain the ordered sequence:

```text
faultCoolingFail
→ coolantTempC rises
→ highCoolantTemp true
→ later engineEnable false
```

The experiment evaluator, PCAP, normalized propulsion state timeline and alarm
timeline remain authoritative for that claim.

## Model boundary

The gain is a transparent low-order teaching calibration. It is not fitted to a
specific MAN, WinGD or Wärtsilä engine and does not validate real cooling-system
thermal mass, trip setpoints or shutdown timing. Target-server repetitions are
still required before reporting measured latency or variance.
