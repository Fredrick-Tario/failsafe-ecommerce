#!/usr/bin/env bash

set -e

LOCATION="southeastasia"
TFSTATE_RG="rg-failsafe-tfstate-sea"
TFSTATE_STORAGE="stfailsafetf$RANDOM"
TFSTATE_CONTAINER="tfstate"

az group create \
    --name "$TFSTATE_RG" \
    --location "$LOCATION"

az storage account create \
    --name "$TFSTATE_STORAGE" \
    --resource-group "$TFSTATE_RG" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --min-tls-version TLS1_2 

STORAGE_ID=$(az storage account show \
    --name "$TFSTATE_STORAGE" \
    --resource-group "$TFSTATE_RG" \
    --query id --output tsv)

USER_OBJECT_ID=$(az ad signed-in-user show --query id --output tsv)

MSYS_NO_PATHCONV=1 az role assignment create \
  --assignee-object-id "$USER_OBJECT_ID" \
  --assignee-principal-type User \
  --role "Storage Blob Data Contributor" \
  --scope "$STORAGE_ID"
  
az storage container create \
    --name "$TFSTATE_CONTAINER" \
    --account-name "$TFSTATE_STORAGE" \
    --auth-mode login

echo "Terraform state storage: $TFSTATE_STORAGE"
