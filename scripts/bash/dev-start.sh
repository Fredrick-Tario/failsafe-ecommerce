#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
PYHTON="$ROOT_DIR/.venv/Scripts/python"
mkdir -p "$ROOT_DIR/logs" "$ROOT_DIR/pids"

start_service() {
    local name=$1
    local port=$2
    local dir=$3
    local pidfile="$ROOT_DIR/pids/$name.pid"
    local logfile="$ROOT_DIR/logs/$name.log"

    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
        echo "[SKIP] $name is already running as PID $(cat "$pidfile")"
        return
    fi

    (
        cd "$ROOT_DIR/$dir"
        nohup "$PYHTON" -m uvicorn app.main:app --host 127.0.0.1 --port "$port" > "$logfile" 2>&1 &
        echo $! > "$pidfile"
    )
    echo "[START] $name on port $port"
}

start_service auth 8001 services/auth-service
start_service product 8002 services/product-service
start_service inventory 8003 services/inventory-service
start_service order 8004 services/order-service
start_service payment 8006 services/payment-service

sleep 1
"$ROOT_DIR/scripts/bash/health-check.sh"
