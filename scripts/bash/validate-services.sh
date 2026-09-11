#!/usr/bin/env bash
set -u

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
failed=0

check_port() {
  local port=$1
  if ss -ltn "sport = :$port" | grep -q LISTEN; then
    echo "[PASS] TCP port $port is listening"
  else
    echo "[FAIL] TCP port $port is not listening" >&2
    failed=1
  fi
}

for port in 8001 8002 8003 8004 8006; do
  check_port "$port"
done

if pg_isready -q; then
  echo '[PASS] PostgreSQL is accepting connections'
else
  echo '[FAIL] PostgreSQL is not ready' >&2
  failed=1
fi

if ! "$ROOT_DIR/scripts/bash/health-check.sh"; then
  failed=1
fi

exit "$failed"