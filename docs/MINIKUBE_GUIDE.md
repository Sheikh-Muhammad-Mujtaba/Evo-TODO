# Minikube Local Development Guide

Quick guide for running Evo-TODO on Minikube.

## Prerequisites

```bash
# Install Minikube, kubectl, Dapr CLI
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/


kubectl version --client



curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube-linux-amd64
sudo mv minikube-linux-amd64 /usr/local/bin/minikube


minikube version


wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

```

## 1. Start Minikube

```bash
minikube start --driver=docker --cpus=2 --memory=3072mb
minikube addons enable metrics-server
minikube addons enable ingress
```

## 2. Install Dapr

```bash
dapr init -k
kubectl rollout status deploy/dapr-operator -n dapr-system
```

## 3. Build Images (in Minikube's Docker)

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)
# Windows PowerShell:
# & minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build images
docker build -t evo-todo/todo-service:latest -f backend/Dockerfile.todo-service backend/

docker build -t evo-todo/agent-service:latest -f backend/Dockerfile.agent-service backend/

docker build -t evo-todo/mcp-server:latest -f backend/mcp_server/Dockerfile backend/

docker build -t evo-todo/frontend:latest frontend/

docker build --build-arg NEXT_PUBLIC_AUTH_URL=http://localhost:3000 -t evo-todo/frontend:latest frontend/
```

## 4. Deploy to Minikube

```bash
# Create namespace, config, secrets
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy infrastructure (Redis, Zipkin)
kubectl apply -f k8s/03-infrastructure.yaml

# Deploy Dapr components
kubectl apply -f dapr/components/

# Deploy services
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

## 5. Access the Application

```bash
# Option 1: Minikube tunnel (for LoadBalancer)
minikube tunnel

# Option 2: Port forward
kubectl port-forward svc/frontend-service 3000:80 -n evo-todo

# Open browser
minikube service frontend-service -n evo-todo
```

## 6. Verify Deployment

```bash
kubectl get pods -n evo-todo
kubectl get svc -n evo-todo
kubectl logs -f deployment/todo-service -n evo-todo

kubectl get pods -n evo-todo -l app=frontend

kubectl logs <new-pod-name> -n evo-todo -c frontend

```

## Cleanup

```bash
kubectl delete namespace evo-todo
minikube stop
```
