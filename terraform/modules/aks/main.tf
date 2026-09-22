variable "name" {
    type        = string
}

variable "resource_group_name" {
    type        = string
}

variable "location" {
    type        = string
}

variable "dns_prefix" {
    type        = string
}

variable "subnet_id" {
    type        = string
}

variable "node_count" {
    type        = number
    default     = 1
}

variable "node_vm_size" {
    type        = string
    default     = "Standard_B2s"
}

variable "tags" {
    type        = map(string)
    default     = {}
}

resource "azurerm_kubernetes_cluster" "this" {
    name                = var.name
    location            = var.location
    resource_group_name = var.resource_group_name
    dns_prefix          = var.dns_prefix
    sku_tier            = "Free"
    tags                = var.tags

    default_node_pool {
        name       = "system"
        node_count = var.node_count
        vm_size    = var.node_vm_size
        vnet_subnet_id = var.subnet_id
    }

    identity {
        type = "SystemAssigned"
    }

    network_profile {
        network_plugin    = "azure"
    }
}

output "name" {
    value = azurerm_kubernetes_cluster.this.name
}

output "id" {
    value = azurerm_kubernetes_cluster.this.id
}