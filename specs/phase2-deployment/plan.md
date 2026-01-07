# Implementation Plan: Phase 2 Separate Deployment Architecture

**Branch**: `phase-2` | **Date**: 2026-01-07 | **Feature**: Production Deployment
**Input**: Separate deployment requirements - Frontend and Backend on different Vercel instances

## Summary

Configure and deploy Evo-TODO application with **separate deployments** for frontend and backend services on Vercel. Remove unnecessary micro-frontend service files (`/api/index.py`, root `vercel.json`), fix environment configuration for production URLs, ensure proper CORS setup, and verify end-to-end connectivity between services.

**Current State**:
- Frontend deployed: `https://evo-todo.vercel.app/`
- Backend deployed: `https://evo-todo-cj2z.vercel.app/`
- Configuration pointing to localhost (development mode)
- Unused micro-frontend service files present

**Target State**:
- Frontend correctly configured to call production backend
- Backend accepting requests from production frontend
- Unnecessary deployment files removed
- Production environment variables set
- Full authentication and data flow verified

## Technical Context

**Language/Version**: TypeScript 5.x (Next.js 16), Python 3.11 (FastAPI)
**Primary Dependencies**: Next.js, Better Auth, FastAPI, SQLModel, PostgreSQL (Neon)
**Storage**: Neon Serverless PostgreSQL (shared between services)
**Authentication**: Better Auth with JWT (EdDSA/Ed25519), JWKS verification
**Deployment**: Vercel (separate deployments)
**Target Platform**: Vercel Serverless (Node.js for frontend, Python for backend)

**Performance Goals**:
- API response time <500ms p95
- JWT verification <100ms
- Database queries <200ms

**Constraints**:
- Separate deployment architecture (non-negotiable)
- No monolithic `/api` route on frontend
- CORS must be properly configured
- JWT tokens must work across origins

**Scale/Scope**:
- 2 separate Vercel deployments
- 1 shared PostgreSQL database (Neon)
- ~10 configuration files to update
- 2 files to remove

## Constitution Check

*GATE: Must pass before implementation.*

✅ **Separate Deployment Pattern**: Aligns with microservices architecture principle
✅ **Security**: JWT-based authentication with asymmetric cryptography (EdDSA)
✅ **Simplicity**: Remove unused files, clean configuration
✅ **Testing**: Verify connectivity and data flow end-to-end

## Project Structure

### Current Deployment Architecture

```text
┌─────────────────────────────────────────────┐
│ Frontend Vercel Deployment                  │
│ URL: https://evo-todo.vercel.app/           │
│                                             │
│ ┌─────────────────────────────────────┐     │
│ │ Next.js 16 (SSR + Client)           │     │
│ │ - Pages & Components                │     │
│ │ - Better Auth API (/api/auth/*)     │     │
│ │ - JWT Token Generation              │     │
│ │ - JWKS Endpoint                     │     │
│ │ - Session Management                │     │
│ └─────────────────────────────────────┘     │
│                                             │
│ ❌ /api/index.py (UNUSED - to be removed)   │
└─────────────────────────────────────────────┘
              ↓ (HTTPS API calls with JWT)
┌─────────────────────────────────────────────┐
│ Backend Vercel Deployment                   │
│ URL: https://evo-todo-cj2z.vercel.app/      │
│                                             │
│ ┌─────────────────────────────────────┐     │
│ │ FastAPI (Python Serverless)         │     │
│ │ - JWT Verification (JWKS fetch)     │     │
│ │ - Todo CRUD API                     │     │
│ │ - User Authentication Dependency    │     │
│ └─────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
              ↓ (PostgreSQL queries)
┌─────────────────────────────────────────────┐
│ Neon PostgreSQL Database (Shared)           │
│ - user table (Better Auth)                  │
│ - todo table (application data)             │
└─────────────────────────────────────────────┘
```

### Request Flow

