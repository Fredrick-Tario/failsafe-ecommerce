#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$[BASH_SOURCE[0]}")/../.." && pwd)
TIMESTAMP=$(date -u '+%Y%m%d_%H%M%SZ')
EVIDENCE="$ROOT_DIR/reports/evidence-$TIMESTAMP"
mkdir -p "$EVIDENCE"

cp -a "$ROOT_DIR/logs" "$EVIDENCE/application-logs" 2>/dev/null || true
uname -a > "$EVIDENCE/uname.txt"
uptime > "$EVIDENCE/uptime.txt"
df -h > "$EVIDENCE/disk.txt"
free -h > "$EVIDENCE/memory.txt"
ss -ltn > "$EVIDENCE/listening-ports.txt" 2>&1 || true
ps aux --sort=-%cpu | head -n 25 > "$EVIDENCE/top-cpu.txt" 
ps aux --sort=-%mem | head -n 25 > "$EVIDENCE/top-memory.txt"
pg_isready > "$EVIDENCE/postgres_ready.txt" 2>&1 || true

ARCHIVE="$ROOT_DIR/reports/evidence-$TIMESTAMP.tar.gz"
TAR -czf "$ARCHIVE" -C "$(dirname "$EVIDENCE")" "$(basename "$EVIDENCE")"
echo "Evidence bundle: $ARCHIVE"