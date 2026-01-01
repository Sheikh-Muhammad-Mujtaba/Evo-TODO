# Implementation Plan: JWT Authentication Integration

**Branch**: `004-jwt-auth` | **Date**: 2026-01-01 | **Phase**: 2.2
**Specification**: [`/specs/004-jwt-auth/spec.md`](/specs/004-jwt-auth/spec.md)
**Input**: Feature specification with 5 P1 user stories covering JWT token issuance, frontend attachment, backend verification, and user isolation

## Summary

Implement JWT-based authentication across a decoupled Next.js frontend and FastAPI backend using Better Auth's JWT plugin. The solution enables secure, stateless API authentication with user-scoped data access through asymmetrically-signed tokens verified via JWKS endpoints. This ensures no shared secrets between frontend and backend while maintaining compatibility with the Evo-TODO task management system.

**Key outcomes**:
- Better Auth JWT plugin configured for EdDSA token issuance
- Frontend API client with automatic token attachment and expiration handling
- FastAPI middleware for JWT verification via JWKS
- All 6 task API endpoints protected with user ownership validation
- End-to-end user isolation: users can only access/modify their own tasks

## Technical Context

**Frontend Language/Version**: TypeScript/Next.js 16+ (App Router)
**Backend Language/Version**: Python 3.10+ with FastAPI 0.100+
**Primary Frontend Dependencies**:
- `better-auth` with JWT and jwtClient plugins
- `jose` for token utilities
- Native fetch API for requests

**Primary Backend Dependencies**:
- `fastapi` for API framework
- `python-jose[cryptography]` for JWT verification
- `httpx` for async JWKS fetching
- `pydantic` for validation
- `SQLModel` for ORM (existing)

**Storage**: PostgreSQL (Neon Serverless) - managed by SQLModel
- Better Auth manages: `user`, `session`, `account`, `jwks` tables
- Application manages: `task` table with `user_id` foreign key

**Testing**:
- Frontend: Jest, React Testing Library
- Backend: pytest with async support
- Integration: Postman/curl or Python requests library

**Target Platform**: Web (SaaS) - Linux servers for both frontend and backend

**Project Type**: Web application with separate frontend (Next.js) and backend (FastAPI)

**Performance Goals**:
- JWT verification: < 50ms average (from spec SC-003)
- Full task lifecycle (login → CRUD → logout): < 30s (from spec SC-008)
- API response time: < 200ms for all endpoints

**Constraints**:
- User isolation enforced at API boundary - no endpoint returns unfiltered data
- Token expiration: 7 days (non-negotiable per spec)
- All requests require valid JWT token
- Cross-origin requests must come from trusted origins

**Scale/Scope**:
- Initial: Single-tenant task management
- Target: 10,000+ concurrent users
- 6 API endpoints to implement
- ~2000 LOC total (frontend + backend combined)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Gate 1: Full-Stack Web Application with Separation of Concerns** ✅ PASS
- Frontend: Next.js 16+ (App Router) with better-auth
- Backend: FastAPI async Python
- Database: PostgreSQL via SQLModel ORM
- All layers properly separated and decoupled

**Gate 2: User-Scoped Data & JWT Authentication (Mandatory)** ✅ PASS
- All API endpoints require JWT token in Authorization header
- Every response filtered by user_id derived from JWT token
- No endpoint returns unfiltered data
- Token validation at API boundary via middleware/dependencies

**Gate 3: Clean Code Principles** ✅ PASS
- Small, focused functions (verify_token, get_user_task, etc.)
- Clear naming conventions throughout
- Single responsibility: authentication vs. authorization vs. business logic
- Dependency injection pattern for testability
- No complex nesting or coupling

**Gate 4: Task-Driven Implementation** ✅ PASS
- All code will map to Task IDs in tasks.md (next phase)
- Every PR will reference task ID
- Implementation fully traceable

**Gate 5: Performance Over Brevity** ✅ PASS
- JWT verification via JWKS caching (not refetching every time)
- Indexed database queries for user_id filtering
- Async/await for non-blocking I/O
- Performance targets documented in Technical Context

**Gate 6: No Manual Code Writing** ✅ PASS
- This plan serves as template for implementation
- Quickstart.md provides scaffolded code patterns
- OpenAPI contract auto-generated from requirements

**Gate 7: MCP Integration for Documentation (Mandatory)** ✅ PASS
- Better Auth MCP: Used for JWT plugin research and configuration
- Context7 MCP: Used for FastAPI JWT verification patterns
- All decisions documented with MCP source references

**Result**: ✅ **ALL GATES PASSED** - Plan complies with constitution

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Selected**: Web application with separate frontend and backend

#### Frontend (Next.js)

