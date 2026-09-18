# FailSafe Azure Foundation

## Subscription model
- Learning model: one Azure subscription
- Dev: Terraform-managed resource group
- Staging: Terraform-managed resource group
- Production: Terraform-managed resource group
- Terraform state: separate bootstrap resource group

## Rule
Never mix Terraform state between environments.