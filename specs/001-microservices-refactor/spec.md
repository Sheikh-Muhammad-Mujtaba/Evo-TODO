# Feature Specification: Microservices Migration & Dapr Integration

**Feature Branch**: `001-microservices-refactor`
**Created**: 2026-02-04
**Status**: Draft
**Input**: User description: "### **Implementation Directive: Microservices migration & Dapr Integration**

> **Objective:** Transition the current monolithic backend into a decoupled, microservices-based architecture. You must separate the **Agent logic** from the **Todo logic** to ensure fault isolation and scalability.
> **1. Structural Reorganization**
> * **Action:** create folders in current `backend/` with name `/todo-service/` , '/agent-service/' and '/mcp-server/'.to devide and migrate backend into a new microservices 
> * **Action:** analyze current backend structure functionality and then migrte the related code into the related microservice folder also make sure everything is correctly setup and code is clean for cloud archetecture.
> * **Action:** Create a shared library path: `packages/shared-models/` to store SQLModel definitions used by both services.
> 
> 
> **2. Service Decoupling (The "Logic Split")**
> * **todo-service:** Migrate current todo code make sure It should exclusively handle Task CRUD and User Auth. 
> * **agent-service:** Move `chat_agent.py` and the `/api/chat` endpoint here. This service will handle LLM interactions (Gemini 2.5 Flash), context windowing, and summarization.
> * **mcp-server:** analyze mcp_server make sure everything is setup correctly for the mono repo structure  and dockerd
> * **Communication:** All services now must communicate internally with each other via **Dapr Service Invocation** to execute task tools (Add, List, etc.), rather than importing local modules. 
> * **frontend api:**  Create Api routing for the frontend to communicate all the backend services so the only our api is exposed to frontend and it will me communicating via it.
> 
> **3. Dapr Sidecar Integration**
> * **Action:** Update the root `docker-compose.yml` to launch all micro services, each with a `daprd` (Dapr) sidecar.
> * **Action:** Create a `/dapr/components` directory and define a Redis-based `pubsub.yaml` for asynchronous events (like background summarization).
> 
> 
> **4. Execution Workflow**
> * **Step 1:** Create spects with the knowledge using the `sp.specify` command.
> * **Step 2:** Migrate the codebase service-by-service, starting with the `todo-service` cleanup.
> * **Step 3:** Use the **Better Auth MCP** to ensure both services can verify the same JWT shared secret.
> 
> 
> **Constraint:** 
Don't change any code logics just make sure everything is clean and well structured and works perfectly with each other.
Begin the file migration and code refactoring according to the requirnment. 
Reference the new Task IDs in every file you create or modify."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structural Reorganization (Priority: P1)
As a developer, I want to reorganize the monolithic backend into separate microservices (`todo-service`, `agent-service`, `mcp-server`) and a shared library (`packages/shared-models`) to improve modularity and scalability.

**Why this priority**: This is the foundational step for the entire microservices refactor.

**Independent Test**: The project structure is verified to have the new service directories and the shared models directory.

**Acceptance Scenarios**:
1. **Given** the monolithic backend, **When** the reorganization is performed, **Then** the `backend` directory is replaced with `backend/services/todo-service`, `backend/services/agent-service`, `backend/services/mcp-server`, and `packages/shared-models` directories.

### User Story 2 - Service Decoupling (Priority: P1)
As a developer, I want to decouple the services so that `todo-service` handles only CRUD and auth, `agent-service` handles LLM interactions, and `mcp-server` is correctly set up.

**Why this priority**: This is the core of the microservices refactor, ensuring each service has a single responsibility.

**Independent Test**: The `todo-service` no longer contains any agent logic, and the `agent-service` contains all LLM-related logic.

**Acceptance Scenarios**:
1. **Given** the reorganized services, **When** the decoupling is complete, **Then** `todo-service` only contains CRUD and auth logic, and `agent-service` contains all chat and agent logic.

### User Story 3 - Dapr Integration (Priority: P1)
As a developer, I want to integrate Dapr for inter-service communication and asynchronous events to ensure a robust and scalable microservices architecture.

**Why this priority**: Dapr is essential for the microservices to communicate effectively.

**Independent Test**: The services can communicate with each other using Dapr service invocation, and the `docker-compose.yml` starts all services with Dapr sidecars.

**Acceptance Scenarios**:
1. **Given** the decoupled services, **When** Dapr is integrated, **Then** `agent-service` can call `todo-service` endpoints via Dapr, and the `docker-compose.yml` launches all services with Dapr sidecars.

### User Story 4 - Frontend API Gateway (Priority: P1)
As a developer, I want to create a unified API gateway for the frontend to communicate with all backend services, enhancing security and simplifying frontend development.

**Why this priority**: A single entry point for the frontend is crucial for a clean architecture and security.

**Independent Test**: The frontend application makes all API calls to a single gateway endpoint.

**Acceptance Scenarios**:
1. **Given** the microservices architecture, **When** the API gateway is implemented, **Then** the frontend communicates with all backend services through the gateway.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST be reorganized into three distinct services: `backend/services/todo-service`, `backend/services/agent-service`, and `backend/services/mcp-server`, located within the backend folder.
- **FR-002**: The system MUST have a `packages/shared-models` directory for shared SQLModel definitions.
- **FR-003**: The `todo-service` MUST exclusively handle Task CRUD and User Auth.
- **FR-004**: The `agent-service` MUST handle all LLM interactions, context windowing, and summarization.
- **FR-005**: The `mcp-server` MUST be correctly set up for the monorepo and Docker.
- **FR-006**: All inter-service communication MUST use Dapr Service Invocation.
- **FR-007**: The root `docker-compose.yml` MUST launch all microservices, each with a Dapr sidecar.
- **FR-008**: The system MUST have a `/dapr/components` directory with a Redis-based `pubsub.yaml`.
- **FR-009**: The system MUST have a unified API gateway for the frontend.
- **FR-010**: The microservices architecture MUST be deployable on Kubernetes (e.g., Minikube for local development).

## Edge Cases

- What happens if a Dapr sidecar fails to start?
- How does the system handle a service being down or unresponsive?
- What happens if the shared models in `packages/shared-models` are out of sync between services?

## Dependencies and Assumptions

- **Dependencies**:
  - Dapr
  - Docker & Docker Compose
  - Python 3.13+
  - Node.js 18+
  - Redis
  - Kubernetes (Minikube for local development)
- **Assumptions**:
  - The existing backend logic can be cleanly separated into the defined microservices.
  - The Better Auth MCP can be used to manage JWT secrets across services.
  - The developer has a working knowledge of Dapr, microservices architecture, and Kubernetes concepts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The `todo-service` and `agent-service` can be deployed and scaled independently.
- **SC-002**: The `agent-service` successfully communicates with the `todo-service` via Dapr to perform CRUD operations.
- **SC-003**: The frontend application communicates with the backend services through a single API gateway.
- **SC-004**: The `docker-compose.yml` successfully launches all services and their Dapr sidecars.