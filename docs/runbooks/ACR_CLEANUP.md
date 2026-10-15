# ACR Cleanup Runbook

## List repositories
az acr repository list --name <ACR_NAME> --output table

## List tags newest first
az acr repository show-tags \
  --name <ACR_NAME> \
  --repository failsafe/auth \
  --orderby time_desc \
  --output table

## Delete one old tag/image
az acr repository delete \
  --name <ACR_NAME> \
  --image failsafe/auth:<OLD_TAG> \
  --yes

## Delete a whole test repository when no longer needed
az acr repository delete \
  --name <ACR_NAME> \
  --repository failsafe/auth \
  --yes