#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_SRC="$ROOT/deploy/systemd/lng-ot-lab.service"
UNIT_DST="/etc/systemd/system/lng-ot-lab.service"
command -v docker >/dev/null || { echo "Docker is required" >&2; exit 1; }
docker compose version >/dev/null || { echo "Docker Compose v2 is required" >&2; exit 1; }
"$ROOT/deploy/check-secrets.sh" "$ROOT/.env"
sed "s#__PROJECT_ROOT__#$ROOT#g" "$UNIT_SRC" | sudo tee "$UNIT_DST" >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now lng-ot-lab.service
exec sudo systemctl status --no-pager lng-ot-lab.service
