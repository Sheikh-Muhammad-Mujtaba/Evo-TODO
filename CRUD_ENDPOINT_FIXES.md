# CRUD Endpoint Fixes - Tasks & User Stories

**Feature**: Todo CRUD API Frontend-Backend Alignment  
**Status**: Tasks Created  
**Total Tasks**: 8  
**Critical Issues**: 3  
**Phase**: Red (Bug Fix)  

---

## User Stories & Priority

### US1: Complete CRUD Operations (P1 - CRITICAL)
**Goal**: Ensure all CRUD endpoints work end-to-end from frontend to backend  
**Acceptance Criteria**:
- User can create todo with title and description
- User can fetch single todo by ID
- User can update todo (toggle status)
- User can delete todo
- All requests include proper JWT authentication
- All responses properly typed

**Test Criteria**: Manual testing of all 5 CRUD endpoints with valid & invalid data

### US2: Frontend API Consistency (P1 - HIGH)
**Goal**: Frontend code matches backend API contract exactly  
**Acceptance Criteria**:
- Field mapping: snake_case ↔ camelCase documented
- Request/Response types strongly typed (no `any`)
- All CRUD methods have JSDoc documentation
- Frontend validation matches backend constraints
- Pagination support implemented

**Test Criteria**: Code review of API contract alignment

---

## Tasks by Phase

### Phase 1: Setup & Analysis (No code changes)
- [x] Analysis complete: Identified 8 issues across 3 categories

### Phase 2: Critical Fixes (Red Phase - Bug Fixes)

#### Task Group 1: Missing Single Todo Fetch Method

- [ ] T001 [P] [US1] Add `getTodoById()` method to useTodos hook in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: Method accepts todo ID string, returns Promise<Todo>, calls GET /api/todos/{id}

- [ ] T002 [P] [US1] Update `transformTodoResponse()` to handle single todo responses in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: Converter handles both array and single object responses

#### Task Group 2: Fix PATCH Endpoint Request Format

- [ ] T003 [P] [US1] Fix `updateTodo()` to use correct TodoToggle schema in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: PATCH requests send only `{ is_complete: boolean }` not full object; confirm 200 response

- [ ] T004 [P] [US1] Add separate `updateTodoFields()` method for title/description updates in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: New method handles partial updates, sends correct field names (snake_case)

#### Task Group 3: Add Missing Description Field Support

- [ ] T005 [P] [US2] Add `description` field to createTodo request in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: POST /api/todos request includes description field from Todo object

- [ ] T006 [P] [US2] Add description parameter to updateTodo payload in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: PATCH requests can update description field independently

#### Task Group 4: Add Documentation & Type Safety

- [ ] T007 [P] [US2] Add JSDoc comments to all CRUD methods in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: Each method documents: parameters, return type, error handling, example usage
  ```typescript
  /**
   * Fetch all todos with optional pagination and filtering
   * @param skip - Number of items to skip (default: 0)
   * @param limit - Number of items to return (default: 100, max 1000)
   * @returns Promise<Todo[]> - Array of todos for current user
   * @throws Error if authentication fails or API error occurs
   */
  const refreshTodos = async (skip = 0, limit = 100) => { ... }
  ```

- [ ] T008 [P] [US2] Create typed request/response interfaces in `frontend/lib/hooks/useTodos.ts`
  **Acceptance**: 
  - `TodoCreateRequest` interface for POST body
  - `TodoUpdateRequest` interface for PATCH body
  - `TodoListResponse` interface for GET /api/todos
  - Replace all `any` types with proper interfaces
  ```typescript
  interface TodoCreateRequest {
    title: string
    description?: string
  }
  
  interface TodoToggleRequest {
    is_complete: boolean
  }
  
  interface TodoListResponse {
    todos: TodoResponse[]
    total: number
  }
  ```

---

## Implementation Order

