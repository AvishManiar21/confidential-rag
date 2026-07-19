#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if network is already running
check_running() {
    if curl -s http://localhost:8080/health &> /dev/null; then
        log_warning "Midnight network already running at http://localhost:8080"
        log_info "To restart, run: ./scripts/stop-all.sh && ./scripts/start-local-network.sh"
        exit 0
    fi
}

# Start Midnight local development network
start_network() {
    log_info "Starting Midnight local development network..."

    # Check if midnight-cli is installed
    if ! command -v midnight-cli &> /dev/null; then
        log_error "midnight-cli not found. Run ./scripts/setup-midnight.sh first"
        exit 1
    fi

    # Start network in background
    log_info "Launching network daemon..."
    nohup midnight-cli start-network --local > midnight-network.log 2>&1 &
    NETWORK_PID=$!

    # Save PID for later shutdown
    echo $NETWORK_PID > .midnight-network.pid

    log_info "Waiting for network to start (PID: $NETWORK_PID)..."

    # Wait for network to be ready (max 60 seconds)
    local waited=0
    while [ $waited -lt 60 ]; do
        if curl -s http://localhost:8080/health &> /dev/null; then
            log_success "Network is ready!"
            log_info "  RPC endpoint: http://localhost:8080"
            log_info "  Network log:  midnight-network.log"
            log_info "  PID file:     .midnight-network.pid"
            return 0
        fi
        sleep 2
        waited=$((waited + 2))
        echo -n "."
    done

    echo ""
    log_error "Network failed to start within 60 seconds"
    log_info "Check midnight-network.log for errors"
    exit 1
}

# Main
main() {
    echo ""
    log_info "=== Starting Midnight Local Network ==="
    echo ""

    check_running
    start_network

    echo ""
    log_success "=== Midnight network started successfully ==="
    echo ""
    log_info "To stop: kill \$(cat .midnight-network.pid) or ./scripts/stop-all.sh"
    echo ""
}

main "$@"
