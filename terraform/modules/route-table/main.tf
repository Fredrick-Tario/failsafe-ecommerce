variable "name" {
    type = string
}

variable "resource_group_name" {
    type = string
}

variable  "location" {
    type = string
}

variable "tags" {
    type =map(string)
    default = {}
}

resource "azurerm_route_table" "this" {
  name = var.name
  resource_group_name = var.resource_group_name
  location = var.location
  tags = var.tags
}

output "id" {
    value = azurerm_route_table.this.id
}