```text
frontend/
├── src/
│   ├── lib/
│   │   ├── auth-client.ts           # Better Auth client with JWT plugin
│   │   └── api-client.ts            # API client with token attachment
│   ├── components/
│   │   ├── login-form.tsx           # Sign in form, stores JWT
│   │   ├── task-list.tsx            # List tasks for authenticated user
│   │   ├── task-create.tsx          # Create new task
│   │   └── task-item.tsx            # Edit/delete individual task
│   ├── hooks/
│   │   ├── use-auth.ts              # useAuth hook from better-auth
│   │   └── use-auth-error.ts        # Token expiration handler
│   ├── app/
│   │   ├── login/page.tsx           # Login route
│   │   ├── dashboard/page.tsx       # Protected task dashboard
│   │   └── layout.tsx               # Root layout with auth context
│   └── env.ts                       # Type-safe environment variables
├── tests/
│   ├── api-client.test.ts           # Test token attachment
│   ├── components/
│   │   ├── login-form.test.tsx
│   │   └── task-list.test.tsx
│   └── integration/
│       └── e2e.test.ts              # End-to-end: login → create → delete
├── .env.local                       # Local development env vars
└── package.json                     # Dependencies: better-auth, jose, etc.
```

#### Backend (FastAPI)

```text
backend/
├── src/
│   ├── auth/
│   │   └── jwt.py                  # JWT verification & JWKS fetching
│   ├── models/
│   │   └── task.py                 # Task Pydantic models
│   ├── routes/
│   │   └── tasks.py                # All 6 task endpoints (GET/POST/PUT/DELETE/PATCH)
│   ├── database.py                 # SQLModel session & async setup
│   ├── config.py                   # Configuration (JWT URLs, etc.)
│   └── main.py                     # FastAPI app setup, CORS, route registration
├── tests/
│   ├── test_jwt.py                 # Test token verification
│   ├── test_tasks.py               # Test all 6 endpoints
│   ├── test_user_isolation.py      # Test cross-user access rejected
│   └── fixtures/
│       └── conftest.py             # Test fixtures: db, auth, client
├── .env                            # Env vars: DATABASE_URL, JWT config
├── requirements.txt                # Dependencies: fastapi, python-jose, etc.
└── alembic/                        # Database migrations (existing)
```

**Structure Decision**:
- Separate frontend (Next.js) and backend (FastAPI) directories
- Clear separation of concerns: auth (better-auth) vs. api (fastapi)
- Each layer independently testable
- Routes/endpoints organized by domain (tasks)
- Database management via SQLModel + Alembic migrations
- Configuration externalized via environment variables

## Complexity Tracking

✅ **No constitution violations** - All gates passed. No justifications needed.

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
1. Better Auth JWT plugin configuration and migration
2. Database schema validation (jwks table created)
3. Frontend API client with token attachment logic
4. Token storage and retrieval in localStorage

### Phase 2: Frontend Integration (Week 2)
1. Login form with JWT token storage
2. Auth context/hook for session management
3. Token expiration detection and re-authentication prompts
4. Protected routes (redirect to login if no token)

### Phase 3: Backend Implementation (Week 2-3)
1. JWT verification middleware setup
2. JWKS fetching and caching logic
3. User ownership validation dependency
4. All 6 task endpoint implementations with user filtering

### Phase 4: Testing & Integration (Week 3)
1. Unit tests for token verification
2. API endpoint tests with valid/invalid tokens
3. Cross-user isolation tests (403 Forbidden)
4. End-to-end integration tests (login → CRUD → logout)

### Phase 5: Hardening & Deployment (Week 4)
1. Error handling and edge cases
2. Performance optimization (JWKS caching)
3. Security audit and penetration testing
4. Production deployment and monitoring

---

## Success Metrics

| Metric | Target | How to Verify |
|--------|--------|---------------|
| All endpoints require JWT | 100% | Each endpoint returns 401 without token |
| User isolation enforced | 100% | Cross-user requests return 403 Forbidden |
| Token verification latency | < 50ms | Load test with 1000 concurrent requests |
| API response time | < 200ms | Benchmark all 6 endpoints |
| Session persistence | 100% | Token survives browser refresh |
| Token expiration handling | 100% | Expired tokens prompt re-auth |
| Code coverage | > 80% | pytest/jest coverage reports |

---

## Artifacts Delivered

| Artifact | Status | Purpose |
|----------|--------|---------|
| `spec.md` | ✅ Complete | Feature requirements and acceptance criteria |
| `research.md` | ✅ Complete | Technical decisions and rationales |
| `data-model.md` | ✅ Complete | Entity definitions and database schema |
| `api-contract.openapi.json` | ✅ Complete | API endpoint specifications |
| `quickstart.md` | ✅ Complete | Step-by-step implementation guide |
| `plan.md` (this file) | ✅ Complete | Architecture and roadmap |
| `tasks.md` | ⏳ Next Phase | Task list for implementation (`/sp.tasks`) |

---

## References

- **Specification**: `/specs/004-jwt-auth/spec.md`
- **Better Auth JWT Docs**: https://better-auth.com/docs/plugins/jwt
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **Constitution**: `.specify/memory/constitution.md`
- **OpenAPI Contract**: `/specs/004-jwt-auth/contracts/api-contract.openapi.json`
