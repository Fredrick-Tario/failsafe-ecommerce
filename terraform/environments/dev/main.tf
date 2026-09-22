locals {
    tags = {
        Project     = "FailSafe-E-Commerce"
        Environment = var.environment
        ManagedBy    = "Terraform"
        Purpose      = "SRE-Lab"
    }
}

module "resource_group" {
    source            = "../../modules/resource-group"
    name              = "vnet-failsafe-${var.environment}-sea"
    location          = var.location
    tags              = local.tags
}

module "vnet" {
    source            = "../../modules/vnet"
    name              = "vnet-failsafe-${var.environment}-sea"
    resource_group_name = module.resource_group.name
    location          = var.location
    address_space     = [var.vnet_cidr]
    tags              = local.tags
}

module "aks_subnet" {
    source            = "../../modules/subnet"
    name              = "snet-aks"
    resource_group_name = module.resource_group.name
    virtual_network_name = module.vnet.name
    address_prefixes = [var.aks_subnet_cidr]
}

module "mgmt_subnet" {
    source            = "../../modules/subnet"
    name              = "snet-mgmt"
    resource_group_name = module.resource_group.name
    virtual_network_name = module.vnet.name
    address_prefixes = [var.mgmt_subnet_cidr]
}

module "mgmt_nsg" {
    source            = "../../modules/nsg"
    name              = "nsg-failsafe-mgmt-${var.environment}"
    resource_group_name = module.resource_group.name
    location          = var.location
    admin_cidr       = var.admin_cidr
    tags              = local.tags
}

module "acr" {
    count             =  var.enable_acr ? 1 : 0
    source            = "../../modules/acr"
    name              = "acrfailsafe${var.environment}${var.unique_suffix}"
    resource_group_name = module.resource_group.name
    location          = var.location
    tags              = local.tags
}

module "key_vault" {
    count             = var.enable_key_vault ? 1 : 0
    source            = "../../modules/key-vault"
    name              = "kv-failsafe-${var.environment}-${var.unique_suffix}"
    resource_group_name = module.resource_group.name
    location          = var.location
    tenant_id         = data.azurerm_client_config.current.tenant_id
    tags              = local.tags
}

module "storage" {
    count             = var.enable_storage ? 1 : 0
    source            = "../../modules/storage"
    name              = "stfailsafe${var.environment}${var.unique_suffix}"
    resource_group_name = module.resource_group.name
    location          = var.location
    tags              = local.tags
}

module "aks" {
    count             = var.enable_aks ? 1 : 0
    source            = "../../modules/aks"
    name              = "aks-failsafe-${var.environment}-sea"
    resource_group_name = module.resource_group.name
    location          = var.location
    dns_prefix        = "failsafe-${var.environment}"
    subnet_id          = module.aks_subnet.id
    tags              = local.tags
}

module "linux_vm" {
    count             = var.enable_vm ? 1 : 0
    source            = "../../modules/linux-vm"
    name              = "vm-failsafe-mgmt-${var.environment}"
    resource_group_name = module.resource_group.name
    location          = var.location
    subnet_id          = module.mgmt_subnet.id
    nsg_id             = module.mgmt_nsg.id
    ssh_public_key_path = var.ssh_public_key_path
    tags              = local.tags
}