# Quickstart: Cloud-Native Deployment

This guide provides a quick way to build and test the containerized application locally.

## Prerequisites

- Docker installed and running.
- A local Kubernetes cluster (e.g., Minikube, Kind, Docker Desktop's Kubernetes).
- `kubectl` configured to point to your local cluster.

## Building the Docker Images

From the project root, you can build the Docker images for the frontend and backend:

```bash
# Build the backend image
docker build -t evo-todo-backend:latest -f backend/Dockerfile .

# Build the frontend image
docker build -t evo-todo-frontend:latest -f frontend/Dockerfile .
```

## Running with Docker Compose

For a simpler local setup that mimics the multi-container environment (without Kubernetes), you can use the `docker-compose.yml` file at the project root.

1.  **Create a `.env` file** at the project root with the necessary environment variables (see `.env.example`).
2.  **Run Docker Compose**:
    ```bash
    docker-compose up --build
    ```

This will build the images and start the frontend, backend, and a PostgreSQL database.

## Deploying to a Local Kubernetes Cluster

1.  **Build and Push Images**: Build the images as shown above and push them to a container registry that your local Kubernetes cluster can access. If you are using a local cluster like Minikube, you can often build directly into the cluster's Docker daemon.

2.  **Create Secrets**: Before applying the manifests, you need to create the Kubernetes Secrets for the database URL and any other sensitive data.
    ```bash
    kubectl create secret generic evo-todo-secrets --from-literal=DATABASE_URL='<your-database-url>'
    ```

3.  **Apply the Manifests**:
    ```bash
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/hpa.yaml
    ```

4.  **Access the Application**: You will likely need to set up port forwarding or an Ingress to access the application from your local machine. For example, to access the frontend service:
    ```bash
    kubectl port-forward svc/evo-todo-frontend 8080:80
    ```
    You can then access the application at `http://localhost:8080`.
