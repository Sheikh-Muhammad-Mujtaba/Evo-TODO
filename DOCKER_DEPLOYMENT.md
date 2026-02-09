# Docker Deployment Guide

This guide explains how to build and run the Evo-TODO microservices architecture using Docker and Docker Compose.

## Architecture Overview

The application consists of the following services:
- **PostgreSQL**: Database for storing todos and user data
- **Dapr Placement**: Dapr control plane for actor placement
- **Todo Service**: FastAPI service handling CRUD operations for todos
- **Agent Service**: AI-powered agent service with Gemini integration
- **MCP Server**: Model Context Protocol server for agent-to-service communication
- **Frontend**: Next.js web application
- **Dapr Sidecars**: Service mesh sidecars for inter-service communication

## Prerequisites

- Docker Engine 20.10+
- Docker Compose V2
- At least 4GB RAM available for Docker

## Configuration

### 1. Environment Variables

Copy the example environment file and configure your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
POSTGRES_USER=evo_todo_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=evo_todo

# JWT (generate with: openssl rand -base64 32)
JWT_SECRET_KEY=your-256-bit-secret-key

# AI API Key (required for agent service)
GEMINI_API_KEY=your-gemini-api-key

# MCP Secret
MCP_INTERNAL_SECRET=your-mcp-secret
```

### 2. Build Docker Images

Build all service images:

```bash
# Build all services
docker-compose build

# Or build specific services
docker-compose build todo-service
docker-compose build agent-service
docker-compose build mcp-server
docker-compose build frontend
```

## Running the Application

### Start All Services

```bash
docker-compose up -d
```

### Start Specific Services

```bash
# Start only backend services
docker-compose up -d postgres dapr-placement todo-service daprd-todo

# Start with logs
docker-compose up postgres dapr-placement todo-service daprd-todo
```

### Check Service Health

```bash
# Check all running containers
docker-compose ps

# Check logs for specific service
docker-compose logs -f todo-service
docker-compose logs -f agent-service
docker-compose logs -f mcp-server

# Check Dapr sidecar
docker-compose logs -f daprd-todo
```

### Test Service Endpoints

```bash
# Todo Service
curl http://localhost:8001/health

# Agent Service
curl http://localhost:8002/health

# MCP Server
curl http://localhost:8003/api/health

# Frontend
curl http://localhost:3000
```

## Service Ports

| Service | Internal Port | External Port | Description |
|---------|--------------|---------------|-------------|
| PostgreSQL | 5432 | 5432 | Database |
| Dapr Placement | 50000 | 50000 | Dapr control plane |
| Todo Service | 8000 | 8001 | Todo CRUD API |
| Agent Service | 8000 | 8002 | AI Agent API |
| MCP Server | 8000 | 8003 | MCP Protocol Server |
| Frontend | 3000 | 3000 | Next.js Web App |

## Dapr Configuration

Dapr components are configured in `./dapr/components/`:

- `pubsub.yaml`: In-memory pub/sub for development

### Accessing Dapr Sidecars

Each service has a Dapr sidecar accessible at port 3500:

```bash
# Check Dapr health
curl http://localhost:3500/v1.0/health

# Invoke service via Dapr
curl http://localhost:3500/v1.0/invoke/todo-service/method/health
```

## Troubleshooting

### Container Won't Start

```bash
# Check container logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>

# Rebuild and restart
docker-compose up -d --build <service-name>
```

### Database Connection Issues

```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U evo_todo_user -d evo_todo
```

### Dapr Issues

```bash
# Check Dapr placement
docker-compose logs dapr-placement

# Check specific sidecar
docker-compose logs daprd-todo

# Restart Dapr services
docker-compose restart dapr-placement daprd-todo daprd-agent daprd-mcp
```

### MCP Connection Issues

```bash
# Test MCP server directly
curl -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# Check MCP server logs
docker-compose logs -f mcp-server
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v

# Stop specific service
docker-compose stop <service-name>
```

## Development Mode

For development with hot reload:

```bash
# Override command in docker-compose.override.yml
# Or run services locally and only use Docker for infrastructure:

# Start only infrastructure
docker-compose up -d postgres dapr-placement

# Run services locally
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001  # Todo service
uvicorn app.agent_main:app --reload --port 8002  # Agent service
uvicorn mcp_server.server:app --reload --port 8003  # MCP server
```

## Production Considerations

For production deployment:

1. **Use production-grade pub/sub**: Replace in-memory pub/sub with Redis or RabbitMQ
2. **Add secrets management**: Use Docker secrets or external secret stores
3. **Configure resource limits**: Add CPU/memory limits in docker-compose.yml
4. **Enable TLS**: Configure HTTPS for all services
5. **Setup monitoring**: Add Prometheus, Grafana, or similar
6. **Use external database**: Consider managed PostgreSQL service
7. **Implement backup strategy**: Regular database backups
8. **Review security**: Update all secrets, enable authentication

## Useful Commands

```bash
# View resource usage
docker stats

# Clean up unused images
docker system prune -a

# Export logs
docker-compose logs > logs.txt

# Scale services (if configured)
docker-compose up -d --scale worker=3

# Execute command in running container
docker-compose exec todo-service bash
```

## Support

For issues or questions:
1. Check service logs: `docker-compose logs <service-name>`
2. Verify configuration in `.env`
3. Review Dapr component configuration
4. Check network connectivity between services
