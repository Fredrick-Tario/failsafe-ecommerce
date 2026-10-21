#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"

write_env() {
    local service=$1
    local database=$2

    cat > "services/${service}/.env" <<EOF
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${database}
EOF
}

write_env auth-service failsafe_auth
write_env product-service failsafe_product
write_env inventory-service failsafe_inventory
write_env order-service failsafe_order
write_env payment-service failsafe_payment

AUTH_SECRET_KEY="$(printf 'x%.0s' {1..32})"
echo "AUTH_SECRET_KEY=${AUTH_SECRET_KEY}" >> services/auth-service/.env