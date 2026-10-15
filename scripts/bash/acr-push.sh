
#!/usr/bin/env bash
set -euo pipefail

ACR_NAME="${1:?Usage: ./scripts/bash/acr-push.sh <acr-name> [version]}"
VERSION="${2:-v0.1.0}"
GIT_SHA="$(git rev-parse --short HEAD)"
LOGIN_SERVER="$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)"

# Authenticate to Azure Container Registry
az acr login --name "$ACR_NAME"

# Local Docker images and target ACR repositories
images=(
    "failsafe-auth:0.1.0|failsafe/auth"
    "failsafe-product:0.1.0|failsafe/product"
    "failsafe-inventory:0.1.0|failsafe/inventory"
    "failsafe-order:0.1.0|failsafe/order"
    "failsafe-payment:0.1.0|failsafe/payment"
    "failsafe-frontend:0.1.0|failsafe/frontend"
)

for item in "${images[@]}"; do
    local_image="${item%%|*}"
    repo="${item#*|}"

    echo "Processing $repo..."

    docker tag "$local_image" "$LOGIN_SERVER/$repo:$VERSION"
    docker tag "$local_image" "$LOGIN_SERVER/$repo:$GIT_SHA"

    docker push "$LOGIN_SERVER/$repo:$VERSION"
    docker push "$LOGIN_SERVER/$repo:$GIT_SHA"

    echo "Successfully pushed $repo"
done

echo "All FailSafe images successfully pushed to $LOGIN_SERVER"
