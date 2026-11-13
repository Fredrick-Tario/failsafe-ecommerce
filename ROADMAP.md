# FailSafe E-Commerce — Progress & Roadmap

[← Back to README](README.md) · [Project Scope](docs/planning/PROJECT_SCOPE.md) · [Initial SRE Targets](docs/sre/SLO.md)

**Last documentation review:** November 13, 2026  
**Repository snapshot checked:** `main` at [`7a2e8f1`](https://github.com/Fredrick-Tario/failsafe-ecommerce/commit/7a2e8f141b818a430f652077fb8870dd3a230242) (November 6, 2026)

This document tracks **what exists, what is being validated, and what comes next**. It describes the repository and the reported AKS milestone; it does **not** claim that every component is deployed, verified, or running continuously.

**Status guide:** `Done` = implementation exists in the repo; `Current` = next validation/engineering focus; `Planned` = substantial work remains. A checked item does not automatically mean production-ready.

## At a Glance

| Area | Status | Notes |
|---|---|---|
| Microservices and PostgreSQL | **Done** | Five FastAPI services, models, and Alembic migrations |
| React frontend and Docker Compose | **Done (foundation)** | UI, Nginx, Dockerfiles, and Compose stack exist; routing needs validation |
| CI and automated checks | **Done (configured)** | GitHub Actions jobs for lint, tests, scans, builds, and Terraform validation |
| Azure / Terraform / Ansible | **Done (foundation)** | Reusable modules, environments, configuration roles, cost-safe feature flags |
| ACR and AKS foundation | **Done / validating** | Deployment manifests, probes, scripts; latest commit reports tested AKS and image validation |
| Kubernetes networking | **Current** | Gateway/HTTPRoute definitions exist; confirm traffic paths and policies |
| Kubernetes scaling and reliability | **Planned** | HPA, disruption handling, resilience tests |
| Automated CD | **Planned** | CI exists; continuous deployment workflow not yet implemented |
| Secrets and security hardening | **Planned** | Basic secret references/scans exist; advanced integration remains |
| Prometheus application monitoring | **Planned** | Compose + Prometheus self-scrape configuration exist |
| Grafana dashboards | **Planned** | Grafana Compose service and datasource provisioning exist |
| Centralized logging and SRE validation | **Planned** | Basic logs, scripts, and SLO targets exist; full platform/measurements remain |

## Implemented Foundations

### Application and local environment

- [x] Auth, product, inventory, order, and simulated payment APIs using FastAPI
- [x] PostgreSQL databases, SQLAlchemy models, and Alembic migrations
- [x] Order service calling inventory reservation and simulated payment authorization
- [x] React + TypeScript frontend and Nginx container configuration
- [x] Dockerfiles, Docker Compose networking, and health checks
- [x] Integration test for the order flow and initial auth/security test

### CI, infrastructure, and operations

- [x] GitHub Actions CI with linting, tests, Docker builds, and a required-results gate
- [x] Dependency audits, secret scanning (Gitleaks), image scanning (Trivy), and Terraform validation
- [x] Terraform modules for Azure infrastructure, including networking, ACR, AKS, storage, and Key Vault resources
- [x] Dev/staging/production Terraform environment definitions (not proof all are deployed)
- [x] Cost-control variables to disable paid Azure resources when not needed
- [x] Ansible base-role and management-host configuration files
- [x] Scripts for ACR image publication, backup/restore, and operational checks

### Kubernetes foundation (Step 16)

- [x] `failsafe-dev` Namespace, ConfigMap, example Secret, and ClusterIP services
- [x] Service and PostgreSQL Deployment manifests
- [x] Resource requests/limits and health/readiness probes in Kubernetes manifests
- [x] ACR image-tag/push helpers and initial AKS configuration
- [x] Latest commit reports AKS tested and working; rerun deployment verification when resuming the cloud lab

> These are **repository implementation milestones**. Runtime behavior, public routing, security, and reliability still need validation.

## Current Focus — Kubernetes Validation & Networking (Steps 16–17)

The latest visible work is on the AKS foundation. The most useful next work is to **make application access and in-cluster networking reproducible**, rather than immediately adding another tool.

- [ ] Recreate the cost-controlled Azure/AKS lab and document the successful verification commands
- [ ] Fix/validate the Gateway and HTTPRoute manifests and confirm browser-to-frontend access
- [ ] Verify Nginx API path rewrites and frontend-to-backend requests inside containers
- [ ] Confirm internal DNS, service endpoints, pod readiness, and downstream connectivity
- [ ] Define and test appropriate Kubernetes NetworkPolicies
- [ ] Record a repeatable success checklist: images pulled, pods ready, APIs reachable, order test passes

**Definition of done:** the storefront and core APIs are reachable through the intended routes, an order test passes, and the validation can be repeated after tearing down and recreating the lab.

## Next Milestones

| Step | Phase | What will be added or verified |
|---:|---|---|
| **18** | Kubernetes Scaling & Reliability | HPA, rollout/rollback, disruption handling, resource tuning, and controlled failure tests |
| **19** | GitHub Actions CD | Versioned images, gated deployments to AKS, and deployment verification/rollback |
| **20** | Secrets & Security | Safer secret delivery, RBAC, least privilege, network controls, and image/policy hardening |
| **21** | Prometheus Monitoring | Application `/metrics`, service discovery/scraping, alerts, and useful operational metrics |
| **22** | Grafana Observability | Dashboards for availability, latency, errors, saturation, and service health |
| **23** | Logging & Troubleshooting | Structured/centralized logs, troubleshooting queries, and actionable incident runbooks |
| **24** | SRE Metrics & Reliability Targets | Measured SLIs/SLOs, load tests, incident drills, and postmortems |

### Later extensions (optional)

- [ ] Load and chaos-style experiments with documented hypotheses and results
- [ ] Automated reliability reporting and operational scorecards
- [ ] Deployment cost comparison and reproducible cost-saving teardown
- [ ] Demonstrate one complete incident: detection → diagnosis → mitigation → postmortem

---

**Project principle:** Every tool should support a real engineering outcome: faster delivery, safer changes, better visibility, or more reliable recovery.

[← Back to README](README.md)
