# Evo-TODO Constitution

## Core Principles

### I. Python 3.13+ with uv Package Management
Python 3.13+ is the enforced runtime. All dependencies must be managed exclusively via uv for consistency, security, and performance. No pip, poetry, or other package managers permitted. All project operations (install, build, test, run) flow through uv toolchain.

### II. Strictly In-Memory Storage
All data and state MUST be held exclusively in memory. No persistent storage (files, databases, network caches) is permitted. This design enables fast iteration, simplified testing, and deterministic behavior. State is ephemeral; loss of process = loss of data. This is a non-negotiable architectural constraint.

### III. Clean Code Principles (Mandatory)
Code must follow clean code discipline: functions are small and focused (single responsibility), variable names are clear and self-documenting, nesting is minimal, and logic is testable in isolation. Complexity must be justified. Code reviews enforce clarity over brevity.

### IV. Task-Driven Implementation
All code MUST map to a Task ID. Every pull request, feature, and refactor starts with a task definition in tasks.md. Orphaned code (not traceable to a task) is not permitted. This ensures accountability, reviewability, and architectural coherence.

### V. Performance Over Brevity
Design and implementation prioritize measurable performance (latency, throughput, memory efficiency) over code brevity or cleverness. Profiling and optimization are expected for critical paths. Trade-offs must be documented with rationale.

### VI. No Manual Code Writing
Code generation, scaffolding, and templating are preferred. Manual coding is permitted only after generator/template approach is exhausted and justified. Reduces human error and ensures consistency across the codebase.

## Technology Stack

- **Runtime**: Python 3.13+ (non-negotiable)
- **Package Manager**: uv (exclusive)
- **Storage**: In-memory only (no persistent state)
- **Code Quality**: Clean code principles, single responsibility, testable functions
- **Task Tracking**: All code linked to Task IDs in tasks.md

## Development Workflow

1. **Task-First**: Every feature, fix, or refactor begins with a task definition in tasks.md.
2. **Approval Before Code**: Tasks are reviewed and approved before implementation starts.
3. **Mapping Enforcement**: Every commit MUST reference its Task ID. Code without traceability is rejected.
4. **Testing**: Code must be testable in isolation; integration tests validate end-to-end behavior.
5. **Code Review**: All PRs reviewed for clean code adherence, task mapping, and performance considerations.

## Non-Negotiable Constraints

- No persistent storage mechanisms (files, databases, network caches).
- No package managers other than uv.
- No code without a Task ID mapping.
- No manual code generation if automated approach is feasible.
- No brevity at the expense of clarity and performance.

## Governance

This constitution supersedes all other development practices and guidelines. Amendments require:
1. Documentation of the change and rationale.
2. Explicit approval (tracked in commit/PR).
3. Migration plan for existing code (if backward incompatible).

All PRs and reviews MUST verify compliance with these principles. Use `CLAUDE.md` for agent-specific guidance on development workflows. Violations are non-negotiable and must be remediated before merge.

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
