# Implementation Plan: Microservices Migration & Dapr Integration

**Branch**: `001-microservices-refactor` | **Date**: 2026-02-04 | **Spec**: specs/001-microservices-refactor/spec.md
**Input**: Feature specification from `/specs/001-microservices-refactor/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The objective is to transition the current monolithic backend into a decoupled, microservices-based architecture by separating Agent and Todo logic, integrating Dapr for inter-service communication, and ensuring clean, scalable, cloud-ready code. This includes reorganizing the project structure, decoupling services, integrating Dapr sidecars, and setting up appropriate communication patterns.

## Technical Context

**Language/Version**: Python 3.13+ (for backend services), Node.js 18+ (for frontend)
**Primary Dependencies**: FastAPI, SQLModel, Next.js, React, Tailwind CSS, Dapr, Docker, Docker Compose, Kubernetes (Minikube for local development), Redis
**Storage**: PostgreSQL (Neon Serverless for production, Docker for local development)
**Testing**: Pytest (Python), Jest/React Testing Library (Frontend)
**Target Platform**: Kubernetes (Minikube for local development)
**Project Type**: Microservices (Backend), Web Application (Frontend)
**Performance Goals**: Decoupled services should improve scalability and fault isolation; Dapr communication should be performant.
**Constraints**: All inter-service communication MUST use Dapr; shared models MUST reside in `packages/shared-models`; all code MUST reference a Task ID.
**Scale/Scope**: Transition from monolithic to microservices for better scalability, fault isolation, and maintainability.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The plan aligns with the updated constitution (v3.1.0 Microservices Refactor), particularly regarding Microservices Architecture, Dapr Integration, Shared Models Contract, and Task-Driven Implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-microservices-refactor/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification
└── checklists/
    └── requirements.md  # Specification Quality Checklist
```

### Source Code (repository root)

```text
Evo-TODO/
├── frontend/                   # Next.js 16+ React application
├── backend/
│   ├── services/
│   │   ├── todo-service/           # FastAPI application (Task CRUD and User Auth)
│   │   ├── agent-service/          # FastAPI application (LLM interactions, context, summarization)
│   │   └── mcp-server/             # MCP Server (to be analyzed and potentially refactored)
├── packages/
│   └── shared-models/          # Shared SQLModel definitions
├── dapr/
│   └── components/             # Dapr components (e.g., pubsub.yaml)
├── docker-compose.yml          # Docker Compose for local development (including Dapr sidecars)
├── k8s/                        # Kubernetes deployment configurations
```

**Structure Decision**: The selected structure is a monorepo containing distinct service directories under `backend/services/`, a `packages/` directory for shared components, and a `dapr/` directory for Dapr-specific configurations. This aligns with the microservices objective.

## Complexity Tracking

No constitution violations detected that require justification.
