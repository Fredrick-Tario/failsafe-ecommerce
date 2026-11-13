<div align="center">

# FailSafe E-Commerce

**A production-inspired DevOps, Cloud, and Site Reliability Engineering lab.**

*Build it. Deploy it. Break it. Observe it. Recover it.*

[![FailSafe CI](https://github.com/Fredrick-Tario/failsafe-ecommerce/actions/workflows/ci.yml/badge.svg)](https://github.com/Fredrick-Tario/failsafe-ecommerce/actions/workflows/ci.yml)

[Architecture](#architecture-at-a-glance) · [Docker](#2-docker-compose-how-the-services-connect) · [Azure](#4-azure-how-the-infrastructure-connects) · [Kubernetes](#5-kubernetes-how-the-cluster-connects) · [CI Pipeline](#6-cicd-and-security-checks) · [Roadmap](ROADMAP.md)

</div>

---

## About

**FailSafe E-Commerce** is a hands-on engineering environment built around a simplified e-commerce application. The storefront is the workload; **reliability and operations are the real project**.

Five Python/FastAPI services, a React frontend, and PostgreSQL create a small but connected system where I can practice the engineering work surrounding an application: containerization, infrastructure as code, delivery pipelines, cloud networking, orchestration, security, observability, and incident response.

It is a **learning lab, not a commercial store or production-ready payment platform**. Payments are simulated, and the cloud lab is intentionally provisioned only when needed to control costs.

### Why I built it

I wanted to understand how technologies work **together**, not just how to run their commands individually. A working API is only the beginning: What happens when a service becomes unavailable? How does a request reach a container? How are images delivered to a cluster? How do I find a failed dependency, recover a deployment, or prove the system is healthy?

FailSafe gives those questions a concrete environment.

> **Engineering goal:** Understand the entire path from source code to a running, observable, and recoverable system—and document what is implemented, what has been tested, and what still needs work.

### Project at a glance

| Area | Current state |
| --- | --- |
| **Application** | Five FastAPI services, PostgreSQL, React/TypeScript UI |
| **Local runtime** | Dockerfiles, Docker Compose, Nginx, health checks |
| **Automation** | GitHub Actions CI, tests, image builds, quality/security scans |
| **Azure** | Terraform modules, VNet/subnets, optional ACR/AKS and supporting resources |
| **Kubernetes** | Deployments, Services, ConfigMap, Secret references, resource limits, probes |
| **Current engineering focus** | AKS networking, routing, and repeatable end-to-end validation |
| **Still planned** | Automated CD, autoscaling, mature secret delivery, application metrics, dashboards, incident drills |

**Progress details:** [ROADMAP.md](ROADMAP.md) separates **implemented**, **in progress**, and **planned** work. Files and configuration in the repository do not, by themselves, prove that an environment is currently running or production-ready.

---

## Architecture at a glance

FailSafe has three interconnected layers:

1. **Application layer:** the storefront, APIs, and per-service data boundaries.
2. **Delivery and infrastructure layer:** GitHub Actions, Docker images, Terraform, Azure, and ACR.
3. **Runtime and operations layer:** Docker Compose locally, AKS in Azure, health checks, and evolving observability.

```mermaid
flowchart TB
    Code["Source code"] --> CI["GitHub Actions<br/>CI checks"]
    CI -. "manual publish" .-> ACR["Azure registry<br/>ACR"]
    TF["Terraform"] --> AKS["Azure AKS"]
    ACR --> AKS

    Browser["Browser"] --> Web["React UI<br/>Nginx"]
    Web --> API["Five FastAPI<br/>services"]
    API --> DB[("PostgreSQL<br/>five databases")]

    AKS -. "hosts" .-> Web
    AKS -. "hosts" .-> API
```

**Read this as a logical overview, not a claim of fully automated deployment.** Docker images can be manually published to ACR; the [automated CD phase](ROADMAP.md#next-milestones) is still ahead. Local Compose and Azure/AKS are two ways to run the application, not one always-on environment.

---

## 1. The application and its responsibilities

A small e-commerce workload is enough to create meaningful dependencies, failures, and operational decisions.

| Component | Responsibility | Local port |
| --- | --- | ---: |
| **Frontend** | Storefront UI, account access, cart, and ordering | `8000` |
| **Auth API** | Registration, login, JWT-based authentication | `8001` |
| **Product API** | Product catalog and product data | `8002` |
| **Inventory API** | Stock availability and reservation | `8003` |
| **Order API** | Order creation, coordination, and status | `8004` |
| **Payment API** | Simulated payment authorization—no real charges | `8005` |
| **PostgreSQL** | Five service-specific logical databases | `5432` |

The **Order API** coordinates the important cross-service workflow: reserve inventory, request test payment authorization, then persist the order. Communication currently uses synchronous HTTP calls, which makes timeouts and downstream failures visible and testable.

### Example: an order moving through the system

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant Web as Frontend
    participant Order as Order API
    participant Stock as Inventory API
    participant Pay as Payment API
    participant DB as PostgreSQL

    Customer->>Web: Place order
    Web->>Order: Create order
    Order->>Stock: Reserve stock
    Stock-->>Order: Reservation result
    Order->>Pay: Authorize test payment
    Pay-->>Order: Payment status
    Order->>DB: Save order and items
    DB-->>Order: Database result
    Order-->>Web: Order response
    Web-->>Customer: Show result
```

**What this design teaches:** A successful request depends on more than the Order API being online. Inventory, payment, networking, timeouts, and the database all affect the outcome. The present flow is a practice implementation: compensating reservations and more robust distributed-transaction handling are future reliability improvements.

> The sequence above is the **intended successful business flow**. The current Nginx API prefix configuration still needs an end-to-end routing fix before treating browser checkout as validated.

---

## 2. Docker Compose: how the services connect

Local development uses **one Docker Compose project** and the user-defined bridge network `failsafe-net`. Containers discover each other through Compose service names, while selected ports are published to the host for local testing.

```mermaid
flowchart TB
    User["Browser"] --> Web["Frontend<br/>Nginx :8000"]

    subgraph Compose["Docker Compose network"]
        Web --> Auth["Auth<br/>:8001"]
        Web --> Product["Product<br/>:8002"]
        Web --> Inventory["Inventory<br/>:8003"]
        Web --> Order["Order<br/>:8004"]
        Web --> Payment["Payment<br/>:8005"]

        Order -->|reserve| Inventory
        Order -->|authorize| Payment

        Auth --> Postgres[("PostgreSQL<br/>:5432")]
        Product --> Postgres
        Inventory --> Postgres
        Order --> Postgres
        Payment --> Postgres
    end
```

**Connections and decisions**

- **Nginx** serves the built React frontend and is intended to reverse-proxy `/api/` requests to the appropriate FastAPI containers.
- **Docker DNS** resolves names such as `inventory-service` and `payment-service` inside the Compose network—no hard-coded container IPs are needed.
- **`depends_on` + health checks** help control startup order; API `/health` endpoints provide lightweight process checks.
- **PostgreSQL** is one server/container with **five distinct logical databases** (`failsafe_auth`, `failsafe_product`, `failsafe_inventory`, `failsafe_order`, and `failsafe_payment`), not five separate database servers.
- **Named volumes** retain local PostgreSQL, Prometheus, and Grafana data across ordinary container restarts. The local database has a different persistence setup from the current Kubernetes lab.

### Database boundaries

| Service | Database | Reason for separating it |
| --- | --- | --- |
| Auth | `failsafe_auth` | Isolates user and identity data |
| Product | `failsafe_product` | Owns catalog data |
| Inventory | `failsafe_inventory` | Owns stock records |
| Order | `failsafe_order` | Owns orders and order items |
| Payment | `failsafe_payment` | Owns simulated payment records |

This separation gives each service ownership of its data model while keeping the learning environment inexpensive. It is **logical isolation on a shared PostgreSQL instance**, not full infrastructure-level database independence.

### Why Docker is used here

Containers package the service runtime and dependencies into repeatable images. Compose provides a convenient local integration environment; the **same containerized service architecture** can then be deployed to Kubernetes, where networking, health management, rollout behavior, and resource controls are different.

---

## 3. From code to container images

A Dockerfile exists for each FastAPI service and for the frontend. The frontend image builds the React/Vite application and serves the resulting static files through Nginx. The Python images run their individual APIs.

```mermaid
flowchart LR
    Code["Source"] --> Build["Docker build"]
    Build --> Images["Six images"]
    Images --> Local["Compose<br/>local runtime"]
    Images -. "manual push" .-> ACR["ACR"]
    ACR --> AKS["AKS<br/>image pull"]
```

**Image set:** `auth`, `product`, `inventory`, `order`, `payment`, and `frontend`. The helper [`scripts/bash/acr-push.sh`](scripts/bash/acr-push.sh) tags and publishes the six images to Azure Container Registry. It uses a version tag and the short Git commit SHA to help identify builds.

**Why tagging matters:** A deployable image should point to a specific build. Later, the CD pipeline can promote and roll back known image versions instead of relying on an ambiguous moving tag.

---

## 4. Azure: how the infrastructure connects

Azure is the cloud deployment environment. **Terraform** defines the resources; **Ansible** contains configuration automation for the optional management VM. Azure paid services are controlled with opt-in flags in the development environment to keep the practice lab cost-conscious.

### Infrastructure map

```mermaid
flowchart TB
    TF["Terraform"] --> RG

    subgraph Azure["Azure - Southeast Asia"]
        RG["Resource group"] --> VNet["Virtual network"]
        VNet --> AS["AKS subnet"]
        VNet --> MS["Mgmt subnet"]
        VNet --> DS["DB subnet"]
        VNet --> OS["Monitor subnet"]

        AS --> AKS["AKS cluster"]
        MS --> VM["Linux VM"]

        RG --> ACR["ACR registry"]
        RG --> Vault["Key Vault"]
        RG --> Storage["Storage"]
    end
```

**Diagram note:** This illustrates resources covered by the Terraform design. **ACR, AKS, Key Vault, storage, and the management VM are optional resources** in the dev configuration; the diagram does not mean they are all running or deployed simultaneously. Database and monitoring subnets are network segments, not proof that managed database or monitoring services have been provisioned.

### What each Azure component does

| Component | Role in FailSafe |
| --- | --- |
| **Resource group** | Groups Azure resources for organized lifecycle management |
| **Virtual Network (VNet)** | Provides the private network address space |
| **Subnets** | Separate AKS, management, database, and monitoring network roles |
| **AKS** | Runs and manages containerized Kubernetes workloads |
| **ACR** | Stores versioned application container images |
| **Network security / routes** | Controls access and traffic paths through NSGs and route-table definitions |
| **Key Vault** | Provisioning capability exists; workload secret integration is a later hardening step |
| **Storage** | Terraform storage module and separate state-management design |
| **Management VM + Ansible** | Optional Linux host for configuration and operational practice |

### Build-to-Azure relationship

```mermaid
flowchart LR
    Git["GitHub"] --> CI["Actions CI"]
    CI -. "manual" .-> Push["Push images"]
    Push --> ACR["Azure ACR"]
    ACR --> AKS["AKS Pods"]
    TF["Terraform"] --> AKS
```

**Understanding the boundaries:** Terraform creates infrastructure; ACR stores images; AKS pulls and runs them. None of those roles replaces the others. The repository currently has a **CI pipeline and manual ACR publishing helpers**, while automated deployment to AKS is a planned CD milestone.

**Cost strategy:** Development resources such as AKS and ACR can be turned off via Terraform feature flags and recreated for exercises. Resource teardown should always be followed by a cost check—turning off one component does not guarantee the entire Azure subscription has no charges.

---

## 5. Kubernetes: how the cluster connects

Kubernetes manages the containers after deployment. The checked-in manifests define a `failsafe-dev` Namespace, ConfigMap, example Secret, Deployments, ClusterIP Services, health probes, resource requests/limits, and initial Gateway API routing resources.

### Intended network and request path

```mermaid
flowchart TB
    Client["Browser"] --> Route

    subgraph Cluster["Azure AKS cluster"]
        Route["Gateway<br/>HTTPRoute"]
        subgraph NS["failsafe-dev namespace"]
            Route --> WebSvc["Frontend<br/>Service"]
            WebSvc --> WebPod["Frontend<br/>Pod"]

            WebPod --> AuthSvc["Auth Svc"]
            WebPod --> ProdSvc["Product Svc"]
            WebPod --> InvSvc["Inventory Svc"]
            WebPod --> OrderSvc["Order Svc"]
            WebPod --> PaySvc["Payment Svc"]

            AuthSvc --> AuthPod["Auth Pod"]
            ProdSvc --> ProdPod["Product Pod"]
            InvSvc --> InvPod["Inventory Pod"]
            OrderSvc --> OrderPod["Order Pod"]
            PaySvc --> PayPod["Payment Pod"]

            OrderPod --> InvSvc
            OrderPod --> PaySvc

            AuthPod --> DbSvc["Postgres Svc"]
            ProdPod --> DbSvc
            InvPod --> DbSvc
            OrderPod --> DbSvc
            PayPod --> DbSvc
            DbSvc --> DbPod["Postgres Pod"]
        end
    end
```

*This diagram describes the **target request path**, not a verified public endpoint. The checked-in Gateway/HTTPRoute manifests and Nginx proxy paths need correction/validation; see [Known validation gaps](#known-validation-gaps).*

### Kubernetes objects and why they matter

| Object | What it does in this project |
| --- | --- |
| **Namespace** | Groups the lab workloads under `failsafe-dev` |
| **Deployment** | Declares the desired application Pods and container images |
| **Pod** | Runs one application or database container instance |
| **Service** | Gives Pods stable in-cluster names and ports |
| **ConfigMap** | Holds non-secret settings and downstream service URLs |
| **Secret** | Provides database credentials and other sensitive values to Pods |
| **Probes** | Check whether containers are alive and ready to receive traffic |
| **Requests / limits** | Express expected CPU/memory use and constrain resource consumption |
| **Gateway / HTTPRoute** | Intended entry-point and route from external traffic to the frontend |

The key idea is **Pods are replaceable; Services provide stable addresses**. For example, the Order Pod reaches `inventory-service:8003` and `payment-service:8005` by Service name. Kubernetes DNS resolves those names to a Service, which forwards traffic to matching Pods.

### How a Service finds a Pod

```mermaid
flowchart LR
    Caller["Order Pod"] --> DNS["Cluster DNS"]
    DNS --> Svc["Inventory<br/>Service"]
    Svc --> Pod["Inventory<br/>Pod"]
    Config["ConfigMap"] -. "URL" .-> Caller
    Secret["Secret"] -. "DB auth" .-> Pod
```

The `Service` uses selectors to find Pods with matching labels. Liveness/readiness probes influence health and whether workloads should receive traffic; they do **not** by themselves guarantee business-level reliability.

> **Current database limitation:** The Kubernetes PostgreSQL Deployment uses `emptyDir` storage, which is temporary. It is acceptable for a disposable learning lab but **not persistent storage for a production database**. A PersistentVolumeClaim or a suitable managed data service would be needed for durable state.

---

## 6. CI/CD and security checks

GitHub Actions runs **continuous integration (CI)** on pushes and pull requests to `main` and supports manual workflow dispatch. The configured pipeline aims to catch problems *before* changes become deployment candidates.

### CI quality gate

```mermaid
flowchart TB
    Change["Push or PR"] --> CI["GitHub Actions"]

    subgraph Jobs["Parallel CI jobs"]
        Lint["Ruff lint"]
        Unit["Unit tests"]
        E2E["Integration tests"]
        Build["Docker build"]
        Audit["Dependency audit"]
        Secrets["Secret scan"]
        Trivy["Image scan"]
        TF["Terraform check"]
    end

    CI --> Lint
    CI --> Unit
    CI --> E2E
    CI --> Build
    CI --> Audit
    CI --> Secrets
    CI --> Trivy
    CI --> TF

    Lint --> Gate{"CI gate"}
    Unit --> Gate
    E2E --> Gate
    Build --> Gate
    Audit --> Gate
    Secrets --> Gate
    Trivy --> Gate
    TF --> Gate

    Gate -->|pass| Ready["Build candidate"]
    Gate -->|fail| Fix["Fix and rerun"]
```

| Job | Purpose | Tooling |
| --- | --- | --- |
| Lint | Catch style and basic code issues | Ruff |
| Unit tests | Check existing service behavior | pytest |
| Integration tests | Run the stack and exercise the order flow | Docker Compose + pytest |
| Docker builds | Ensure containers can be built | Docker |
| Dependency audit | Check Python and frontend dependencies | pip-audit, npm audit |
| Secret scan | Detect accidentally committed credentials | Gitleaks |
| Container scan | Inspect image vulnerabilities | Trivy |
| Terraform check | Check formatting and validate infrastructure definitions | Terraform |
| CI gate | Require the listed jobs to succeed | GitHub Actions |

**CI is not CD.** The current workflow tests and validates code; it does **not automatically deploy each successful commit to AKS**. Image publishing and AKS deployment are currently separate procedures. The planned CD phase will connect tested images, deployment approval/gating, rollout verification, and rollback.

**Security approach:** Start with secret scanning, dependency scanning, image scanning, isolated network boundaries, and Kubernetes Secret references; then improve least-privilege access, Key Vault integration, policy enforcement, and credentials rotation as the project grows. These scans are safeguards—not a claim of complete security.

---

## 7. Observability and reliability

The lab includes **health and readiness endpoints**, operational scripts, initial SLO targets, and starter Prometheus/Grafana configuration. Fully measured application observability is still on the roadmap.

```mermaid
flowchart LR
    Grafana["Grafana"] -->|query| Prom["Prometheus"]
    Prom -->|scrape| Self["Prometheus<br/>itself"]
    Prom -. "planned" .-> API["API metrics"]
    Logs["App logs"] -. "planned" .-> Store["Central logs"]
```

At the checked-in state, Prometheus is configured to **scrape itself**, and Grafana has a Prometheus data-source configuration. Application `/metrics` endpoints, useful dashboards, alerts, and centralized log aggregation are **not yet completed**.

### Initial reliability targets

These targets are defined in [`docs/sre/SLO.md`](docs/sre/SLO.md); they are **objectives, not measured achievements**.

| Indicator | Initial target |
| --- | --- |
| Availability | At least **99.9%** |
| p95 latency | Below **500 ms** during normal lab load |
| HTTP 5xx error rate | Below **1%** |
| Critical order-flow success | At least **99%** in controlled tests |

The long-term aim is to connect **signals → diagnosis → recovery**: collect meaningful metrics and logs, use dashboards and alerts, deliberately introduce failures, then capture the fix and lessons in an incident report.

---

## 8. Run locally

> **Prerequisites:** Git, Docker with Compose v2, Bash (Linux/macOS/Git Bash), and optionally OpenSSL for generating a local authentication key. This is a development-lab setup, not a production deployment guide.

### 1. Clone and configure

```bash
git clone https://github.com/Fredrick-Tario/failsafe-ecommerce.git
cd failsafe-ecommerce
cp .env.example .env
```

Add the variables required by `compose.yaml` to your **local** root `.env` file:

```dotenv
POSTGRES_USER=failsafe
POSTGRES_PASSWORD=replace-with-local-password
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=replace-with-local-password
```

Each API needs its own environment file, with a connection URL to its logical database. For example, create `services/product-service/.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://failsafe:replace-with-local-password@postgres:5432/failsafe_product
```

Repeat for `auth`, `inventory`, `order`, and `payment`, changing the last database name accordingly. Also add `AUTH_SECRET_KEY` to `services/auth-service/.env`; generate a strong random value (for example with `openssl rand -hex 32`). If a password contains reserved URI characters, percent-encode it in the connection URL.

**Never commit real `.env` files, credentials, Terraform state files, or runtime database dumps.**

### 2. Start and initialize

```bash
docker compose up -d --build

for service in auth product inventory order payment; do
  docker compose exec -T "${service}-service" alembic upgrade head
done

docker compose ps
```

### 3. Inspect the services

| Component | Local URL |
| --- | --- |
| Frontend | <http://localhost:8000> |
| Auth API docs | <http://localhost:8001/docs> |
| Product API docs | <http://localhost:8002/docs> |
| Order API docs | <http://localhost:8004/docs> |
| Prometheus | <http://localhost:9090> |
| Grafana | <http://localhost:3000> |

```bash
# Individual service health
curl -fsS http://localhost:8001/health
curl -fsS http://localhost:8004/health

# Review container state and logs
docker compose ps
docker compose logs --tail=100 order-service

# Stop without deleting named volumes
docker compose down
```

**Setup caveat:** The existing `.env.example` is incomplete, and the checked-in Nginx routing rules have known path issues. You may need to resolve those gaps before the entire storefront flow works from the browser. API endpoints can still be inspected individually. Avoid `docker compose down -v` unless you intentionally want to delete named-volume data.

---

## 9. Repository map

```text
failsafe-ecommerce/
├── .github/workflows/       # CI and Azure login checks
├── services/                # Five FastAPI services
├── frontend/                # React, Vite, Nginx
├── database/                # Initialization and seeds
├── kubernetes/base/         # Deployments, Services, routing
├── terraform/               # Azure modules and environments
├── ansible/                 # Host automation and roles
├── monitoring/              # Prometheus and Grafana setup
├── scripts/                 # ACR, backup, health, ops tools
├── tests/                   # Integration tests
├── docs/                    # Planning, cloud, SRE, runbooks
├── compose.yaml             # Local container stack
├── ROADMAP.md               # Progress and future work
└── README.md                # Project overview
```

### Documentation

- **[Progress & roadmap](ROADMAP.md)** — what is implemented, in progress, and planned
- **[Project scope](docs/planning/PROJECT_SCOPE.md)** — project boundaries and learning outcomes
- **[Azure foundation](docs/cloud/AZURE_FOUNDATION.md)** — environment strategy
- **[Networking plan](docs/networking/NETWORK_PLAN.md)** — VNets, subnets, and CIDR allocations
- **[Initial SLOs](docs/sre/SLO.md)** — reliability targets
- **[CI workflow](.github/workflows/ci.yml)** — actual automated checks
- **[Kubernetes manifests](kubernetes/base/)** — declared runtime components

---

## 10. Progress and what's next

The README explains **what FailSafe is and how its pieces fit**. The separate [**ROADMAP.md**](ROADMAP.md) tracks implementation and verification status so this page stays readable.

| Implemented foundations | Current focus | Planned next |
| --- | --- | --- |
| Five APIs, databases, migrations | Kubernetes routing and DNS | Scaling and resilience tests |
| React UI and Compose stack | Gateway/HTTPRoute validation | Automated AKS deployment |
| GitHub Actions CI and scans | End-to-end API routing checks | Key Vault/workload security |
| Terraform, Ansible, ACR helpers | Repeatable AKS lab verification | Prometheus app metrics and Grafana dashboards |
| Kubernetes Deployments and Services | Probes, connectivity and traffic checks | Centralized logs, measured SLOs, incidents |

### Known validation gaps

The following are **issues found in source configuration**, not evidence of a presently running production outage:

1. [`kubernetes/base/gateway.yaml`](kubernetes/base/gateway.yaml) uses `apiversion` instead of `apiVersion`; check Gateway/HTTPRoute namespace and controller compatibility as well.
2. [`frontend/nginx.conf`](frontend/nginx.conf) forwards `/api/` paths without the needed prefix rewriting; frontend and payment route naming are not fully consistent.
3. [`scripts/bash/health-check.sh`](scripts/bash/health-check.sh) has a Bash assignment typo (`failures = 0` instead of `failures=0`).
4. The AKS PostgreSQL Pod uses **temporary `emptyDir` storage**; durable database storage remains a separate design task.
5. Prometheus/Grafana configuration is **a foundation**, not yet application-level observability.
6. Tracked backup dumps and generated Terraform plan artifacts should be reviewed and sanitized before broad sharing.

**See [ROADMAP.md](ROADMAP.md) for the complete milestone list and progress checklist.**

---

## What this project demonstrates

FailSafe is designed to exercise practical engineering judgment—not just collect technologies:

- **Application architecture:** service boundaries, API contracts, database ownership, downstream dependencies, and failure handling.
- **Platform engineering:** images, networking, DNS, volumes, Kubernetes Services, configuration, probes, and resource controls.
- **Cloud engineering:** infrastructure as code, Azure networking, isolated environments, resource lifecycles, and cost-aware provisioning.
- **DevOps:** reproducible builds, quality gates, automated tests, security checks, and evolving deployment automation.
- **SRE:** defining measurable objectives, observing failure modes, validating recovery, and documenting incidents.

The engineering journey is incremental: **build → validate → deploy → observe → fail → recover → improve**.

---

<div align="center">

**FailSafe E-Commerce is an evolving engineering lab, built to learn how real systems behave under change and failure.**

[View progress](ROADMAP.md) · [Explore the code](https://github.com/Fredrick-Tario/failsafe-ecommerce) · [MIT License](LICENSE)

</div>
