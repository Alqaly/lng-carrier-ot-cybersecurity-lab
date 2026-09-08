#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0
check(){ if "$@" >/dev/null 2>&1; then printf 'PASS  %s
' "$*"; else printf 'FAIL  %s
' "$*"; fail=1; fi; }
printf 'LNG Carrier Virtual Engineering Lab server preflight

'
check command -v docker
check docker compose version
check docker info
check command -v python3
check command -v curl
check "$ROOT/deploy/check-secrets.sh" "$ROOT/.env"
if command -v timedatectl >/dev/null 2>&1; then
  if timedatectl show -p NTPSynchronized --value 2>/dev/null | grep -qi true; then echo 'PASS  host time synchronized'; else echo 'WARN  host time is not reported synchronized'; fi
fi
mem_kb=$(awk '/MemTotal/{print $2}' /proc/meminfo 2>/dev/null || echo 0)
echo "INFO  host RAM: ${mem_kb} kB (record only; sizing is measured with ./labctl profile-resources)"
free_kb=$(df -Pk . | awk 'NR==2{print $4}')
echo "INFO  free disk: ${free_kb} kB (commissioning capacity must include images, backups and retained evidence)"
for p in 1881 3000 4840 4841 4842 5020 5021 5022 8086 8100 8200 8300 8400 8443 8444 8445 8500 8600; do
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq "[:.]${p}$"; then echo "WARN  port $p already listening"; fi
done
exit "$fail"
