module "database_subnet" {
  source               = "../../modules/subnet"
  name                 = "snet-database"
  resource_group_name  = module.resource_group.name
  virtual_network_name = module.vnet.name
  address_prefixes     = [var.database_subnet_cidr]
}

module "monitoring_subnet" {
  source               = "../../modules/subnet"
  name                 = "snet-monitoring"
  resource_group_name  = module.resource_group.name
  virtual_network_name = module.vnet.name
  address_prefixes     = [var.monitoring_subnet_cidr]
}

module "database_route_table" {
  source              = "../../modules/route-table"
  name                = "rt-failsafe-database-${var.environment}"
  resource_group_name = module.resource_group.name
  location            = var.location
  tags                = local.tags
}

resource "azurerm_subnet_route_table_association" "database" {
  subnet_id      = module.database_subnet.id
  route_table_id = module.database_route_table.id
}

module "monitoring_route_table" {
  source              = "../../modules/route-table"
  name                = "rt-failsafe-monitoring-${var.environment}"
  resource_group_name = module.resource_group.name
  location            = var.location
  tags                = local.tags
}

resource "azurerm_subnet_route_table_association" "monitoring" {
  subnet_id      = module.monitoring_subnet.id
  route_table_id = module.monitoring_route_table.id
}

module "private_dns" {
  count               = var.enable_private_dns ? 1 : 0
  source              = "../../modules/private-dns"
  zone_name           = "failsafe.internal"
  resource_group_name = module.resource_group.name
  virtual_network_id  = module.vnet.id
  tags                = local.tags
}