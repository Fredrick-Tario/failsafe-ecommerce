#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
TIMESTAMP=$(date -u '+%Y%m%d_%H%M%SZ')
DEST="$ROOT_DIR/backups/automated/$TIMESTAMP"
DATABASES=(failsafe_auth failsafe_product failsafe_inventory failsafe_order failsafe_payment)

mkdir -p "$DEST"

for db in "${DATABASES[@]}"; do
    echo "[BACKUP] $db"
    pg_dump -h 127.0.0.1 -U failsafe_app -d "$db" -F c -f "$DEST/$db.dump"
done

sha256sum "$DEST"/*.dump > "$DEST/SHA256SUMS"
printf 'created_utc=%s\n' "$TIMESTAMP" > "$DEST/manifest.txt"

printf 'Backup set created: %s\n' "$DEST"