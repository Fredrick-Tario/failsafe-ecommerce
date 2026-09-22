variable "subscription_id" {
    type        = string
}

variable "location" {
    type        = string
}

variable "environment" {
    type        = string
}

variable "unique_suffix" {
    type        = string
}

variable "admin_cidr" {
    type        = string
}

variable "ssh_public_key_path" {
    type        = string
    default     = "~/.ssh/id_ed25519.pub"
}

# Cost-safe feature flags: paid workload services are off by default.
variable "enable_acr" {
    type        = bool
    default     = false
}

variable "enable_aks"{
    type        = bool
    default     = false
}

variable "enable_key_vault" {
    type        = bool
    default     = false
}

variable "enable_storage" {
    type        = bool
    default     = false
}

variable "enable_vm" {
    type        = bool
    default     = false
}

variable "vnet_cidr" {
    type        = string
    default     = "10.10.0.0/16"
}

variable "aks_subnet_cidr" {
    type        = string
    default     = "10.10.1.0/24"
}

variable "mgmt_subnet_cidr" {
    type        = string
    default     = "10.10.2.0/24"
}