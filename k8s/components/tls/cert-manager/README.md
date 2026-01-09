# cert-manager Installation

cert-manager is required for automatic TLS certificate management.

## Prerequisites

- Kubernetes 1.22+
- Helm 3.0+ (recommended) or kubectl

## Installation via Helm (Recommended)

```bash
# Add the Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager with CRDs
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.14.0 \
  --set installCRDs=true
```

## Installation via kubectl

```bash
# Apply cert-manager manifests directly
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml
```

## Verify Installation

```bash
# Check that all pods are running
kubectl get pods -n cert-manager

# Expected output:
# NAME                                       READY   STATUS    RESTARTS   AGE
# cert-manager-xxxxxxxxx-xxxxx               1/1     Running   0          1m
# cert-manager-cainjector-xxxxxxxxx-xxxxx    1/1     Running   0          1m
# cert-manager-webhook-xxxxxxxxx-xxxxx       1/1     Running   0          1m
```

## Troubleshooting

### Check cert-manager logs
```bash
kubectl logs -n cert-manager -l app=cert-manager
```

### Check certificate status
```bash
kubectl get certificates -A
kubectl describe certificate <name> -n <namespace>
```

### Check certificate requests
```bash
kubectl get certificaterequests -A
```

## Uninstallation

```bash
# Via Helm
helm uninstall cert-manager -n cert-manager

# Via kubectl
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml
```
