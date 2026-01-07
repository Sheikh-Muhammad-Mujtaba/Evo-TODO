# Evo-TODO Project Summary

## Project Overview

**Evo-TODO** is a full-stack task management application built with modern web technologies, featuring JWT-based authentication via Better Auth and a clean, responsive UI. The project follows Spec-Driven Development (SDD) principles with comprehensive documentation and architectural decision records.

## Tech Stack Summary

### Frontend
- **Framework**: Next.js 16+ (App Router, Server Components)
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS 3.4+ with Shadcn UI components
- **Authentication**: Better Auth 1.4+ (JWT + JWKS)
- **State**: React Hooks + Custom Hooks
- **Theme**: next-themes 0.4+ (dark/light mode)
- **Forms**: React Hook Form 7.50+
- **Icons**: Lucide React 0.562+
- **Notifications**: Sonner 2.0+

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: PostgreSQL (Neon Serverless supported)
- **Authentication**: Better Auth JWT (EdDSA/JWKS)
- **Driver**: psycopg3

### Development Tools
- **Package Managers**: npm (frontend), uv (backend)
- **Testing**: Jest 30+ (frontend), pytest (backend planned)
- **Containerization**: Docker + Docker Compose
- **Version Control**: Git

## Complete Project Structure

```
Evo-TODO/
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py              # DEPRECATED - Better Auth handles auth
│   │   │   ├── deps.py              # JWT validation dependencies
│   │   │   ├── todos.py             # Todo CRUD endpoints
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── auth.py              # JWT verification logic
│   │   │   ├── config.py            # Configuration settings
│   │   │   ├── jwks_client.py       # JWKS client for JWT verification
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── database.py          # Database connection & session
│   │   │   ├── todo.py              # Todo SQLModel
│   │   │   ├── user.py              # User SQLModel (maps to Better Auth)
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── todo.py              # Todo Pydantic schemas
│   │   │   ├── user.py              # User Pydantic schemas
│   │   │   └── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   └── __init__.py
│   ├── tests/                       # Test files
│   │   ├── integration/
│   │   └── unit/
│   ├── .env                         # Environment variables
│   ├── .env.example                 # Example configuration
│   ├── Dockerfile                   # Docker configuration
│   ├── pyproject.toml               # Python dependencies
│   ├── migrate_db.py                # Database migration script
│   ├── README.md                    # Backend documentation
│   └── uv.lock                      # Dependency lock file
│
├── frontend/                         # Next.js Frontend
│   ├── app/
│   │   ├── (auth)/                  # Authentication route group
│   │   │   ├── layout.tsx
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── dashboard/               # Dashboard route group (protected)
│   │   │   ├── layout.tsx           # Dashboard layout with sidebar/navbar
│   │   │   ├── page.tsx            # Dashboard home (placeholder)
│   │   │   └── todos/
│   │   │       └── page.tsx         # Main tasks page
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts     # Better Auth server handler
│   │   ├── layout.tsx               # Root layout with providers
│   │   ├── page.tsx                 # Landing page
│   │   ├── globals.css              # Global styles
│   │   └── favicon.ico
│   ├── components/
│   │   ├── auth/                    # Authentication components
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── common/                  # Common UI components
│   │   │   ├── EmptyState.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── dashboard/               # Dashboard-specific components
│   │   │   ├── DashboardUI.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── landing/                 # Landing page components
│   │   │   ├── CallToActionSection.tsx
│   │   │   ├── FeatureHighlights.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── LandingNavBar.tsx
│   │   │   └── SocialProof.tsx
│   │   ├── todos/                   # Task management components
│   │   │   ├── BulkActions.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskList.tsx
│   │   │   └── TasksContainer.tsx
│   │   └── ui/                      # Shadcn UI base components
│   │       ├── alert.tsx
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       └── label.tsx
│   ├── lib/
│   │   ├── api.ts                   # API client with JWT injection
│   │   ├── auth-client.ts           # Better Auth client configuration
│   │   ├── auth.ts                  # Auth utilities
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useBulkSelection.ts
│   │   │   ├── useTheme.ts
│   │   │   └── useTodos.ts          # Main todo state management
│   │   ├── types/                   # TypeScript types
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── todo.ts
│   │   └── utils.ts                 # Utility functions
│   ├── docs/                        # Documentation
│   │   ├── API_CONTRACT.md
│   │   ├── BACKEND_API_CORRECTION.md
│   │   ├── FRONTEND_TASKS_ALIGNED.md
│   │   ├── JWT_ATTACHMENT.md
│   │   ├── JWT_STRUCTURE.md
│   │   └── PHASE_0_VALIDATION_REPORT.md
│   ├── middleware.ts                # Route protection middleware
│   ├── next.config.js               # Next.js configuration
│   ├── tailwind.config.ts           # Tailwind CSS configuration
│   ├── tsconfig.json                # TypeScript configuration
│   ├── jest.config.js               # Jest configuration
│   ├── package.json                 # Dependencies
│   ├── Dockerfile                   # Docker configuration
│   └── README.md                    # Frontend documentation
│
├── specs/                           # Feature specifications (SDD)
│   ├── 001-cli-todo/               # Phase 1: CLI Todo App
│   │   ├── checklists/
│   │   ├── contracts/
│   │   ├── data-model.md
│   │   ├── plan.md
│   │   ├── quickstart.md
│   │   ├── spec.md
│   │   └── tasks.md
│   ├── 002-phase-ii/               # Phase 2: Web API + Auth
│   │   ├── acceptance-criteria.md
│   │   ├── api-contract.md
│   │   ├── better-auth-jwks-implementation.md
│   │   ├── data-model.md
│   │   ├── IMPLEMENTATION-STATUS.md
│   │   ├── INDEX.md
│   │   ├── plan.md
│   │   ├── spec.md
│   │   └── tasks.md
│   ├── 003-phase2-frontend-ui/     # Phase 2: Frontend UI
│   │   ├── checklists/
│   │   ├── plan.md
│   │   ├── research.md
│   │   ├── spec.md
│   │   └── tasks.md
│   ├── 004-jwt-auth/               # JWT Authentication
│   │   ├── checklists/
│   │   ├── contracts/
│   │   ├── data-model.md
│   │   ├── plan.md
│   │   ├── spec.md
│   │   └── tasks.md
│   ├── 005-professional-ui/        # Professional UI Enhancements
│   │   ├── checklists/
│   │   ├── contracts/
│   │   ├── plan.md
│   │   ├── spec.md
│   │   └── tasks.md
│   ├── 006-cleanup-finalize/       # Cleanup & Finalization
│   │   ├── architecture.md
│   │   ├── checklists/
│   │   ├── IMPLEMENTATION-KICKOFF.md
│   │   ├── PHASE-2-AUDIT-FINDINGS.md
│   │   ├── PHASE-3-INTEGRATION-TESTS.md
│   │   ├── plan.md
│   │   ├── spec.md
│   │   └── tasks.md
│   └── phase2-deployment/
│       └── plan.md
│
├── history/                         # Development history
│   └── prompts/                    # Prompt History Records (PHRs)
│       ├── 001-cli-todo/
│       ├── 002-phase-ii/
│       ├── 003-phase2-frontend-ui/
│       ├── 004-jwt-auth/
│       ├── 005-professional-ui/
│       ├── 006-cleanup-finalize/
│       ├── constitution/
│       ├── frontend-enhancements/
│       ├── frontend-fixes/
│       ├── general/
│       └── routing-fixes/
│
├── src/                            # Phase 1 CLI Source (deprecated)
│   └── todo_app/
│       ├── main.py
│       ├── models/
│       ├── services/
│       └── ui/
│
├── tests/                          # Phase 1 Tests (deprecated)
│   ├── contract/
│   ├── integration/
│   └── unit/
│
├── CLAUDE.md                       # Claude Code Rules (SDD)
├── GEMINI.md                       # Gemini CLI Rules (SDD)
├── README.md                       # Project README
├── docker-compose.yml              # Docker Compose configuration
├── package.json                    # Root package.json
└── pyproject.toml                  # Root Python dependencies
```

