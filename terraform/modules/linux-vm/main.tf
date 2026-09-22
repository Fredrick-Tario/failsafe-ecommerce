variable "name" {
    type        = string
}

variable "resource_group_name" {
    type        = string
}

variable "location" {
    type        = string
}

variable "subnet_id" {
    type        = string
}

variable "nsg_id" {
    type        = string
}

variable "admin_username" {
    type        = string
    default     = "azureuser"
}

variable "ssh_public_key_path" {
    type        = string
}

variable "tags" {
    type        = map(string)
    default     = {}
}

resource "azurerm_public_ip" "this" {
    name                = "pip-${var.name}"
    resource_group_name = var.resource_group_name
    location            = var.location
    allocation_method   = "Static"
    sku                 = "Standard"
}

resource "azurerm_network_interface" "this" {
    name                = "nic-${var.name}"
    resource_group_name = var.resource_group_name
    location            = var.location

    ip_configuration {
        name            = "primary"
        subnet_id       = var.subnet_id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id = azurerm_public_ip.this.id
    }
}

resource "azurerm_network_interface_security_group_association" "this" {
    network_interface_id        = azurerm_network_interface.this.id
    network_security_group_id   = var.nsg_id
}


resource "azurerm_linux_virtual_machine" "this" {
    name                = var.name
    resource_group_name = var.resource_group_name
    location            = var.location
    size                = "Standard_B1s"
    admin_username      = var.admin_username
    network_interface_ids = [
        azurerm_network_interface.this.id,
    ]
    disable_password_authentication = true
    tags                = var.tags

    admin_ssh_key {
        username   = var.admin_username
        public_key = file(var.ssh_public_key_path)
    }

    os_disk {
        caching              = "ReadWrite"
        storage_account_type = "Standard_LRS"
    }

    source_image_reference {
        publisher = "Canonical"
        offer     = "ubuntu-24_04-lts"
        sku       = "server"
        version   = "latest"
    }
}

output "public_ip" { value = azurerm_public_ip.this.ip_address }