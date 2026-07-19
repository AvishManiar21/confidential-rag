#!/usr/bin/env bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Confirm before reset
read -p "This will delete all data in PostgreSQL and ChromaDB. Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Cancelled"
    exit 0
fi

log_warning "Resetting databases..."
echo ""

cd "$PROJECT_ROOT"

# Stop services
log_info "Stopping services..."
docker-compose stop postgres chromadb

# Remove volumes
log_info "Removing database volumes..."
docker-compose rm -f -v postgres chromadb

# Remove volume data
log_info "Cleaning volume data..."
docker volume rm confidential-rag_postgres-data 2>/dev/null || true
docker volume rm confidential-rag_chroma-data 2>/dev/null || true

# Restart services
log_info "Restarting services..."
docker-compose up -d postgres chromadb

# Wait for services
log_info "Waiting for services to be ready..."
sleep 10

# Reinitialize database
log_info "Reinitializing PostgreSQL schema..."
cd "$PROJECT_ROOT/backend"
if [ -d "venv" ]; then
    source venv/bin/activate
    python setup_db.py
else
    python3 setup_db.py
fi

echo ""
log_success "Database reset complete!"
echo ""
log_info "Next steps:"
log_info "  1. Upload demo data:  python demo/upload-demo-data.py"
log_info "  2. Run queries:       python demo/run-demo-queries.py"
echo ""
