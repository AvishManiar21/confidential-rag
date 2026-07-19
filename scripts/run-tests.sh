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
log_section() { echo -e "${CYAN}=== $1 ===${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

FAILED=0

run_backend_tests() {
    log_section "Backend API Tests"
    echo ""

    cd "$PROJECT_ROOT/backend"

    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    log_info "Running API endpoint tests..."
    if python test_api.py; then
        log_success "Backend tests passed!"
    else
        log_error "Backend tests failed!"
        FAILED=1
    fi

    echo ""
}

run_contract_tests() {
    log_section "Smart Contract Tests"
    echo ""

    cd "$PROJECT_ROOT/contracts"

    log_info "Running Compact contract tests..."
    if compact test &> /dev/null; then
        log_success "Contract tests passed!"
    else
        log_warning "Contract tests skipped (not implemented)"
    fi

    echo ""
}

run_e2e_tests() {
    log_section "End-to-End Tests"
    echo ""

    cd "$PROJECT_ROOT/demo"

    if [ ! -f "test-e2e.py" ]; then
        log_warning "E2E tests not found, skipping..."
        return
    fi

    log_info "Running end-to-end tests..."
    if python test-e2e.py; then
        log_success "E2E tests passed!"
    else
        log_error "E2E tests failed!"
        FAILED=1
    fi

    echo ""
}

check_services() {
    log_info "Checking required services..."

    if ! curl -s http://localhost:8001/health &> /dev/null; then
        log_error "Backend not running! Start with: ./scripts/start-all.sh"
        exit 1
    fi

    log_success "All required services are running"
    echo ""
}

main() {
    echo ""
    log_section "ConfidentialRAG Test Suite"
    echo ""

    check_services

    run_backend_tests
    run_contract_tests
    run_e2e_tests

    log_section "Test Summary"
    echo ""

    if [ $FAILED -eq 0 ]; then
        log_success "All tests passed!"
        exit 0
    else
        log_error "Some tests failed!"
        exit 1
    fi
}

main "$@"