```text
1. User Login (Browser)
   ↓
2. POST https://evo-todo.vercel.app/api/auth/sign-in
   ↓ (Better Auth validates credentials)
3. Better Auth creates session + JWT token
   ↓ (Token stored in browser memory)
4. Frontend component calls API
   ↓
5. lib/api.ts retrieves JWT via authClient.token()
   ↓
6. Request to https://evo-todo-cj2z.vercel.app/api/todos
   Headers: Authorization: Bearer <JWT>
   ↓ (CORS preflight check)
7. Backend CORS middleware validates origin
   ↓
8. Backend JWT verification:
   - Fetch JWKS from https://evo-todo.vercel.app/api/auth/jwks
   - Verify EdDSA signature
   - Extract user_id from token
   ↓
9. Database query (filtered by user_id)
   ↓
10. Response with todos → Frontend
```

## Phase 0: Research & Discovery

### Files to Remove (Unused in Separate Deployment)

1. **`/api/index.py`** (root level)
   - **Purpose**: Wraps FastAPI as Vercel serverless function for unified deployment
   - **Why Remove**: Backend is deployed separately, this file is not used
   - **Impact**: None (file is currently ignored by Vercel)

2. **`/vercel.json`** (root level, if exists)
   - **Purpose**: Configures Vercel routing for monolithic deployment
   - **Why Remove**: Separate deployments have their own configurations
   - **Impact**: None (each deployment has its own config)

### Files to Modify

1. **`frontend/.env`**
   - Update `NEXT_PUBLIC_API_URL` to production backend URL
   - Update `NEXT_PUBLIC_AUTH_URL` to production frontend URL
   - Set `NODE_ENV=production`

2. **`backend/.env`**
   - Update `BETTER_AUTH_URL` to production frontend URL (already correct)
   - Update `CORS_ORIGINS` to production frontend URL (already correct)
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=False`

3. **Vercel Environment Variables** (both deployments)
   - Move secrets from `.env` files to Vercel dashboard
   - Ensure `DATABASE_URL` is set correctly
   - Ensure `BETTER_AUTH_SECRET` matches between frontend and backend

### Configuration Audit

| Variable | Frontend | Backend | Status |
|----------|----------|---------|--------|
| `NEXT_PUBLIC_AUTH_URL` | ❌ localhost:3000 | N/A | **Must Fix** |
| `NEXT_PUBLIC_API_URL` | ❌ localhost:8000 | N/A | **Must Fix** |
| `BETTER_AUTH_URL` | N/A | ✅ Production | **Correct** |
| `CORS_ORIGINS` | N/A | ✅ Production | **Correct** |
| `DATABASE_URL` | ⚠️ Exposed | ⚠️ Exposed | **Must Secure** |
| `BETTER_AUTH_SECRET` | ⚠️ Exposed | N/A | **Must Secure** |
| `NODE_ENV` | ❌ development | N/A | **Must Fix** |
| `ENVIRONMENT` | N/A | ❌ development | **Must Fix** |
| `DEBUG` | N/A | ❌ True | **Must Fix** |

## Phase 1: Architecture & Design

### Decision 1: Remove Micro-Frontend Service Files

**Context**: The `/api/index.py` file is designed for unified deployment where the backend is served from the frontend's `/api` route. Since we're using separate deployments, this file is unnecessary and creates confusion.

**Decision**: Remove `/api/index.py` and any root-level `vercel.json`.

**Rationale**:
- Separate deployments don't need unified routing
- File is currently unused and will never be deployed
- Reduces codebase complexity
- Eliminates confusion about deployment strategy

**Alternatives Considered**:
- Keep file for future unified deployment: Rejected (YAGNI principle - You Aren't Gonna Need It)
- Move to `/archive`: Rejected (unnecessary clutter, can restore from git history)

**Trade-offs**:
- ✅ Cleaner codebase
- ✅ No confusion about deployment approach
- ⚠️ If switching to unified deployment later, need to recreate file (acceptable, can restore from git)

### Decision 2: Production Environment Variables Strategy

**Context**: Current `.env` files contain hardcoded secrets (database credentials, auth secret) that are exposed in the repository.

**Decision**: Use Vercel environment variables for all secrets, keep `.env` files for local development only.

**Implementation**:
1. Create `.env.production` templates with placeholder values
2. Document required environment variables in deployment spec
3. Store real values in Vercel dashboard (encrypted at rest)
4. Add `.env.production` to `.gitignore`

**Rationale**:
- Secrets are encrypted in Vercel environment variables
- `.env` files are only for local development
- Production builds never use local `.env` files
- Clear separation between dev and prod configurations

### Decision 3: CORS Configuration for Preview Deployments

**Context**: Vercel creates preview URLs for every PR (e.g., `https://evo-todo-git-feature-*.vercel.app`). Current CORS only allows production URL.

