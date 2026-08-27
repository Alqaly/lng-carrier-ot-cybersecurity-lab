# Incident Walkthrough

## 1. Establish operational state

Record:
- transfer mode,
- pump/valve commands,
- feedback,
- flow,
- tank levels,
- safety state.

## 2. Preserve evidence

Save:
- PCAP,
- OpenPLC logs,
- virtual-I/O logs,
- process-runtime state,
- historian timeline.

## 3. Identify the failure layer

Is the problem:
- operator intent,
- PLC logic,
- Modbus transport,
- I/O mapping,
- process model,
- feedback,
- OPC UA,
- historian?

## 4. Contain carefully

Do not confuse a cybersecurity containment step with a safe process shutdown procedure.

## 5. Recover

Re-establish:
- known PLC program,
- expected network path,
- correct I/O map,
- consistent process state.

## 6. Explain the event

A good final report contains:
- what changed,
- when,
- where,
- protocol evidence,
- process consequence,
- root cause,
- corrective action.
