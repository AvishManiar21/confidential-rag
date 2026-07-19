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
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTRACTS_DIR="$PROJECT_ROOT/contracts"

compile_contract() {
    log_info "Compiling Compact contract..."

    cd "$CONTRACTS_DIR"

    # Check if contract exists
    if [ ! -f "ConfidentialRAG.compact" ]; then
        log_error "Contract not found: ConfidentialRAG.compact"
        exit 1
    fi

    # Check if compact-cli is installed
    if ! command -v compact &> /dev/null; then
        log_error "compact-cli not found. Run ./scripts/setup-midnight.sh first"
        exit 1
    fi

    # Compile
    log_info "Running: compact compile ConfidentialRAG.compact"

    if compact compile ConfidentialRAG.compact; then
        log_success "Contract compiled successfully!"
        echo ""

        # List outputs
        if [ -f "ConfidentialRAG.compact.js" ]; then
            log_info "Output files:"
            ls -lh ConfidentialRAG.compact.* | awk '{print "  " $9 " (" $5 ")"}'
        fi

        echo ""
        log_info "Next steps:"
        log_info "  1. Start network: ./scripts/start-local-network.sh"
        log_info "  2. Deploy:        ./scripts/deploy-contract.sh"
    else
        log_error "Compilation failed!"
        exit 1
    fi
}

main() {
    echo ""
    log_info "=== Compact Contract Compiler ==="
    echo ""
    compile_contract
    echo ""
}

main "$@"
