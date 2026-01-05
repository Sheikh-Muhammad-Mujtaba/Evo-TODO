# Evo-TODO Application Structure & Overview

**Date**: 2026-01-04
**Status**: Phase II Implementation
**Branch**: `006-cleanup-finalize`

---

## Complete Application Structure

```
Evo-TODO/
│
├── 📁 frontend/                       # Next.js 16+ React Application
│   │
│   ├── 📁 app/                        # App Router Directory Structure
│   │   ├── layout.tsx                 # Root layout wrapper with providers
│   │   ├── page.tsx                   # Landing page (public)
│   │   ├── globals.css                # Global styles & Tailwind setup
│   │   │
│   │   ├── 📁 (auth)/                 # Auth route group (public)
│   │   │   ├── login/
│   │   │   │   └── page.tsx           # Login form page
│   │   │   └── signup/
│   │   │       └── page.tsx           # Signup form page
│   │   │
│   │   ├── 📁 (protected)/            # Protected route group (requires auth)
│   │   │   └── page.tsx               # Dashboard redirect
│   │   │
│   │   ├── 📁 dashboard/              # Dashboard routes (protected)
│   │   │   ├── layout.tsx             # Dashboard layout (sidebar, navbar)
│   │   │   ├── page.tsx               # Dashboard home page
│   │   │   └── todos/
│   │   │       └── page.tsx           # Todos management page (CRUD UI)
│   │   │
│   │   ├── 📁 api/                    # API routes (if needed)
│   │   │   └── [route].ts             # Server-side API endpoints
│   │   │
│   │   ├── favicon.ico
│   │   └── (other static assets)
│   │
│   ├── 📁 components/                 # Reusable React Components
│   │   │
│   │   ├── 📁 auth/                   # Authentication Components
│   │   │   ├── LoginForm.tsx          # Login form with validation
│   │   │   └── SignupForm.tsx         # Signup form with validation
│   │   │
│   │   ├── 📁 todos/                  # Todo Management Components
│   │   │   ├── TaskForm.tsx           # Form to create/edit todos
│   │   │   ├── TaskItem.tsx           # Individual todo display
│   │   │   ├── TaskList.tsx           # List container for todos
│   │   │   ├── TasksContainer.tsx     # Smart container with logic
│   │   │   └── BulkActions.tsx        # Bulk select/delete operations
│   │   │
│   │   ├── 📁 dashboard/              # Dashboard Components
│   │   │   ├── DashboardUI.tsx        # Main dashboard layout
│   │   │   ├── Navbar.tsx             # Top navigation bar
│   │   │   └── Sidebar.tsx            # Side navigation menu
│   │   │
│   │   ├── 📁 landing/                # Landing Page Components
│   │   │   ├── HeroSection.tsx        # Hero section with CTA
│   │   │   ├── FeatureHighlights.tsx  # Feature cards
│   │   │   ├── CallToActionSection.tsx # CTA section
│   │   │   ├── Footer.tsx             # Footer with links
│   │   │   ├── SocialProof.tsx        # Testimonials/social proof
│   │   │   └── LandingNavBar.tsx      # Landing page navigation
│   │   │
│   │   ├── 📁 common/                 # Shared Utility Components
│   │   │   ├── EmptyState.tsx         # Empty state display
│   │   │   └── LoadingSpinner.tsx     # Loading indicator
│   │   │
│   │   └── 📁 ui/                     # shadcn/ui Component Library
│   │       ├── button.tsx             # Button component
│   │       ├── input.tsx              # Text input component
│   │       ├── label.tsx              # Label component
│   │       ├── alert.tsx              # Alert/notification component
│   │       └── (other UI components)
│   │
│   ├── 📁 lib/                        # Utilities & Hooks
│   │   │
│   │   ├── api.ts                     # API client with JWT auth
│   │   ├── auth.ts                    # Better Auth server integration
│   │   ├── auth-client.ts             # Better Auth client setup
│   │   ├── utils.ts                   # Helper functions
│   │   │
│   │   ├── 📁 hooks/                  # Custom React Hooks
│   │   │   ├── useAuth.ts             # Authentication state & methods
│   │   │   ├── useTodos.ts            # Todo CRUD operations hook
│   │   │   ├── useBulkSelection.ts    # Bulk selection logic
│   │   │   └── useTheme.ts            # Theme management
│   │   │
│   │   └── 📁 types/                  # TypeScript Type Definitions
│   │       ├── api.ts                 # API request/response types
│   │       ├── auth.ts                # Authentication types
│   │       └── todo.ts                # Todo domain types
│   │
│   ├── middleware.ts                  # Next.js middleware (auth, routing)
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.ts             # Tailwind CSS theme config
│   ├── postcss.config.js              # PostCSS configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── jest.config.js                 # Jest test configuration
│   ├── jest.setup.js                  # Jest setup file
│   ├── components.json                # shadcn/ui configuration
│   ├── package.json                   # Dependencies & scripts
│   ├── package-lock.json              # Dependency lock file
│   ├── Dockerfile                     # Docker image for production
│   └── README.md                      # Frontend-specific documentation
│
├── 📁 backend/                        # FastAPI Python Application
│   │
│   ├── 📁 app/
│   │   │
│   │   ├── main.py                    # FastAPI app entry point
│   │   │   │                           # - CORS configuration
│   │   │   │                           # - JWT middleware
│   │   │   │                           # - Route registration
│   │   │   │                           # - Error handlers
│   │   │   │                           # - Health endpoint
│   │   │
│   │   ├── 📁 models/                 # SQLModel Database Entities
│   │   │   ├── user.py                # User database model
│   │   │   │   │                       # - Fields: id, email, password_hash, name
│   │   │   │   │                       # - Relationships: todos (one-to-many)
│   │   │   │   │                       # - Better Auth compatible
│   │   │   │
│   │   │   └── todo.py                # Todo database model
│   │   │       │                       # - Fields: id, title, description, completed
│   │   │       │                       # - user_id (foreign key)
│   │   │       │                       # - timestamps: created_at, updated_at
│   │   │       │                       # - Relationship: user (many-to-one)
│   │   │
│   │   ├── 📁 schemas/                # Pydantic Request/Response Schemas
│   │   │   ├── user.py                # User create/read schemas
│   │   │   │   │                       # - UserCreate, UserRead, UserUpdate
│   │   │   │   │                       # - Validation rules
│   │   │   │
│   │   │   └── todo.py                # Todo create/read/update schemas
│   │   │       │                       # - TodoCreate, TodoRead, TodoUpdate
│   │   │       │                       # - Field validation
│   │   │
│   │   ├── 📁 api/                    # Route Handlers (Endpoints)
│   │   │   ├── auth.py                # Authentication endpoints
│   │   │   │   │                       # - POST /auth/signup
│   │   │   │   │                       # - POST /auth/signin
│   │   │   │   │                       # - POST /auth/logout
│   │   │   │   │                       # - JWT token generation/validation
│   │   │   │
│   │   │   ├── todos.py               # Todo CRUD endpoints
│   │   │   │   │                       # - GET /api/todos (list user's todos)
│   │   │   │   │                       # - POST /api/todos (create)
│   │   │   │   │                       # - GET /api/todos/{id} (read)
│   │   │   │   │                       # - PUT /api/todos/{id} (update)
│   │   │   │   │                       # - PATCH /api/todos/{id} (partial update)
│   │   │   │   │                       # - DELETE /api/todos/{id} (delete)
│   │   │   │   │                       # - User data isolation enforced
│   │   │   │
│   │   │   └── deps.py                # Dependency Injection
│   │   │       │                       # - get_current_user()
│   │   │       │                       # - get_db()
│   │   │       │                       # - JWT validation
│   │   │
│   │   └── 📁 core/
│   │       ├── config.py              # Settings & Environment Variables
│   │       │   │                       # - DATABASE_URL
│   │       │   │                       # - JWT_SECRET_KEY
│   │       │   │                       # - JWT_ALGORITHM
│   │       │   │                       # - CORS_ORIGINS
│   │       │   │                       # - ENVIRONMENT
│   │       │
│   │       ├── security.py            # JWT & Password Functions
│   │       │   │                       # - create_access_token()
│   │       │   │                       # - verify_token()
│   │       │   │                       # - hash_password()
│   │       │   │                       # - verify_password()
│   │       │
│   │       └── database.py            # Database Connection
│   │           │                       # - SessionLocal
│   │           │                       # - engine
│   │           │                       # - create_db_tables()
│   │
│   ├── 📁 tests/                      # Test Suite
│   │   ├── 📁 unit/                   # Unit tests
│   │   ├── 📁 integration/            # Integration tests
│   │   └── 📁 contract/               # Contract tests
│   │
│   ├── pyproject.toml                 # Python project configuration
│   │   │                               # - Dependencies: fastapi, sqlmodel, etc.
│   │   │                               # - Python version: 3.13+
│   │   │                               # - Build tools: uv
│   │   │
│   ├── uv.lock                        # Dependency lock file
│   ├── migrate_db.py                  # Database initialization script
│   ├── test-db-connection.mjs         # Database connection test
│   ├── Dockerfile                     # Docker image for production
│   ├── .env.example                   # Environment variables template
│   └── README.md                      # Backend-specific documentation
│
├── 📁 specs/                          # Feature Specifications & Plans
│   ├── 001-cli-todo/
│   ├── 002-phase-ii/
│   ├── 003-phase2-frontend-ui/
│   ├── 004-jwt-auth/
│   ├── 005-professional-ui/
│   └── 006-cleanup-finalize/          # Current feature
│       ├── spec.md                    # Feature specification
│       ├── plan.md                    # Implementation plan
│       ├── structure.md               # This file (detailed structure)
│       ├── architecture.md            # Architecture documentation
│       ├── setup-guide.md             # Setup & deployment guide
│       ├── api-documentation.md       # API reference
│       ├── component-inventory.md     # Component listing
│       ├── checklists/
│       │   └── requirements.md        # Quality checklist
│       └── tasks.md                   # (to be generated)
│
├── 📁 history/                        # Prompt History Records
│   └── prompts/
│       ├── constitution/              # Constitution-related prompts
│       ├── spec/                      # Spec creation prompts
│       ├── plan/                      # Planning prompts
│       ├── tasks/                     # Task generation prompts
│       └── ...
│
├── docker-compose.yml                 # Docker Compose orchestration
│   │                                   # - PostgreSQL service
│   │                                   # - FastAPI backend service
│   │                                   # - Next.js frontend service
│   │                                   # - Volume management
│   │                                   # - Port mapping
│
├── .env.example                       # Environment template for Docker Compose
│   │                                   # - POSTGRES_USER
│   │                                   # - POSTGRES_PASSWORD
│   │                                   # - POSTGRES_DB
│   │                                   # - JWT_SECRET_KEY
│
├── pyproject.toml                     # Root Python project config (if monorepo tools)
├── uv.lock                            # Root dependency lock (if monorepo tools)
├── README.md                          # Root project documentation
├── BETTER_AUTH_IMPORT_FIX.md          # (archived - historical issue)
├── CRUD_ENDPOINT_FIXES.md             # (archived - historical issue)
└── (other project files)
```

