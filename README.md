# FailSafe E-Commerce

**A hands-on DevOps and Site Reliability Engineering (SRE) lab built around a microservices e-commerce application.**

*Build it. Deploy it. Break it. Observe it. Recover it.*

[![FailSafe CI](https://github.com/Fredrick-Tario/failsafe-ecommerce/actions/workflows/ci.yml/badge.svg)](https://github.com/Fredrick-Tario/failsafe-ecommerce/actions/workflows/ci.yml)

**Explore:** [Progress & Roadmap](ROADMAP.md) · [Project Scope](docs/planning/PROJECT_SCOPE.md) · [SRE Targets](docs/sre/SLO.md) · [CI Pipeline](.github/workflows/ci.yml)

## About

FailSafe is a **production-inspired engineering practice environment**, not a commercial online store. Its simple storefront and five backend services provide a realistic workload for learning how to **build, automate, deploy, secure, troubleshoot, and operate** distributed applications.

The goal is not to add every e-commerce feature. It is to understand what happens **after the code works**: how services communicate, how infrastructure is provisioned, what fails in deployment, and how to restore a healthy system.

## Why I Built This

I wanted to go beyond following isolated Docker, cloud, or Kubernetes tutorials. FailSafe connects those tools into one system where I can practice the full engineering lifecycle:

**Code → Test → Package → Provision → Deploy → Observe → Troubleshoot → Improve**

It is both a learning project and a record of my progress toward **DevOps, Cloud, and SRE engineering**.

## Architecture

The diagram below shows the **logical application design**. Local development uses Docker Compose; the Azure/Kubernetes environment is being validated separately.

```mermaid
flowchart TB
    User["User / Browser"] --> Web["React + TypeScript Frontend<br/>Nginx in Docker"]

    subgraph APIs["FastAPI Microservices"]
        Auth["Auth"]
        Product["Product"]
        Inventory["Inventory"]
        Order["Order"]
        Payment["Payment (simulated)"]
    end

    Web --> Auth
    Web --> Product
    Web --> Inventory
    Web --> Order
    Web --> Payment

    Order -->|Reserve stock| Inventory
    Order -->|Authorize test payment| Payment

    Auth --> DB[("PostgreSQL<br/>Five logical databases")]
    Product --> DB
    Inventory --> DB
    Order --> DB
    Payment --> DB
```

> **Design note:** Each backend service has its own logical database; the local lab runs them on a shared PostgreSQL server. Payments are simulated and no real customer or payment data is required.

### Application services

| Component | Responsibility | Local port |
|---|---|---:|
| **Frontend** | Storefront, account actions, cart, and order UI | `8000` |
| **Auth** | Registration, login, and token-based authentication | `8001` |
| **Product** | Product catalog API | `8002` |
| **Inventory** | Stock records and reservation API | `8003` |
| **Order** | Order creation and coordination with downstream services | `8004` |
| **Payment** | Simulated payment authorization | `8005` |

### Technology stack

| Area | Tools |
|---|---|
| **Application** | Python, FastAPI, React, TypeScript, Vite, Nginx |
| **Data** | PostgreSQL, SQLAlchemy, Alembic |
| **Containers & orchestration** | Docker, Docker Compose, Kubernetes, Azure Kubernetes Service (AKS) |
| **Cloud & infrastructure** | Azure, Azure Container Registry (ACR), Terraform, Ansible |
| **CI & security checks** | GitHub Actions, pytest, Ruff, Trivy, Gitleaks, pip-audit |
| **Observability foundation** | Health/readiness checks, Prometheus and Grafana configuration |

## Engineering Workflow

The repository includes an automated **CI pipeline** and scripts for manually building/pushing images to ACR. **Automated CD is a future milestone**, not a completed feature.

```mermaid
flowchart LR
    Push["Push / Pull Request"] --> CI["GitHub Actions CI"]
    CI --> Checks["Lint · Tests · Builds<br/>Dependency / Secret / Image Scans<br/>Terraform Validation"]
    Checks --> Gate{"CI gate"}
    Gate -->|Pass| Manual["Manual image publish<br/>to Azure Container Registry"]
    Manual --> AKS["AKS lab deployment"]
    Gate -.->|Planned| CD["Automated CD pipeline"]
    CD -.-> AKS
```

**Already represented in the repository:** service APIs and database migrations, a Docker Compose stack, CI jobs and security scans, Terraform environment definitions, Ansible configuration, ACR helper scripts, and initial AKS deployments/services with probes and resource settings.

**Still being developed or verified:** Kubernetes traffic routing and reliability, automated CD, production-style secret handling, application metrics, Grafana dashboards, centralized logs, load testing, and measured SLOs.

**[See the detailed, actively maintained ROADMAP.md →](ROADMAP.md)**

## Run Locally

**Prerequisites:** Git, Docker Engine or Docker Desktop with Compose v2, and a Bash-compatible shell (Linux/macOS/Git Bash).

```bash
git clone https://github.com/Fredrick-Tario/failsafe-ecommerce.git
cd failsafe-ecommerce
cp .env.example .env
```

Before starting, provide these **local-only** settings in the root `.env` file (use your own values):

```dotenv
POSTGRES_USER=failsafe
POSTGRES_PASSWORD=your-local-password
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-grafana-password
```

Each `services/<name>-service/.env` also needs a `DATABASE_URL` pointing to its own `failsafe_<name>` database. Example for `services/product-service/.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://failsafe:your-local-password@postgres:5432/failsafe_product
```

Create matching files for `auth`, `inventory`, `order`, and `payment` (replace the database suffix). Add a strong `AUTH_SECRET_KEY` to `services/auth-service/.env`. URL-encode special characters in database passwords when building connection URLs. **Never commit real `.env` files or secrets.**

Then build, start, and migrate:

```bash
docker compose up -d --build

for service in auth product inventory order payment; do
  docker compose exec -T "${service}-service" alembic upgrade head
done

docker compose ps
```

| Local endpoint | Address |
|---|---|
| Storefront | `http://localhost:8000` |
| Auth API docs | `http://localhost:8001/docs` |
| Order API docs | `http://localhost:8004/docs` |
| Prometheus (initial self-monitoring config) | `http://localhost:9090` |
| Grafana (datasource scaffold) | `http://localhost:3000` |

To stop the stack without deleting named volumes:

```bash
docker compose down
```

> **Lab status:** Some startup, reverse-proxy, and Kubernetes routing details still need end-to-end validation. See [Known Gaps](ROADMAP.md#known-gaps-to-validate) before treating this as a turnkey or production deployment.

## Repository Guide

| Path | What's inside |
|---|---|
| [`services/`](services/) | Five FastAPI microservices, models, migrations, and tests |
| [`frontend/`](frontend/) | React UI, Nginx config, and Dockerfile |
| [`kubernetes/`](kubernetes/) | AKS deployment, service, configuration, and routing manifests |
| [`terraform/`](terraform/) | Azure modules and dev/staging/production definitions |
| [`ansible/`](ansible/) | Linux host configuration and automation roles |
| [`.github/workflows/`](.github/workflows/) | CI and Azure login test workflows |
| [`monitoring/`](monitoring/) | Early Prometheus and Grafana configuration |
| [`scripts/`](scripts/) | Operational, validation, ACR, and backup helpers |
| [`docs/`](docs/) | Scope, networking, cloud, reliability, and runbooks |
| [`ROADMAP.md`](ROADMAP.md) | Completed work, current focus, planned work, and validation gaps |

## Reliability Goals

The repository defines **initial targets**, not yet measured achievements: **99.9% availability**, **p95 latency below 500 ms**, **HTTP 5xx rate below 1%**, and **order-flow success of at least 99%** in controlled tests. Measurement, dashboards, and incident exercises are planned in later milestones.

Read the [SLO document](docs/sre/SLO.md) for the current definitions.

---

**FailSafe is a learning lab under active development.** Its purpose is to make systems engineering practical: build the system, understand its failure modes, and improve its reliability one milestone at a time.

[License](LICENSE) · [Full Progress & Roadmap](ROADMAP.md)
