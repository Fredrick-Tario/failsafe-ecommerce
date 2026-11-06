#!/usr/bin/env bash

for service in auth product inventory order payment frontend; do
  echo "Checking failsafe-$service"

  az acr repository show-tags \
    --name acrfailsafedevfse01 \
    --repository "failsafe/$service" \
    -o table
done