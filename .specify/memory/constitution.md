# Evo-TODO Constitution (Phase II)

## Core Principles

### I. Full-Stack Web Application with Separation of Concerns
- **Frontend**: Next.js 16+ (App Router) – modern React with server and client components
- **Backend**: FastAPI – high-performance async Python API
- **Database**: SQLModel + Neon Serverless PostgreSQL – type-safe ORM with scalable cloud database
- **Authentication**: Better Auth with JWT integration – secure, user-scoped data access
This stack enables rapid development, type safety across layers, and production-ready scalability.

### II. User-Scoped Data and JWT Authentication (Mandatory)
All API endpoints MUST accept a JWT token in the Authorization header. Every response MUST be filtered by `user_id` derived from the token. No endpoint returns unfiltered data. This enforces data isolation, security, and multi-tenant correctness. Token validation happens at the API boundary; internal functions assume valid, authenticated context.

### III. Clean Code Principles (Mandatory)
Code must follow clean code discipline: functions are small and focused (single responsibility), variable names are clear and self-documenting, nesting is minimal, and logic is testable in isolation. Complexity must be justified. Code reviews enforce clarity over brevity.

### IV. Task-Driven Implementation
All code MUST map to a Task ID. Every pull request, feature, and refactor starts with a task definition in tasks.md. Orphaned code (not traceable to a task) is not permitted. This ensures accountability, reviewability, and architectural coherence.

### V. Performance Over Brevity
Design and implementation prioritize measurable performance (latency, throughput, memory efficiency) over code brevity or cleverness. Profiling and optimization are expected for critical paths. Trade-offs must be documented with rationale.

### VI. No Manual Code Writing
Code generation, scaffolding, and templating are preferred. Manual coding is permitted only after generator/template approach is exhausted and justified. Reduces human error and ensures consistency across the codebase.

### VII. MCP Integration for Documentation and Authentication
- **Context7 MCP**: Use for accessing updated technical documentation and debugging context to avoid errors and ensure correctness.
- **Better Auth MCP**: Use for all Better Auth integration, configuration, and best practices to ensure secure and correct authentication implementation.
These MCPs provide authoritative, up-to-date guidance; all debugging and authentication work MUST reference these sources first.

## Technology Stack (Phase II)

- **Frontend**: Next.js 16+ (App Router)
- **Backend**: FastAPI (async Python)
- **ORM**: SQLModel (type-safe, Pydantic-integrated)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT
- **Code Quality**: Clean code principles, single responsibility, testable functions
- **Task Tracking**: All code linked to Task IDs in tasks.md

## Development Workflow

1. **Task-First**: Every feature, fix, or refactor begins with a task definition in tasks.md.
2. **MCP-Driven Documentation**: Consult **Context7 MCP** for debugging and technical guidance; consult **Better Auth MCP** for all authentication work.
3. **Approval Before Code**: Tasks are reviewed and approved before implementation starts.
4. **Mapping Enforcement**: Every commit MUST reference its Task ID. Code without traceability is rejected.
5. **JWT Validation**: All API requests require valid JWT tokens; all responses filtered by user_id.
6. **Testing**: Code must be testable in isolation; integration tests validate end-to-end behavior.
7. **Code Review**: All PRs reviewed for clean code adherence, task mapping, authentication/authorization, MCP compliance, and performance considerations.

## Git Branching Strategy (Phase II)

- **Main Release Branch**: `phase-2` (final merged branch for Phase II)
- **Feature Branches**: `phase2-XXY-feature-name` (e.g., `phase2-001-auth`, `phase2-002-todo-crud`)
- **Rules**: All PRs target `phase-2`. Feature branches are short-lived and deleted after merge.

## Non-Negotiable Constraints

- All API endpoints MUST require JWT tokens in Authorization header.
- All responses MUST be filtered by user_id from JWT claims.
- No unfiltered data access; data isolation is enforced at API boundary.
- All code MUST reference a Task ID (in commit messages and PR descriptions).
- SQLModel + PostgreSQL for all persistent data (no in-memory-only storage).
- No manual code generation if automated approach is feasible.
- No brevity at the expense of clarity and performance.
- **MCP Usage (Mandatory)**:
  - All debugging and technical documentation queries MUST use **Context7 MCP** for current, authoritative guidance.
  - All Better Auth integration, configuration, and security implementation MUST use **Better Auth MCP** as source of truth.
  - MCPs are consulted FIRST before manual implementation or external documentation.

## Governance

This constitution supersedes all other development practices and guidelines. Amendments require:
1. Documentation of the change and rationale.
2. Explicit approval (tracked in commit/PR).
3. Migration plan for existing code (if backward incompatible).

All PRs and reviews MUST verify compliance with these principles. Use `CLAUDE.md` for agent-specific guidance on development workflows. Violations are non-negotiable and must be remediated before merge.

**Version**: 2.0.0 (Phase II) | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-29