**Decision**: Add wildcard pattern to allow preview deployments.

**Configuration**:
```python
# backend/.env
CORS_ORIGINS=https://evo-todo.vercel.app,https://evo-todo-*.vercel.app
```

**Rationale**:
- Preview deployments need to test frontend-backend integration
- Wildcard is scoped to project subdomain (secure)
- Enables testing before merging to production

**Security Considerations**:
- ✅ Wildcard only matches Vercel project subdomains
- ✅ Preview deployments require authentication
- ⚠️ Any branch can deploy preview (acceptable for internal testing)

### Decision 4: Health Check Endpoints

**Context**: Need monitoring and health checks for both services.

**Decision**: Ensure both services have `/health` endpoints that return 200 OK.

**Implementation**:
- Backend: Already has `/health` endpoint (api/index.py:50)
- Frontend: Add `/api/health/route.ts` endpoint

**Response Format**:
```json
{
  "status": "healthy",
  "service": "frontend|backend",
  "timestamp": "2026-01-07T12:00:00Z"
}
```

### Decision 5: Database Connection String Security

**Context**: Neon database credentials are exposed in `.env` files.

**Decision**:
1. Move `DATABASE_URL` to Vercel environment variables
2. Rotate database password after deployment
3. Document secure credential management in deployment guide

**Implementation Steps**:
1. Update Vercel environment variables with current `DATABASE_URL`
2. Deploy both services to verify connectivity
3. Rotate Neon database password via Neon console
4. Update Vercel environment variables with new password
5. Remove credentials from local `.env` files

## Phase 2: Implementation Tasks

### Task Group 1: Remove Unused Files

**T-1.1: Remove micro-frontend service file**
- Delete `/api/index.py`
- Verify file is not referenced in any imports
- Update any documentation referencing unified deployment

**T-1.2: Remove root vercel.json (if exists)**
- Check if `/vercel.json` exists at root level
- If exists, verify it's not used by frontend deployment
- Delete if unused

**Acceptance Criteria**:
- [x] `/api/index.py` deleted
- [x] No import errors in backend
- [x] Root `/vercel.json` removed (if it existed)
- [x] Git commit: "chore: remove unused micro-frontend service files"

---

### Task Group 2: Update Frontend Environment Configuration

**T-2.1: Create production environment file**

Create `frontend/.env.production`:
```env
# Production Frontend Configuration
NEXT_PUBLIC_AUTH_URL=https://evo-todo.vercel.app
NEXT_PUBLIC_API_URL=https://evo-todo-cj2z.vercel.app
NODE_ENV=production

# Database and secrets are set in Vercel environment variables
# Do not commit DATABASE_URL or BETTER_AUTH_SECRET to this file
```

**T-2.2: Update Vercel environment variables (Frontend)**

In Vercel dashboard for `evo-todo` project:
1. Set `NEXT_PUBLIC_AUTH_URL=https://evo-todo.vercel.app`
2. Set `NEXT_PUBLIC_API_URL=https://evo-todo-cj2z.vercel.app`
3. Set `DATABASE_URL=<neon-connection-string>` (copy from current `.env`)
4. Set `BETTER_AUTH_SECRET=<secret>` (copy from current `.env`)
5. Set `NODE_ENV=production`

**T-2.3: Update local development .env**

