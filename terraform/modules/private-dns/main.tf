variable "zone_name" {
    type = string
}

variable "resource_group_name" {
    type = string
}

variable "virtual_network_id" {
    type = string
}

variable "tags" {
    type = map(string)
    default = {}
}

resource "azurerm_private_dns_zone" "this" {
    name = var.zone_name
    resource_group_name = var.resource_group_name
    tags = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "this" {
    name = "link-failsafe-vnet"
    resource_group_name = var.resource_group_name
    private_dns_zone_name = azurerm_private_dns_zone.this.name
    virtual_network_id = var.virtual_network_id
    registration_enabled = false
    tags = var.tags
}

output "zone_name" {
    value = azurerm_private_dns_zone.this.name 
}

