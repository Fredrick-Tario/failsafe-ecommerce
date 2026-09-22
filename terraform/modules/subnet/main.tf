variable name {
    type        = string
}

variable "resource_group_name" {
    type        = string
}

variable "virtual_network_name" {
    type        = string
}

variable "address_prefixes" {
    type        = list(string)
}

resource "azurerm_subnet" "this" {
    name                 = var.name
    resource_group_name  = var.resource_group_name
    virtual_network_name = var.virtual_network_name
    address_prefixes     = var.address_prefixes
}

output "name" {
    value = azurerm_subnet.this.name
}

output "id" {
    value = azurerm_subnet.this.id
}