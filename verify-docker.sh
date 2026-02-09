#!/bin/bash
# Docker Configuration Verification Script

echo "🔍 Evo-TODO Docker Configuration Verification"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo "📦 Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is installed: $(docker --version)"
else
    echo -e "${RED}✗${NC} Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
echo "📦 Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose is installed: $(docker-compose --version)"
else
    echo -e "${RED}✗${NC} Docker Compose is not installed"
    exit 1
fi

echo ""
echo "📁 Checking required files..."

# Check Dockerfiles
files=(
    "backend/Dockerfile.todo-service"
    "backend/Dockerfile.agent-service"
    "backend/mcp_server/Dockerfile"
    "frontend/Dockerfile"
    "docker-compose.yml"
    "dapr/components/pubsub.yaml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${RED}✗${NC} $file is missing"
    fi
done

echo ""
echo "🔐 Checking environment configuration..."

if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    # Check required variables
    required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "JWT_SECRET_KEY" "GEMINI_API_KEY" "MCP_INTERNAL_SECRET")

    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env; then
            value=$(grep "^${var}=" .env | cut -d'=' -f2)
            if [ -z "$value" ] || [[ "$value" == *"your-"* ]] || [[ "$value" == *"change"* ]]; then
                echo -e "${YELLOW}⚠${NC}  $var is set but needs to be updated"
            else
                echo -e "${GREEN}✓${NC} $var is configured"
            fi
        else
            echo -e "${RED}✗${NC} $var is missing"
        fi
    done
else
    echo -e "${YELLOW}⚠${NC}  .env file not found. Copy .env.example to .env and configure it."
    echo "    Run: cp .env.example .env"
fi

echo ""
echo "🏗️  Validating docker-compose.yml..."
if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} docker-compose.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.yml has errors"
    docker-compose config
    exit 1
fi

echo ""
echo "📊 Service configuration summary:"
echo "  - PostgreSQL: Port 5432"
echo "  - Todo Service: Port 8001"
echo "  - Agent Service: Port 8002"
echo "  - MCP Server: Port 8003"
echo "  - Frontend: Port 3000"
echo "  - Dapr Placement: Port 50000"

echo ""
echo "🎯 Next steps:"
echo "  1. Configure .env file if not done"
echo "  2. Build images: docker-compose build"
echo "  3. Start services: docker-compose up -d"
echo "  4. Check health: curl http://localhost:8001/health"
echo ""
echo "📖 See DOCKER_DEPLOYMENT.md for detailed instructions"