---

## Component Categories & Purposes

### Authentication Components (`frontend/components/auth/`)

| Component | Purpose | Key Props | Used In |
|-----------|---------|-----------|---------|
| **LoginForm** | Login page form with email/password | `onSubmit`, `loading`, `error` | `/login` |
| **SignupForm** | Signup page form with registration | `onSubmit`, `loading`, `error` | `/signup` |

### Todo Components (`frontend/components/todos/`)

| Component | Purpose | Key Props | Used In |
|-----------|---------|-----------|---------|
| **TaskForm** | Form to create/edit todos | `initialValue`, `onSubmit`, `loading` | Todo pages |
| **TaskItem** | Individual todo display & actions | `todo`, `onUpdate`, `onDelete` | TaskList |
| **TaskList** | Container for list of todos | `todos`, `onUpdate`, `onDelete` | TasksContainer |
| **TasksContainer** | Smart component managing state | `userId` | Todo pages |
| **BulkActions** | Bulk select/delete controls | `selectedIds`, `onDelete` | Todo pages |

### Dashboard Components (`frontend/components/dashboard/`)

| Component | Purpose | Key Props | Used In |
|-----------|---------|-----------|---------|
| **DashboardUI** | Main dashboard layout | `user` | Dashboard routes |
| **Navbar** | Top navigation bar | `user`, `onLogout` | Dashboard layout |
| **Sidebar** | Side navigation menu | `active` | Dashboard layout |

