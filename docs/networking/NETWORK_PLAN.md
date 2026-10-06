Primary Azure region: Southeast asia

Address Spaces
Environment     VNet CIDR
dev             10.10.0.0/16
staging         10.20.0.0/16
production      10.30.0.0/16

Dev Subnets
Subnet
snet-aks        10.10.1.0/24    AKS nodes
snet-mgmt       10.10.2.0/24    Management VM
snet-database   10.10.3.0/24    Reserved database tier
snet-monitoring 10.10.4.0/24    Monitoring tier

- Never overlap environment address spaces.
- Keep one role per subnet.
- Keep room for future subnets.
- Do not expose the database subnet directly to the Internet.
- Review terraform plan before changing an existing subnet CIDR.
