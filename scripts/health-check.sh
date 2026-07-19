#!/usr/bin/env bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_service() {
    local name="$1"
    local url="$2"
    local expected="${3:-200}"

    printf "  %-20s " "$name:"

    if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "$expected"; then
        echo -e "${GREEN}✓ UP${NC}"
        return 0
    else
        echo -e "${RED}✗ DOWN${NC}"
        return 1
    fi
}

echo ""
echo -e "${BLUE}=== Service Health Check ===${NC}"
echo ""

TOTAL=0
HEALTHY=0

# PostgreSQL
printf "  %-20s " "PostgreSQL:"
if docker exec confidential-rag-postgres pg_isready -U raguser &> /dev/null; then
    echo -e "${GREEN}✓ UP${NC}"
    HEALTHY=$((HEALTHY + 1))
else
    echo -e "${RED}✗ DOWN${NC}"
fi
TOTAL=$((TOTAL + 1))

# ChromaDB
if check_service "ChromaDB" "http://localhost:8000/api/v1/heartbeat"; then
    HEALTHY=$((HEALTHY + 1))
fi
TOTAL=$((TOTAL + 1))

# Ollama
if check_service "Ollama" "http://localhost:11434/api/tags"; then
    HEALTHY=$((HEALTHY + 1))
fi
TOTAL=$((TOTAL + 1))

# Midnight Network
if check_service "Midnight Network" "http://localhost:8080/health"; then
    HEALTHY=$((HEALTHY + 1))
fi
TOTAL=$((TOTAL + 1))

# FastAPI Backend
if check_service "FastAPI" "http://localhost:8001/health"; then
    HEALTHY=$((HEALTHY + 1))
fi
TOTAL=$((TOTAL + 1))

# Streamlit Frontend
printf "  %-20s " "Streamlit:"
if curl -s http://localhost:8501 &> /dev/null; then
    echo -e "${GREEN}✓ UP${NC}"
    HEALTHY=$((HEALTHY + 1))
else
    echo -e "${RED}✗ DOWN${NC}"
fi
TOTAL=$((TOTAL + 1))

echo ""
echo -e "Status: ${HEALTHY}/${TOTAL} services healthy"
echo ""

if [ $HEALTHY -eq $TOTAL ]; then
    echo -e "${GREEN}All systems operational!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some services are down${NC}"
    echo "Run './scripts/start-all.sh' to start all services"
    exit 1
fi
