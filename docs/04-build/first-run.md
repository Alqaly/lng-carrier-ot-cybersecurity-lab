# Safe first run

Your first goal is concrete: **open the right interface and observe one Cargo
signal change for an explainable reason**. Complete one route at a time.

## Get a checkout

For a new installation, run this from the directory where you keep projects:

```bash
git clone https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab.git
cd lng-carrier-ot-cybersecurity-lab
git status --short
```

The last command should print nothing. All commands below run from this
repository directory unless a step says otherwise.

### Existing checkout with local changes

If pulling reports that `deploy/preflight.sh` would be overwritten, repeating
`git pull` cannot resolve it. `git stash pop` does not create a stash.

The simplest way to read/review the new source while preserving every old file
is a separate checkout. From your existing repository directory:

```bash
cd ..
git clone https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab.git lng-carrier-review
cd lng-carrier-review
git status --short
```

If that destination already exists, choose an unused name. Your original folder,
edits, `.env` and FUXA state remain in the original location. This does **not**
migrate an existing deployment. Do not start a second full lab beside a running
one: host ports conflict, and named volumes are not copied by Git. Use
[backup and recovery](backup-and-recovery.md) when upgrading a commissioned instance.

A clean existing checkout on `main` can use `git pull --ff-only origin main`.
An upgrade requires a new commissioning run at the new commit; preserve older evidence.

## Read the course with Docker

Prerequisites: Git, Docker, Compose v2 and a reachable daemon. Check them first:

```bash
docker compose version
docker info
./labctl docs up
```

Open **http://127.0.0.1:8088** on the host running Docker.
You should see the course title, a Cargo process illustration and links to the visual guide.
This route needs no lab `.env`, PLC project or HMI credentials.
To stop the course: `./labctl docs down`.

## Read the course without Docker

Use Python 3.12 or 3.13 with venv support; these match the course builder/CI families.
On Kali/Debian/Ubuntu, the basic tools can be installed with:

```bash
sudo apt update
sudo apt install git python3 python3-venv curl
```

From the repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-docs.txt
python -m mkdocs serve --dev-addr 127.0.0.1:8000
```

Open **http://127.0.0.1:8000**. Keep that terminal running; Ctrl-C stops the preview.
A browser website is now available, but the process models are not running.
Start with the [visual guide](../00-learning/visual-guide.md).

## Prepare the lab host

The reference deployment is Linux with Docker Engine, Compose v2 and systemd.
OpenPLC Editor and Wireshark are needed for later control/packet work, not simply to read the course.
Hardware sizing is still unmeasured: image downloads, FMU compilation and retained evidence
need available memory/disk. Record actual consumption during target commissioning.

If Docker is missing, follow the official instructions for your host:
[Kali](https://www.kali.org/docs/containers/installing-docker-on-kali/),
[Debian](https://docs.docker.com/engine/install/debian/) or
[other Linux distributions](https://docs.docker.com/engine/install/).
Use one package source consistently. This project requires `docker compose` v2;
the older `docker-compose` executable is insufficient.

For Docker socket permissions, use the
[official Linux post-install guide](https://docs.docker.com/engine/install/linux-postinstall/).
Docker group membership grants root-level host privileges; do not make the socket world-writable.
After changing group membership, log out/in and verify `docker info` without sudo.

Create/activate the review environment if you have not already done so:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-ci.txt -r requirements-docs.txt
./labctl review
./labctl doctor
docker info
```

**Continue when:** review passes, doctor finds the tools, and `docker info`
returns server information. Doctor checks tool availability; it does not prove daemon access.

Initialize private credentials:

```bash
./labctl setup
./labctl preflight
```

Setup creates a private `.env` with random credentials, mode `0600`, and validates it.
An existing file is preserved byte for byte. It does not rotate credentials in initialized
InfluxDB/Grafana volumes. If validation fails, edit the existing private file locally
and run `./labctl secrets-check`. Do not copy an example file over working credentials.

