#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONTRACTS_DIR="$PROJECT_ROOT/contracts"

# Logging functions
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

# Progress indicator
show_progress() {
    local msg="$1"
    echo -ne "${BLUE}[....] ${NC}${msg}"
}

update_progress() {
    local status="$1"
    if [ "$status" = "ok" ]; then
        echo -e "\r${GREEN}[ OK ]${NC}"
    else
        echo -e "\r${RED}[FAIL]${NC}"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=0

    # Check Node.js
    show_progress "Checking Node.js (v18+)... "
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
        if [ "$NODE_VERSION" -ge 18 ]; then
            update_progress "ok"
            log_info "  Found Node.js $(node -v)"
        else
            update_progress "fail"
            log_error "  Node.js 18+ required, found v$NODE_VERSION"
            missing=1
        fi
    else
        update_progress "fail"
        log_error "  Node.js not found. Install from https://nodejs.org"
        missing=1
    fi

    # Check npm
    show_progress "Checking npm... "
    if command -v npm &> /dev/null; then
        update_progress "ok"
        log_info "  Found npm $(npm -v)"
    else
        update_progress "fail"
        log_error "  npm not found"
        missing=1
    fi

    # Check Git
    show_progress "Checking Git... "
    if command -v git &> /dev/null; then
        update_progress "ok"
    else
        update_progress "fail"
        log_warning "  Git not found (optional)"
    fi

    if [ $missing -ne 0 ]; then
        log_error "Missing required prerequisites. Please install them and try again."
        exit 1
    fi

    log_success "All prerequisites met!"
}

# Install Midnight CLI
install_midnight_cli() {
    log_info "Installing Midnight CLI tools..."

    show_progress "Installing @midnight-ntwrk/compact-cli... "
    if npm install -g @midnight-ntwrk/compact-cli &> /dev/null; then
        update_progress "ok"
    else
        update_progress "fail"
        log_error "Failed to install compact-cli"
        exit 1
    fi

    show_progress "Installing @midnight-ntwrk/midnight-cli... "
    if npm install -g @midnight-ntwrk/midnight-cli &> /dev/null; then
        update_progress "ok"
    else
        update_progress "fail"
        log_error "Failed to install midnight-cli"
        exit 1
    fi

    log_success "Midnight CLI tools installed!"
}

# Initialize Midnight development environment
init_midnight() {
    log_info "Initializing Midnight development environment..."

    cd "$PROJECT_ROOT"

    # Check if already initialized
    if [ -f ".midnight/config.json" ]; then
        log_warning "Midnight already initialized, skipping..."
        return
    fi

    show_progress "Initializing Midnight... "
    if midnight-cli init --yes &> /dev/null; then
        update_progress "ok"
        log_success "Midnight initialized!"
    else
        update_progress "fail"
        log_error "Failed to initialize Midnight"
        exit 1
    fi
}

# Install project dependencies
install_dependencies() {
    log_info "Installing project dependencies..."

    cd "$PROJECT_ROOT"

    # Create package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        log_info "Creating package.json..."
        cat > package.json << 'EOF'
{
  "name": "confidential-rag",
  "version": "1.0.0",
  "description": "Privacy-Preserving Document Q&A System using Zero-Knowledge Proofs",
  "scripts": {
    "compile": "cd contracts && compact compile ConfidentialRAG.compact",
    "deploy:local": "cd contracts && compact deploy --network local",
    "deploy:testnet": "cd contracts && compact deploy --network testnet",
    "test:contract": "cd contracts && compact test",
    "start:network": "./scripts/start-local-network.sh",
    "midnight:status": "./scripts/check-midnight-status.sh"
  },
  "dependencies": {
    "@midnight-ntwrk/compact-cli": "^0.1.0",
    "@midnight-ntwrk/midnight-cli": "^0.1.0"
  },
  "devDependencies": {},
  "author": "ConfidentialRAG Team",
  "license": "MIT"
}
EOF
    fi

    show_progress "Installing npm dependencies... "
    if npm install &> /dev/null; then
        update_progress "ok"
    else
        update_progress "fail"
        log_error "Failed to install npm dependencies"
        exit 1
    fi

    log_success "Dependencies installed!"
}

# Compile Compact contract
compile_contract() {
    log_info "Compiling Compact contract..."

    cd "$CONTRACTS_DIR"

    if [ ! -f "ConfidentialRAG.compact" ]; then
        log_error "Contract file not found: ConfidentialRAG.compact"
        exit 1
    fi

    show_progress "Compiling ConfidentialRAG.compact... "
    if compact compile ConfidentialRAG.compact &> /dev/null; then
        update_progress "ok"
        log_success "Contract compiled successfully!"

        if [ -f "ConfidentialRAG.compact.js" ]; then
            log_info "  Output: ConfidentialRAG.compact.js"
        fi
    else
        update_progress "fail"
        log_error "Contract compilation failed"
        log_info "Running with verbose output..."
        compact compile ConfidentialRAG.compact
        exit 1
    fi
}

# Deploy contract to local network
deploy_contract() {
    log_info "Deploying contract to local network..."

    # Check if local network is running
    if ! curl -s http://localhost:8080/health &> /dev/null; then
        log_warning "Local Midnight network not running"
        log_info "Start it with: ./scripts/start-local-network.sh"
        log_info "Skipping deployment..."
        return
    fi

    cd "$CONTRACTS_DIR"

    show_progress "Deploying ConfidentialRAG contract... "
    if compact deploy --network local &> deployment.log 2>&1; then
        update_progress "ok"
        log_success "Contract deployed to local network!"

        # Extract contract address if available
        if grep -q "Contract address:" deployment.log; then
            CONTRACT_ADDR=$(grep "Contract address:" deployment.log | awk '{print $3}')
            log_info "  Contract address: $CONTRACT_ADDR"
        fi
    else
        update_progress "fail"
        log_warning "Deployment failed (is network running?)"
        log_info "Run './scripts/start-local-network.sh' first"
    fi
}

# Main setup flow
main() {
    echo ""
    log_info "=== Midnight Development Environment Setup ==="
    echo ""

    check_prerequisites
    echo ""

    install_midnight_cli
    echo ""

    init_midnight
    echo ""

    install_dependencies
    echo ""

    compile_contract
    echo ""

    deploy_contract
    echo ""

    log_success "=== Midnight setup complete! ==="
    echo ""
    log_info "Next steps:"
    log_info "  1. Start local network:  ./scripts/start-local-network.sh"
    log_info "  2. Deploy contract:      npm run deploy:local"
    log_info "  3. Check status:         npm run midnight:status"
    echo ""
}

# Run main function
main "$@"
