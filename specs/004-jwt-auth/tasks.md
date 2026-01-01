# Tasks: JWT Authentication Integration (Phase 2.2)

**Input**: Design documents from `/specs/004-jwt-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md
**Status**: Ready for implementation
**Branch**: `004-jwt-auth`

**Implementation Strategy**: All tasks validated against Better Auth documentation, FastAPI best practices, and the specification. Each task includes:
- Clear acceptance criteria
- File paths for implementation
- Validation steps from docs
- Error handling requirements
- Testing checklist items

---

## Phase 1: Setup & Project Initialization

**Purpose**: Project structure, dependencies, and configuration

- [ ] T001 [P] Initialize frontend project with Next.js 16+ App Router (`frontend/package.json`)
  - [ ] Add `better-auth`, `jose`, `typescript` dependencies
  - [ ] Validate: `npm install` succeeds without conflicts
  - [ ] Reference: Better Auth docs - Installation section

- [ ] T002 [P] Initialize backend project with FastAPI (`backend/requirements.txt`)
  - [ ] Add: `fastapi==0.100+`, `python-jose[cryptography]`, `httpx`, `pydantic`, `sqlmodel`
  - [ ] Validate: `pip install -r requirements.txt` succeeds
  - [ ] Reference: FastAPI docs - Installation section

- [ ] T003 [P] Create project directory structure per plan.md
  - [ ] Frontend: `frontend/src/{lib,components,hooks,app,tests}`
  - [ ] Backend: `backend/src/{auth,models,routes,tests}`
  - [ ] Database: migrations folder for Alembic
  - [ ] Validate: All directories exist with `.gitkeep` files

- [ ] T004 Create environment configuration files
  - [ ] Frontend: `frontend/.env.local` with `NEXT_PUBLIC_AUTH_URL`, `NEXT_PUBLIC_API_URL`
  - [ ] Backend: `backend/.env` with `DATABASE_URL`, `BETTER_AUTH_BASE_URL`
  - [ ] Validate: Sample `.env.example` files created with placeholder values

- [ ] T005 [P] Setup linting and formatting
  - [ ] Frontend: ESLint + Prettier configuration
  - [ ] Backend: Black + isort configuration
  - [ ] Validate: `npm run lint` and `pytest --linting` run without errors

- [ ] T006 Setup git hooks and commit validation
  - [ ] Create pre-commit hooks to run linting before commits
  - [ ] Validate: `git commit` triggers linting checks

**Checkpoint**: Project structure ready - can begin foundational work

---

## Phase 2: Foundational Infrastructure (BLOCKING - MUST COMPLETE BEFORE USER STORIES)

**Purpose**: Core authentication, database, and API infrastructure that all user stories depend on

⚠️ **CRITICAL**: No user story work can begin until this entire phase is complete

### Better Auth Setup (Frontend Foundation)

- [ ] T007 Configure Better Auth JWT plugin
  - [ ] File: `frontend/src/auth.ts` (or equivalent)
  - [ ] Enable JWT plugin with EdDSA (Ed25519) signing
  - [ ] Configure JWT payload to include `sub` (user ID) and `email`
  - [ ] Set expiration to 7 days
  - [ ] Add `trustedOrigins` for frontend URL
  - [ ] Validate: Code matches Better Auth JWT docs - "Installation" section
  - [ ] Error check: JWT plugin must be listed in `plugins: [jwt()]`

- [ ] T008 Run Better Auth database migration
  - [ ] Command: `npx @better-auth/cli migrate`
  - [ ] Validate: `jwks`, `user`, `session`, `account` tables created in PostgreSQL
  - [ ] Error check: No migration errors; tables visible in DB client
  - [ ] Reference: Better Auth docs - JWT Plugin Schema section

- [ ] T009 Create Better Auth client with jwtClient plugin
  - [ ] File: `frontend/src/lib/auth-client.ts`
  - [ ] Import: `createAuthClient` from `better-auth/react`
  - [ ] Add `jwtClient()` plugin to client configuration
  - [ ] Validate: Code matches Better Auth docs - "Client Configuration" section
  - [ ] Error check: `authClient.token()` method is available

### Frontend API Client Foundation

- [ ] T010 Create ApiClient class with token attachment
  - [ ] File: `frontend/src/lib/api-client.ts`
  - [ ] Implement `ApiClient` class with:
     - [ ] `getToken()` method: retrieves from localStorage
     - [ ] `ensureValidToken()` method: fetches new token if needed
     - [ ] `request()` method: attaches `Authorization: Bearer <token>` header
  - [ ] Validate: Token is attached to every request (check in network tab)
  - [ ] Error check: 401 response triggers `auth:unauthorized` event
  - [ ] Handle: 401 errors by removing token and prompting re-auth

- [ ] T011 Implement token expiration listener
  - [ ] File: `frontend/src/hooks/use-auth-error.ts`
  - [ ] Listen for `auth:unauthorized` event
  - [ ] Remove token from localStorage on 401
  - [ ] Redirect to `/login` with `?expired=true` query param
  - [ ] Validate: Expired token triggers redirect to login

### Backend JWT Verification Foundation

- [ ] T012 Create JWT verification module with JWKS caching
  - [ ] File: `backend/src/auth/jwt.py`
  - [ ] Implement:
     - [ ] `get_jwks()`: Async function to fetch and cache JWKS from Better Auth
     - [ ] `verify_token()`: Extract JWT from Authorization header
     - [ ] Parse unverified header to get `kid` (key ID)
     - [ ] Fetch matching public key from JWKS
     - [ ] Verify token signature using `python-jose`
     - [ ] Return user_id from token `sub` claim
  - [ ] Cache JWKS: Use `@lru_cache(maxsize=1)` to avoid repeated HTTP calls
  - [ ] Error handling:
     - [ ] Return 401 for missing token
     - [ ] Return 401 for invalid signature
     - [ ] Return 401 for expired token (check `exp` claim)
  - [ ] Validate: Code matches Context7 docs - FastAPI JWT patterns
  - [ ] Reference: python-jose docs for `jwtVerify()` usage

- [ ] T013 Create user ownership validation dependency
  - [ ] File: `backend/src/auth/jwt.py`
  - [ ] Implement `verify_user_ownership(path_user_id: str, token_user_id: str)`
  - [ ] Raise 403 Forbidden if IDs don't match
  - [ ] Use FastAPI `Depends()` for dependency injection
  - [ ] Validate: Called in every route handler before business logic

### Database & ORM Foundation

- [ ] T014 [P] Create Task Pydantic models
  - [ ] File: `backend/src/models/task.py`
  - [ ] Define:
     - [ ] `TaskBase`: title (required, 1-255 chars), description (optional, max 2000)
     - [ ] `TaskCreate`: extends TaskBase
     - [ ] `TaskUpdate`: all fields optional
     - [ ] `Task`: full entity with id, user_id, completed, created_at, updated_at
  - [ ] Validate: All fields have correct types and constraints (matching spec SC)
  - [ ] Error check: Pydantic validation works for invalid inputs

- [ ] T015 [P] Create SQLModel Task entity
  - [ ] File: `backend/src/models/task.py` (or separate file)
  - [ ] Define SQLModel table `task`:
     - [ ] Columns: id (str, UUID), user_id (str, UUID, FK to user), title, description, completed (bool), created_at, updated_at
     - [ ] Constraints: user_id NOT NULL, title NOT NULL and length > 0
     - [ ] Indices: (user_id), (completed), (user_id, created_at DESC)
  - [ ] Foreign key: CASCADE delete if user is deleted
  - [ ] Validate: Schema matches data-model.md specification

- [ ] T016 Setup async database session and engine
  - [ ] File: `backend/src/database.py`
  - [ ] Create async SQLAlchemy engine for PostgreSQL
  - [ ] Create async session factory
  - [ ] Implement `get_db()` dependency for FastAPI
  - [ ] Validate: Database connection works
  - [ ] Error check: Async context manager works correctly

### FastAPI App Foundation

- [ ] T017 Create FastAPI app with CORS and error handling
  - [ ] File: `backend/src/main.py`
  - [ ] Create `FastAPI()` instance with title, version, description
  - [ ] Configure CORS:
     - [ ] Allow frontend origin (localhost:3000 for dev, production URL for prod)
     - [ ] Allow credentials: true
     - [ ] Allow methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
     - [ ] Allow headers: Content-Type, Authorization, X-Requested-With
  - [ ] Add global exception handlers for:
     - [ ] `HTTPException`: return status code and detail
     - [ ] `ValidationError`: return 422 with error details
  - [ ] Add health check endpoint: GET `/health`
  - [ ] Validate: CORS headers present in responses
  - [ ] Error check: 400 Bad Request for invalid payloads

- [ ] T018 Setup API routing structure
  - [ ] File: `backend/src/main.py`
  - [ ] Create APIRouter for tasks: `router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])`
  - [ ] Include router in FastAPI app: `app.include_router(router)`
  - [ ] Validate: Routes accessible at `/api/{user_id}/tasks/*`

**Checkpoint**: Foundation infrastructure complete - All user stories can now begin in parallel

---

## Phase 3: User Story 1 - User Logs In and Receives JWT Token (Priority: P1) 🎯 MVP

**Goal**: Users can authenticate via Better Auth and receive JWT tokens for API requests

**Independent Test**: Log in → token stored in localStorage → token contains user ID and email

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create login form component
  - [ ] File: `frontend/src/components/login-form.tsx`
  - [ ] Form fields: email (required), password (required)
  - [ ] Handle `authClient.signIn.email()` call
  - [ ] On success:
     - [ ] Fetch JWT token: `const { data } = await authClient.token()`
     - [ ] Store in localStorage: `localStorage.setItem('jwt_token', data.token)`
  - [ ] On error: Display error message
  - [ ] Validate: Token stored after successful login
  - [ ] Error handling: Show validation errors for empty fields

- [ ] T020 [P] [US1] Create login page with routing
  - [ ] File: `frontend/src/app/login/page.tsx`
  - [ ] Import and render `<LoginForm />`
  - [ ] Add redirect to dashboard on successful login
  - [ ] Validate: Navigate to `/login` works without auth

- [ ] T021 [US1] Create useAuth hook for session state
  - [ ] File: `frontend/src/hooks/use-auth.ts`
  - [ ] Hook returns:
     - [ ] `session`: Current user session (from Better Auth)
     - [ ] `isLoading`: Boolean
     - [ ] `isAuthenticated`: Check if JWT token exists
     - [ ] `logout()`: Clear token and session
  - [ ] Validate: Hook returns correct user data after login

- [ ] T022 [US1] Create protected layout with auth check
  - [ ] File: `frontend/src/app/layout.tsx`
  - [ ] Wrap children with auth context/provider
  - [ ] Check authentication on mount
  - [ ] Redirect unauthenticated users to `/login`
  - [ ] Validate: Cannot access `/dashboard` without login

### Validation for User Story 1

- [ ] T023 [US1] Validate JWT token structure
  - [ ] Manual test: Log in and inspect localStorage
  - [ ] Decode token (use jwt.io or jose.jwtDecode)
  - [ ] Verify claims: `sub` (user ID), `email`, `iat`, `exp`, `iss`, `aud`
  - [ ] Validate: Token expires in ~7 days from issuance
  - [ ] Error check: Invalid credentials fail silently

- [ ] T024 [US1] Validate token persistence across page refresh
  - [ ] Steps:
     1. Log in successfully
     2. Inspect localStorage for `jwt_token`
     3. Refresh page (`F5`)
     4. Check token still exists
     5. Verify user still logged in
  - [ ] Validate: Page refresh doesn't clear token

- [ ] T025 [US1] Document User Story 1 in quickstart.md
  - [ ] Verify quickstart.md Frontend Phase 1-2 sections match implementation
  - [ ] Validate: All code examples run without errors
  - [ ] Cross-check: Better Auth docs, quickstart.md, and implementation align

**Checkpoint**: User Story 1 complete - Users can log in and receive JWT tokens

---

## Phase 4: User Story 2 - Frontend Attaches JWT Token to API Requests (Priority: P1)

**Goal**: Every API request from frontend automatically includes JWT token in Authorization header

**Independent Test**: Make API call → Authorization header contains `Bearer <token>` → Backend receives token

### Implementation for User Story 2

- [ ] T026 [P] [US2] Implement ApiClient request method with token attachment
  - [ ] File: `frontend/src/lib/api-client.ts`
  - [ ] Method: `async request<T>(endpoint: string, options: RequestInit): Promise<T>`
  - [ ] Steps:
     1. Call `ensureValidToken()`
     2. Get token from localStorage
     3. Create headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
     4. Merge with options.headers
     5. Call `fetch(url, {...options, headers})`
  - [ ] Handle errors:
     - [ ] 401: Remove token, dispatch `auth:unauthorized` event
     - [ ] Non-200: Parse error response and throw
  - [ ] Validate: Token present in Authorization header (check network tab)

- [ ] T027 [P] [US2] Create ApiClient methods for all 6 task endpoints
  - [ ] File: `frontend/src/lib/api-client.ts`
  - [ ] Methods:
     - [ ] `listTasks(userId: string): Promise<any[]>`  → GET `/api/{user_id}/tasks`
     - [ ] `createTask(userId: string, title, description?): Promise<any>` → POST `/api/{user_id}/tasks`
     - [ ] `getTask(userId: string, taskId: string): Promise<any>` → GET `/api/{user_id}/tasks/{taskId}`
     - [ ] `updateTask(userId: string, taskId: string, updates: any): Promise<any>` → PUT `/api/{user_id}/tasks/{taskId}`
     - [ ] `deleteTask(userId: string, taskId: string): Promise<void>` → DELETE `/api/{user_id}/tasks/{taskId}`
     - [ ] `toggleTaskCompletion(userId: string, taskId: string): Promise<any>` → PATCH `/api/{user_id}/tasks/{taskId}/complete`
  - [ ] Each calls `request()` with appropriate method and body
  - [ ] Validate: All methods callable and return correct types

- [ ] T028 [P] [US2] Create task hooks for React components
  - [ ] File: `frontend/src/hooks/use-tasks.ts`
  - [ ] Hooks:
     - [ ] `useTaskList(userId)`: Fetch and manage task list state
     - [ ] `useCreateTask(userId)`: Handle task creation with loading/error states
     - [ ] `useUpdateTask(userId)`: Handle task updates
     - [ ] `useDeleteTask(userId)`: Handle task deletion
  - [ ] Each hook:
     - [ ] Returns `{data, loading, error, mutate}`
     - [ ] Handles errors gracefully
     - [ ] Shows 401 error if token missing/invalid
  - [ ] Validate: Hooks return correct data structure

### Validation for User Story 2

- [ ] T029 [US2] Validate Authorization header in API requests
  - [ ] Manual test:
     1. Log in and obtain JWT token
     2. Open DevTools Network tab
     3. Make API call via `apiClient.listTasks()`
     4. Inspect request headers
  - [ ] Verify: `Authorization: Bearer <token>` header present
  - [ ] Error check: Header format is exactly `Bearer ` (space) then token

- [ ] T030 [US2] Validate token attachment for all HTTP methods
  - [ ] Test each method: GET, POST, PUT, DELETE, PATCH
  - [ ] Verify Authorization header in all requests
  - [ ] Error check: HEAD and OPTIONS also include header

- [ ] T031 [US2] Validate missing token error handling
  - [ ] Steps:
     1. Clear localStorage: `localStorage.removeItem('jwt_token')`
     2. Try to call `apiClient.listTasks()`
  - [ ] Verify: Error thrown or 401 received
  - [ ] Validate: `auth:unauthorized` event dispatched
  - [ ] Check: Redirect to login triggered

**Checkpoint**: User Story 2 complete - Frontend attaches tokens to all requests

---

## Phase 5: User Story 3 - Backend Verifies JWT Token and Identifies User (Priority: P1)

**Goal**: Backend validates JWT tokens and extracts user ID for request context

**Independent Test**: Send request with valid token → 200 OK with user_id extracted; invalid token → 401 Unauthorized

### Implementation for User Story 3

- [ ] T032 [P] [US3] Implement JWT verification middleware dependency
  - [ ] File: `backend/src/auth/jwt.py`
  - [ ] Dependency: `async def verify_token(credentials: HTTPAuthCredentials = Depends(HTTPBearer()))`
  - [ ] Extract token from `credentials.credentials`
  - [ ] Call `get_jwks()` to fetch public keys (cached)
  - [ ] Decode JWT using `python-jose`:
     - [ ] Unverified header to get `kid`
     - [ ] Find matching key in JWKS
     - [ ] Call `jwt.decode()` with key
  - [ ] Return user_id from `sub` claim
  - [ ] Error handling:
     - [ ] JWTError → 401 with "Invalid authentication credentials"
     - [ ] Missing token → 401 (HTTPBearer handles this)
     - [ ] Expired token → 401 (python-jose checks `exp`)
  - [ ] Validate: Code matches Context7 FastAPI docs - JWT verification section

- [ ] T033 [US3] Test verify_token with valid token
  - [ ] Steps:
     1. Get valid token from login
     2. Create mock request with Authorization header
     3. Call `verify_token()` dependency
  - [ ] Verify: Returns correct user_id
  - [ ] Check: No exceptions thrown

- [ ] T034 [US3] Test verify_token with invalid token
  - [ ] Test cases:
     - [ ] Invalid signature: Malformed JWT
     - [ ] Expired token: Token with `exp` < current time
     - [ ] Wrong algorithm: Token signed with different algorithm
     - [ ] Missing token: No Authorization header
  - [ ] Verify: All cases raise HTTPException(status_code=401)
  - [ ] Check: Error message is user-friendly

- [ ] T035 [US3] Test JWKS caching performance
  - [ ] Measure: Time to verify first token (fetches JWKS)
  - [ ] Measure: Time to verify second token (uses cache)
  - [ ] Validate: Second call is significantly faster (cache hit)
  - [ ] Success: Both calls < 50ms (SC-003 requirement)

### Validation for User Story 3

- [ ] T036 [US3] Manual test: Valid token returns 200
  - [ ] Steps:
     1. Get token from login
     2. Create curl request with token: `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/{user_id}/tasks`
  - [ ] Verify: 200 OK response
  - [ ] Check: Response contains task data (if tasks exist)

- [ ] T037 [US3] Manual test: Missing token returns 401
  - [ ] Steps: `curl http://localhost:8000/api/{user_id}/tasks` (no Authorization header)
  - [ ] Verify: 401 Unauthorized response
  - [ ] Check: Response detail: "Not authenticated"

- [ ] T038 [US3] Manual test: Invalid token returns 401
  - [ ] Steps: `curl -H "Authorization: Bearer invalid.token.here" http://localhost:8000/api/{user_id}/tasks`
  - [ ] Verify: 401 Unauthorized
  - [ ] Check: Response detail: "Invalid authentication credentials"

**Checkpoint**: User Story 3 complete - Backend verifies tokens and extracts user IDs

---

## Phase 6: User Story 4 - Users Only See Their Own Tasks (Priority: P1)

**Goal**: API filters tasks by authenticated user ID; cross-user requests rejected with 403

**Independent Test**: User A logs in → sees only User A's tasks; User A cannot access User B's tasks (403 Forbidden)

### Implementation for User Story 4

- [ ] T039 [US4] Create helper function for user task validation
  - [ ] File: `backend/src/routes/tasks.py` or `backend/src/auth/jwt.py`
  - [ ] Function: `async def get_user_task(user_id: str, task_id: str, db: AsyncSession, current_user_id: str = Depends(verify_token))`
  - [ ] Steps:
     1. Call `verify_user_ownership(user_id, current_user_id)` → 403 if mismatch
     2. Query: `SELECT * FROM task WHERE id = task_id AND user_id = current_user_id`
     3. Return task if found
     4. Raise 404 if not found
  - [ ] Validate: Helper used in all task routes

- [ ] T040 [P] [US4] Implement GET /api/{user_id}/tasks (list tasks)
  - [ ] File: `backend/src/routes/tasks.py`
  - [ ] Handler: `async def list_tasks(user_id: str, db: AsyncSession, current_user_id: str = Depends(verify_token))`
  - [ ] Steps:
     1. Call `verify_user_ownership(user_id, current_user_id)` → 403 if mismatch
     2. Query: `SELECT * FROM task WHERE user_id = current_user_id`
     3. Return `{data: [tasks], count: len(tasks)}`
  - [ ] Error handling: 403 if user_id doesn't match token
  - [ ] Validate: Only returns tasks for authenticated user

- [ ] T041 [P] [US4] Add user ownership validation to all routes
  - [ ] Routes to update:
     - [ ] GET `/api/{user_id}/tasks/{task_id}`
     - [ ] PUT `/api/{user_id}/tasks/{task_id}`
     - [ ] DELETE `/api/{user_id}/tasks/{task_id}`
     - [ ] PATCH `/api/{user_id}/tasks/{task_id}/complete`
  - [ ] Each route:
     - [ ] Extract `user_id` from path
     - [ ] Get `current_user_id` from `verify_token()` dependency
     - [ ] Call `verify_user_ownership()` at start
     - [ ] Filter all queries by `user_id = current_user_id`
  - [ ] Validate: All routes follow same pattern

### Validation for User Story 4

- [ ] T042 [US4] Test: User A cannot access User B's task
  - [ ] Setup:
     1. Create User A and User B accounts
     2. User A creates Task X
     3. Get User B's token
  - [ ] Test: `GET /api/{user_b_id}/tasks` as User B
  - [ ] Verify: Does not include Task X
  - [ ] Test: `GET /api/{user_b_id}/tasks/{task_x_id}` as User B
  - [ ] Verify: 404 Not Found or 403 Forbidden (spec says either acceptable)

- [ ] T043 [US4] Test: Cross-user modifications rejected
  - [ ] Setup: User A has Task X
  - [ ] Test as User B:
     - [ ] PUT `/api/{user_b_id}/tasks/{task_x_id}` → 403 Forbidden
     - [ ] DELETE `/api/{user_b_id}/tasks/{task_x_id}` → 403 Forbidden
     - [ ] PATCH `/api/{user_b_id}/tasks/{task_x_id}/complete` → 403 Forbidden
  - [ ] Verify: All return 403 Forbidden

- [ ] T044 [US4] Test: URL user_id mismatch returns 403
  - [ ] Setup: User A has token
  - [ ] Test: GET `/api/{different_user_id}/tasks` as User A
  - [ ] Verify: 403 Forbidden
  - [ ] Verify: Response message indicates access denied

**Checkpoint**: User Story 4 complete - User isolation enforced on all endpoints

---

## Phase 7: User Story 5 - Task CRUD Operations with User Isolation (Priority: P1)

**Goal**: All task operations (create, read, update, delete, toggle) work with user isolation

**Independent Test**: Complete full task lifecycle: login → create → read → update → delete (all filtered by user ID)

### Implementation for User Story 5

- [ ] T045 [P] [US5] Implement POST /api/{user_id}/tasks (create task)
  - [ ] File: `backend/src/routes/tasks.py`
  - [ ] Handler: `async def create_task(user_id: str, task: TaskCreate, db: AsyncSession, current_user_id: str = Depends(verify_token))`
  - [ ] Steps:
     1. Verify ownership: `verify_user_ownership(user_id, current_user_id)`
     2. Create Task entity: `Task(id=uuid4(), user_id=current_user_id, title=task.title, ...)`
     3. Save to DB: `db.add(new_task); await db.commit()`
     4. Return 201 Created with task data
  - [ ] Validation:
     - [ ] Title required, 1-255 chars
     - [ ] Description optional, max 2000 chars
     - [ ] Return 422 for invalid input
  - [ ] Validate: Created task belongs to authenticated user

- [ ] T046 [P] [US5] Implement GET /api/{user_id}/tasks/{task_id} (read task)
  - [ ] File: `backend/src/routes/tasks.py`
  - [ ] Handler: `async def get_task(user_id: str, task_id: str, db: AsyncSession, current_user_id: str = Depends(verify_token))`
  - [ ] Use `get_user_task()` helper
  - [ ] Return Task if owned by user, else 404
  - [ ] Validate: Cannot read another user's task

- [ ] T047 [P] [US5] Implement PUT /api/{user_id}/tasks/{task_id} (update task)
  - [ ] File: `backend/src/routes/tasks.py`
  - [ ] Handler: `async def update_task(user_id: str, task_id: str, updates: TaskUpdate, db: AsyncSession, current_user_id: str = Depends(verify_token))`
  - [ ] Steps:
     1. Get task using `get_user_task()` → 403/404 if not found
     2. Update fields: title, description, completed (if provided)
     3. Update `updated_at` timestamp
     4. Save: `await db.commit()`
     5. Return updated Task
  - [ ] Validate: All fields update correctly
  - [ ] Partial updates: Only specified fields updated

- [ ] T048 [P] [US5] Implement DELETE /api/{user_id}/tasks/{task_id} (delete task)
  - [ ] File: `backend/src/routes/tasks.py`
  - [ ] Handler: `async def delete_task(user_id: str, task_id: str, db: AsyncSession, current_user_id: str = Depends(verify_token))`
  - [ ] Steps:
     1. Get task using `get_user_task()` → 403/404 if not found
     2. Delete: `await db.delete(task); await db.commit()`
     3. Return 204 No Content
  - [ ] Validate: Task deleted from DB
  - [ ] Error handling: Cannot delete another user's task (403)

- [ ] T049 [P] [US5] Implement PATCH /api/{user_id}/tasks/{task_id}/complete (toggle completion)
  - [ ] File: `backend/src/routes/tasks.py`
  - [ ] Handler: `async def toggle_task_completion(user_id: str, task_id: str, db: AsyncSession, current_user_id: str = Depends(verify_token))`
  - [ ] Steps:
     1. Get task using `get_user_task()` → 403/404 if not found
     2. Toggle: `task.completed = not task.completed`
     3. Update timestamp: `task.updated_at = datetime.utcnow()`
     4. Save: `await db.commit()`
     5. Return updated Task
  - [ ] Validate: Completion status toggles correctly

### Validation for User Story 5

- [ ] T050 [US5] Test full task lifecycle: Create → Read → Update → Toggle → Delete
  - [ ] Setup: Authenticated user with JWT token
  - [ ] Steps:
     1. POST `/api/{user_id}/tasks` with title "Test Task"
     2. Verify 201 Created, task has `id`
     3. GET `/api/{user_id}/tasks/{task_id}`
     4. Verify 200 OK, data matches
     5. PUT `/api/{user_id}/tasks/{task_id}` with new title
     6. Verify 200 OK, title updated
     7. PATCH `/api/{user_id}/tasks/{task_id}/complete`
     8. Verify 200 OK, `completed = true`
     9. DELETE `/api/{user_id}/tasks/{task_id}`
     10. Verify 204 No Content
  - [ ] Measure: Total time < 30 seconds (SC-008)

- [ ] T051 [US5] Test error handling for invalid inputs
  - [ ] POST with empty title → 422 Unprocessable Entity
  - [ ] PUT with title > 255 chars → 422 Unprocessable Entity
  - [ ] POST with description > 2000 chars → 422 Unprocessable Entity
  - [ ] Verify: Error response includes field-level error messages

- [ ] T052 [US5] Test concurrent operations
  - [ ] Create multiple tasks (5+) quickly
  - [ ] Update same task from two requests simultaneously
  - [ ] Verify: No race conditions, last write wins
  - [ ] Verify: Database integrity maintained

- [ ] T053 [US5] Test performance of all 6 endpoints
  - [ ] Benchmark each endpoint with 100 requests
  - [ ] Measure: Average response time
  - [ ] Verify: All endpoints < 200ms average (SC target)
  - [ ] Verify: Token verification < 50ms (SC-003)

**Checkpoint**: User Story 5 complete - Full CRUD with user isolation working

---

## Phase 8: Cross-Story Integration & Validation

**Purpose**: Verify all user stories work together correctly

- [ ] T054 [P] Validate all 6 endpoints accessible
  - [ ] Test: GET, POST, PUT, DELETE, PATCH work
  - [ ] Verify: All endpoints require JWT token (401 without)
  - [ ] Verify: All endpoints filter by user_id (403 for wrong user)

- [ ] T055 [P] Validate user isolation across all operations
  - [ ] Test with 3 users:
     1. User A creates Task X
     2. User B creates Task Y
     3. User C creates Task Z
  - [ ] Each user:
     - [ ] Can see only own task (GET /api/{user_id}/tasks)
     - [ ] Cannot update other users' tasks (PUT returns 403)
     - [ ] Cannot delete other users' tasks (DELETE returns 403)
  - [ ] Verify: Complete data isolation

- [ ] T056 [P] Validate error responses match spec
  - [ ] 401 Unauthorized: Missing or invalid token
  - [ ] 403 Forbidden: User_id mismatch
  - [ ] 404 Not Found: Task doesn't exist or belongs to another user
  - [ ] 422 Unprocessable Entity: Invalid request body
  - [ ] Response format: `{detail: "...", error_code: "..."}`

- [ ] T057 Test session persistence across requests
  - [ ] Log in and obtain token
  - [ ] Make 10 consecutive API calls
  - [ ] Verify: All use same token
  - [ ] Verify: Token in localStorage still valid

- [ ] T058 Test token expiration handling
  - [ ] Manually expire token (modify localStorage or use dev tools)
  - [ ] Make API request with expired token
  - [ ] Verify: 401 response
  - [ ] Verify: Frontend dispatches `auth:unauthorized` event
  - [ ] Verify: User redirected to login

**Checkpoint**: All user stories integrated and working together

---

## Phase 9: Documentation & Hardening

**Purpose**: Complete documentation and security validation

- [ ] T059 [P] Validate quickstart.md matches implementation
  - [ ] Frontend Phase 1-2 sections:
     - [ ] Better Auth JWT setup
     - [ ] API client implementation
     - [ ] Token storage
  - [ ] Backend Phase 3 sections:
     - [ ] JWT verification
     - [ ] Routes implementation
     - [ ] User ownership validation
  - [ ] All code examples executable

- [ ] T060 [P] Update README with setup instructions
  - [ ] Frontend: npm install, env setup, `npm run dev`
  - [ ] Backend: pip install, env setup, `uvicorn` command
  - [ ] Database: PostgreSQL connection, migration steps
  - [ ] Testing: How to run tests for each component

- [ ] T061 Validate API contract matches OpenAPI spec
  - [ ] File: `specs/004-jwt-auth/contracts/api-contract.openapi.json`
  - [ ] Verify all 6 endpoints documented
  - [ ] Verify error responses (401, 403, 404, 422) documented
  - [ ] Verify security scheme (Bearer JWT) defined
  - [ ] Tool: Use Swagger UI or OpenAPI validator

- [ ] T062 [P] Add security headers to FastAPI app
  - [ ] File: `backend/src/main.py`
  - [ ] Add middleware:
     - [ ] `X-Content-Type-Options: nosniff`
     - [ ] `X-Frame-Options: DENY`
     - [ ] `X-XSS-Protection: 1; mode=block`
  - [ ] Validate: Headers present in all responses

- [ ] T063 [P] Configure logging for authentication events
  - [ ] File: `backend/src/auth/jwt.py`
  - [ ] Log:
     - [ ] Token verification attempts (success/failure)
     - [ ] 401 errors with reason
     - [ ] 403 errors with user IDs involved
  - [ ] Exclude: Full token values, passwords
  - [ ] Validate: Logs appear in application output

- [ ] T064 Validate environment configuration management
  - [ ] Frontend: `NEXT_PUBLIC_AUTH_URL`, `NEXT_PUBLIC_API_URL`
  - [ ] Backend: `DATABASE_URL`, `BETTER_AUTH_BASE_URL`
  - [ ] All secrets loaded from `.env` (never in code)
  - [ ] Validate: `git status` shows `.env` in `.gitignore`

**Checkpoint**: Documentation and hardening complete

---

## Phase 10: End-to-End Testing & Validation

**Purpose**: Full system validation against specification

- [ ] T065 Validate SC-001: All endpoints require JWT
  - [ ] Test all 6 endpoints without token
  - [ ] Verify: All return 401 Unauthorized
  - [ ] Reference: Spec SC-001

- [ ] T066 Validate SC-002: User isolation enforced
  - [ ] Cross-user access attempts
  - [ ] Verify: 403 Forbidden for wrong user
  - [ ] Reference: Spec SC-002

- [ ] T067 Validate SC-003: JWT verification < 50ms
  - [ ] Load test with 100 concurrent requests
  - [ ] Measure: Average token verification time
  - [ ] Verify: < 50ms average
  - [ ] Reference: Spec SC-003, plan.md Performance Goals

- [ ] T068 Validate SC-004: 100% of requests include token
  - [ ] Monitor 50 consecutive requests
  - [ ] Verify: All have Authorization header
  - [ ] Reference: Spec SC-004

- [ ] T069 Validate SC-005: Sessions persist across refreshes
  - [ ] Log in, open DevTools, note token in localStorage
  - [ ] Refresh page (F5)
  - [ ] Verify: Token still in localStorage
  - [ ] Verify: Can make API calls without re-login
  - [ ] Reference: Spec SC-005

- [ ] T070 Validate SC-006: Expired tokens handled gracefully
  - [ ] Wait for token expiration (7 days) OR manually expire
  - [ ] Try API request
  - [ ] Verify: 401 Unauthorized
  - [ ] Verify: Redirected to login
  - [ ] Reference: Spec SC-006

- [ ] T071 Validate SC-007: All 6 endpoints work
  - [ ] GET `/api/{user_id}/tasks` ✓
  - [ ] POST `/api/{user_id}/tasks` ✓
  - [ ] GET `/api/{user_id}/tasks/{id}` ✓
  - [ ] PUT `/api/{user_id}/tasks/{id}` ✓
  - [ ] DELETE `/api/{user_id}/tasks/{id}` ✓
  - [ ] PATCH `/api/{user_id}/tasks/{id}/complete` ✓
  - [ ] Reference: Spec SC-007

- [ ] T072 Validate SC-008: Full lifecycle < 30 seconds
  - [ ] Time: Login → Create task → Read task → Update task → Toggle → Delete
  - [ ] Verify: Total time < 30 seconds
  - [ ] Reference: Spec SC-008

- [ ] T073 [P] Run automated integration tests
  - [ ] All endpoints with valid token
  - [ ] All endpoints with invalid token (401)
  - [ ] All endpoints with wrong user (403)
  - [ ] All CRUD operations
  - [ ] Error scenarios
  - [ ] Performance benchmarks

**Checkpoint**: All success criteria (SC) validated

---

## Phase 11: Final Review & Sign-Off

**Purpose**: Ready for production deployment

- [ ] T074 Code review checklist
  - [ ] All tasks complete
  - [ ] No hardcoded secrets or tokens
  - [ ] Error messages user-friendly
  - [ ] Logging covers critical operations
  - [ ] Dependencies up-to-date (no security vulnerabilities)

- [ ] T075 Database validation
  - [ ] All migrations applied
  - [ ] Indices created for performance
  - [ ] Foreign key constraints enforced
  - [ ] Backups configured

- [ ] T076 Documentation sign-off
  - [ ] README updated and tested
  - [ ] API documentation complete
  - [ ] Quickstart guide verified
  - [ ] Environment setup documented

- [ ] T077 Deployment checklist
  - [ ] Frontend build succeeds (`npm run build`)
  - [ ] Backend production dependencies installed
  - [ ] Database migrations run on production DB
  - [ ] Environment variables configured for production
  - [ ] Health checks passing

- [ ] T078 Final validation against specification
  - [ ] All 5 user stories implemented ✓
  - [ ] All 18 functional requirements met ✓
  - [ ] All 8 success criteria validated ✓
  - [ ] All edge cases handled ✓
  - [ ] Constitution compliance verified ✓

**Checkpoint**: READY FOR PRODUCTION

---

## Dependencies & Parallel Execution

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational - BLOCKING)
    ↓
Phases 3-7 (User Stories - CAN RUN IN PARALLEL)
    ↓
Phases 8-11 (Integration, Testing, Deploy)
```

### User Story Parallelization

Once Phase 2 (Foundational) completes:
- Developer A: Phase 3 (US1 - Login & JWT)
- Developer B: Phase 4 (US2 - Token Attachment)
- Developer C: Phase 5 (US3 - Backend Verification)
- Developer D: Phase 6 (US4 - User Isolation)
- Developer E: Phase 7 (US5 - Full CRUD)

All stories are **independently testable** and can be deployed incrementally.

### Within-Phase Parallelization

Tasks marked with [P] can run in parallel:
- Setup phase: T001, T002, T003, T005, T006 can run together
- Foundational: T007-T009, T012-T018 can run together
- Each user story: Models and tests can run in parallel

---

## Task Status Tracking

Use this template for git commit messages:

```
[T-XXX] Brief description

Relates to: User Story N (US-N)
Validates: Requirement FR-XXX or SC-XXX
Ref: Spec section or docs reference
```

Example:
```
[T-045] Implement POST /api/{user_id}/tasks (create task)

Relates to: User Story 5 (US5)
Validates: FR-012, SC-007
Ref: quickstart.md Backend Phase 3, OpenAPI endpoint spec
```

---

## Final Notes

- **Total Tasks**: 78 tasks across all phases
- **Setup Phase**: 6 tasks (can start immediately)
- **Foundational Phase**: 12 tasks (MUST complete before user stories)
- **User Story Phases**: 60 tasks (5 stories × 12 tasks average)
- **Integration & Testing**: 27 tasks (validation against specification)
- **Deployment**: 4 tasks (final sign-off)

- **Estimated Timeline**:
  - Sequential: 4-5 weeks (one developer)
  - Parallel: 2 weeks (5 developers after foundational)

- **MVP Scope**: Complete Phases 1-3 (Setup + Foundational + US1)
  - Result: Users can log in and receive JWT tokens
  - Time: ~3-4 days for experienced developer
  - Validate: Run tests in T023-T025

- **All tasks validated against**:
  - Specification (spec.md)
  - Implementation Plan (plan.md)
  - Research Decisions (research.md)
  - Data Model (data-model.md)
  - API Contract (contracts/api-contract.openapi.json)
  - Quickstart Guide (quickstart.md)
  - Better Auth Documentation
  - FastAPI Documentation
  - Project Constitution