## Architecture Overview

### Authentication Flow

1. **User Registration/Login**:
   - Frontend: User enters credentials via `LoginForm` or `SignupForm`
   - Better Auth client calls `/api/auth/sign-in` or `/api/auth/sign-up`
   - Better Auth server generates JWT token (EdDSA/Ed25519)
   - Token stored in cookie + client state

2. **API Request Flow**:
   - Frontend injects JWT in `Authorization: Bearer <token>` header
   - Backend validates JWT via JWKS endpoint
   - Backend verifies claims (issuer, audience, expiration)
   - Backend extracts user from `sub` claim
   - Backend verifies user exists in database

3. **Route Protection**:
   - Middleware checks for session cookie
   - Dashboard layout validates actual session
   - Unauthenticated users redirected to `/login`

### Database Schema

#### User Table (Better Auth managed)
```sql
CREATE TABLE "user" (
  id VARCHAR PRIMARY KEY,           -- UUID string
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  emailVerified BOOLEAN,
  image VARCHAR,
  createdAt TIMESTAMP,
  updatedAt TIMESTAMP
);
```

#### Todo Table
```sql
CREATE TABLE todos (
  id UUID PRIMARY KEY,
  user_id VARCHAR REFERENCES "user"(id),
  title VARCHAR(500) NOT NULL,
  description VARCHAR(2000),
  is_complete BOOLEAN DEFAULT FALSE,
  priority VARCHAR DEFAULT 'medium',
  due_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_todos_user_created ON todos(user_id, created_at);
CREATE INDEX idx_todos_user ON todos(user_id);
```