### Critical Path (Must Complete First)
1. T001 - Add getTodoById() [Enables individual todo fetching]
2. T003 - Fix PATCH schema [Fixes update endpoint]
3. T005 - Add description support [Enables full CRUD]

### Then Complete (Can Parallelize)
- T002, T004, T006, T007, T008 (all other enhancements)

### Parallel Opportunities
All 8 tasks can be parallelized since they modify different methods in the same file and don't block each other (assume file lock is handled by version control).

---

## Testing Strategy

### Manual Test Cases Per Task

**T001 - getTodoById**
```bash
# Before: No way to fetch single todo
# After: Should fetch and return specific todo
- Create a todo and note its ID
- Call getTodoById(id)
- Verify returned Todo matches backend data
```

**T003 - Fix PATCH Schema**
```bash
# Before: PATCH sends wrong format → 422 error
# After: PATCH sends is_complete → 200 OK
- Create a todo (status: pending)
- Call updateTodo(id, { status: 'completed' })
- Verify is_complete: true sent to backend
- Verify 200 response and todo marked complete
```

**T005 - Add Description**
```bash
# Before: Description field ignored
# After: Description saved and returned
- Call createTodo({ title, description: 'Test desc' })
- Verify POST request includes description
- Verify response contains description field
```

**T007 - JSDoc Documentation**
```bash
# Code review verification:
- Each CRUD method has @param for each parameter
- Each method has @returns documenting return type
- Each method has @throws listing potential errors
- All parameters and return types are accurate
```

**T008 - Type Safety**
```bash
# Code review verification:
- No remaining `any` types in useTodos.ts
- All API requests use typed interfaces
- Type checking catches wrong parameter types
- Response data properly typed as Todo[], not any[]
```

---

## Success Criteria - All Issues Resolved

| Issue ID | Description | Task(s) | Status |
|----------|-------------|---------|--------|
| C1 | Missing description field | T005, T006 | 🟡 Pending |
| C2 | Missing getTodoById | T001, T002 | 🟡 Pending |
| C3 | Wrong PATCH format | T003 | 🟡 Pending |
| C4 | Missing documentation | T007 | 🟡 Pending |
| C5 | Type safety (any types) | T008 | 🟡 Pending |
| C6 | Field name mapping | T007 | 🟡 Pending |
| C7 | Input validation | None (low priority) | ⏳ Deferred |
| C8 | Pagination params | None (enhancement) | ⏳ Deferred |

---

## File Changes Summary

### Modified Files
- `frontend/lib/hooks/useTodos.ts` (All 8 tasks modify this file)

### Potential New Files (Optional)
- `frontend/lib/schemas/todo.ts` (Extract interfaces from useTodos.ts if desired)

### No Backend Changes Needed
Backend implementation is complete and correct; frontend just needs to match it.

---

## Phase Completion Checklist

- [ ] T001: getTodoById() method added
- [ ] T002: Response transformer handles both array & single objects
- [ ] T003: PATCH endpoint uses correct schema (is_complete only)
- [ ] T004: updateTodoFields() method for partial updates
- [ ] T005: Description field in createTodo requests
- [ ] T006: Description field in updateTodo requests
- [ ] T007: JSDoc comments on all CRUD methods
- [ ] T008: Strong typing - no `any` types remain
- [ ] Manual test: All 5 CRUD endpoints work correctly
- [ ] Code review: API contract matches backend specification

---

## Time Estimate

- Setup & Analysis: 30 min (✅ Complete)
- T001-T002 (getTodoById): 20 min
- T003-T004 (PATCH fixes): 30 min  
- T005-T006 (Description field): 20 min
- T007-T008 (Documentation & Types): 40 min
- Manual testing: 30 min
- **Total: ~3 hours**

---

## Risk Assessment

**No High-Risk Tasks**: All changes are frontend-only, no database migrations or API changes needed

**Breaking Changes**: None (adding methods, not removing)

**Rollback Strategy**: Simple git revert if needed

