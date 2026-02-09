# Minikube Local Deployment Guide

Complete guide for deploying Evo-TODO on Minikube for local development and testing.

## Prerequisites

- Docker Desktop or Docker Engine
- Minikube installed
- kubectl installed
- Dapr CLI installed

## Installation

### 1. Install Minikube

```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows (using Chocolatey)
choco install minikube
```

### 2. Install kubectl

```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Windows (using Chocolatey)
choco install kubernetes-cli
```

### 3. Install Dapr CLI

```bash
# macOS/Linux
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (using PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

## Setup Minikube

### 1. Start Minikube

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable metrics server (required for HPA)
minikube addons enable metrics-server

# Enable ingress (optional, for domain-based routing)
minikube addons enable ingress
```

### 2. Initialize Dapr on Minikube

```bash
# Initialize Dapr in Kubernetes mode
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
#   dapr-dashboard         dapr-system  True     Running  1         0.14.0   1m   2023-xx-xx
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2023-xx-xx
#   dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2023-xx-xx
#   dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2023-xx-xx
#   dapr-placement-server  dapr-system  True     Running  1         1.12.0   1m   2023-xx-xx
```

## Build Docker Images for Minikube

Minikube runs its own Docker daemon, so you need to build images inside Minikube:

```bash
# Point your shell to minikube's docker-daemon
eval $(minikube docker-env)

# Build all images
docker build -t evo-todo/todo-service:latest -f backend/Dockerfile.todo-service backend/
docker build -t evo-todo/agent-service:latest -f backend/Dockerfile.agent-service backend/
docker build -t evo-todo/mcp-server:latest -f backend/mcp_server/Dockerfile backend/
docker build -t evo-todo/frontend:latest frontend/

# Verify images
docker images | grep evo-todo
```

## Deploy to Minikube

### 1. Create Namespace

```bash
kubectl apply -f k8s/00-namespace.yaml
```

### 2. Configure Secrets

Create a `.env.minikube` file with your NeonDB credentials:

```bash
# .env.minikube
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
JWT_SECRET_KEY=$(openssl rand -base64 32)
GEMINI_API_KEY=your-gemini-api-key
MCP_INTERNAL_SECRET=$(openssl rand -base64 32)
```

Create secrets from file:

```bash
kubectl create secret generic evo-todo-secrets \
  --from-env-file=.env.minikube \
  --namespace=evo-todo
```

### 3. Deploy ConfigMap

```bash
# Update CORS_ORIGINS in 01-configmap.yaml for local access
kubectl apply -f k8s/01-configmap.yaml
```

### 4. Deploy Dapr Components

```bash
# For local development, use in-memory pub/sub
kubectl apply -f dapr/components/pubsub.yaml
kubectl apply -f dapr/components/appconfig.yaml
```

### 5. Deploy Applications

```bash
# Deploy all services
kubectl apply -f k8s/deployment-updated.yaml
kubectl apply -f k8s/service-updated.yaml

# Wait for deployments to be ready
kubectl wait --for=condition=available --timeout=300s \
  deployment/todo-service \
  deployment/agent-service \
  deployment/mcp-server \
  deployment/frontend \
  -n evo-todo
```

### 6. Deploy HPA (Optional)

```bash
kubectl apply -f k8s/hpa-updated.yaml
```

## Access Services

### 1. Port Forward (Recommended for development)

```bash
# Todo Service
kubectl port-forward -n evo-todo svc/todo-service-service 8001:8000

# Agent Service
kubectl port-forward -n evo-todo svc/agent-service-service 8002:8000

# MCP Server
kubectl port-forward -n evo-todo svc/mcp-server-service 8003:8000

# Frontend
kubectl port-forward -n evo-todo svc/frontend-service 3000:80
```

Now access:
- Frontend: http://localhost:3000
- Todo API: http://localhost:8001
- Agent API: http://localhost:8002
- MCP Server: http://localhost:8003

### 2. Using Minikube Service

```bash
# Get service URL
minikube service frontend-service -n evo-todo --url

# Open in browser
minikube service frontend-service -n evo-todo
```

### 3. Using Minikube Tunnel (LoadBalancer)

```bash
# Start tunnel (requires sudo/admin)
minikube tunnel

# In another terminal, get external IP
kubectl get svc frontend-service -n evo-todo
```

## Monitoring and Debugging

### Check Pod Status

```bash
# List all pods
kubectl get pods -n evo-todo

# Check specific pod
kubectl describe pod <pod-name> -n evo-todo

# View logs
kubectl logs <pod-name> -n evo-todo

# View Dapr sidecar logs
kubectl logs <pod-name> -n evo-todo -c daprd
```

### Dapr Dashboard

```bash
# Open Dapr dashboard
dapr dashboard -k

# Access at: http://localhost:8080
```

### Check HPA

```bash
# Watch HPA status
kubectl get hpa -n evo-todo --watch

# Generate load to test scaling
kubectl run -it --rm load-generator --image=busybox:1.28 --restart=Never -- /bin/sh
# Inside the pod:
while true; do wget -q -O- http://todo-service-service.evo-todo.svc.cluster.local:8000/health; done
```

### Dapr Service Invocation

```bash
# Test Dapr service-to-service invocation
kubectl exec -it <any-pod> -n evo-todo -c daprd -- \
  curl http://localhost:3500/v1.0/invoke/todo-service/method/health
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace evo-todo

# Or delete individual resources
kubectl delete -f k8s/deployment-updated.yaml
kubectl delete -f k8s/service-updated.yaml
kubectl delete -f k8s/hpa-updated.yaml

# Stop minikube
minikube stop

# Delete minikube cluster
minikube delete
```

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl get events -n evo-todo --sort-by='.lastTimestamp'

# Check pod details
kubectl describe pod <pod-name> -n evo-todo

# Check image pull
kubectl get pods -n evo-todo -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[*].imageID}{"\n"}{end}'
```

### Dapr Sidecar Issues

```bash
# Check if Dapr is running
dapr status -k

# Check Dapr configuration
kubectl get components -n evo-todo

# View Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### HPA Not Scaling

```bash
# Check metrics server
kubectl top nodes
kubectl top pods -n evo-todo

# Check HPA status
kubectl describe hpa <hpa-name> -n evo-todo

# Verify resource requests are set
kubectl get deployment <deployment-name> -n evo-todo -o yaml | grep -A 5 resources
```

### Database Connection Issues

```bash
# Test connection from pod
kubectl exec -it <pod-name> -n evo-todo -- /bin/sh
# Inside pod:
curl -v $DATABASE_URL  # Won't work, but shows if env var is set

# Check secrets
kubectl get secret evo-todo-secrets -n evo-todo -o yaml
kubectl get secret evo-todo-secrets -n evo-todo -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

## Tips for Local Development

1. **Faster rebuilds**: Use `skaffold` or `tilt` for automatic rebuilds
2. **Local registry**: Setup a local registry for faster image pulls
3. **Resource limits**: Reduce resource limits for local development
4. **Debug mode**: Set `DEBUG=True` in ConfigMap
5. **Hot reload**: Use volume mounts for code changes (not recommended for K8s)

## Next Steps

- Setup ingress for domain-based routing
- Add monitoring with Prometheus/Grafana
- Configure persistent volumes for stateful services
- Setup CI/CD pipeline
- Test autoscaling under load
