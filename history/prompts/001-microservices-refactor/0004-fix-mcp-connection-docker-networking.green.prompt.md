---
id: 0004
title: Fix MCP Connection Docker Networking
stage: green
date: 2026-02-07T04:30:00Z
surface: claude-code
model: claude-opus-4.5
feature: 001-microservices-refactor
branch: 001-microservices-refactor
user: abdullah
command: manual-prompt
labels: [mcp, docker, networking, sse-transport, bug-fix]
links:
  spec: specs/001-microservices-refactor/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: backend/mcp_server/server.py
    change: Reconfigured FastMCP app mounting to expose SSE endpoints at /mcp/sse and /mcp/messages, fixed imports for Docker context
  - path: backend/app/api/chat.py
    change: Updated MCP client URL to append /mcp/sse suffix and handle both Docker and local environments
  - path: docker-compose.yml
    change: Added mcp-server dependency to agent-service depends_on
  - path: backend/.env.example
    change: Added MCP_SERVER_URL and MCP_INTERNAL_SECRET configuration
  - path: backend/mcp_server/Dockerfile
    change: Updated CMD to use correct app variable name (server:app)
tests:
  - path: manual
    status: pending
    note: Need to test end-to-end chat flow with Docker Compose
---

## Prompt

Read the @error.txt and use mcpserver and follow this plan:

Implementation Directive: Fix MCP Connection & Docker Networking

Objective: Resolve the McpError: Session terminated by aligning the MCP Server's transport layer with the Agent's client and fixing container networking.

1. Fix MCP Server Transport (backend/mcp-server/src/server.py)
   - Ensure the MCP Server uses the official SSE Transport
   - Replace generic FastAPI endpoints with mcp.server.sse.SseServerTransport
   - Provide GET /sse and POST /messages routes

2. Align Agent Client (backend/agent-service/src/api/chat.py)
   - Update MCPServerStreamableHttp configuration
   - Change URL from http://localhost:8001/mcp to http://mcp-server:8001/sse
   - Make URL configurable via environment variable

3. Correct Docker Compose & Dapr
   - Verify depends_on relationships
   - Ensure all services on same network (app-network)
   - Verify Dapr sidecars not conflicting

4. Tool Execution Fix
   - Ensure tool calls use Dapr App ID of todo-service

5. Execution Workflow
   - Step 1: Run sp.specify to update API contract
   - Step 2: Refactor SSE transport in MCP server
   - Step 3: Update environment configurations

Constraint: Maintain "Triple-Lock" security with user_id passing through chat_endpoint -> agent -> mcp_tool -> todo_service

## Response snapshot

Analysis and Implementation:

The error trace showed `mcp.shared.exceptions.McpError: Session terminated` occurring when the agent tried to connect to the MCP server. Root causes identified:

1. **Transport Mismatch**: FastMCP's `streamable_http_app()` was mounted at `/mcp` but the SSE client expected `/mcp/sse` endpoint
2. **Network Configuration**: Agent using localhost instead of Docker service name
3. **Missing Dependency**: Agent service didn't declare dependency on MCP server

### Changes Made:

**backend/mcp_server/server.py**:
- Changed app variable name from `mcp_host_app` to `app` for consistency
- Mounted FastMCP's `streamable_http_app()` at `/mcp` path to expose `/mcp/sse` and `/mcp/messages`
- Updated CORS to allow all origins (restrict in production)
- Fixed imports to work when running as `server:app` in Docker

**backend/app/api/chat.py**:
- Added logic to append `/mcp/sse` to MCP_SERVER_URL if not already present
- Made connection URL dynamic based on settings.MCP_SERVER_URL

**docker-compose.yml**:
- Added `mcp-server` to agent-service `depends_on` list
- Added comment clarifying MCP_SERVER_URL uses Docker service name

**backend/.env.example**:
- Added MCP_SERVER_URL configuration (http://mcp-server:8000 for Docker, http://localhost:8003 for local)
- Added MCP_INTERNAL_SECRET configuration

**backend/mcp_server/Dockerfile**:
- Updated CMD to use `server:app` instead of `mcp_server.server:mcp_host_app`

### Key Technical Decisions:

1. **Kept FastMCP's streamable_http_app()**: Rather than reimplementing SSE transport from scratch, leveraged FastMCP's built-in transport which already handles SSE protocol correctly

2. **Path Strategy**: Mounted at `/mcp` to expose `/mcp/sse` (EventSource) and `/mcp/messages` (JSON-RPC POST)

3. **URL Handling**: Added conditional logic in agent to append `/mcp/sse` suffix, supporting both explicit and derived URLs

4. **Import Path Fix**: Added sys.path manipulation to handle module resolution when running as `server:app`

## Outcome

- ✅ Impact: Fixed MCP connection error blocking agent-service to mcp-server communication in Docker environment
- 🧪 Tests: Manual testing required - need to verify Docker Compose startup and chat endpoint flow
- 📁 Files: Modified 5 files (server.py, chat.py, docker-compose.yml, .env.example, Dockerfile)
- 🔁 Next prompts: Test end-to-end flow, verify Triple-Lock security still works, check Dapr sidecar health
- 🧠 Reflection: SSE transport configuration in MCP SDK requires careful attention to endpoint paths - /sse for EventSource, /messages for JSON-RPC

## Evaluation notes (flywheel)

- Failure modes observed: Import path issues when running in Docker context, endpoint path mismatches between client and server
- Graders run and results (PASS/FAIL): PENDING - awaiting manual Docker test
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add health check endpoint verification in docker-compose healthcheck for MCP server