## Start the process and I/O layer

For a learning session, run:

```bash
./labctl build
./labctl smoke
```

Build compiles the three FMUs and starts the process, I/O, coordinator, alarm and portal services.
**Continue when:** smoke reports Cargo, PMS, Propulsion and Vessel PASS.
Open the Learning Portal at **http://127.0.0.1:8500**, then follow the
[first Cargo investigation](../06-scenarios/first-cargo-investigation.md).
That exercise establishes PMS power before requesting Cargo flow.

For formal acceptance, choose `./labctl commission start` instead of the
individual build/demo route. It runs Gates A/B with retained logs, then requires
live PLC evidence. Preserve its printed run directory and use
[status/resume/record](commissioning-orchestrator.md).
A manual-evidence pause is expected; it is not a complete commissioning result.

## Which page should open?

| Interface | Local URL | When available | What you should see |
|---|---|---|---|
| Docker course | http://127.0.0.1:8088 | After `docs up` | Static lessons, images and search |
| Native course | http://127.0.0.1:8000 | While MkDocs serves | The same lessons |
| Learning Portal | http://127.0.0.1:8500 | After process build | Model values, provenance and teaching views |
| Cargo process | http://127.0.0.1:8100/state | After process build | JSON with `ready`, `time_s`, `flowMeasured`, levels and commands |
| Cargo/PMS/Propulsion PLC | https://127.0.0.1:8443 / 8444 / 8445 | After starting those runtimes | Runtime engineering interface; project commissioning remains |
| FUXA | http://127.0.0.1:1881 | After starting FUXA | Operator/editor surface; live bindings must be configured |
| Grafana | http://127.0.0.1:3000 | After starting Grafana | Trends only after historian data is commissioned |

A blank/unbound FUXA screen is not the Learning Portal and does not prove the plant failed.
For a remote server, `127.0.0.1` in your laptop browser means your laptop.
Forward only the interface you need, for example:

```bash
ssh -L 8500:127.0.0.1:8500 your-user@your-server
```

Replace the SSH destination with your real server account; then open the local portal URL.
[Full endpoint reference](../08-reference/endpoints-and-interfaces.md)

## If a step fails

| Symptom | Inspect | Next action |
|---|---|---|
| Pull would overwrite a file | `git status --short` | Preserve the old checkout; use the separate-checkout route above |
| Python venv unavailable | Python/venv installation | Install your distribution's venv package |
| Existing venv points to a missing Python | `.venv/bin/python` | Preserve/rename that venv and recreate it with installed Python |
| Compose v2 unavailable | `docker compose version` | Install the Compose plugin matching your Docker installation |
| Cannot connect to daemon | `docker info` | Check daemon status and user access before lab commands |
| Port is occupied | `ss -ltn` and `docker compose ps` | Identify the existing service; do not kill unrelated processes |
| FMU missing or build failed | Builder output; `docker compose logs --tail=80 cargo-plant` | Resolve the first build/runtime error; smoke must pass before demos |
| Cargo pump command on, flow zero | PMS bus and `powerAvailable` | Establish supply as shown in the first exercise; then check feedback/faults |
| Stale historian after PLC stop | OPC UA Quality/timestamps | Follow the commissioned outage/recovery procedure |
| Source-drift error | Run's recorded commit | Resume with matching source or start a new run; never rewrite provenance |

Stop a temporary learning lab with `docker compose stop`; it retains containers and volumes.
Do not remove volumes to fix an unexplained error. For a systemd-managed deployment,
use the [daemon guide](server-daemon-deployment.md) so the manager does not restart it unexpectedly.

When reporting a failure, include the failing command, its error, `git rev-parse HEAD`,
`docker compose version` and relevant service logs. Redact credentials and private addresses.

Your next milestone is one explained Cargo observation. Full acceptance later requires
live PLC/OPC UA/HMI/historian commissioning, 21 verified experiment runs, reboot and restore evidence.
