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
CONTRACTS_DIR="$PROJECT_ROOT/contracts"

# Default network
NETWORK="${1:-local}"

check_network() {
    log_info "Checking network connectivity..."

    if [ "$NETWORK" = "local" ]; then
        if ! curl -s http://localhost:8080/health &> /dev/null; then
            log_error "Local network not running!"
            log_info "Start it with: ./scripts/start-local-network.sh"
            exit 1
        fi
        log_success "Local network is running"
    else
        log_info "Using network: $NETWORK"
    fi
}

compile_if_needed() {
    cd "$CONTRACTS_DIR"

    if [ ! -f "ConfidentialRAG.compact.js" ]; then
        log_warning "Compiled contract not found, compiling..."
        ./scripts/compile-contract.sh
    else
        log_info "Using existing compiled contract"
    fi
}

deploy_contract() {
    cd "$CONTRACTS_DIR"

    log_info "Deploying contract to $NETWORK network..."
    echo ""

    # Deploy with verbose output
    if compact deploy --network "$NETWORK" 2>&1 | tee deployment.log; then
        echo ""
        log_success "Contract deployed successfully!"

        # Extract and display contract address
        if grep -q "Contract address:" deployment.log; then
            CONTRACT_ADDR=$(grep "Contract address:" deployment.log | awk '{print $3}')
            echo ""
            log_info "Contract Address: $CONTRACT_ADDR"

            # Save to .env file
            ENV_FILE="$PROJECT_ROOT/backend/.env"
            if [ -f "$ENV_FILE" ]; then
                # Update existing or append
                if grep -q "MIDNIGHT_CONTRACT_ADDRESS=" "$ENV_FILE"; then
                    sed -i "s/MIDNIGHT_CONTRACT_ADDRESS=.*/MIDNIGHT_CONTRACT_ADDRESS=$CONTRACT_ADDR/" "$ENV_FILE"
                else
                    echo "MIDNIGHT_CONTRACT_ADDRESS=$CONTRACT_ADDR" >> "$ENV_FILE"
                fi
                log_info "Updated backend/.env with contract address"
            fi

            # Save deployment info
            cat > deployment-info.json << EOF
{
  "network": "$NETWORK",
  "contractAddress": "$CONTRACT_ADDR",
  "deployedAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "deployer": "$(whoami)"
}
EOF
            log_info "Saved deployment info to deployment-info.json"
        fi

        echo ""
        log_info "Next steps:"
        log_info "  1. Update backend config with contract address"
        log_info "  2. Start backend:  cd backend && python run.py"
        log_info "  3. Test API:       python backend/test_api.py"

    else
        echo ""
        log_error "Deployment failed!"
        log_info "Check deployment.log for details"
        exit 1
    fi
}

main() {
    echo ""
    log_info "=== Compact Contract Deployment ==="
    log_info "Network: $NETWORK"
    echo ""

    check_network
    compile_if_needed
    echo ""
    deploy_contract
    echo ""
}

main "$@"
