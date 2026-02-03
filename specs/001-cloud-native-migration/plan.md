# Implementation Plan: Cloud-Native Migration

**Branch**: `001-cloud-native-migration`
**Date**: 2026-02-03
**Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-cloud-native-migration/spec.md`

## Summary

This plan outlines the technical approach for migrating the Evo-TODO application to a cloud-native architecture using Docker and Kubernetes. The goal is to create a scalable, resilient, and manageable deployment by containerizing the frontend and backend services, setting up Kubernetes manifests for orchestration, and automating the build and deployment process with a CI/CD pipeline defined in GitHub Actions.

## Technical Context

**Language/Version**: Python 3.13 (backend), Node.js 20 (frontend)
**Primary Dependencies**: Docker, Kubernetes, GitHub Actions
**Storage**: Kubernetes Secrets for sensitive data (e.g., database connection strings, Better Auth secrets)
**Testing**: pytest (for backend tests integrated into the pipeline)
**Target Platform**: Kubernetes
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Container startup time < 10s, zero-downtime rolling updates.
**Constraints**: Final container image size < 200MB.

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Full-Stack Separation | ✅ PASS | The plan maintains the separation of frontend and backend in distinct containers and services. |
| II. User-Scoped Data / JWT | ✅ PASS | The Kubernetes networking configuration will be set up to ensure the JWT handshake between frontend and backend is maintained. |
| III. Clean Code Principles | ✅ PASS | Dockerfiles will be structured for clarity and maintainability (e.g., multi-stage builds). |
| IV. Task-Driven Implementation | ✅ PASS | All artifacts created (Dockerfiles, k8s manifests) will be traceable to tasks from the spec. |
| V. Performance Over Brevity | ✅ PASS | Multi-stage Docker builds and slim base images are prioritized to meet performance and size constraints. |
| VI. No Manual Code Writing | ✅ PASS | The CI/CD pipeline automates the build, test, and deployment process, reducing manual intervention. |

**Gate Status**: ✅ **PASS** - Plan complies with all constitutional requirements.

## Project Structure

### Documentation (this feature)
```text
specs/001-cloud-native-migration/
├── plan.md              # This file
├── spec.md              # The feature specification
└── checklists/
    └── requirements.md  # The specification quality checklist
```

### Source Code (repository root)

New artifacts to be created:

```text
.github/
└── workflows/
    └── deploy.yml       # CI/CD pipeline for building and deploying to Kubernetes

k8s/
├── deployment.yaml      # Kubernetes manifests for frontend and backend Deployments
├── service.yaml         # Kubernetes manifests for frontend and backend Services
└── hpa.yaml             # Kubernetes Horizontal Pod Autoscaler manifests for services

backend/
└── Dockerfile           # Multi-stage Dockerfile for the backend service

