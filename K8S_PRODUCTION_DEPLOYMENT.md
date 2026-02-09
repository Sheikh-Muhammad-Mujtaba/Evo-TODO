# Production Kubernetes Deployment Guide

Complete guide for deploying Evo-TODO to production Kubernetes clusters (AWS EKS, GCP GKE, Azure AKS, or self-hosted).

## Prerequisites

- Production Kubernetes cluster (1.24+)
- kubectl configured with cluster access
- Helm 3.x installed
- Docker registry (Docker Hub, ECR, GCR, ACR)
- NeonDB database with connection string
- Dapr CLI installed

## Pre-Deployment Checklist

- [ ] Kubernetes cluster provisioned
- [ ] kubectl access configured
- [ ] Docker registry setup and accessible
- [ ] NeonDB database created
- [ ] Domain name configured (if using ingress)
- [ ] SSL/TLS certificates ready
- [ ] Secrets management solution chosen
- [ ] Monitoring solution ready
- [ ] Backup strategy defined

## 1. Cluster Setup

### Install Required Components

#### 1.1 Install Dapr

```bash
# Install Dapr to your cluster
dapr init -k

# For production, use Helm with custom values
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm upgrade --install dapr dapr/dapr \
  --version=1.12 \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.prometheus.enabled=true

# Verify installation
dapr status -k
```

#### 1.2 Install Metrics Server (if not present)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### 1.3 Install Cert-Manager (for TLS)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

#### 1.4 Install Ingress Controller

**NGINX Ingress (recommended)**:
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

**Or Traefik**:
```bash
helm repo add traefik https://traefik.github.io/charts
helm install traefik traefik/traefik \
  --namespace traefik \
  --create-namespace
```

### 1.5 Install Redis (for Dapr pub/sub)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis \
  --namespace evo-todo \
  --create-namespace \
  --set auth.enabled=true \
  --set auth.password="CHANGE_ME" \
  --set master.persistence.enabled=true \
  --set master.persistence.size=8Gi
```

## 2. Build and Push Docker Images

### 2.1 Tag Images for Registry

```bash
# Set your registry
REGISTRY=your-registry.azurecr.io  # or docker.io/username, gcr.io/project-id, etc.
VERSION=v1.0.0

# Tag images
docker tag evo-todo/todo-service:latest $REGISTRY/evo-todo/todo-service:$VERSION
docker tag evo-todo/agent-service:latest $REGISTRY/evo-todo/agent-service:$VERSION
docker tag evo-todo/mcp-server:latest $REGISTRY/evo-todo/mcp-server:$VERSION
docker tag evo-todo/frontend:latest $REGISTRY/evo-todo/frontend:$VERSION
```

### 2.2 Push to Registry

```bash
# Login to registry
docker login $REGISTRY

# Push images
docker push $REGISTRY/evo-todo/todo-service:$VERSION
docker push $REGISTRY/evo-todo/agent-service:$VERSION
docker push $REGISTRY/evo-todo/mcp-server:$VERSION
docker push $REGISTRY/evo-todo/frontend:$VERSION
```

### 2.3 Update Deployment Files

Update image references in `k8s/deployment-updated.yaml`:

```yaml
spec:
  containers:
  - name: todo-service
    image: your-registry.azurecr.io/evo-todo/todo-service:v1.0.0
    imagePullPolicy: Always  # Change to Always for production
```

## 3. Setup Secrets Management

### Option A: Kubernetes Secrets (Simple)

```bash
# Create production secrets
kubectl create namespace evo-todo

kubectl create secret generic evo-todo-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@host/db?sslmode=require' \
  --from-literal=JWT_SECRET_KEY='your-secret-key' \
  --from-literal=GEMINI_API_KEY='your-api-key' \
  --from-literal=MCP_INTERNAL_SECRET='your-mcp-secret' \
  --namespace=evo-todo
```

### Option B: External Secrets Operator (Recommended)

**AWS Secrets Manager**:
```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets-system \
  --create-namespace

# Create SecretStore (see AWS/Azure/GCP specific docs)
```

**Azure Key Vault** or **GCP Secret Manager**: Similar setup

## 4. Deploy Application

### 4.1 Create Namespace

```bash
kubectl apply -f k8s/00-namespace.yaml
```

### 4.2 Update ConfigMap for Production

Edit `k8s/01-configmap.yaml`:

```yaml
data:
  ENVIRONMENT: "production"
  DEBUG: "False"
  CORS_ORIGINS: "https://your-domain.com"
  MCP_SERVER_URL: "http://mcp-server-service:8000"
```

Apply:
```bash
kubectl apply -f k8s/01-configmap.yaml
```

### 4.3 Deploy Dapr Components

Update Redis connection in `dapr/components/pubsub-redis-k8s.yaml`:

```yaml
metadata:
- name: redisHost
  value: redis-master.evo-todo.svc.cluster.local:6379
- name: redisPassword
  secretKeyRef:
    name: redis
    key: redis-password
```

Apply:
```bash
kubectl apply -f dapr/components/appconfig.yaml
kubectl apply -f dapr/components/pubsub-redis-k8s.yaml
```

### 4.4 Deploy Services

```bash
# Deploy applications
kubectl apply -f k8s/deployment-updated.yaml
kubectl apply -f k8s/service-updated.yaml

