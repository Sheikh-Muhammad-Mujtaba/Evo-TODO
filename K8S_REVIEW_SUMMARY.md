# Kubernetes, Dapr & HPA Configuration Review

## Summary of Issues Found

I reviewed all Kubernetes configurations in the `/k8s` directory and found several critical issues that need to be addressed.

---

## 🔴 CRITICAL ISSUES

### 1. Missing Dapr Annotations ❌

**Problem**: Deployments don't have Dapr sidecar injection annotations.

**Current State**:
```yaml
spec:
  template:
    metadata:
      labels:
        app: backend
```

**Required Fix**:
```yaml
spec:
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/config: "appconfig"
```

**Impact**: Without these annotations, Dapr sidecars won't be injected, breaking service-to-service communication.

---

### 2. Missing Environment Variables & Secrets ❌

**Problem**: Deployments have no environment configuration.

**Required**:
- Database connection details
- JWT secrets
- API keys (Gemini)
- MCP secrets
- ConfigMaps and Secrets

**Impact**: Services will fail to start or connect to dependencies.

---

### 3. Incorrect Port Configuration ❌

**Problems**:
- MCP Server uses port 8001 in service.yaml but should use 8000
- Backend service name conflicts with actual service architecture
- No PostgreSQL service defined

**Current** (service.yaml line 35-36):
```yaml
port: 8001
targetPort: 8001
```

**Should Be**:
```yaml
port: 8000
targetPort: 8000
```

---

### 4. Missing Resource Limits & Requests ❌

**Problem**: No CPU/memory limits defined in deployments.

**Required for HPA to work**:
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Impact**: HPA **WILL NOT WORK** without resource requests. This is a hard requirement.

---

### 5. Missing Database (PostgreSQL) Deployment ❌

**Problem**: No PostgreSQL StatefulSet or Deployment defined.

**Required**:
- PostgreSQL StatefulSet with persistent volume
- PostgreSQL Service
- Or connection to external managed database

**Impact**: All services depend on database and will fail.

---

### 6. Incomplete Service Architecture ❌

**Current deployments**:
- ❌ "backend" (generic, unclear)
- ✅ frontend
- ✅ mcp-server (but wrong port)

**Should have**:
- ✅ todo-service
- ✅ agent-service
- ✅ mcp-server
- ✅ frontend
- ✅ postgres

---

### 7. Missing Dapr Components Configuration ❌

**Problem**: Dapr components (pubsub.yaml) configured for Docker, not Kubernetes.

**Current** (dapr/components/pubsub.yaml):
- Uses `in-memory` pubsub
- No secretStore reference for Kubernetes

**Required for K8s**:
- Redis deployment for production pub/sub
- Proper Kubernetes secret references
- State store component
- Pub/sub component

---

### 8. HPA Missing Behavior Configuration ⚠️

**Current HPA** is basic but functional.

**Recommended additions**:
```yaml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300
    policies:
    - type: Percent
      value: 50
      periodSeconds: 60
  scaleUp:
    stabilizationWindowSeconds: 0
    policies:
    - type: Percent
      value: 100
      periodSeconds: 30
```

---

## 📋 Required Fixes Checklist

### Immediate (Blocking):
- [ ] Add Dapr annotations to all deployments
- [ ] Create ConfigMap with environment variables
- [ ] Create Secrets for sensitive data
- [ ] Add resource requests/limits (required for HPA)
- [ ] Fix MCP server port configuration
- [ ] Create PostgreSQL StatefulSet
- [ ] Create proper service definitions for all microservices
- [ ] Update Dapr components for Kubernetes

### Important:
- [ ] Add health check probes for all services
- [ ] Configure HPA behavior policies
- [ ] Add network policies
- [ ] Setup ingress controller
- [ ] Configure persistent volumes for PostgreSQL
- [ ] Add Redis for Dapr pub/sub

### Recommended:
- [ ] Add namespace configuration
- [ ] Setup monitoring (Prometheus)
- [ ] Configure service mesh policies
- [ ] Add pod disruption budgets
- [ ] Configure pod security policies
- [ ] Setup external secrets operator

---

## 🏗️ Correct Architecture

### Required Kubernetes Resources:

```
k8s/
├── 00-namespace.yaml              # Namespace definition
├── 01-configmap.yaml              # Application config
├── 02-secrets.yaml                # Secrets (use external secrets in prod)
├── 03-postgres-statefulset.yaml  # Database
├── 04-postgres-service.yaml       # Database service
├── 05-todo-deployment.yaml        # Todo service
├── 06-todo-service.yaml           # Todo K8s service
├── 07-agent-deployment.yaml       # Agent service
├── 08-agent-service.yaml          # Agent K8s service
├── 09-mcp-deployment.yaml         # MCP server
├── 10-mcp-service.yaml            # MCP K8s service
├── 11-frontend-deployment.yaml    # Frontend
├── 12-frontend-service.yaml       # Frontend K8s service
├── 13-ingress.yaml                # Ingress rules
├── 14-hpa.yaml                    # Horizontal Pod Autoscalers
└── 15-dapr-config.yaml            # Dapr configuration

dapr/
└── components/
    ├── pubsub-redis.yaml          # Pub/sub for K8s
    ├── statestore-redis.yaml      # State store
    └── appconfig.yaml             # Dapr app configuration
```

---

## 🔧 Example: Correct Deployment with Dapr

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-service
  namespace: evo-todo
  labels:
    app: todo-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-service
  template:
    metadata:
      labels:
        app: todo-service
      annotations:
        # CRITICAL: Dapr annotations
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-service"
        dapr.io/app-port: "8000"
        dapr.io/config: "appconfig"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: todo-service
        image: evo-todo/todo-service:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http

        # CRITICAL: Resource limits for HPA
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi

        # Environment from ConfigMap
        envFrom:
        - configMapRef:
            name: evo-todo-config
        - secretRef:
            name: evo-todo-secrets

        # Health probes
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

---

## 🚀 Deployment Order

1. **Install Dapr** (if not already):
   ```bash
   dapr init -k
   ```

2. **Create namespace**:
   ```bash
   kubectl apply -f k8s/00-namespace.yaml
   ```

3. **Create ConfigMap & Secrets**:
   ```bash
   kubectl apply -f k8s/01-configmap.yaml
   kubectl apply -f k8s/02-secrets.yaml
   ```

4. **Deploy Database**:
   ```bash
   kubectl apply -f k8s/03-postgres-statefulset.yaml
   kubectl apply -f k8s/04-postgres-service.yaml
   ```

5. **Deploy Dapr Components**:
   ```bash
   kubectl apply -f dapr/components/
   ```

6. **Deploy Services**:
   ```bash
   kubectl apply -f k8s/05-todo-deployment.yaml
   kubectl apply -f k8s/06-todo-service.yaml
   # ... repeat for other services
   ```

7. **Deploy HPA**:
   ```bash
   kubectl apply -f k8s/14-hpa.yaml
   ```

8. **Verify**:
   ```bash
   kubectl get pods -n evo-todo
   kubectl get hpa -n evo-todo
   dapr list -k -n evo-todo
   ```

---

## 🧪 Testing Dapr Integration

```bash
# Check Dapr sidecar injection
kubectl get pods -n evo-todo
# Should show 2/2 containers (app + dapr sidecar)

# Check Dapr components
kubectl get components -n evo-todo

# Test service invocation via Dapr
kubectl exec -it <pod-name> -n evo-todo -c daprd -- \
  curl http://localhost:3500/v1.0/invoke/todo-service/method/health

# Check Dapr logs
kubectl logs <pod-name> -n evo-todo -c daprd
```

---

## 📊 HPA Validation

For HPA to work, you MUST have:

1. ✅ **Metrics Server** installed:
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

2. ✅ **Resource requests** in all deployments

3. ✅ **Load testing** to trigger scaling:
   ```bash
   kubectl run -it --rm load-generator --image=busybox:1.28 -- /bin/sh
   while true; do wget -q -O- http://todo-service:8000/health; done
   ```

4. ✅ **Monitor HPA**:
   ```bash
   kubectl get hpa -n evo-todo --watch
   ```

---

## 🎯 Next Steps

1. **Fix deployment.yaml**: Add Dapr annotations and resources
2. **Create ConfigMap & Secrets**: Add all environment variables
3. **Fix service.yaml**: Correct ports and add missing services
4. **Update hpa.yaml**: Add behavior policies
5. **Create PostgreSQL**: Add StatefulSet
6. **Update Dapr components**: Configure for Kubernetes
7. **Test locally**: Use kind or minikube
8. **Deploy to cluster**: Follow deployment order above

---

## 📖 References

- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Dapr Sidecar Injection](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/#deploy-your-app)
- [K8s Resource Requests/Limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

---

## ⚠️ IMPORTANT NOTES

1. **HPA will NOT work without resource requests** - This is non-negotiable
2. **Dapr sidecars require annotations** - Services won't communicate without them
3. **Database is critical** - All services depend on PostgreSQL
4. **Secrets management** - Don't commit real secrets to Git
5. **Test locally first** - Use minikube or kind before cloud deployment

**Status**: ❌ Configurations need significant updates before deployment