### API Endpoints

#### Health Check
- **GET** `/health` - Health status

#### Todo CRUD
- **GET** `/api/todos` - List all user todos (with pagination)
- **GET** `/api/todos/{id}` - Get specific todo
- **POST** `/api/todos` - Create new todo
- **PUT** `/api/todos/{id}` - Update todo fields
- **PATCH** `/api/todos/{id}` - Toggle completion status
- **DELETE** `/api/todos/{id}` - Delete todo

### Frontend Routes

#### Public Routes
- `/` - Landing page
- `/login` - Login page
- `/signup` - Signup page

#### Protected Routes
- `/dashboard` - Dashboard home (placeholder)
- `/dashboard/todos` - Main tasks page (default)

## Configuration

### Frontend Environment Variables (.env)
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth URL
NEXT_PUBLIC_AUTH_URL=http://localhost:3000

# Node environment
NODE_ENV=development
```

### Backend Environment Variables (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/evo_todo

# Better Auth Configuration
BETTER_AUTH_URL=http://localhost:3000

# JWKS Cache Configuration
JWKS_CACHE_LIFESPAN=300        # 5 minutes
JWKS_CACHE_MAX_KEYS=16

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=True
```

## Key Features

### Frontend Features
- ✅ User authentication (signup, login, logout)
- ✅ JWT token management (automatic injection)
- ✅ Todo CRUD operations (create, read, update, delete)
- ✅ Task filtering (all, pending, completed)
- ✅ Task sorting (title, priority, dueDate, createdAt)
- ✅ Bulk selection and deletion
- ✅ Dark/light theme toggle (system preference support)
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Empty state handling
- ✅ Loading states and error handling
- ✅ Toast notifications (success, error)

### Backend Features
- ✅ JWT authentication (EdDSA/Ed25519)
- ✅ JWKS-based token verification
- ✅ User data isolation (all queries filtered by user_id)
- ✅ Todo CRUD with ownership validation
- ✅ Pagination support
- ✅ Input validation (Pydantic schemas)
- ✅ Database connection pooling (Neon optimized)
- ✅ CORS configuration
- ✅ Auto-documentation (Swagger UI, ReDoc)
- ✅ Health check endpoint

## Development Workflow (SDD)

### Spec-Driven Development Process

1. **Clarify** (`/sp.specify`): Create feature specification
2. **Plan** (`/sp.plan`): Generate architectural plan
3. **Tasks** (`/sp.tasks`): Break down into actionable tasks
4. **Implement** (`/sp.implement`): Execute tasks in TDD workflow
5. **Document** (`/sp.phr`): Create Prompt History Records
6. **ADR** (`/sp.adr`): Document architectural decisions

### PHR (Prompt History Record) Creation

