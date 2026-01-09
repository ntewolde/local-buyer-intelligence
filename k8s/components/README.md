# Kubernetes Components

This directory contains optional Kustomize components for production-ready deployments.

## Available Components

| Component | Description | Namespace |
|-----------|-------------|-----------|
| `tls` | cert-manager + Let's Encrypt certificates | cert-manager |
| `monitoring` | Prometheus + Grafana metrics stack | monitoring |
| `logging` | Loki + Promtail log aggregation | monitoring |
| `managed-db` | External database with PgBouncer | local-buyer-intelligence |

## Installation Order

Components should be installed in the following order:

### 1. TLS (cert-manager)

First, install cert-manager (required for TLS):

```bash
# Install cert-manager via Helm (recommended)
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.14.0 \
  --set installCRDs=true

# Then apply cluster issuers
kubectl apply -k k8s/components/tls
```

### 2. Monitoring

```bash
kubectl apply -k k8s/components/monitoring
```

Access Grafana:
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Open http://localhost:3000 (admin/admin)
```

Access Prometheus:
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090
```

### 3. Logging

```bash
kubectl apply -k k8s/components/logging
```

View logs in Grafana (requires monitoring component):
- Go to Grafana → Explore → Select "Loki" datasource
- Query: `{namespace="local-buyer-intelligence"}`

### 4. Managed Database (Production Only)

Before applying, update the credentials in `managed-db/external-db-secret.yaml`:

```bash
# Edit the secret with your actual database credentials
vim k8s/components/managed-db/external-db-secret.yaml

# Apply the component
kubectl apply -k k8s/components/managed-db
```

## Environment-Specific Usage

### Local Development (Minikube)

Components are optional for local development due to resource constraints:

```bash
# Basic deployment (no components)
kubectl apply -k k8s/overlays/local
```

### Staging

```bash
# Deploy base application
kubectl apply -k k8s/overlays/staging

# Add observability (optional)
kubectl apply -k k8s/components/monitoring
kubectl apply -k k8s/components/logging
```

### Production

```bash
# Deploy base application
kubectl apply -k k8s/overlays/production

# Add all components
kubectl apply -k k8s/components/tls
kubectl apply -k k8s/components/monitoring
kubectl apply -k k8s/components/logging
kubectl apply -k k8s/components/managed-db
```

## Component Details

### TLS Component

- **Self-signed issuer**: For local development
- **Let's Encrypt staging**: For testing (rate-limit friendly)
- **Let's Encrypt production**: For production (trusted certificates)

Update the email address in cluster issuers before production use.

### Monitoring Component

- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards and visualization (port 3000)
- **Pre-configured dashboards**: Overview dashboard included
- **Auto-discovery**: Scrapes pods with `prometheus.io/scrape: "true"` annotation

### Logging Component

- **Loki**: Log aggregation and storage
- **Promtail**: Log collection agent (DaemonSet)
- **Retention**: 7 days (configurable in loki/configmap.yaml)
- **Storage**: 10Gi PVC

### Managed Database Component

- **PgBouncer**: Connection pooling (transaction mode)
- **Replicas**: 2 for high availability
- **Removes**: In-cluster PostgreSQL StatefulSet

## Troubleshooting

### Check component status

```bash
# TLS
kubectl get clusterissuers
kubectl get certificates -A

# Monitoring
kubectl get pods -n monitoring
kubectl logs -n monitoring -l app=prometheus

# Logging
kubectl get pods -n monitoring -l app=loki
kubectl logs -n monitoring -l app=promtail

# Managed DB
kubectl get pods -l app=pgbouncer
```

### Common Issues

1. **cert-manager not ready**: Wait for all pods in cert-manager namespace to be running
2. **Prometheus not scraping**: Check pod annotations and RBAC permissions
3. **Loki not receiving logs**: Verify Promtail has access to /var/log/pods
4. **PgBouncer connection issues**: Verify external database credentials
