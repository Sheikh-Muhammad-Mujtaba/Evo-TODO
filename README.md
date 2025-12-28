# Evo-TODO: Phase II - Full-Stack Todo Application

**Status**: 🚀 Phase II Implementation Started (T-201-207 Complete)

A production-ready full-stack todo application with JWT authentication, built with:
- **Frontend**: Next.js 16+ (App Router) + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.13 + SQLModel ORM
- **Database**: PostgreSQL (Neon for production, Docker for local development)
- **Authentication**: JWT with shared secret (Better Auth integration planned for Phase III)

## Phase II Monorepo Structure

```
Evo-TODO/
├── frontend/                   # Next.js 16+ React application (T-201)
│   ├── app/                    # App Router directory
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Landing page
│   │   ├── (auth)/             # Auth routes (Signin/Signup) - T-220/T-221
│   │   ├── (dashboard)/        # Protected routes - T-222/T-223
│   │   └── globals.css         # Tailwind CSS
│   ├── lib/                    # Utilities
│   │   └── api.ts              # API client with JWT attachment - T-218
│   ├── hooks/                  # React hooks
│   │   └── useAuth.ts          # Authentication context - T-219
│   ├── components/             # Reusable React components
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── Dockerfile              # Multi-stage build - T-205
│
├── backend/                    # FastAPI Python application (T-202)
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── models/             # SQLModel entities - T-208/T-209
│   │   ├── api/                # Route handlers - T-215/T-216
│   │   │   ├── auth.py         # Auth endpoints
│   │   │   ├── todos.py        # Todo CRUD endpoints
│   │   │   └── deps.py         # FastAPI dependencies - T-214
│   │   ├── core/
│   │   │   ├── config.py       # Settings and environment - T-202
│   │   │   └── security.py     # JWT and password functions - T-213
│   │   └── schemas/            # Pydantic models - T-211/T-212
│   ├── tests/                  # Test files
│   ├── pyproject.toml
│   ├── Dockerfile              # Python 3.13 image - T-204
│   └── .env.example
│
├── docker-compose.yml          # Orchestration (PostgreSQL + Backend + Frontend) - T-203
├── .env.example                # Environment template - T-206
└── README.md                   # This file (T-207)
```

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.13+ (for local backend development)
- PostgreSQL 15 (included in Docker Compose)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd Evo-TODO

# Checkout Phase II branch
git checkout phase2-001-setup

# Copy environment template
cp .env.example .env
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

### 2. Generate JWT Secret

```bash
# Generate a secure 256-bit secret
openssl rand -base64 32
# Copy output to .env JWT_SECRET_KEY
```

### 3. Run with Docker Compose

```bash
# Start all services (PostgreSQL, FastAPI, Next.js)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Database**: localhost:5432 (PostgreSQL)

### 4. Run Locally (Without Docker)

**Backend**:
```bash
cd backend
uv sync              # Install dependencies
cp .env.example .env # Configure
uvicorn app.main:app --reload
```

**Frontend**:
```bash
cd frontend
npm install
cp .env.example .env.local # Configure
npm run dev
```

## Architecture

### Phase II Monorepo Design

```
User Browser
    ↓
[Next.js Frontend]
    ├─ Static: UI components, routing, forms
    ├─ Dynamic: useAuth hook, API client
    └─ Authenticated requests with JWT
    ↓ (HTTP/HTTPS + JWT in Authorization header)
