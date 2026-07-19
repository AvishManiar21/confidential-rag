#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "Starting all services..."
echo ""

# Start Docker services
log_info "Starting Docker containers..."
cd "$PROJECT_ROOT"
docker-compose up -d

echo ""
log_info "Waiting for services to be ready..."
sleep 10

# Check Docker services
log_info "Checking Docker services..."
docker-compose ps

echo ""

# Start Midnight network if not running
if ! curl -s http://localhost:8080/health &> /dev/null; then
    log_info "Starting Midnight network..."
    cd "$SCRIPT_DIR"
    ./start-local-network.sh
else
    log_success "Midnight network already running"
fi

echo ""
log_success "All services started!"
echo ""
log_info "Service endpoints:"
log_info "  PostgreSQL:  http://localhost:5432"
log_info "  ChromaDB:    http://localhost:8000"
log_info "  Ollama:      http://localhost:11434"
log_info "  FastAPI:     http://localhost:8001"
log_info "  Streamlit:   http://localhost:8501"
log_info "  Midnight:    http://localhost:8080"
echo ""
log_info "Check status: ./scripts/check-midnight-status.sh"
echo ""
