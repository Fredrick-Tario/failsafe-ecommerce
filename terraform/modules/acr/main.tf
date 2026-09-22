variable "name" {
    type        = string
}

variable "resource_group_name" {
    type        = string
}

variable "location" {
    type        = string
}

variable "tags" {
    type        = map(string)
    default     = {}
}

resource "azurerm_container_registry" "this" {
    name                = var.name
    location            = var.location
    resource_group_name = var.resource_group_name
    sku                 = "Basic"
    admin_enabled       = true
    tags                = var.tags
}

output "id" {
    value = azurerm_container_registry.this.id
}

output "login_server" {
    value = azurerm_container_registry.this.login_server
}