# Wait for rollout
kubectl rollout status deployment/todo-service -n evo-todo
kubectl rollout status deployment/agent-service -n evo-todo
kubectl rollout status deployment/mcp-server -n evo-todo
kubectl rollout status deployment/frontend -n evo-todo
```

### 4.5 Deploy HPA

```bash
kubectl apply -f k8s/hpa-updated.yaml

# Verify HPA
kubectl get hpa -n evo-todo
```

## 5. Setup Ingress and TLS

### 5.1 Create Ingress Resource

Create `k8s/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: evo-todo-ingress
  namespace: evo-todo
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - your-domain.com
    - api.your-domain.com
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
  - host: api.your-domain.com
    http:
      paths:
      - path: /todos
        pathType: Prefix
        backend:
          service:
            name: todo-service-service
            port:
              number: 8000
      - path: /agent
        pathType: Prefix
        backend:
          service:
            name: agent-service-service
            port:
              number: 8000
```

Apply:
```bash
kubectl apply -f k8s/ingress.yaml
```

### 5.2 Setup Let's Encrypt

```yaml
# k8s/cert-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

```bash
kubectl apply -f k8s/cert-issuer.yaml
```

## 6. Monitoring and Observability

### 6.1 Install Prometheus & Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### 6.2 Setup Dapr Metrics

Dapr exposes metrics on port 9090 (already configured in deployment annotations).

### 6.3 Setup Logging

**Option 1: EFK Stack**
```bash
# Elasticsearch, Fluentd, Kibana
# See: https://github.com/elastic/helm-charts
```

**Option 2: Loki Stack**
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace monitoring
```

## 7. Backup and Disaster Recovery

### 7.1 Database Backups

NeonDB provides automatic backups. Configure:
- Backup retention period
- Point-in-time recovery settings
- Backup schedule

### 7.2 Kubernetes Resource Backups

```bash
# Install Velero
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm install velero vmware-tanzu/velero \
  --namespace velero \
  --create-namespace
```

## 8. Security Hardening

### 8.1 Network Policies

Create `k8s/network-policy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: evo-todo-network-policy
  namespace: evo-todo
spec:
  podSelector:
    matchLabels:
      app: todo-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: agent-service
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 8000
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
```

### 8.2 Pod Security Standards

```yaml
# k8s/pod-security.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: evo-todo
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 8.3 RBAC

Ensure proper service accounts and RBAC policies are in place.

## 9. Production Verification

### 9.1 Health Checks

```bash
# Check all deployments
kubectl get deployments -n evo-todo

# Check pods are running
kubectl get pods -n evo-todo

# Check services
kubectl get svc -n evo-todo

# Check ingress
kubectl get ingress -n evo-todo
```

### 9.2 Test Endpoints

```bash
# Health checks
curl https://api.your-domain.com/todos/health
curl https://api.your-domain.com/agent/health

# Frontend
curl https://your-domain.com
```

### 9.3 Load Testing

```bash
# Install k6 or use existing tool
k6 run load-test.js
```

### 9.4 Monitor HPA

```bash
kubectl get hpa -n evo-todo --watch
```

## 10. Operational Procedures

### Rolling Updates

```bash
# Update image
kubectl set image deployment/todo-service \
  todo-service=$REGISTRY/evo-todo/todo-service:v1.1.0 \
  -n evo-todo

# Monitor rollout
kubectl rollout status deployment/todo-service -n evo-todo

# Rollback if needed
kubectl rollout undo deployment/todo-service -n evo-todo
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment/todo-service --replicas=5 -n evo-todo

# Update HPA
kubectl edit hpa todo-service-hpa -n evo-todo
```

### Debugging

```bash
# Get logs
kubectl logs -f deployment/todo-service -n evo-todo

# Get Dapr logs
kubectl logs -f deployment/todo-service -n evo-todo -c daprd

# Execute into pod
kubectl exec -it <pod-name> -n evo-todo -- /bin/sh

# Port forward for debugging
kubectl port-forward svc/todo-service-service 8000:8000 -n evo-todo
```

## 11. Cost Optimization

1. **Right-size resources**: Monitor and adjust CPU/memory requests
2. **Use spot/preemptible instances**: For non-critical workloads
3. **Enable cluster autoscaling**: Scale nodes based on demand
4. **Use HPA effectively**: Auto-scale pods
5. **Implement pod disruption budgets**: Minimize impact during maintenance

## 12. Maintenance

### Regular Tasks

- [ ] Update Docker images monthly
- [ ] Review and rotate secrets quarterly
- [ ] Update Kubernetes version (follow N-2 policy)
- [ ] Review and optimize HPA settings
- [ ] Monitor and adjust resource limits
- [ ] Review logs for errors
- [ ] Test backup restoration procedure

## Troubleshooting

See `MINIKUBE_DEPLOYMENT.md` for common troubleshooting steps.

Additional production issues:

- **Certificate issues**: Check cert-manager logs
- **Ingress not working**: Verify DNS, check ingress controller logs
- **High memory usage**: Check for memory leaks, adjust limits
- **Database connection pool exhausted**: Increase pool size or add replicas

## Support Contacts

- Cloud Provider: [Support Link]
- Database (NeonDB): [Support Link]
- On-Call: [Contact Info]

---

**Production Deployment Complete!** 🚀

Monitor your deployment and adjust based on real-world traffic patterns.
