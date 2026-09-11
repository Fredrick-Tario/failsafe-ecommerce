#!/usr/bin/env bash
set -euo pipefail

THRESHOLD=${1:-80}
USAGE=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')

if (( USAGE > THRESHOLD )); then
    echo "[ALERT] Root filesystem usage is at ${USAGE}% (threshold ${THRESHOLD}%)" >&2
    exit 1
fi

echo "[OK] Root filesystem usage is at ${USAGE}% (threshold ${THRESHOLD}%)"