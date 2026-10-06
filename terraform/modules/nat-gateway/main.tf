variable "name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}

resource "azurerm_public_ip" "nat" {
    name = "pip-${var.name}"
    resource_group_name = var.resource_group_name
    location = var.location
    allocation_method = "Static"
    sku = "Standard"
    tags = var.tags
}

resource "azurerm_nat_gateway" "this" {
    name = var.name
    resource_group_name = var.resource_group_name
    location = var.location
    sku_name = "Standard"
    tags = var.tags
}

resource "azurerm_nat_gateway_public_ip_association" "this" {
    nat_gateway_id = azurerm_nat_gateway.this.id
    public_ip_address_id = azurerm_public_ip.nat.id
}

resource "azurerm_subnet_nat_gateway_association" "this" {
    subnet_id = var.subnet_id
    nat_gateway_id = azurerm_nat_gateway.this.id 
}

output "id" {
  value = azurerm_nat_gateway.this.id
}

