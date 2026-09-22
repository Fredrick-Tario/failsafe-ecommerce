# FailSafe Cloud Environment Strategy

| Environment | Purpose | Terraform state | Apply rule |
|---|---|---|---|
| dev | Daily learning and experiments | dev.terraform.tfstate | Manual, frequent |
| staging | Pre-production validation | staging.terraform.tfstate | Manual after dev passes |
| production | Final controlled environment | prod.terraform.tfstate | Manual approval only |

## Rules
- Each environment has separate Terraform state.
- Never use production for experiments.
- Dev may use smaller SKUs.
- Staging should resemble production when testing releases.
- Production changes must come from reviewed Terraform.
- Destroy unused lab resources to control cost.