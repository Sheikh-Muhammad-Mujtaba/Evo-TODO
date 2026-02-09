# Minikube Troubleshooting Guide

If you encounter `context deadline exceeded` or connection issues with Minikube:

## 1. Restart Docker & Minikube

The error suggests Minikube is unresponsive.

```bash
# Stop Minikube
minikube stop

# Restart Docker Desktop (Windows) or Docker service (Linux/WSL)
# For WSL:
sudo service docker restart

# Start Minikube again (try with more resources if possible)
minikube start --driver=docker --cpus=4 --memory=6144 --listen-address='0.0.0.0'
```

## 2. Verify Docker Connection

```bash
docker ps
```

If this hangs or fails, your Docker installation is having issues.

## 3. Quick Check of Cluster Status

```bash
kubectl cluster-info
kubectl get nodes
```

## 4. Reset (Last Resort)

If restarting doesn't work, you might need to delete and recreate the cluster:

```bash
minikube delete
minikube start --driver=docker
# Then re-apply all K8s manifests
```

## 5. Enable Tunnel (After Cluster is Healthy)

```bash
minikube tunnel
```
