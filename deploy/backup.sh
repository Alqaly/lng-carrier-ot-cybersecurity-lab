#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
out="${1:-backups/$(date -u +%Y%m%dT%H%M%SZ)}"; mode="${2:---cold}"
mkdir -p "$out"; out_abs="$(cd "$out" && pwd)"
if [ "$mode" != "--cold" ]; then echo "Reference backup requires --cold to quiesce persistent runtime state" >&2; exit 2; fi
was_running=0
if docker compose ps --status running --services 2>/dev/null | grep -q .; then was_running=1; docker compose stop; fi
restore_runtime(){ if [ "$was_running" -eq 1 ]; then docker compose up -d; fi; }
trap restore_runtime EXIT
# Source/config snapshot. Secrets and volatile/recreated evidence are deliberately excluded.
tar --exclude=.env --exclude=backups --exclude=evidence --exclude=.git --exclude=.pytest_cache --exclude='**/__pycache__' -czf "$out/repository-config.tgz" .
for v in plant-fmu openplc-cargo-data openplc-pms-data openplc-propulsion-data alarm-data influx-data; do
  mapfile -t matches < <(docker volume ls -q | grep -E "(^|_)${v}$" || true)
  if [ "${#matches[@]}" -gt 1 ]; then echo "Ambiguous volume mapping for $v: ${matches[*]}" >&2; exit 2; fi
  if [ "${#matches[@]}" -eq 1 ]; then
    docker run --rm -v "${matches[0]}":/source:ro -v "$out_abs":/backup alpine:3.22 sh -c "cd /source && tar czf /backup/${v}.tgz ."
  else echo "skip $v (not created yet)"; fi
done
( cd "$out" && sha256sum *.tgz > SHA256SUMS )
cat > "$out/backup-metadata.json" <<EOF
{"created_at_utc":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","mode":"cold","git_commit":"$(git rev-parse HEAD 2>/dev/null || true)","note":".env is intentionally excluded; secret recovery is separate"}
EOF
printf 'Cold backup written to %s\n' "$out"
