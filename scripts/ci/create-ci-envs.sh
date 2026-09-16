# !/usr/bin/env bash
set -euo pipefail

DB_PASSWORD="${POSTGRES_PASSWORD:-failsafe_ci_password}"
DB_USER="${POSTGRES_USER:-failsafe_app}"

write_env() {
    local service=$1
    local database=$2

    cat > "services/$service/.env" <<EOF
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${database}
EOF
}

write_env auth-service failsafe_auth
write_env product-service failsafe_product
write_env inventory-service failsafe_inventory
write_env order-service failsafe_order
write_env payment-service failsafe_payment

echo "AUTH_SECRET_KEY=ci-only-auth-key" >> services/auth-service/.env
