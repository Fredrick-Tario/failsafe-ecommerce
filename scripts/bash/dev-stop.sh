#!/usr/bin/env bash
set -u

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)

for pidfile in "$ROOT_DIR"/pids/*.pid; do
    [[ -e "$pidfile" ]] || continue
    name=$(basename "$pidfile" .pid)
    pid=$(cat "$pidfile")

    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        echo "[STOP] $name PID $pid"
    else
        echo "[STALE] $name PID $pid not running"
    fi

    rm -f "$pidfile"
done