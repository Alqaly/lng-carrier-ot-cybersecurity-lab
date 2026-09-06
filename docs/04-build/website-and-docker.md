# Website and Docker delivery

Publish the **course**, not your live control network. This project has three
different interfaces with different trust boundaries:

| Delivery | Audience | Contains |
|---|---|---|
| Static MkDocs website | Public readers and learners | Course, references, local-only practice tracking |
| Standalone course container | Self-hosted readers | The same static website, served by unprivileged nginx |
| Private Compose lab | Authorized local engineers | Process models, PLCs, software I/O, FUXA, historian and evidence tools |

The Learning Portal inside the OT stack is a separate runtime teaching interface.
It is not the public documentation site. The course container has no lab mounts,
credentials, shared OT networks or API reverse proxy.

## Read the website with Docker

From a checkout with Docker Compose v2 and daemon access:

```bash
./labctl docs up
```

Open **http://127.0.0.1:8088**. This command does not need `.env` or start the
26-service lab. It uses a separate Compose project and an explicit standalone
file. Startup waits for the course healthcheck. Stop only this project with:

```bash
./labctl docs down
```

Do **not** combine `compose.docs.yml` with `docker-compose.yml`; it is not a lab
overlay. The private stack remains Docker Compose v2 plus systemd on Linux.

## Build a static website without Docker

With the documentation requirements installed in your active virtual environment:

```bash
./labctl docs build
```

The generated `site/` directory is the deployable public artifact. Deploy **only
that directory** to static hosting. Do not upload the repository, `.env`, FUXA
state, raw packet captures, backups or commissioning evidence. The static course
has no server API, no analytics and no account requirement. Practice progress is
self-reported, stored in the reader's browser and exportable as a local JSON file.
Clearing browser data removes that device-local progress.

The learning script resolves assets and chapter links relative to the deployed
site root, including a repository subpath. MkDocs search and local fonts do not
require a third-party font service; external reference links still require network
access and are not bundled as locally licensed assets.

## Container boundary and provenance

The multi-stage build copies only public build inputs. A Dockerfile-specific
ignore file excludes other repository contents and common private artifacts.
The final image contains only built course pages and nginx configuration, runs
as UID/GID 101, drops Linux capabilities under Compose, has a read-only root
filesystem and uses temporary memory-backed storage. Its healthcheck proves
the course server responds, **not that the OT lab is commissioned**.

The course uses the existing Python 3.12 builder family and pinned direct MkDocs
requirement. The static server tag `nginx:1.30.4-alpine` was selected from the
[official image listing](https://hub.docker.com/_/nginx). Image tags and transitive
Python dependencies are not immutable digests; record resolved image digests and
dependency inventories with an actual release build. Do not claim bit-for-bit
reproducibility from a version tag alone.

For Internet hosting, use a managed static host or a separately administered TLS
reverse proxy that serves **only the course**. Keep the local default binding.
Changing it to all interfaces is not a security review. Never proxy PLC, FUXA,
Grafana, InfluxDB or process-control endpoints into the public course site.

## Publication checklist

- Run source review, the learning contract check and strict MkDocs build.
- Run the course-container CI job and check health, chapter and asset routes.
- Review attribution/reuse permissions and any screenshots before publication.
- Record the source commit, image digest and tests that actually ran.
- State separately whether the private lab has passed Gates A–G.
- Keep a previous static build/image for rollback; do not reset private lab volumes.

This upgrade prepares a container and static website build. It does not itself
create a hosted site, publish a registry image or promote a stable lab release.

Implementation references: [Docker build contexts and ignore files](https://docs.docker.com/build/concepts/context/)
and [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/).