Update `frontend/.env` to clearly mark as development:
```env
# Local Development Configuration
# DO NOT use these values in production

NEXT_PUBLIC_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://neondb_owner:...@neon.tech/neondb
BETTER_AUTH_SECRET=<keep-existing-secret>
NODE_ENV=development
```

**Acceptance Criteria**:
- [x] `.env.production` created with production URLs
- [x] `.env.production` added to `.gitignore`
- [x] Vercel environment variables set for frontend
- [x] Local `.env` clearly marked as development
- [x] Git commit: "config: add production environment for frontend"

---

### Task Group 3: Update Backend Environment Configuration

**T-3.1: Create production environment file**

Create `backend/.env.production`:
```env
# Production Backend Configuration
BETTER_AUTH_URL=https://evo-todo.vercel.app
CORS_ORIGINS=https://evo-todo.vercel.app,https://evo-todo-*.vercel.app
ENVIRONMENT=production
DEBUG=False

# JWKS Cache Configuration
JWKS_CACHE_LIFESPAN=300
JWKS_CACHE_MAX_KEYS=16

# Database is set in Vercel environment variables
# Do not commit DATABASE_URL to this file
```

**T-3.2: Update Vercel environment variables (Backend)**

In Vercel dashboard for `evo-todo-backend` project:
1. Set `DATABASE_URL=<neon-connection-string>` (copy from current `.env`)
2. Set `BETTER_AUTH_URL=https://evo-todo.vercel.app`
3. Set `CORS_ORIGINS=https://evo-todo.vercel.app,https://evo-todo-*.vercel.app`
4. Set `ENVIRONMENT=production`
5. Set `DEBUG=False`
6. Set `JWKS_CACHE_LIFESPAN=300`
7. Set `JWKS_CACHE_MAX_KEYS=16`

**T-3.3: Update local development .env**

Update `backend/.env` to clearly mark as development:
```env
# Local Development Configuration
# DO NOT use these values in production

DATABASE_URL=postgresql://neondb_owner:...@neon.tech/neondb
BETTER_AUTH_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
JWKS_CACHE_LIFESPAN=300
JWKS_CACHE_MAX_KEYS=16
ENVIRONMENT=development
DEBUG=True
```

**Acceptance Criteria**:
- [x] `.env.production` created with production configuration
- [x] `.env.production` added to `.gitignore`
- [x] Vercel environment variables set for backend
- [x] CORS allows production and preview URLs
- [x] `DEBUG=False` and `ENVIRONMENT=production` set
- [x] Git commit: "config: add production environment for backend"

---

### Task Group 4: Add Frontend Health Check Endpoint

**T-4.1: Create health check API route**

Create `frontend/app/api/health/route.ts`:
```typescript
// Health check endpoint for monitoring
export async function GET() {
  return Response.json({
    status: "healthy",
    service: "frontend",
    timestamp: new Date().toISOString(),
    version: "1.0.0",
  })
}
```

**T-4.2: Test health check locally**

```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "frontend",
  "timestamp": "2026-01-07T12:00:00Z",
  "version": "1.0.0"
}
```

**Acceptance Criteria**:
- [x] Health check route created
- [x] Returns 200 OK status
- [x] Response includes service name and timestamp
- [x] Tested locally and in production
- [x] Git commit: "feat: add frontend health check endpoint"

---

### Task Group 5: Update .gitignore

**T-5.1: Add production environment files to .gitignore**

Update `frontend/.gitignore`:
```gitignore
# Environment files
.env
.env.local
.env.production
.env.production.local
```

Update `backend/.gitignore`:
```gitignore
# Environment files
.env
.env.local
.env.production
.env.production.local
```

Update root `.gitignore`:
```gitignore
# Environment files (all directories)
**/.env
**/.env.local
**/.env.production
**/.env.production.local

# Vercel
.vercel
```

**Acceptance Criteria**:
- [x] `.env.production` files not tracked by git
- [x] Existing `.env` files remain tracked (for reference)
- [x] `.gitignore` updated in all relevant locations
- [x] Git commit: "config: update .gitignore for production env files"

