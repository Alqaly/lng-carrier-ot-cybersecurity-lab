#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
backup="${1:-}"; confirm="${2:-}"; force="${3:-}"
[ -n "$backup" ] && [ -d "$backup" ] || { echo "Usage: $0 <backup-dir> --yes [--force]" >&2; exit 2; }
( cd "$backup" && sha256sum -c SHA256SUMS )
if [ "$confirm" = "--verify" ]; then echo "PASS  backup hashes verified; no state changed"; exit 0; fi
[ "$confirm" = "--yes" ] || { echo "Restore is destructive; pass --yes (or --verify for verification only)" >&2; exit 2; }
docker compose down --remove-orphans
# Create canonical compose volumes without starting the stack.
docker compose create >/dev/null
for archive in "$backup"/*.tgz; do
  [ -e "$archive" ] || continue
  key="$(basename "$archive" .tgz)"; [ "$key" = repository-config ] && continue
  mapfile -t matches < <(docker volume ls -q | grep -E "(^|_)${key}$" || true)
  [ "${#matches[@]}" -eq 1 ] || { echo "Cannot resolve exactly one Docker volume for $key" >&2; exit 2; }
  vol="${matches[0]}"
  nonempty="$(docker run --rm -v "$vol":/target alpine:3.22 sh -c 'find /target -mindepth 1 -maxdepth 1 -print -quit' || true)"
  if [ -n "$nonempty" ] && [ "$force" != "--force" ]; then echo "Refusing to overwrite non-empty $vol; rerun with --force" >&2; exit 2; fi
  docker run --rm -v "$vol":/target -v "$(cd "$backup" && pwd)":/backup alpine:3.22 sh -c "rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true; cd /target && tar xzf /backup/$(basename "$archive")"
  echo "restored $key -> $vol"
done
echo "Restore complete. Do not claim recovery PASS until Gates A–G and a retained experiment are rerun."
