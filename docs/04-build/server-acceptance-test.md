# Server Acceptance Test

This is the sequence to run on the server before calling the lab commissioned.

The canonical execution interface is the resumable orchestrator:

```bash
./labctl commission start
./labctl commission resume evidence/commissioning/<run>
```

It executes the machine-verifiable work below, stops at live engineering checkpoints, and packages supplied evidence with commit provenance and SHA-256 hashes. The detailed gates remain here so the acceptance meaning stays reviewable. See `commissioning-orchestrator.md` for recording examples and recovery after interruption.

## Gate A — host and source

```bash
./labctl preflight
./labctl test
./labctl config-check
```

Pass condition: no failed static/research/pedagogy/traceability gate and rendered Compose config is valid.

## Gate B — physics and I/O

```bash
./labctl build
./labctl smoke
./labctl demo pms
./labctl demo cargo
./labctl demo propulsion
./labctl demo vessel
```

These demos deliberately bypass the PLC. Pass condition: each dynamic model responds causally and the software I/O carries the expected Modbus values.

## Gate C — controller commissioning

Commission the three OpenPLC projects using the documented mapping. For every domain, verify online command, feedback and measurement tags.

Then capture at least one normal control transaction:

```bash
./labctl capture cargo modbus
```

Pass condition: the packet, I/O map and PLC online state tell the same story.

## Gate D — supervisory path

For each domain:

```bash
./labctl opcua cargo
./labctl bind-plan cargo
./labctl hist-install cargo
```

Repeat for PMS and propulsion.

Pass condition: no missing/ambiguous required binding; historian samples match live PLC values and preserve useful timing/status information.

## Gate E — operator HMI

Bootstrap/bind FUXA, then:

```bash
./labctl fuxa export
./labctl fuxa validate
```

Capture screenshots for normal Cargo, PMS and propulsion operation. The screen must be operator/task oriented; protocol diagnostics belong in engineering views.

## Gate F — research experiments

Run all IDs in `experiments/manifest.json`. A run is complete only when required evidence is present and the evaluator can compute/report the declared result or explicitly explain why a metric is unavailable.

Minimum publication evidence should include:

- normal Cargo baseline,
- blocked-flow Cargo event,
- flow-sensor integrity event,
- generator-trip/cross-system response,
- propulsion cooling fault,
- unexpected Modbus source,
- OPC UA supervisory outage.

## Gate G — persistence and recovery

Install the daemon, reboot the server and verify service recovery:

```bash
sudo ./deploy/install-systemd.sh
sudo reboot
# after reboot
systemctl status lng-ot-lab
./labctl smoke
```

After the PLC, OPC UA, historian and HMI have been commissioned, run the post-commissioning service probe:

```bash
./labctl runtime-verify
```

This verifies process health plus reachability of the three Modbus I/O endpoints, three OpenPLC management endpoints, three OPC UA endpoints, InfluxDB, Grafana, FUXA, the alarm chronicle, learning portal and vessel coordinator. It is a reachability gate—not a substitute for semantic tag/experiment evidence.

Then:

```bash
./labctl backup
```

Restore the backup on a clean test host before claiming recovery readiness.

## Final acceptance statement

Do not write “fully tested” until Gates A–G are completed on the target server and the evidence is stored with the release/experiment record.

```bash
./labctl commission finalize evidence/commissioning/<run>
```

Finalization exits nonzero if an artifact merely exists but lacks semantic PASS, has the wrong Gate/filename identity, references another Git commit, points outside the run, or has a mismatched evidence hash.
