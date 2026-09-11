#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <database> <backup.dump>" >&2
    exit 2
fi

DATABASE=$1
BACKUP=$2

case "$DATABASE" in
  failsafe_auth|failsafe_product|failsafe_inventory|failsafe_order|failsafe_payment) ;;
  *)
    echo "Refusing unknown database: $DATABASE" >&2
    exit 2
    ;;
esac

if [[ ! -f "$BACKUP" ]]; then
    echo "Backup file not found: $BACKUP" >&2
    exit 2
fi

pg_restore \
    -h 127.0.0.1 \
    -U failsafe_app \
    -d "$DATABASE" \
    --clean \
    --if-exists \
    --no-owner \
    --exit-on-error \
    "$BACKUP"

echo "Restore completed for $DATABASE"
