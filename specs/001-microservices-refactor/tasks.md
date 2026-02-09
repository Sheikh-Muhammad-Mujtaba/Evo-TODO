---

description: "Task list for Microservices Migration & Dapr Integration"
---

# Tasks: Microservices Migration & Dapr Integration

**Input**: Design documents from `/specs/001-microservices-refactor/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Paths assume a monorepo structure with `backend/services/`, `packages/`, `dapr/`, `frontend/`, `k8s/` at the repository root.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the new project structure and shared components.

- [X] T001 Create `backend/services/` and `packages/` directories.
- [X] T002 Create `backend/services/todo-service/` and `backend/services/agent-service/` directories.
- [X] T003 Create `packages/shared-models/` directory for shared SQLModel definitions.
- [X] T004 Create `dapr/components/` directory for Dapr components.
- [X] T005 Create `k8s/` directory for Kubernetes deployment configurations.
- [X] T006 Copy essential configuration files (e.g., `.env.example`, `pyproject.toml` stubs) into new `backend/services/` service directories as needed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement core Dapr integration and update `docker-compose.yml`.

- [X] T007 Update the root `docker-compose.yml` to define services and Dapr sidecars for `backend/services/todo-service` and `backend/services/agent-service`.
- [X] T008 Define a Redis-based `pubsub.yaml` in `dapr/components/`.
- [X] T009 [P] Configure basic `Dockerfile` for `todo-service`.
- [X] T010 [P] Configure basic `Dockerfile` for `agent-service`.
- [X] T011 [P] Configure basic `Dockerfile` for `backend/mcp_server`.
- [ ] T012 [P] Run database migrations for todo-service using `python migrate_db.py` inside the `todo-service` container.

---

## Phase 3: User Story 1 - Structural Reorganization (Priority: P1) 🎯 MVP

**Goal**: The project structure is verified to have the new service directories and the shared models directory.

**Independent Test**: The project structure is verified to have the new service directories and the shared models directory.

### Implementation for User Story 1

- [X] T013 [US1] Analyze current `backend/` structure and functionality.
- [X] T014 [US1] Migrate `backend/app/` content to `backend/services/todo-service/app/`.
- [X] T015 [US1] Migrate `backend/alembic/` to `backend/services/todo-service/alembic/`.
- [ ] T016 [US1] Migrate `backend/app/models/` content to `backend/services/todo-service/app/models/`.
- [X] T017 [US1] Migrate other `backend/` root files (e.g., `Dockerfile`, `pyproject.toml`, `uv.lock`, `README.md`, `migrate_db.py`) to `backend/services/todo-service/`. (Remaining content like `mcp_server/` and `tests/` will stay in `backend/`).

---

## Phase 4: User Story 2 - Service Decoupling (Priority: P1)

**Goal**: `todo-service` handles only CRUD and auth, `agent-service` handles LLM interactions, and `mcp-server` is correctly set up.

**Independent Test**: The `todo-service` no longer contains any agent logic, and the `agent-service` contains all LLM-related logic.

### Implementation for User Story 2

- [X] T018 [US2] Remove AI Agent and chat-related imports and the `/api/chat` endpoint from `backend/services/todo-service/app/main.py`.
- [X] T019 [US2] Identify and extract AI Agent dependencies (e.g., `app/agents/chat_agent.py`, related models/schemas) from `backend/services/todo-service/`.
- [X] T020 [US2] Move `chat_agent.py` and related AI Agent logic to `backend/services/agent-service/app/agents/`.
- [X] T021 [US2] Move chat endpoints from `backend/services/todo-service/app/api/chat.py` to `backend/services/agent-service/app/api/chat.py`.
- [X] T022 [US2] Remove any remaining AI Agent dependencies and chat endpoints from `backend/services/todo-service/`.
- [X] T023 [US2] Implement initial FastAPI app in `backend/services/agent-service/app/main.py` and integrate chat router.
- [X] T024 [US2] Ensure `backend/services/todo-service/` exclusively handles Task CRUD and User Auth, removing any agent-related imports or logic.
- [X] T025 [US2] Analyze `backend/mcp_server/` structure and set it up as an independent microservice within the `backend/` directory, ensuring it is ready for Dockerization and Dapr integration.
- [X] T026 [US2] Implement missing API endpoints in `backend/services/todo-service/app/api/todos.py` for `api/todos/stats` and `api/todos/check_duplicate`, and ensure all existing Todo CRUD endpoints (`api/todos`, `api/todos/{id}`) are fully functional for Dapr invocation.
- [X] T027 [US2] Remove agent-related dependencies (e.g., modelcontextprotocol, openai-agents, fastmcp) from `backend/services/todo-service/pyproject.toml`.
- [ ] T028 [US2] Remove agent-related settings (e.g., GEMINI_API_KEY, MCP_SERVER_URL) from `backend/services/todo-service/app/core/config.py`.

---

## Phase 5: User Story 3 - Dapr Integration (Priority: P1)

**Goal**: Services can communicate with each other using Dapr service invocation, and `docker-compose.yml` starts all services with Dapr sidecars.

**Independent Test**: The services can communicate with each other using Dapr service invocation, and the `docker-compose.yml` starts all services with Dapr sidecars.

### Implementation for User Story 3

- [X] T029 [US3] Configure `backend/services/agent-service/` to use `MCPServerStreamableHttp` to call the Dapr-enabled `backend/mcp_server` for task tools.
- [X] T030 [US3] Implement Dapr Service Invocation in `backend/mcp_server/` to call `backend/services/todo-service/` task tools, passing the user's JWT token.
- [ ] T031 [US3] Verify Dapr service invocation works correctly between `backend/services/agent-service/` and `backend/services/todo-service/`.

---

## Phase 6: User Story 4 - Frontend API Gateway (Priority: P1)

**Goal**: The frontend application makes all API calls to a single gateway endpoint.

**Independent Test**: The frontend application makes all API calls to a single gateway endpoint.

### Implementation for User Story 4

- [ ] T032 [US4] Design and implement an API Gateway (e.g., using FastAPI in `services/api-gateway/` or a reverse proxy in `docker-compose.yml`) for frontend communication.
- [ ] T033 [US4] Update frontend API client (`frontend/lib/api.ts`) to route requests through the new API gateway endpoint.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finalize configuration, ensure better auth MCP is set up, and clean up.

- [ ] T034 Use the Better Auth MCP to ensure both `backend/services/todo-service` and `backend/services/agent-service` can verify the same JWT shared secret.
- [ ] T035 Update and verify environment variables for all services (`.env` files) to reflect microservices setup.
- [ ] T036 Code cleanup and refactoring across all new `backend/services/` service directories for consistency and adherence to clean code principles.
- [ ] T037 Update project-level documentation (`README.md`, `AGENT.md`) to reflect microservices architecture, Dapr integration, and Kubernetes deployment.
- [ ] T038 Develop and configure Kubernetes manifests for deploying `backend/services/todo-service`, `backend/services/agent-service`, `backend/mcp_server` and Dapr components to Minikube.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion. User stories can proceed in parallel or sequentially.
- **Polish (Phase 7)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1 - Structural Reorganization)**: Can start after Foundational.
- **User Story 2 (P1 - Service Decoupling)**: Depends on User Story 1.
- **User Story 3 (P1 - Dapr Integration)**: Depends on User Story 2.
- **User Story 4 (P1 - Frontend API Gateway)**: Depends on User Story 3.

### Within Each User Story

- Core migration/logic split before integration tasks.
- Ensure file paths are updated correctly during migration.

### Parallel Opportunities

- Tasks in Phase 1 (Setup) can run in parallel where indicated [P].
- Tasks in Phase 2 (Foundational) can run in parallel where indicated [P].
- Once Foundational phase completes, tasks within different user stories can be parallelized, but the user stories themselves have dependencies.

---

## Implementation Strategy

### Incremental Delivery

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Structural Reorganization) -> Validate structure
4. Complete Phase 4: User Story 2 (Service Decoupling) -> Validate service responsibilities
5. Complete Phase 5: User Story 3 (Dapr Integration) -> Validate inter-service communication
6. Complete Phase 6: User Story 4 (Frontend API Gateway) -> Validate frontend communication
7. Complete Phase 7: Polish & Cross-Cutting Concerns

---

## Notes

- All code MUST reference a Task ID in commit messages, PR descriptions, and file content.
- Verify each phase completes successfully before proceeding to the next.
- Avoid conflicts by ensuring tasks affecting the same files are synchronized.