frontend/
└── Dockerfile           # Multi-stage Dockerfile for the frontend service
```

## Implementation Phases

### Phase 1: Containerization

**Goal**: Create optimized, production-ready Docker images for the frontend and backend services.

**Tasks**:
1.  **Create Backend Dockerfile**:
    - Use a multi-stage build.
    - Stage 1 (build): Use a full Python image to install dependencies using `uv`.
    - Stage 2 (final): Use the `python:3.13-slim` base image. Copy in dependencies and application code.
    - Ensure the image runs as a non-root user.
2.  **Create Frontend Dockerfile**:
    - Use a multi-stage build.
    - Stage 1 (build): Use a full Node.js image to install dependencies (`npm install`) and build the Next.js application (`npm run build`).
    - Stage 2 (final): Use the `node:20-alpine` base image. Copy in the built application and `node_modules`.
    - Ensure the image runs as a non-root user.
3.  **Local Testing**: Build both images locally and test them using Docker Compose to ensure they run correctly and can communicate with each other.

### Phase 2: Kubernetes Manifests

**Goal**: Define the Kubernetes resources required to run the application.

**Tasks**:
1.  **`deployment.yaml`**:
    - Create two `Deployment` resources, one for the frontend and one for the backend.
    - Specify the Docker images created in Phase 1.
    - Configure resource requests and limits.
    - Define Liveness and Readiness probes for the backend deployment, targeting the `/health` endpoint.
    - Mount Kubernetes Secrets as environment variables for sensitive data.
2.  **`service.yaml`**:
    - Create two `Service` resources (e.g., `ClusterIP` type), one for the frontend and one for the backend, to provide stable internal endpoints.
3.  **`hpa.yaml`**:
    - Create `HorizontalPodAutoscaler` resources for both deployments to enable auto-scaling based on CPU or memory utilization.
4.  **Ingress Configuration** (to be applied separately or included if an Ingress controller is standard):
    - Define rules to route external traffic to the frontend and backend services.

### Phase 3: CI/CD Pipeline

**Goal**: Automate the build, test, and deployment process using GitHub Actions.

**Tasks**:
1.  **Create `deploy.yml`**:
    - **Trigger**: On push to the `main` branch.
    - **Job 1: Test**:
        - Check out the code.
        - Run backend tests (pytest). If tests fail, the pipeline fails.
    - **Job 2: Build and Push (depends on Test)**:
        - Log in to a container registry (e.g., Docker Hub, GitHub Container Registry).
        - Build the frontend and backend Docker images.
        - Tag the images with the Git commit SHA.
        - Push the images to the registry.
    - **Job 3: Deploy (depends on Build and Push)**:
        - Check out the code.
        - Configure `kubectl` with credentials for the target Kubernetes cluster.
        - Apply the Kubernetes manifests from the `/k8s` directory.

## Key Architectural Decisions

- **Multi-Stage Docker Builds**: Chosen to create minimal, secure, and efficient final images by separating the build environment from the runtime environment. This directly addresses the <200MB image size constraint.
- **Declarative Deployments with Kubernetes**: Kubernetes is chosen for its robustness, scalability, and industry-standard status for container orchestration. This aligns with the goal of a scalable and resilient system.
- **GitHub Actions for CI/CD**: Chosen for its tight integration with GitHub, ease of use, and extensive marketplace of actions.

## Security Implementation Checklist

- [X] **No Secrets in Code**: All secrets, including `DATABASE_URL` and `BETTER_AUTH_SECRET`, will be managed by Kubernetes Secrets and injected into pods as environment variables.
- [X] **Minimal Base Images**: Using `slim` and `alpine` base images reduces the attack surface of the containers.
- [X] **Non-Root Users**: Containers will be configured to run with non-root users to limit potential damage in case of a container breakout.
- [X] **Automated Testing**: The CI/CD pipeline will enforce that all tests pass before a build can proceed to deployment, preventing regressions.

## Testing Strategy

- **CI Pipeline**: The backend's unit and integration tests will be run automatically on every push to `main`.
- **Post-Deployment**:
    - Liveness and Readiness probes will automatically check the health of the backend service.
    - Manual end-to-end testing will be performed after the first successful deployment to verify connectivity between frontend and backend, and to ensure the JWT authentication flow is working correctly.
    - Uptime monitoring tools can be configured to ping the application's public endpoint.

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Kubernetes Complexity | Medium | High | Start with a managed Kubernetes service (e.g., GKE, EKS, AKS) to offload control plane management. Provide clear documentation and training for the team. |
| Networking Issues | Medium | High | Thoroughly test service-to-service communication in a staging environment. Ensure Ingress rules and `BACKEND_URL` environment variables are correctly configured. |
| CI/CD Pipeline Failures | Medium | Medium | Implement robust error handling and notifications in the GitHub Actions workflow. Ensure secrets (e.g., registry credentials) are correctly configured. |

## Definition of Done

- Dockerfiles for frontend and backend are created and successfully build images under 200MB.
- Kubernetes manifests for `Deployment`, `Service`, and `HPA` are created.
- The GitHub Actions workflow successfully automates the testing, building, and deployment of the application.
- The application is running successfully in a Kubernetes cluster and is accessible externally.
- All secrets are managed via Kubernetes Secrets.