### Landing Page Components (`frontend/components/landing/`)

| Component | Purpose | Key Props | Used In |
|-----------|---------|-----------|---------|
| **HeroSection** | Hero with CTA | - | Landing page |
| **FeatureHighlights** | Feature cards | - | Landing page |
| **CallToActionSection** | CTA section | - | Landing page |
| **Footer** | Footer with links | - | Landing page |
| **SocialProof** | Testimonials/proof | - | Landing page |
| **LandingNavBar** | Landing page nav | - | Landing page |

### Common Components (`frontend/components/common/`)

| Component | Purpose | Key Props | Used In |
|-----------|---------|-----------|---------|
| **EmptyState** | Empty state display | `title`, `description`, `action` | List pages |
| **LoadingSpinner** | Loading indicator | `size` | Throughout app |

### UI Components (`frontend/components/ui/`)

| Component | Purpose | Key Props | Source |
|-----------|---------|-----------|--------|
| **Button** | Styled button | `variant`, `size`, `disabled` | shadcn/ui |
| **Input** | Text input field | `type`, `placeholder`, `disabled` | shadcn/ui |
| **Label** | Form label | `htmlFor` | shadcn/ui |
| **Alert** | Alert notification | `variant`, `title`, `message` | shadcn/ui |

---

## Custom Hooks (`frontend/lib/hooks/`)

