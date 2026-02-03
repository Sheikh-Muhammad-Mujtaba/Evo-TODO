# Tasks: Cloud-Native Migration

**Input**: Design documents from `/specs/001-cloud-native-migration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the directory structure for the new artifacts.

- [ ] T001 Create the `/k8s` directory for Kubernetes manifests.
- [ ] T002 Create the `.github/workflows` directory for the CI/CD pipeline.

---

## Phase 2: User Story 1 - Cloud-Native Deployment (Priority: P1) 🎯 MVP

**Goal**: Containerize the application and deploy it to Kubernetes to make it scalable, resilient, and easy to manage.

**Independent Test**: The entire application can be deployed to a Kubernetes cluster from scratch using the defined pipeline, and the application will be fully functional.

### Implementation for User Story 1

- [ ] T003 [US1] [P] Create a multi-stage `Dockerfile` in the `backend/` directory using `python:3.13-slim` for the final stage.
- [ ] T004 [US1] [P] Create a multi-stage `Dockerfile` in the `frontend/` directory using `node:20-alpine` for the final stage.
- [ ] T005 [US1] Create `k8s/deployment.yaml` with `Deployment` resources for both frontend and backend.
- [ ] T006 [US1] Create `k8s/service.yaml` with `Service` resources for both frontend and backend.
- [ ] T007 [US1] Create `k8s/hpa.yaml` with `HorizontalPodAutoscaler` resources for both deployments.
- [ ] T008 [US1] Add Liveness and Readiness probes to the backend deployment in `k8s/deployment.yaml`, targeting the `/health` endpoint.
- [ ] T009 [US1] Create the CI/CD pipeline in `.github/workflows/deploy.yml` with jobs for testing, building, and deploying the application.

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Add final touches and documentation.

- [ ] T010 [P] Add comments with Task IDs to `backend/Dockerfile`.
- [ ] T011 [P] Add comments with Task IDs to `frontend/Dockerfile`.
- [ ] T012 [P] Add comments with Task IDs to `k8s/deployment.yaml`.
- [ ] T013 [P] Add comments with Task IDs to `k8s/service.yaml`.
- [ ] T014 [P] Add comments with Task IDs to `k8s/hpa.yaml`.
- [ ] T015 Update `README.md` with instructions on how to build and run the application using Docker and Kubernetes.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **User Story 1 (Phase 2)**: Depends on Setup completion.
- **Polish (Phase 3)**: Depends on User Story 1 completion.

### Within User Story 1

- Tasks T003 and T004 (Dockerfiles) can be done in parallel.
- Tasks T005, T006, T007 (Kubernetes manifests) can be done after the Dockerfiles are planned.
- Task T008 depends on T005.
- Task T009 depends on all other tasks in the phase being planned.

### Parallel Opportunities

- T003 and T004 can be worked on in parallel.
- T010, T011, T012, T013, T014 can be worked on in parallel after their respective files are created.

## Implementation Strategy

### MVP First (User Story 1 Only)

1.  Complete Phase 1: Setup.
2.  Complete Phase 2: User Story 1.
3.  **STOP and VALIDATE**: Test the full deployment pipeline and ensure the application is running correctly in Kubernetes.
4.  Complete Phase 3: Polish.
5.  Deploy/demo.