output "resource_group_name" {
  value = module.resource_group.name
}

output "acr_login_server" {
  value = try(module.acr[0].login_server, null)
}

output "key_vault_uri" {
  value = try(module.key_vault[0].vault_uri, null)
}

output "workload_storage_name" {
  value = try(module.storage[0].name, null)
}

output "aks_name" {
  value = try(module.aks[0].name, null)
}

output "management_vm_public_ip" {
  value = try(module.linux_vm[0].public_ip, null)
}