| Hook | Purpose | Returns | Used In |
|------|---------|---------|---------|
| **useAuth** | Authentication state & methods | `user`, `login()`, `logout()`, `signup()` | Auth pages, layouts |
| **useTodos** | Todo CRUD operations | `todos`, `create()`, `update()`, `delete()` | Todo pages |
| **useBulkSelection** | Bulk selection logic | `selected`, `toggle()`, `selectAll()` | Todo pages |
| **useTheme** | Theme management | `theme`, `toggle()` | Layout |

---

## Type Definitions (`frontend/lib/types/`)

### `api.ts`
- `ApiResponse<T>` - Standard API response wrapper
- `PaginatedResponse<T>` - Paginated list response
- `ApiError` - Error response structure

### `auth.ts`
- `User` - Authenticated user data
- `SignupRequest` - Signup form data
- `LoginRequest` - Login form data
- `AuthResponse` - Auth response with token

### `todo.ts`
- `Todo` - Todo item data
- `CreateTodoRequest` - Create request data
- `UpdateTodoRequest` - Update request data

---

## API Endpoints (Backend)

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/signin` - Login
- `POST /auth/logout` - Logout

### Todos (User-Scoped)
- `GET /api/todos` - List user's todos
- `POST /api/todos` - Create new todo
- `GET /api/todos/{id}` - Get specific todo
- `PUT /api/todos/{id}` - Full update
- `PATCH /api/todos/{id}` - Partial update
- `DELETE /api/todos/{id}` - Delete todo

### System
- `GET /health` - Health check

---

## Key Data Models

### User (Backend: `models/user.py`)
```
- id: UUID (primary key)
- email: str (unique)
- password_hash: str
- name: str
- created_at: datetime
- updated_at: datetime
- todos: List[Todo] (relationship)
```

### Todo (Backend: `models/todo.py`)
```
- id: UUID (primary key)
- user_id: UUID (foreign key)
- title: str
- description: str (optional)
- is_completed: bool
- created_at: datetime
- updated_at: datetime
- user: User (relationship)
```

---

## Environment Configuration

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend `.env`
```env
DATABASE_URL=postgresql://user:password@localhost:5432/evo_todo
JWT_SECRET_KEY=your-256-bit-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

### Docker Compose `.env`
```env
POSTGRES_USER=evo_todo_user
POSTGRES_PASSWORD=evo_todo_password
POSTGRES_DB=evo_todo
JWT_SECRET_KEY=your-256-bit-secret
```

---

## Build & Deployment

### Development (Docker Compose)
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: localhost:5432
```

### Production
- Frontend: Deployed to static hosting (Vercel, Netlify) or Docker
- Backend: Deployed to cloud platform (AWS, GCP, Heroku)
- Database: Managed PostgreSQL (Neon, AWS RDS, etc.)

---

## Key Technologies

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | Next.js | 16+ |
| **Frontend Runtime** | React | 19+ |
| **Language (Frontend)** | TypeScript | 5.x |
| **Styling** | Tailwind CSS | 3.x |
| **UI Library** | shadcn/ui | Latest |
| **Auth (Frontend)** | Better Auth | Latest |
| **Backend** | FastAPI | 0.50+ |
| **Language (Backend)** | Python | 3.13+ |
| **ORM** | SQLModel | Latest |
| **Database** | PostgreSQL | 15+ |
| **Authentication** | JWT (HS256) | - |
| **Package Manager** | npm (frontend), uv (backend) | - |
| **Container** | Docker | 20+ |
| **Orchestration** | Docker Compose | 3.x |

---

## Development Workflow

1. **Local Setup**: Clone repo, configure `.env` files
2. **Start Services**: `docker-compose up -d`
3. **Frontend Dev**: `cd frontend && npm run dev`
4. **Backend Dev**: `cd backend && uvicorn app.main:app --reload`
5. **Testing**: `npm test` (frontend), `pytest` (backend)
6. **Building**: `npm run build` (frontend), `pip install -e .` (backend)

---

## Known Issues & Status

✅ Phase II complete:
- JWT authentication working
- User data isolation enforced
- CRUD operations functional
- Frontend-backend integration stable

🔄 Phase III (Cleanup & Finalization) in progress:
- Removing unused code
- Validating theme consistency
- Updating documentation
- Final quality assurance

