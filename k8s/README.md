# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the myipcontainer application.

## Files

- `deployment.yaml` - Application deployment with 3 replicas
- `service.yaml` - ClusterIP service to expose the application internally
- `ingress.yaml` - Ingress resource for external access

## Quick Deploy

Deploy all resources at once:

```bash
kubectl apply -f k8s/
```

Or deploy individually:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## Configuration

### Ingress

Before deploying the ingress, update the host in `ingress.yaml`:

```yaml
rules:
- host: your-domain.com  # Change this to your actual domain
```

### TLS (Optional)

To enable HTTPS, uncomment the TLS section in `ingress.yaml` and create a TLS secret:

```bash
kubectl create secret tls myip-tls --cert=path/to/tls.crt --key=path/to/tls.key
```

## Accessing the Application

1. **Port Forward (for testing)**:
   ```bash
   kubectl port-forward service/myipcontainer-service 8080:80
   ```
   Then visit `http://localhost:8080`

2. **Via Ingress** (production):
   - Ensure your ingress controller is installed (e.g., nginx-ingress)
   - Update your DNS to point to the ingress controller's external IP
   - Visit `http://your-domain.com`

## Monitoring

Check the deployment status:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
```

View logs:

```bash
kubectl logs -l app=myipcontainer
```

## Scaling

Scale the deployment:

```bash
kubectl scale deployment myipcontainer --replicas=5
```

## Cleanup

Remove all resources:

```bash
kubectl delete -f k8s/
```