---
id: 0001
title: Create Specification for Microservices Refactor
stage: spec
date: 2026-02-04
surface: cli
model: gemini-2.5-flash
feature: 001-microservices-refactor
branch: 001-microservices-refactor
user: user
command: /sp.specify
labels: [spec, microservices, dapr, kubernetes]
links:
  spec: specs/001-microservices-refactor/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-microservices-refactor/spec.md
 - specs/001-microservices-refactor/checklists/requirements.md
tests:
 - none
---

## Prompt

### **Implementation Directive: Microservices migration & Dapr Integration**

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
Reference the new Task IDs in every file you create or modify.

## Response snapshot

I have created a feature specification for the microservices refactor. The specification includes user stories, functional requirements, and success criteria based on the provided directive. I also created a quality checklist and validated the specification against it. I have since updated the spec to include Kubernetes and Minikube as dependencies and a functional requirement for Kubernetes deployment. This specification has been further updated to reflect the clarified project structure where backend services are located within a 'backend' folder.

## Outcome

- ✅ Impact: A detailed specification for the microservices refactor has been created and updated multiple times, incorporating all user feedback and clarifications regarding technology and project structure.
- 🧪 Tests: No tests were run.
- 📁 Files: 
  - `specs/001-microservices-refactor/spec.md`
  - `specs/001-microservices-refactor/checklists/requirements.md`
- 🔁 Next prompts: `/sp.plan` to create an implementation plan, ensuring it aligns with the updated spec.
- 🧠 Reflection: The `/sp.specify` command was successfully used to create a comprehensive specification from a detailed directive and was iteratively updated based on user clarification regarding project structure and technology choices.

## Evaluation notes (flywheel)

- Failure modes observed: Model initially missed key technology requirements (Kubernetes, Minikube) and project structure clarification.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Enhance initial parsing for implicit and explicit technology and structural requirements from user prompts.
