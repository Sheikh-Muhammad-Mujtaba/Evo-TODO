# Production Kubernetes Deployment Guide

Complete guide for deploying Evo-TODO to production Kubernetes (AKS, EKS, GKE).

## Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Container registry (ACR, ECR, GCR, Docker Hub)
- Dapr installed on cluster

## 1. Build & Push Images

```bash
# Set your registry
export REGISTRY=your-registry.azurecr.io  # or gcr.io/project, etc.

# Build and push
docker build -t $REGISTRY/evo-todo/todo-service:v1.0.0 -f backend/Dockerfile.todo-service backend/
docker build -t $REGISTRY/evo-todo/agent-service:v1.0.0 -f backend/Dockerfile.agent-service backend/
docker build -t $REGISTRY/evo-todo/mcp-server:v1.0.0 -f backend/mcp_server/Dockerfile backend/
docker build -t $REGISTRY/evo-todo/frontend:v1.0.0 frontend/

docker push $REGISTRY/evo-todo/todo-service:v1.0.0
docker push $REGISTRY/evo-todo/agent-service:v1.0.0
docker push $REGISTRY/evo-todo/mcp-server:v1.0.0
docker push $REGISTRY/evo-todo/frontend:v1.0.0
```

## 2. Update Image References

Edit `k8s/deployment.yaml` to use your registry:

```yaml
image: your-registry.azurecr.io/evo-todo/todo-service:v1.0.0
imagePullPolicy: Always
```

## 3. Configure Secrets

**Important:** Never commit real secrets to Git!

```bash
# Create secrets from environment file
kubectl create namespace evo-todo
kubectl create secret generic evo-todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host/db?sslmode=require" \
  --from-literal=JWT_SECRET_KEY="$(openssl rand -base64 32)" \
  --from-literal=GEMINI_API_KEY="your-api-key" \
  --from-literal=MCP_INTERNAL_SECRET="$(openssl rand -base64 32)" \
  -n evo-todo
```

## 4. Install Dapr

```bash
dapr init -k --enable-ha --enable-mtls
kubectl rollout status deploy/dapr-operator -n dapr-system
```

## 5. Deploy Application

```bash
# Apply in order
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
# Skip 02-secrets.yaml if created manually above

# Production Redis (use managed service like Azure Cache for Redis)
# Update dapr/components/pubsub.yaml with production Redis URL

kubectl apply -f k8s/03-infrastructure.yaml  # Or use managed services
kubectl apply -f dapr/components/
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

## 6. Configure Ingress (Production)

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: evo-todo-ingress
  namespace: evo-todo
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: evo-todo-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-service-service
            port:
              number: 8000
```

## 7. Verify Deployment

```bash
kubectl get pods -n evo-todo
kubectl get hpa -n evo-todo
kubectl top pods -n evo-todo
```

## Production Checklist

- [ ] Use managed Redis (Azure Cache, ElastiCache, Memorystore)
- [ ] Use managed PostgreSQL (NeonDB, Azure Database, RDS, Cloud SQL)
- [ ] Configure TLS/SSL with cert-manager
- [ ] Set up monitoring (Prometheus, Azure Monitor, CloudWatch)
- [ ] Configure backup strategy for databases
- [ ] Set appropriate resource limits
- [ ] Enable RBAC and network policies
- [ ] Configure log aggregation (ELK, Loki, CloudWatch Logs)