**When to create PHRs**:
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Routing**:
- Constitution → `history/prompts/constitution/`
- Feature-specific → `history/prompts/<feature-name>/`
- General → `history/prompts/general/`

## Running the Application

### Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Development

#### Backend
```bash
cd backend
uv sync                    # Install dependencies
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install                # Install dependencies
npm run dev               # Start development server
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Data Transformation

### Backend (snake_case) → Frontend (camelCase)

**Backend Format**:
```json
{
  "id": "...",
  "user_id": "...",
  "title": "...",
  "description": "...",
  "is_complete": false,
  "priority": "medium",
  "due_date": "...",
  "created_at": "...",
  "updated_at": "..."
}
```

**Frontend Format**:
```typescript
{
  id: "...",
  userId: "...",
  title: "...",
  description: "...",
  status: "pending" | "completed",  // is_complete → status
  priority: "low" | "medium" | "high",
  dueDate: "...",                   // due_date → dueDate
  createdAt: "...",                 // created_at → createdAt
  updatedAt: "..."                  // updated_at → updatedAt
}
```

## Security Features

1. **JWT Authentication**: EdDSA/Ed25519 asymmetric verification
2. **User Isolation**: All queries filtered by `user_id`
3. **Claim Validation**: Issuer, audience, expiration
4. **Ownership Verification**: 403 for non-owned resources
5. **Input Validation**: Pydantic schemas with strict limits
6. **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
7. **CORS Protection**: Configured allowed origins
8. **Session Validation**: Middleware + layout checks

## Testing Strategy

### Frontend (Jest 30+)
- Component tests (planned)
- Hook tests (planned)
- Integration tests (planned)

### Backend (pytest)
- Unit tests (planned)
- Integration tests (planned)
- Contract tests (planned)

## Known Issues & Improvements

### Current Issues
1. **Dashboard Root Redirect**: `/dashboard` redirects to `/dashboard/todos` immediately
2. **Unused Dashboard Page**: Placeholder content at `/dashboard/page.tsx`
3. **Route Confusion**: Multiple paths lead to tasks page
4. **Missing Tests**: Test suites need to be implemented
5. **Console Logs**: Extensive debugging logs should be removed for production

### Planned Improvements
- Complete test coverage
- Remove debugging console.log statements
- Consolidate routing structure
- Add email verification flow
- Implement password reset
- Add task priority and due date features
- Implement task search functionality
- Add task categories/tags

## AI Agent Guidelines (from CLAUDE.md & GEMINI.md)

### Core Guarantees
- Record every user input in a PHR after every user message
- Create ADR suggestions for architecturally significant decisions
- All changes must be small, testable, and reference code precisely
- Never auto-create ADRs without user consent

### Development Guidelines
1. **Authoritative Source Mandate**: Use MCP tools and CLI commands for all information gathering
2. **Execution Flow**: Prefer CLI interactions over manual file creation
3. **Knowledge Capture**: Create PHRs for all implementation work
4. **Explicit ADR Suggestions**: Suggest ADR creation for significant decisions
5. **Human as Tool Strategy**: Invoke user for clarification and decision-making

### Default Policies
- Clarify and plan first
- Never hardcode secrets or tokens
- Prefer smallest viable diff
- Cite existing code with references
- Keep reasoning private

## Project Status

**Current Phase**: Phase 2 Complete (Web App with Authentication)
**Branch**: `main` (merged from `phase-2`)
**Main Development Branch**: `001-cli-todo`

**Completed Phases**:
- ✅ Phase 1: CLI Todo Application
- ✅ Phase 2: Web API + Better Auth Integration
- ✅ Phase 2: Frontend UI with Next.js

**Next Steps**:
- Implement comprehensive testing
- Production deployment configuration
- Performance optimization
- Feature enhancements (search, categories, etc.)

## Contact & Documentation

- **Project README**: `/README.md`
- **Frontend Docs**: `/frontend/README.md`
- **Backend Docs**: `/backend/README.md`
- **Feature Specs**: `/specs/`
- **History**: `/history/prompts/`

---

**Generated**: 2026-01-07
**Project**: Evo-TODO
**Version**: Phase 2 (Web App)