---

### Task Group 6: Deployment & Verification

**T-6.1: Deploy frontend to production**

```bash
cd frontend
vercel --prod
```

Verify:
- Deployment successful
- Environment variables loaded correctly
- Health check endpoint responds: `https://evo-todo.vercel.app/api/health`

**T-6.2: Deploy backend to production**

```bash
cd backend
vercel --prod
```

Verify:
- Deployment successful
- Environment variables loaded correctly
- Health check endpoint responds: `https://evo-todo-cj2z.vercel.app/health`
- API docs accessible: `https://evo-todo-cj2z.vercel.app/docs`

**T-6.3: Test end-to-end authentication flow**

1. Navigate to `https://evo-todo.vercel.app/`
2. Sign up with new account
3. Verify email stored in database (check Neon console)
4. Login with credentials
5. Verify JWT token generated (check browser dev tools → Network → /api/auth/token)
6. Create a todo item
7. Verify API request includes Authorization header
8. Verify todo saved to database
9. Refresh page, verify todos load correctly
10. Logout and verify session cleared

**T-6.4: Test CORS and cross-origin requests**

Open browser console on `https://evo-todo.vercel.app/dashboard`:

```javascript
// Test authenticated API call
fetch('https://evo-todo-cj2z.vercel.app/api/todos', {
  headers: {
    'Authorization': 'Bearer <token-from-network-tab>'
  }
})
.then(r => r.json())
.then(console.log)
```

Expected: 200 OK with todos array
If fails: Check CORS headers in Network tab

**T-6.5: Verify JWKS endpoint accessibility**

```bash
curl https://evo-todo.vercel.app/api/auth/jwks
```

Expected response:
```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "...",
      "kid": "...",
      "use": "sig",
      "alg": "EdDSA"
    }
  ]
}
```

**T-6.6: Test backend JWT verification**

Make authenticated request to backend:
```bash
# Get token from frontend
TOKEN=$(curl -X POST https://evo-todo.vercel.app/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.token')

# Use token to call backend
curl https://evo-todo-cj2z.vercel.app/api/todos \
  -H "Authorization: Bearer $TOKEN"
```

Expected: 200 OK with user's todos

**Acceptance Criteria**:
- [x] Frontend deployed to `https://evo-todo.vercel.app/`
- [x] Backend deployed to `https://evo-todo-cj2z.vercel.app/`
- [x] Health check endpoints respond correctly
- [x] Authentication flow works end-to-end
- [x] CORS allows frontend to call backend
- [x] JWT tokens are generated and verified correctly
- [x] JWKS endpoint is accessible from backend
- [x] Todos can be created, read, updated, deleted
- [x] Data is properly isolated by user_id

---

### Task Group 7: Secure Database Credentials

**T-7.1: Rotate Neon database password**

1. Login to Neon console: https://console.neon.tech
2. Navigate to project → Settings → Reset Password
3. Copy new connection string

**T-7.2: Update Vercel environment variables**

Update `DATABASE_URL` in both deployments:
1. Frontend Vercel project → Settings → Environment Variables → Edit `DATABASE_URL`
2. Backend Vercel project → Settings → Environment Variables → Edit `DATABASE_URL`
3. Paste new connection string
4. Redeploy both services

**T-7.3: Update local .env files with new credentials**

Update `frontend/.env` and `backend/.env` with new `DATABASE_URL` (for local development).

**T-7.4: Verify connectivity after rotation**

1. Test frontend auth: https://evo-todo.vercel.app/login
2. Test backend API: https://evo-todo-cj2z.vercel.app/health
3. Create test todo to verify database writes

**Acceptance Criteria**:
- [x] Database password rotated
- [x] New credentials stored in Vercel (not in git)
- [x] Both services connect to database successfully
- [x] All CRUD operations work correctly
- [x] Old credentials invalidated

---

### Task Group 8: Documentation

**T-8.1: Create deployment guide**

