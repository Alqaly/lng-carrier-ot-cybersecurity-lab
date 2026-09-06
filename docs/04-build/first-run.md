# Safe first run

There are two separate entry points: **read the course** or **commission the
lab**. Reading the website does not require PLCs, live credentials or a Docker
engine. The [learning journey](../00-learning/learning-journey.md) starts there.

## 1. Preserve your current work

Use a clean Git checkout for commissioning. If `git status --short` prints
changes, stop before pulling or switching branches. Preserve tracked edits and
untracked runtime settings first. Never use a hard reset to make this gate pass.
Mutable FUXA state is ignored by Git; a clean tree is not a runtime backup.

An upgrade starts a **new commissioning run** at the new commit. Keep older
evidence intact. Do not edit its recorded commit to make it look current.

## 2. Install the source-review environment

From the repository directory, on a host with Python 3 and its venv support:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-ci.txt -r requirements-docs.txt
./labctl review
./labctl learn check
./labctl docs build
```

Stop at an error and keep its output. A successful documentation build only
establishes that the course builds; it does not run the OT stack.

## 3. Check Docker access

```bash
./labctl doctor
docker info
```

Docker Compose v2 and a reachable daemon are required. A Docker socket permission
error needs an administrator-approved access fix. Do not make the socket
world-writable or run the entire research workflow under sudo. Docker access
is powerful host access and should only be granted deliberately.

## 4. Initialize private credentials

```bash
./labctl setup
```

For a new checkout this creates random credentials in `.env` at mode `0600`,
without printing the values. An existing `.env` is preserved **byte for byte**;
setup does not rotate credentials in initialized InfluxDB or Grafana volumes.
It then runs the secret validator and fails if placeholders or unsafe file
permissions remain. If this is an older checkout, edit the existing file locally
and re-run `./labctl secrets-check`. Never paste its contents into an issue/chat.

## 5. Begin evidence-backed commissioning

This next command builds and starts the local software lab. Allow time for
container downloads and FMU compilation. Use only an isolated test host.

```bash
./labctl preflight
./labctl commission start
```

Preserve the printed `evidence/commissioning/...` directory. The
[commissioning guide](commissioning-orchestrator.md) explains `status`, `resume`,
manual evidence recording and `finalize`. A manual-evidence pause is expected;
it is not a reason to bypass a gate or invent a screenshot.

## When something stops

| Symptom | Safe next action |
|---|---|
| Pull would overwrite a tracked file | Preserve the local change; inspect whether upstream already contains it |
| `No stash entries found` | No stash was restored; this is not an update or a backup |
| venv module unavailable | Install your distribution's Python venv package, then retry environment creation |
| Docker permission denied | Resolve daemon access through the host administrator |
| Existing placeholder secret | Update the private file locally; do not overwrite initialized service credentials blindly |
| Commissioning source drift | Return to the matching source or begin a new run; preserve previous evidence |
| Verification says legacy evaluation | Preserve the old run; explicitly re-evaluate a copy with the appropriate source and document the re-analysis |

Stable release acceptance still requires the live PLC, OPC UA, historian, HMI,
21 verified runs, reboot and restore evidence. See
[server acceptance](server-acceptance-test.md) for the complete gate contract.
