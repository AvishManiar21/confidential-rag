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

log_info "Stopping all services..."
echo ""

# Stop Docker services
log_info "Stopping Docker containers..."
cd "$PROJECT_ROOT"
docker-compose down

echo ""

# Stop Midnight network
if [ -f "$PROJECT_ROOT/.midnight-network.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/.midnight-network.pid")
    if ps -p $PID &> /dev/null; then
        log_info "Stopping Midnight network (PID: $PID)..."
        kill $PID
        rm "$PROJECT_ROOT/.midnight-network.pid"
        log_success "Midnight network stopped"
    else
        log_warning "Midnight network process not found, cleaning up PID file"
        rm "$PROJECT_ROOT/.midnight-network.pid"
    fi
else
    log_info "Midnight network not running"
fi

echo ""
log_success "All services stopped!"
echo ""
