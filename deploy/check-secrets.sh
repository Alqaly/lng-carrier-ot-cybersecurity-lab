#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT/.env}"
[ -f "$ENV_FILE" ] || { echo "FAIL  missing $ENV_FILE; copy .env.example and replace every placeholder" >&2; exit 2; }
mode="$(stat -c '%a' "$ENV_FILE" 2>/dev/null || stat -f '%Lp' "$ENV_FILE")"
case "$mode" in 600|400) ;; *) echo "FAIL  $ENV_FILE permissions are $mode; require 0600 or 0400" >&2; exit 2;; esac
required=(INFLUX_TOKEN INFLUX_PASSWORD GRAFANA_ADMIN_PASSWORD)
for key in "${required[@]}"; do
  value="$(awk -F= -v k="$key" '$1==k {sub(/^[^=]*=/,""); print; exit}' "$ENV_FILE")"
  [ -n "$value" ] || { echo "FAIL  $key missing/empty in $ENV_FILE" >&2; exit 2; }
  case "$value" in replace-this-*|changeme|password|token) echo "FAIL  $key still uses a placeholder" >&2; exit 2;; esac
done
echo "PASS  secret file exists, is private, and required secrets are non-placeholder"