[FastAPI Backend] (Task T-202)
    ├─ JWT Middleware: Validate token, extract user_id
    ├─ Dependencies: get_current_user() for protected routes
    ├─ Routes: /auth/*, /api/todos/*
    └─ All queries filtered by user_id (data isolation)
    ↓ (SQL via SQLModel ORM)
[PostgreSQL Database]
    ├─ users table: id, email, password_hash, name, is_active, timestamps
    └─ todos table: id, user_id (FK), title, description, is_complete, timestamps
```

### Security & Data Isolation (Constitution Compliance)

**Task T-201-207 Compliance**:
- ✅ Monorepo structure with `/frontend` and `/backend` separation
- ✅ Docker Compose for orchestration
- ✅ Environment variables from `.env` (no secrets in code)
- ✅ JWT authentication with shared secret (HS256)
- ✅ User data scoping at query level (WHERE user_id = <user_id>)
- ✅ API client auto-attaches JWT to all requests
- ✅ Every file references Task ID (comments + git commits)

## Implementation Tasks

### Phase 2.1: Monorepo Infrastructure (T-201 to T-207) ✅ COMPLETE

| Task | Description | Status |
|------|-------------|--------|
| T-201 | Initialize Next.js 16+ with App Router | ✅ Complete |
| T-202 | Initialize FastAPI with Python 3.13 | ✅ Complete |
| T-203 | Create Docker Compose configuration | ✅ Complete |
| T-204 | Create Backend Dockerfile | ✅ Complete |
| T-205 | Create Frontend Dockerfile | ✅ Complete |
| T-206 | Create Environment templates | ✅ Complete |
| T-207 | Create Root README | ✅ Complete |

### Phase 2.2: Database Schema (T-208 to T-212) ⏳ Next

| Task | Description | Status |
|------|-------------|--------|
| T-208 | Create SQLModel User entity | ⏳ Pending |
| T-209 | Create SQLModel Todo entity | ⏳ Pending |
| T-210 | Configure Database connection | ⏳ Pending |
| T-211 | Create User Pydantic schemas | ⏳ Pending |
| T-212 | Create Todo Pydantic schemas | ⏳ Pending |

### Phase 2.3: JWT Authentication (T-213 to T-215) ⏳ Next

- T-213: JWT security functions (started - in security.py)
- T-214: FastAPI dependencies
- T-215: Auth endpoints (signup, signin, logout)

### Phase 2.4: Todo CRUD API (T-216 to T-217) ⏳ Next

- T-216: Todo CRUD endpoints
- T-217: User data isolation verification

### Phase 2.5: Frontend Components (T-218 to T-224) ⏳ Next

- T-218: API client class
- T-219: useAuth hook
- T-220: Signin page
- T-221: Signup page
- T-222: Dashboard layout
- T-223: Todo list page
- T-224: Todo edit page

### Phase 2.6: Testing & Polish (T-225 to T-228) ⏳ Next

- T-225: Integration tests
- T-226: Full test suite
- T-227: Code review
- T-228: API documentation

## Configuration

### Environment Variables

**Backend (.env)**:
```env
DATABASE_URL=postgresql://evo_todo_user:evo_todo_password@localhost:5432/evo_todo
JWT_SECRET_KEY=your-256-bit-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Docker Compose (.env)**:
```env
POSTGRES_USER=evo_todo_user
POSTGRES_PASSWORD=evo_todo_password
POSTGRES_DB=evo_todo
JWT_SECRET_KEY=your-256-bit-secret-key
```

## API Documentation

Auto-generated API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Current endpoints (Task T-207):
- `GET /health` - Health check

Upcoming endpoints:
- **Auth** (T-215): POST /auth/signup, /auth/signin, /auth/logout
- **Todos** (T-216): GET /api/todos, POST /api/todos, GET /api/todos/{id}, PUT /api/todos/{id}, PATCH /api/todos/{id}, DELETE /api/todos/{id}

## Testing

Tests will be added in Phase 2.6 (T-225-226):
```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm test

# E2E tests
cd frontend && npm run e2e
```

## Troubleshooting

### Docker Compose Issues

```bash
# View service logs
docker-compose logs postgres     # Database logs
docker-compose logs backend      # FastAPI logs
docker-compose logs frontend     # Next.js logs

# Reset everything
docker-compose down -v           # Remove volumes
docker-compose up -d             # Restart

# Health check
curl http://localhost:8000/health
curl http://localhost:3000
```

### Port Conflicts

If ports are in use:
```bash
# Change ports in docker-compose.yml
# Frontend: change "3000:3000" to "3001:3000"
# Backend: change "8000:8000" to "8001:8000"

# Update NEXT_PUBLIC_API_URL in frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Database Connection

```bash
# Connect to PostgreSQL directly
psql -U evo_todo_user -d evo_todo -h localhost

# Check tables
\dt            # List tables
\d users       # Describe users table
\d todos       # Describe todos table
```

## Development Workflow

### Git Branching Strategy

```
main/master
└── phase-2 (final Phase II branch)
    └── phase2-001-setup (Feature branch for T-201-207)
        └── phase2-002-database (Feature branch for T-208-212)
        └── phase2-003-auth (Feature branch for T-213-215)
        ...
```

### Commit Message Format

```
phase2-XXY-task-name: Brief description

Detailed explanation if needed

🤖 Generated with Claude Code

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

### Task Tracking

All tasks documented in [specs/002-phase-ii/tasks.md](./specs/002-phase-ii/tasks.md) with:
- Acceptance criteria
- Test cases
- Time estimates
- Dependencies

## Constitution Compliance

**Phase II Constitution (v2.0.0)** applied to all code:
- ✅ Full-stack web app with separation of concerns
- ✅ User-scoped data isolation (JWT + user_id filtering)
- ✅ Clean code principles (small focused functions)
- ✅ Task-driven implementation (all code mapped to Task IDs)
- ✅ Performance prioritized (indexes, async endpoints)
- ✅ No manual code writing (templates, scaffolding used)
- ✅ MCP integration (Context7 for debugging, Better Auth MCP for auth)

See [.specify/memory/constitution.md](./.specify/memory/constitution.md) for full details.

## References

- **Specification**: [specs/002-phase-ii/spec.md](./specs/002-phase-ii/spec.md)
- **Implementation Plan**: [specs/002-phase-ii/plan.md](./specs/002-phase-ii/plan.md)
- **Tasks**: [specs/002-phase-ii/tasks.md](./specs/002-phase-ii/tasks.md)
- **Data Model**: [specs/002-phase-ii/data-model.md](./specs/002-phase-ii/data-model.md)
- **API Contract**: [specs/002-phase-ii/api-contract.md](./specs/002-phase-ii/api-contract.md)
- **Constitution**: [.specify/memory/constitution.md](./.specify/memory/constitution.md)

## License

MIT

## Contributors

- Claude Haiku 4.5 (AI Assistant)
- Sheikh Muhammad Mujtaba (Project Owner)