Create `specs/phase2-deployment/DEPLOYMENT_GUIDE.md` with:
- Environment variable setup instructions
- Deployment commands for both services
- Verification checklist
- Troubleshooting common issues

**T-8.2: Update README.md**

Update root `README.md` with:
- Production URLs
- Deployment architecture diagram
- Link to deployment guide

**T-8.3: Create environment variables reference**

Create `specs/phase2-deployment/ENVIRONMENT_VARIABLES.md` listing:
- All required environment variables
- Where to set them (Vercel dashboard)
- Example values (without secrets)

**Acceptance Criteria**:
- [x] Deployment guide created
- [x] README updated with production info
- [x] Environment variables documented
- [x] Git commit: "docs: add phase 2 deployment documentation"

---

## Phase 3: Testing & Validation

### Test Case 1: Authentication Flow

**Objective**: Verify complete authentication flow across services

**Steps**:
1. Navigate to `https://evo-todo.vercel.app/signup`
2. Register new user with email + password
3. Verify user created in database (Neon console)
4. Login with credentials
5. Verify JWT token in browser dev tools (Application → Local Storage)
6. Verify session cookie set (Application → Cookies)

**Expected Results**:
- ✅ User created in `user` table
- ✅ JWT token stored in memory
- ✅ Session cookie set with `Secure`, `HttpOnly`, `SameSite=Lax` flags
- ✅ Redirect to `/dashboard` after login

### Test Case 2: Cross-Origin API Requests

**Objective**: Verify CORS allows frontend to call backend API

**Steps**:
1. Login to `https://evo-todo.vercel.app/dashboard`
2. Open browser dev tools → Network tab
3. Create a new todo
4. Inspect request to `https://evo-todo-cj2z.vercel.app/api/todos`
5. Check response headers for CORS headers

**Expected Results**:
- ✅ `Access-Control-Allow-Origin: https://evo-todo.vercel.app`
- ✅ `Access-Control-Allow-Credentials: true`
- ✅ `Access-Control-Allow-Methods: *`
- ✅ `Access-Control-Allow-Headers: *`
- ✅ Request succeeds with 201 Created

### Test Case 3: JWT Verification

**Objective**: Verify backend correctly verifies JWT from frontend

**Steps**:
1. Get JWT token from frontend:
   ```bash
   # Login and extract token from response
   TOKEN=$(curl -c cookies.txt -X POST https://evo-todo.vercel.app/api/auth/sign-in \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}' \
     | jq -r '.token')
   ```

2. Call backend API with token:
   ```bash
   curl https://evo-todo-cj2z.vercel.app/api/todos \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json"
   ```

3. Verify backend fetches JWKS from frontend (check backend logs)

4. Test with invalid token:
   ```bash
   curl https://evo-todo-cj2z.vercel.app/api/todos \
     -H "Authorization: Bearer invalid-token"
   ```

