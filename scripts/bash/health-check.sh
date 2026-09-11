#!/usr/bin/env bash
set -u

SERVICES=(
    "auth|http://127.0.0.1:8001/health"
    "product|http://127.0.0.1:8002/health"
    "inventory|http://127.0.0.1:8003/health"
    "order|http://127.0.0.1:8004/health"
    "payment|http://127.0.0.1:8006/health"
)

failures = 0

for entry in "${SERVICES[@]}"; do
    IFS='|' read -r name url <<< "$entry"
    if body=$(curl -fsS --max-time 2 "$url"); then
        printf '[PASS] %-10s %s\n' "$name" "$body"
    else
        printf '[FAIL] %-10s %s\n' "$name" "$url" >&2
        failures=$((failures + 1))
    fi
done

if ((failures > 0)); then
    echo "Health check failed for $failures service(s)." >&2
    exit 1
fi

echo 'All services are healthy.'