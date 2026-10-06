resource "azurerm_network_security_group" "database" {
  name                = "nsg-failsafe-database-${var.environment}"
  location            = var.location
  resource_group_name = module.resource_group.name
  tags                = local.tags
}

resource "azurerm_network_security_rule" "database_from_aks" {
  name                        = "allow-postgres-from-aks"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "5432"
  source_address_prefix       = var.aks_subnet_cidr
  destination_address_prefix  = "*"
  resource_group_name         = module.resource_group.name
  network_security_group_name = azurerm_network_security_group.database.name
}

resource "azurerm_network_security_rule" "database_deny_vnet" {
  name                        = "deny-other-vnet-inbound"
  priority                    = 200
  direction                   = "Inbound"
  access                      = "Deny"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "VirtualNetwork"
  destination_address_prefix  = "*"
  resource_group_name         = module.resource_group.name
  network_security_group_name = azurerm_network_security_group.database.name
}

resource "azurerm_subnet_network_security_group_association" "database" {
  subnet_id                 = module.database_subnet.id
  network_security_group_id = azurerm_network_security_group.database.id
}

resource "azurerm_network_security_group" "monitoring" {
  name                = "nsg-failsafe-monitoring-${var.environment}"
  location            = var.location
  resource_group_name = module.resource_group.name
  tags                = local.tags
}

resource "azurerm_network_security_rule" "monitoring_from_mgmt" {
  name                        = "allow-monitoring"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_ranges     = ["3000", "9090"]
  source_address_prefix       = var.mgmt_subnet_cidr
  destination_address_prefix  = "*"
  resource_group_name         = module.resource_group.name
  network_security_group_name = azurerm_network_security_group.monitoring.name
}

resource "azurerm_network_security_rule" "monitoring_deny_vnet" {
  name                        = "deny-other-vnet-inbound"
  priority                    = 200
  direction                   = "Inbound"
  access                      = "Deny"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "VirtualNetwork"
  destination_address_prefix  = "*"
  resource_group_name         = module.resource_group.name
  network_security_group_name = azurerm_network_security_group.monitoring.name
}

resource "azurerm_subnet_network_security_group_association" "monitoring" {
  subnet_id                 = module.monitoring_subnet.id
  network_security_group_id = azurerm_network_security_group.monitoring.id
}