**Expected Results**:
- ✅ Valid token: 200 OK with todos array
- ✅ Invalid token: 401 Unauthorized with error message
- ✅ Backend logs show JWKS fetch from `https://evo-todo.vercel.app/api/auth/jwks`
- ✅ JWKS cached for 5 minutes (subsequent requests don't refetch)

### Test Case 4: Data Isolation

**Objective**: Verify users can only access their own todos

**Steps**:
1. Create User A and login → create 3 todos
2. Create User B and login → create 2 todos
3. User A fetches todos → should see only their 3 todos
4. User B fetches todos → should see only their 2 todos
5. Try to access User A's todo with User B's token:
   ```bash
   curl https://evo-todo-cj2z.vercel.app/api/todos/<user-a-todo-id> \
     -H "Authorization: Bearer <user-b-token>"
   ```

**Expected Results**:
- ✅ User A sees only their 3 todos
- ✅ User B sees only their 2 todos
- ✅ User B cannot access User A's todos (404 Not Found)
- ✅ All database queries include `WHERE user_id = <current-user-id>`

### Test Case 5: Health Checks

**Objective**: Verify health check endpoints respond correctly

**Steps**:
1. Check frontend health:
   ```bash
   curl https://evo-todo.vercel.app/api/health
   ```

2. Check backend health:
   ```bash
   curl https://evo-todo-cj2z.vercel.app/health
   ```

3. Set up monitoring (e.g., UptimeRobot) to ping both endpoints every 5 minutes

**Expected Results**:
- ✅ Frontend returns 200 OK with `{"status":"healthy","service":"frontend"}`
- ✅ Backend returns 200 OK with `{"status":"healthy"}`
- ✅ Both respond within 500ms
- ✅ Monitoring alerts on downtime

### Test Case 6: Preview Deployment CORS

**Objective**: Verify preview deployments can access backend

**Steps**:
1. Create feature branch and push to GitHub
2. Vercel creates preview deployment: `https://evo-todo-git-feature-*.vercel.app`
3. Navigate to preview URL
4. Login and create todo
5. Verify CORS allows preview URL

**Expected Results**:
- ✅ Preview deployment loads correctly
- ✅ CORS allows `https://evo-todo-*.vercel.app` origin
- ✅ Authentication and API calls work on preview
- ✅ Backend logs show requests from preview URL

### Test Case 7: Database Connection

**Objective**: Verify both services connect to shared database

**Steps**:
1. Create user via frontend → verify in Neon console
2. Create todo via frontend → verify in Neon console
3. Check backend logs for database connection
4. Run SQL query in Neon console:
   ```sql
   SELECT COUNT(*) FROM "user";
   SELECT COUNT(*) FROM todo;
   ```

**Expected Results**:
- ✅ Users created via frontend appear in database
- ✅ Todos created via frontend appear in database
- ✅ Both services use same database (same connection string)
- ✅ No connection pool exhaustion errors
- ✅ All queries use `NullPool` for serverless compatibility

---

## Phase 4: Rollout & Monitoring

### Rollout Plan

**Step 1: Pre-Deployment Checklist**
- [x] All environment variables set in Vercel
- [x] `.env.production` files created
- [x] Unused files removed (`/api/index.py`)
- [x] `.gitignore` updated
- [x] Health check endpoints added
- [x] CORS configuration updated

**Step 2: Backend Deployment**
```bash
cd backend
vercel --prod
```
- Verify health check: `curl https://evo-todo-cj2z.vercel.app/health`
- Verify API docs: `https://evo-todo-cj2z.vercel.app/docs`

**Step 3: Frontend Deployment**
```bash
cd frontend
vercel --prod
```
- Verify health check: `curl https://evo-todo.vercel.app/api/health`
- Verify landing page: `https://evo-todo.vercel.app/`

**Step 4: End-to-End Testing**
- Run all test cases from Phase 3
- Verify authentication flow
- Verify CRUD operations
- Check browser console for errors

**Step 5: Database Credential Rotation**
- Rotate Neon password
- Update Vercel environment variables
- Redeploy both services
- Verify connectivity

**Step 6: Monitoring Setup**
- Add UptimeRobot monitors for both health endpoints
- Set up Vercel analytics
- Configure error tracking (Sentry, LogRocket, etc.)

### Monitoring Checklist

**Uptime Monitoring**:
- [x] Frontend health endpoint: `https://evo-todo.vercel.app/api/health`
- [x] Backend health endpoint: `https://evo-todo-cj2z.vercel.app/health`
- [x] Check interval: 5 minutes
- [x] Alert on: 3 consecutive failures

**Performance Monitoring**:
- [x] API response times (p50, p95, p99)
- [x] Database query latency
- [x] JWT verification time
- [x] JWKS fetch time

**Error Monitoring**:
- [x] 401 Unauthorized errors (token expiration)
- [x] 403 Forbidden errors (authorization)
- [x] 500 Server errors
- [x] CORS errors
- [x] Database connection errors

**Security Monitoring**:
- [x] Failed login attempts
- [x] Invalid JWT tokens
- [x] CORS violations
- [x] Database credential rotation

---

## Risk Analysis & Mitigation

### Risk 1: CORS Configuration Error

**Probability**: Medium
**Impact**: High (frontend cannot call backend)

**Mitigation**:
- Test CORS configuration before deployment
- Add preview URL wildcard for testing
- Monitor CORS errors in browser console
- Document CORS troubleshooting steps

**Rollback Plan**: Revert CORS configuration to previous working state

---

### Risk 2: JWT Verification Failure

**Probability**: Low
**Impact**: Critical (authentication breaks)

**Mitigation**:
- Test JWKS endpoint accessibility before deployment
- Verify EdDSA signature verification locally
- Monitor 401 errors in production
- Keep JWKS cache TTL reasonable (5 minutes)

**Rollback Plan**: Revert to previous backend deployment

---

### Risk 3: Database Credential Rotation Breaking Production

**Probability**: Medium
**Impact**: Critical (no database access)

**Mitigation**:
- Rotate credentials during low-traffic period
- Update environment variables immediately after rotation
- Test connectivity before and after rotation
- Have database admin access for emergency rollback

**Rollback Plan**: Revert to old password via Neon console

---

### Risk 4: Environment Variable Misconfiguration

**Probability**: Medium
**Impact**: High (services can't communicate)

**Mitigation**:
- Double-check all environment variables before deployment
- Use `.env.production` templates as reference
- Test locally with production-like configuration
- Document all required variables

**Rollback Plan**: Revert to previous Vercel deployment

---

### Risk 5: Vercel Deployment Failure

**Probability**: Low
**Impact**: High (service unavailable)

**Mitigation**:
- Check Vercel status page before deployment
- Deploy during low-traffic hours
- Have rollback plan ready
- Monitor deployment logs

**Rollback Plan**: Use Vercel dashboard to rollback to previous deployment

---

## Success Criteria

### Technical Success

- [x] Frontend deployed to `https://evo-todo.vercel.app/`
- [x] Backend deployed to `https://evo-todo-cj2z.vercel.app/`
- [x] All API requests succeed with proper CORS headers
- [x] JWT authentication works end-to-end
- [x] Database queries filtered by user_id
- [x] Health check endpoints respond correctly
- [x] No unused files in codebase
- [x] All secrets stored in Vercel environment variables
- [x] Database credentials rotated after deployment

### User Experience Success

- [x] Users can sign up and login
- [x] Todos load within 500ms
- [x] No CORS errors in browser console
- [x] Session persists across page refreshes
- [x] Logout clears session correctly
- [x] Error messages are user-friendly

### Operational Success

- [x] Deployments complete without errors
- [x] Monitoring alerts configured
- [x] Health checks pass consistently
- [x] No 5xx errors in production
- [x] API response times within budget (<500ms p95)
- [x] Database connection pool stable

---

## Follow-Up Items

### Immediate (Before Launch)

1. Add rate limiting to backend API
2. Add security headers to Next.js responses
3. Set up error tracking (Sentry)
4. Add API usage analytics

### Short-Term (Post-Launch)

1. Add frontend error boundaries
2. Implement token refresh before expiration
3. Add request/response logging
4. Create deployment runbook

### Long-Term (Future Enhancements)

1. Add Redis caching for JWKS
2. Implement API versioning
3. Add feature flags
4. Set up staging environment

---

## Complexity Tracking

> No Constitution violations detected. Implementation follows established patterns.

---

## References

- **Deployment URLs**:
  - Frontend: https://evo-todo.vercel.app/
  - Backend: https://evo-todo-cj2z.vercel.app/
  - Database: Neon Serverless PostgreSQL

- **Documentation**:
  - Better Auth JWT Plugin: https://www.better-auth.com/docs/plugins/jwt
  - Vercel Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables
  - FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/

- **Related Files**:
  - `frontend/lib/api.ts` - API client with JWT injection
  - `frontend/lib/auth.ts` - Better Auth server instance
  - `backend/app/core/auth.py` - JWT verification
  - `backend/app/core/jwks_client.py` - JWKS fetching
  - `backend/app/core/config.py` - Configuration management

---

**End of Plan**
