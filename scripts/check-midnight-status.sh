#!/usr/bin/env bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

check_cli_tools() {
    echo -e "${BLUE}=== CLI Tools ===${NC}"

    if command -v midnight-cli &> /dev/null; then
        VERSION=$(midnight-cli --version 2>&1 | head -n1 || echo "unknown")
        log_success "midnight-cli: $VERSION"
    else
        log_error "midnight-cli: Not installed"
    fi

    if command -v compact &> /dev/null; then
        VERSION=$(compact --version 2>&1 | head -n1 || echo "unknown")
        log_success "compact-cli: $VERSION"
    else
        log_error "compact-cli: Not installed"
    fi

    echo ""
}

check_network() {
    echo -e "${BLUE}=== Midnight Network ===${NC}"

    # Check if network is running
    if curl -s http://localhost:8080/health &> /dev/null; then
        log_success "Local network: Running (http://localhost:8080)"

        # Try to get network info
        if curl -s http://localhost:8080/api/v1/network/info &> /dev/null; then
            CHAIN_ID=$(curl -s http://localhost:8080/api/v1/network/info | grep -o '"chainId":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
            log_info "  Chain ID: $CHAIN_ID"
        fi
    else
        log_error "Local network: Not running"
        log_info "  Start with: ./scripts/start-local-network.sh"
    fi

    # Check PID file
    if [ -f "$PROJECT_ROOT/.midnight-network.pid" ]; then
        PID=$(cat "$PROJECT_ROOT/.midnight-network.pid")
        if ps -p $PID &> /dev/null; then
            log_info "  Process PID: $PID"
        else
            log_warning "  Stale PID file (process not running)"
        fi
    fi

    echo ""
}

check_contract() {
    echo -e "${BLUE}=== Smart Contract ===${NC}"

    cd "$PROJECT_ROOT/contracts"

    # Check source file
    if [ -f "ConfidentialRAG.compact" ]; then
        SIZE=$(wc -l < ConfidentialRAG.compact)
        log_success "Source: ConfidentialRAG.compact ($SIZE lines)"
    else
        log_error "Source: ConfidentialRAG.compact not found"
    fi

    # Check compiled output
    if [ -f "ConfidentialRAG.compact.js" ]; then
        SIZE=$(stat -f%z "ConfidentialRAG.compact.js" 2>/dev/null || stat -c%s "ConfidentialRAG.compact.js" 2>/dev/null || echo "0")
        SIZE_KB=$((SIZE / 1024))
        log_success "Compiled: ConfidentialRAG.compact.js (${SIZE_KB}KB)"
    else
        log_warning "Compiled: Not found (run ./scripts/compile-contract.sh)"
    fi

    # Check deployment info
    if [ -f "deployment-info.json" ]; then
        log_success "Deployment: Found deployment-info.json"
        if command -v jq &> /dev/null; then
            ADDR=$(jq -r '.contractAddress' deployment-info.json 2>/dev/null || echo "")
            NETWORK=$(jq -r '.network' deployment-info.json 2>/dev/null || echo "")
            if [ -n "$ADDR" ]; then
                log_info "  Address: $ADDR"
                log_info "  Network: $NETWORK"
            fi
        fi
    else
        log_warning "Deployment: Not deployed (run ./scripts/deploy-contract.sh)"
    fi

    echo ""
}

check_docker_services() {
    echo -e "${BLUE}=== Docker Services ===${NC}"

    if ! command -v docker &> /dev/null; then
        log_warning "Docker not installed"
        return
    fi

    # List of expected containers
    CONTAINERS=("confidential-rag-postgres" "confidential-rag-chromadb" "confidential-rag-ollama")

    for container in "${CONTAINERS[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            STATUS=$(docker inspect --format='{{.State.Status}}' "$container")
            HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "n/a")

            if [ "$STATUS" = "running" ]; then
                if [ "$HEALTH" = "healthy" ]; then
                    log_success "$container: Running (healthy)"
                elif [ "$HEALTH" = "n/a" ]; then
                    log_success "$container: Running"
                else
                    log_warning "$container: Running ($HEALTH)"
                fi
            else
                log_warning "$container: $STATUS"
            fi
        else
            log_error "$container: Not running"
        fi
    done

    echo ""
}

check_backend() {
    echo -e "${BLUE}=== Backend Services ===${NC}"

    # FastAPI backend
    if curl -s http://localhost:8001/health &> /dev/null; then
        log_success "FastAPI: Running (http://localhost:8001)"

        # Check version
        VERSION=$(curl -s http://localhost:8001/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "")
        if [ -n "$VERSION" ]; then
            log_info "  Version: $VERSION"
        fi
    else
        log_error "FastAPI: Not running"
    fi

    # Streamlit frontend
    if curl -s http://localhost:8501 &> /dev/null; then
        log_success "Streamlit: Running (http://localhost:8501)"
    else
        log_error "Streamlit: Not running"
    fi

    echo ""
}

show_summary() {
    echo -e "${BLUE}=== Quick Start Commands ===${NC}"
    echo "  Setup Midnight:    ./scripts/setup-midnight.sh"
    echo "  Start network:     ./scripts/start-local-network.sh"
    echo "  Compile contract:  ./scripts/compile-contract.sh"
    echo "  Deploy contract:   ./scripts/deploy-contract.sh"
    echo "  Start all:         ./scripts/start-all.sh"
    echo "  Run tests:         ./scripts/run-tests.sh"
    echo ""
}

main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Midnight Development Status Check       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
    echo ""

    check_cli_tools
    check_network
    check_contract
    check_docker_services
    check_backend
    show_summary
}

main "$@"
