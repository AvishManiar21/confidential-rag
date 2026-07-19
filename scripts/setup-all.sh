#!/usr/bin/env bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

show_banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                  ║${NC}"
    echo -e "${CYAN}║       ConfidentialRAG Complete Setup             ║${NC}"
    echo -e "${CYAN}║                                                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_prerequisites() {
    log_step "Checking prerequisites..."

    local missing=()

    if ! command -v docker &> /dev/null; then
        missing+=("Docker")
    fi

    if ! command -v docker-compose &> /dev/null; then
        missing+=("Docker Compose")
    fi

    if ! command -v node &> /dev/null; then
        missing+=("Node.js")
    fi

    if ! command -v python3 &> /dev/null; then
        missing+=("Python 3")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing prerequisites: ${missing[*]}"
        log_info "Please install missing tools and try again"
        exit 1
    fi

    log_success "All prerequisites found!"
}

setup_midnight() {
    log_step "Setting up Midnight development environment..."

    cd "$SCRIPT_DIR"
    if [ -x "setup-midnight.sh" ]; then
        ./setup-midnight.sh
    else
        log_error "setup-midnight.sh not found or not executable"
        exit 1
    fi
}

setup_python_env() {
    log_step "Setting up Python environment..."

    cd "$PROJECT_ROOT/backend"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate and install dependencies
    log_info "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt > /dev/null

    log_success "Python environment ready!"
}

start_docker_services() {
    log_step "Starting Docker services..."

    cd "$PROJECT_ROOT"

    log_info "Starting PostgreSQL, ChromaDB, and Ollama..."
    docker-compose up -d postgres chromadb ollama

    log_info "Waiting for services to be healthy..."
    local waited=0
    while [ $waited -lt 60 ]; do
        if docker-compose ps | grep -q "healthy"; then
            log_success "Docker services are ready!"
            return 0
        fi
        sleep 2
        waited=$((waited + 2))
        echo -n "."
    done

    echo ""
    log_warning "Services may not be fully ready, continuing..."
}

pull_ollama_model() {
    log_step "Pulling Ollama model..."

    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        log_warning "Ollama not running, skipping model pull"
        return
    fi

    log_info "Pulling llama2 model (this may take a while)..."
    docker exec confidential-rag-ollama ollama pull llama2

    log_success "Ollama model ready!"
}

initialize_database() {
    log_step "Initializing database..."

    cd "$PROJECT_ROOT/backend"

    source venv/bin/activate
    python setup_db.py

    log_success "Database initialized!"
}

compile_and_deploy() {
    log_step "Compiling and deploying smart contract..."

    cd "$SCRIPT_DIR"

    # Compile contract
    ./compile-contract.sh

    # Start network
    log_info "Starting Midnight local network..."
    ./start-local-network.sh

    # Deploy contract
    ./deploy-contract.sh local

    log_success "Contract deployed!"
}

show_next_steps() {
    echo ""
    log_success "=== Setup Complete! ==="
    echo ""
    log_info "Services Status:"
    log_info "  PostgreSQL:  http://localhost:5432"
    log_info "  ChromaDB:    http://localhost:8000"
    log_info "  Ollama:      http://localhost:11434"
    log_info "  Midnight:    http://localhost:8080"
    echo ""
    log_info "Next steps:"
    log_info "  1. Start all services:  ./scripts/start-all.sh"
    log_info "  2. Load demo data:      python demo/upload-demo-data.py"
    log_info "  3. Run demo queries:    python demo/run-demo-queries.py"
    log_info "  4. Access frontend:     http://localhost:8501"
    echo ""
    log_info "Useful commands:"
    log_info "  Check status:           ./scripts/check-midnight-status.sh"
    log_info "  Run tests:              ./scripts/run-tests.sh"
    log_info "  Stop all:               ./scripts/stop-all.sh"
    echo ""
}

rollback_on_error() {
    log_error "Setup failed! Rolling back..."

    cd "$PROJECT_ROOT"
    docker-compose down &> /dev/null || true

    if [ -f ".midnight-network.pid" ]; then
        kill "$(cat .midnight-network.pid)" &> /dev/null || true
        rm .midnight-network.pid
    fi

    log_info "Rollback complete. Fix the issue and try again."
    exit 1
}

main() {
    # Set error handler
    trap rollback_on_error ERR

    show_banner
    check_prerequisites
    echo ""

    setup_midnight
    echo ""

    setup_python_env
    echo ""

    start_docker_services
    echo ""

    pull_ollama_model
    echo ""

    initialize_database
    echo ""

    compile_and_deploy
    echo ""

    show_next_steps
}

main "$@"
