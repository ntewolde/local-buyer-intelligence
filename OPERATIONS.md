# Operations Manual

## Local Buyer Intelligence Platform

This guide covers installation, daily operations, and troubleshooting for all deployment environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
   - [Option A: Local Development](#option-a-local-development)
   - [Option B: Docker Compose](#option-b-docker-compose)
   - [Option C: Kubernetes (Minikube)](#option-c-kubernetes-minikube)
   - [Option D: Production Kubernetes](#option-d-production-kubernetes)
3. [Configuration](#configuration)
4. [Startup Procedures](#startup-procedures)
5. [Shutdown Procedures](#shutdown-procedures)
6. [Daily Operations](#daily-operations)
7. [Monitoring & Logs](#monitoring--logs)
8. [Offline Handling](#offline-handling)
9. [Troubleshooting](#troubleshooting)
10. [Backup & Recovery](#backup--recovery)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Docker Desktop | Latest | Container runtime |
| Python | 3.9+ | Backend development |
| Node.js | 18+ | Frontend development |
| Git | Latest | Version control |

### Optional (for Kubernetes)

| Software | Version | Purpose |
|----------|---------|---------|
| kubectl | 1.28+ | Kubernetes CLI |
| minikube | 1.30+ | Local Kubernetes |
| Helm | 3.0+ | Package manager |

### Install Commands (macOS)

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required software
brew install python@3.11 node git

# Install Docker Desktop manually from https://docker.com/products/docker-desktop

# Install Kubernetes tools (optional)
brew install kubectl minikube helm
```

---

## Installation

### Option A: Local Development

Best for: Active development and debugging.

#### Step 1: Clone Repository

```bash
git clone https://github.com/ntewolde/local-buyer-intelligence.git
cd local-buyer-intelligence
```

#### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/local_buyer_intelligence
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
ENVIRONMENT=development
EOF
```

#### Step 3: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
EOF
```

#### Step 4: Database Setup

```bash
# Start PostgreSQL and Redis (using Docker)
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=local_buyer_intelligence \
  postgres:14-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run migrations
cd ../backend
source venv/bin/activate
alembic upgrade head
```

---

### Option B: Docker Compose

Best for: Local testing of production-like environment.

#### Step 1: Clone Repository

```bash
git clone https://github.com/ntewolde/local-buyer-intelligence.git
cd local-buyer-intelligence
```

#### Step 2: Create Environment File

```bash
cat > .env << 'EOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=local_buyer_intelligence
SECRET_KEY=docker-secret-key-change-in-production
MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
EOF
```

#### Step 3: Start Services

```bash
docker-compose up -d
```

#### Step 4: Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

---

### Option C: Kubernetes (Minikube)

Best for: Testing Kubernetes deployment locally.

#### Step 1: Start Minikube

```bash
# Start cluster
minikube start

# Enable ingress addon
minikube addons enable ingress
```

#### Step 2: Build Local Images

```bash
# Point Docker to Minikube's daemon
eval $(minikube docker-env)

# Build images
docker build -t local-buyer-intelligence-backend:local ./backend
docker build -t local-buyer-intelligence-frontend:local ./frontend \
  --build-arg NEXT_PUBLIC_API_URL=http://api.127.0.0.1.nip.io \
  --build-arg NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
```

#### Step 3: Deploy Application

```bash
# Deploy base application
kubectl apply -k k8s/overlays/local

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=backend -n local-buyer-intelligence --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n local-buyer-intelligence --timeout=120s
```

#### Step 4: Deploy Monitoring (Optional)

```bash
kubectl apply -k k8s/components/monitoring
kubectl apply -k k8s/components/logging
```

#### Step 5: Access Application

```bash
# Option 1: Port forwarding
kubectl port-forward -n local-buyer-intelligence svc/frontend-service 3000:3000 &
kubectl port-forward -n local-buyer-intelligence svc/backend-service 8000:8000 &

# Open browser
open http://localhost:3000

# Option 2: Minikube tunnel (uses ingress)
minikube tunnel
# Then access http://app.127.0.0.1.nip.io
```

---

### Option D: Production Kubernetes

Best for: Production deployment on cloud Kubernetes.

#### Prerequisites

- Kubernetes cluster (EKS, GKE, DigitalOcean, etc.)
- kubectl configured with cluster access
- Container registry access (ghcr.io)

#### Step 1: Install cert-manager (for TLS)

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.14.0 \
  --set installCRDs=true
```

#### Step 2: Configure Secrets

```bash
# Create namespace
kubectl create namespace local-buyer-intelligence

# Create secrets (replace with actual values)
kubectl create secret generic app-secrets \
  --namespace local-buyer-intelligence \
  --from-literal=SECRET_KEY='your-production-secret-key' \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/db'
```

#### Step 3: Deploy Application

```bash
kubectl apply -k k8s/overlays/production
```

#### Step 4: Deploy Components

```bash
kubectl apply -k k8s/components/tls
kubectl apply -k k8s/components/monitoring
kubectl apply -k k8s/components/logging
kubectl apply -k k8s/components/managed-db  # If using external database
```

---

## Configuration

### Environment Variables

#### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | Yes | - | Redis connection string |
| `SECRET_KEY` | Yes | - | JWT signing key (min 32 chars) |
| `MAPBOX_ACCESS_TOKEN` | No | - | Mapbox API token for maps |
| `ENVIRONMENT` | No | `production` | `development`, `staging`, `production` |
| `CELERY_TASK_ALWAYS_EAGER` | No | `false` | Run Celery tasks synchronously |

#### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API URL |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | No | - | Mapbox API token |

### GitHub Secrets (CI/CD)

| Secret | Purpose |
|--------|---------|
| `KUBE_CONFIG` | Kubernetes cluster credentials |
| `NEXT_PUBLIC_API_URL` | Production API URL |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Mapbox token for Docker builds |

---

## Startup Procedures

### Local Development

```bash
# Terminal 1: Start databases
docker start postgres redis

# Terminal 2: Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Start Celery worker
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info

# Terminal 4: Start frontend
cd frontend
npm run dev
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Kubernetes (Minikube)

```bash
# 1. Start Docker Desktop first (required)

# 2. Start Minikube
minikube start

# 3. Deploy application
kubectl apply -k k8s/overlays/local

# 4. Wait for pods
kubectl get pods -n local-buyer-intelligence -w

# 5. Start port forwarding
kubectl port-forward -n local-buyer-intelligence svc/frontend-service 3000:3000 &
kubectl port-forward -n local-buyer-intelligence svc/backend-service 8000:8000 &

# 6. (Optional) Deploy monitoring
kubectl apply -k k8s/components/monitoring
kubectl port-forward -n monitoring svc/grafana 3001:3000 &
```

### Kubernetes (Production)

```bash
# Deployments are automated via GitHub Actions
# Manual deployment if needed:
kubectl apply -k k8s/overlays/production

# Verify rollout
kubectl rollout status deployment/backend -n local-buyer-intelligence
kubectl rollout status deployment/frontend -n local-buyer-intelligence
```

---

## Shutdown Procedures

### Local Development

```bash
# Stop frontend (Ctrl+C in terminal)

# Stop Celery worker (Ctrl+C in terminal)

# Stop backend (Ctrl+C in terminal)

# Stop databases
docker stop postgres redis
```

### Docker Compose

```bash
# Graceful shutdown (waits for containers to stop)
docker-compose down

# Shutdown and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Kubernetes (Minikube)

```bash
# 1. Stop port forwarding
pkill -f "kubectl port-forward"

# 2. Stop Minikube (preserves state)
minikube stop

# 3. (Optional) Delete cluster entirely
minikube delete
```

### Kubernetes (Production)

```bash
# Scale down gracefully
kubectl scale deployment --all --replicas=0 -n local-buyer-intelligence

# Or delete deployments
kubectl delete -k k8s/overlays/production

# Keep database running for data preservation
```

---

## Daily Operations

### Health Checks

```bash
# Local/Docker
curl http://localhost:8000/health

# Kubernetes
kubectl exec -n local-buyer-intelligence deploy/backend -- curl -s localhost:8000/health
```

### View Application Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery-worker

# Kubernetes
kubectl logs -f -l app=backend -n local-buyer-intelligence
kubectl logs -f -l app=frontend -n local-buyer-intelligence
kubectl logs -f -l app=celery-worker -n local-buyer-intelligence
```

### Check Pod Status

```bash
kubectl get pods -n local-buyer-intelligence
kubectl get pods -n monitoring  # If monitoring is deployed
```

### Run Database Migrations

```bash
# Docker Compose
docker-compose exec backend alembic upgrade head

# Kubernetes
kubectl exec -n local-buyer-intelligence deploy/backend -- alembic upgrade head
```

### Restart Services

```bash
# Docker Compose
docker-compose restart backend

# Kubernetes
kubectl rollout restart deployment/backend -n local-buyer-intelligence
```

---

## Monitoring & Logs

### Access Monitoring Tools (Kubernetes)

```bash
# Grafana (dashboards)
kubectl port-forward -n monitoring svc/grafana 3001:3000
# Open http://localhost:3001 (admin/admin)

# Prometheus (metrics)
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090

# View logs in Grafana
# Go to Explore → Select "Loki" → Query: {namespace="local-buyer-intelligence"}
```

### Key Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `up` | Service availability | < 1 for 1 minute |
| `http_requests_total` | Request count | Sudden drops |
| `http_request_duration_seconds` | Response time | P95 > 2s |
| `container_memory_usage_bytes` | Memory usage | > 80% of limit |

### Log Queries (Loki)

```
# All backend logs
{app="backend"}

# Errors only
{app="backend"} |= "error"

# Specific endpoint
{app="backend"} |= "/api/v1/geographies"

# Celery task logs
{app="celery-worker"} |= "Task"
```

---

## Offline Handling

### Scenario 1: No Internet Connection

**What still works:**
- Local development with local database
- Minikube cluster (if already running)
- Previously pulled Docker images

**What doesn't work:**
- Pulling new Docker images
- GitHub Actions CI/CD
- External API calls (Mapbox, Census API)
- Package installations (pip, npm)

**Mitigation:**
```bash
# Ensure images are cached
docker pull ghcr.io/ntewolde/local-buyer-intelligence-backend:latest
docker pull ghcr.io/ntewolde/local-buyer-intelligence-frontend:latest

# Pre-install dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Scenario 2: Docker Desktop Not Running

**Symptoms:**
- `minikube start` fails with connection error
- `docker` commands fail

**Resolution:**
```bash
# macOS: Start Docker Desktop from Applications
open -a Docker

# Wait for Docker to be ready
while ! docker info > /dev/null 2>&1; do sleep 1; done
echo "Docker is ready"
```

### Scenario 3: Minikube Won't Start

**Resolution:**
```bash
# Check Docker is running first
docker info

# Delete and recreate cluster
minikube delete
minikube start

# If still failing, reset Docker
# Docker Desktop → Troubleshoot → Reset to factory defaults
```

### Scenario 4: Database Connection Failed

**Symptoms:**
- Backend returns 500 errors
- "Connection refused" in logs

**Resolution:**
```bash
# Docker Compose
docker-compose restart postgres
docker-compose logs postgres

# Kubernetes
kubectl get pods -n local-buyer-intelligence | grep postgres
kubectl logs -n local-buyer-intelligence postgres-0

# Check if PVC is bound
kubectl get pvc -n local-buyer-intelligence
```

### Scenario 5: Services Not Responding

**Kubernetes quick recovery:**
```bash
# Restart all deployments
kubectl rollout restart deployment --all -n local-buyer-intelligence

# If that fails, delete and recreate pods
kubectl delete pods --all -n local-buyer-intelligence

# Check events for errors
kubectl get events -n local-buyer-intelligence --sort-by='.lastTimestamp'
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use different port
npm run dev -- -p 3001
```

#### 2. Backend Import Errors

```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Frontend Build Fails

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

#### 4. Kubernetes ImagePullBackOff

```bash
# Check image exists
docker images | grep local-buyer-intelligence

# For minikube, ensure Docker env is set
eval $(minikube docker-env)

# Rebuild image
docker build -t local-buyer-intelligence-backend:local ./backend
```

#### 5. Database Migration Fails

```bash
# Check current migration state
alembic current

# Generate new migration if needed
alembic revision --autogenerate -m "description"

# Force to specific revision
alembic stamp head
alembic upgrade head
```

#### 6. Celery Tasks Not Running

```bash
# Check Celery worker is running
docker-compose ps celery-worker

# Check Redis connection
redis-cli ping

# View Celery logs
docker-compose logs -f celery-worker
```

### Debug Commands

```bash
# Check all container logs
docker-compose logs --tail=100

# Interactive shell in container
docker-compose exec backend /bin/bash

# Kubernetes pod shell
kubectl exec -it -n local-buyer-intelligence deploy/backend -- /bin/bash

# Check resource usage
kubectl top pods -n local-buyer-intelligence
```

---

## Backup & Recovery

### Database Backup

```bash
# Docker Compose
docker-compose exec postgres pg_dump -U postgres local_buyer_intelligence > backup.sql

# Kubernetes
kubectl exec -n local-buyer-intelligence postgres-0 -- \
  pg_dump -U postgres local_buyer_intelligence > backup.sql
```

### Database Restore

```bash
# Docker Compose
cat backup.sql | docker-compose exec -T postgres psql -U postgres local_buyer_intelligence

# Kubernetes
cat backup.sql | kubectl exec -i -n local-buyer-intelligence postgres-0 -- \
  psql -U postgres local_buyer_intelligence
```

### Full Cluster Backup (Kubernetes)

```bash
# Export all resources
kubectl get all -n local-buyer-intelligence -o yaml > cluster-backup.yaml

# Export secrets (be careful with these)
kubectl get secrets -n local-buyer-intelligence -o yaml > secrets-backup.yaml
```

---

## Quick Reference

### Useful Commands

| Action | Command |
|--------|---------|
| Start local dev | `docker-compose up -d` |
| Stop local dev | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Start minikube | `minikube start` |
| Stop minikube | `minikube stop` |
| Deploy to K8s | `kubectl apply -k k8s/overlays/local` |
| Check pods | `kubectl get pods -n local-buyer-intelligence` |
| Port forward | `kubectl port-forward svc/frontend-service 3000:3000 -n local-buyer-intelligence` |
| View K8s logs | `kubectl logs -f deploy/backend -n local-buyer-intelligence` |

### Access URLs

| Environment | Frontend | Backend API | API Docs |
|-------------|----------|-------------|----------|
| Local Dev | http://localhost:3000 | http://localhost:8000 | http://localhost:8000/docs |
| Docker Compose | http://localhost:3000 | http://localhost:8000 | http://localhost:8000/docs |
| Minikube (port-forward) | http://localhost:3000 | http://localhost:8000 | http://localhost:8000/docs |
| Minikube (ingress) | http://app.127.0.0.1.nip.io | http://api.127.0.0.1.nip.io | http://api.127.0.0.1.nip.io/docs |

### Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| Grafana | admin | admin |
| PostgreSQL | postgres | postgres |

---

## Support

For issues:
1. Check this troubleshooting guide
2. Review logs for error messages
3. Open an issue at https://github.com/ntewolde/local-buyer-intelligence/issues
