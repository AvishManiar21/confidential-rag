# ConfidentialRAG Development Scripts

Production-quality automation scripts for Midnight blockchain development, service management, and testing.

## Overview

These scripts provide a complete development environment for the ConfidentialRAG project, handling:

- Midnight CLI installation and configuration
- Smart contract compilation and deployment
- Docker service orchestration
- Database management
- Health monitoring
- Automated testing

## Prerequisites

- **Node.js 18+** - Required for Midnight CLI
- **Docker & Docker Compose** - For backend services
- **Python 3.10+** - For backend and demo scripts
- **Git** - For version control (optional)
- **Bash** - Unix-like shell (Git Bash on Windows)

## Quick Start

```bash
# Complete setup in one command
./scripts/setup-all.sh

# Or step by step:
./scripts/setup-midnight.sh       # Install Midnight CLI
./scripts/start-all.sh             # Start all services
./scripts/health-check.sh          # Verify everything is running
```

## Scripts Reference

### Midnight Setup Scripts

#### `setup-midnight.sh`

**Purpose**: Install Midnight CLI tools, compile contract, and deploy to local network.

**What it does**:
1. Checks prerequisites (Node.js, npm, Git)
2. Installs `@midnight-ntwrk/compact-cli` globally
3. Installs `@midnight-ntwrk/midnight-cli` globally
4. Initializes Midnight development environment
5. Installs project npm dependencies
6. Compiles Compact contract
7. Deploys contract to local network (if running)

**Usage**:
```bash
./scripts/setup-midnight.sh
```

**Output**:
- Installed CLI tools
- Compiled contract (`.compact.js` files)
- Deployment info (if network running)

**Troubleshooting**:
- **"Node.js 18+ required"**: Upgrade Node.js from https://nodejs.org
- **"npm install failed"**: Check internet connection, clear npm cache
- **"Deployment failed"**: Start network first with `./scripts/start-local-network.sh`

---

#### `start-local-network.sh`

**Purpose**: Start Midnight local development blockchain node.

**What it does**:
1. Checks if network is already running
2. Launches `midnight-cli start-network` in background
3. Waits for network health endpoint to respond
4. Saves process PID for cleanup

**Usage**:
```bash
./scripts/start-local-network.sh
```

**Output**:
- Network running on `http://localhost:8080`
- Log file: `midnight-network.log`
- PID file: `.midnight-network.pid`

**Troubleshooting**:
- **"Already running"**: Stop with `kill $(cat .midnight-network.pid)`
- **"Failed to start"**: Check `midnight-network.log` for errors
- **Port conflict**: Another process using port 8080

---

#### `compile-contract.sh`

**Purpose**: Compile Compact smart contract from source.

**What it does**:
1. Validates `ConfidentialRAG.compact` exists
2. Runs `compact compile` command
3. Lists generated output files

**Usage**:
```bash
./scripts/compile-contract.sh
```

**Input**: `contracts/ConfidentialRAG.compact`

**Output**: `contracts/ConfidentialRAG.compact.js`

**Troubleshooting**:
- **"Contract not found"**: Ensure you're in project root
- **Syntax errors**: Check contract code, review Compact docs
- **CLI not found**: Run `./scripts/setup-midnight.sh` first

---

#### `deploy-contract.sh`

**Purpose**: Deploy compiled contract to Midnight network (local or testnet).

**What it does**:
1. Checks network connectivity
2. Compiles contract if not already compiled
3. Deploys to specified network
4. Saves contract address to `.env` and `deployment-info.json`

**Usage**:
```bash
./scripts/deploy-contract.sh           # Deploy to local
./scripts/deploy-contract.sh local     # Deploy to local
./scripts/deploy-contract.sh testnet   # Deploy to testnet
```

**Output**:
- Contract address
- `contracts/deployment-info.json`
- Updated `backend/.env`

**Troubleshooting**:
- **"Network not running"**: Start with `./scripts/start-local-network.sh`
- **"Deployment failed"**: Check account has funds (testnet faucet)
- **"Transaction timeout"**: Network congestion, retry

---

#### `check-midnight-status.sh`

**Purpose**: Comprehensive status check of all Midnight services.

**What it does**:
- Checks CLI tools installed
- Verifies network is running
- Validates contract compilation
- Checks deployment status
- Lists Docker container health
- Shows backend service status

**Usage**:
```bash
./scripts/check-midnight-status.sh
```

**Output**: Color-coded status report with ✓/✗ indicators

---

### Development Scripts

#### `setup-all.sh`

**Purpose**: One-command setup for entire project.

**What it does**:
1. Checks all prerequisites
2. Runs `setup-midnight.sh`
3. Creates Python virtual environment
4. Installs Python dependencies
5. Starts Docker services
6. Pulls Ollama LLM model
7. Initializes PostgreSQL database
8. Compiles and deploys contract

**Usage**:
```bash
./scripts/setup-all.sh
```

**Duration**: 10-15 minutes (first run)

**Rollback**: Automatically rolls back on error

---

#### `start-all.sh`

**Purpose**: Start all services (Docker + Midnight).

**What it does**:
1. Starts Docker Compose stack
2. Waits for services to be healthy
3. Starts Midnight network if not running

**Usage**:
```bash
./scripts/start-all.sh
```

**Services started**:
- PostgreSQL (port 5432)
- ChromaDB (port 8000)
- Ollama (port 11434)
- FastAPI backend (port 8001)
- Streamlit frontend (port 8501)
- Midnight network (port 8080)

---

#### `stop-all.sh`

**Purpose**: Stop all services gracefully.

**What it does**:
1. Stops Docker Compose stack
2. Kills Midnight network process
3. Cleans up PID files

**Usage**:
```bash
./scripts/stop-all.sh
```

---

#### `reset-db.sh`

**Purpose**: Reset PostgreSQL and ChromaDB to clean state.

**What it does**:
1. Stops database containers
2. Removes Docker volumes
3. Restarts containers
4. Re-runs database schema migration

**Usage**:
```bash
./scripts/reset-db.sh
# Confirms before proceeding
```

**Warning**: Deletes all documents and embeddings!

---

#### `health-check.sh`

**Purpose**: Quick health check of all services.

**What it does**:
- Pings each service endpoint
- Reports UP/DOWN status
- Counts healthy vs total services

**Usage**:
```bash
./scripts/health-check.sh
```

**Exit codes**:
- `0`: All healthy
- `1`: Some services down

---

#### `run-tests.sh`

**Purpose**: Run all test suites.

**What it does**:
1. Checks backend is running
2. Runs backend API tests
3. Runs contract tests
4. Runs E2E tests
5. Reports summary

**Usage**:
```bash
./scripts/run-tests.sh
```

**Exit codes**:
- `0`: All tests passed
- `1`: Some tests failed

---

## Common Workflows

### First Time Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd confidential-rag

# 2. Complete setup
./scripts/setup-all.sh

# 3. Verify everything is running
./scripts/check-midnight-status.sh
```

### Daily Development

```bash
# Start services
./scripts/start-all.sh

# Check status
./scripts/health-check.sh

# Make code changes...

# Recompile and redeploy contract
./scripts/compile-contract.sh
./scripts/deploy-contract.sh

# Run tests
./scripts/run-tests.sh

# Stop when done
./scripts/stop-all.sh
```

### Troubleshooting

```bash
# Full status check
./scripts/check-midnight-status.sh

# View logs
docker-compose logs -f backend
cat midnight-network.log

# Reset databases
./scripts/reset-db.sh

# Full restart
./scripts/stop-all.sh
./scripts/start-all.sh
```

### Testing & Demo

```bash
# Upload demo data
python demo/upload-demo-data.py

# Run demo queries
python demo/run-demo-queries.py

# Run E2E tests
python demo/test-e2e.py

# Or use make commands
make demo
make test
```

## Script Features

### Error Handling

All scripts include:
- Exit on error (`set -euo pipefail`)
- Prerequisite validation
- Rollback on failure (where applicable)
- Detailed error messages

### Color-Coded Output

- **Blue**: Informational messages
- **Green**: Success indicators
- **Yellow**: Warnings
- **Red**: Errors

### Progress Indicators

- Spinner during long operations
- Real-time status updates
- Time estimates for setup

### Logging

- Each script logs to console
- Network logs: `midnight-network.log`
- Deployment logs: `contracts/deployment.log`
- Docker logs: `docker-compose logs`

## Windows Compatibility

These scripts are designed for Unix shells (bash). On Windows:

**Option 1: Git Bash**
- Recommended for Windows users
- Comes with Git for Windows
- Run scripts normally

**Option 2: WSL (Windows Subsystem for Linux)**
- Full Linux environment
- Best compatibility

**Option 3: PowerShell equivalents**
- Not provided in this release
- Can be adapted from bash scripts

## Environment Variables

Scripts respect these environment variables:

- `BACKEND_URL`: Backend API endpoint (default: `http://localhost:8001`)
- `MIDNIGHT_RPC_URL`: Midnight RPC endpoint (default: `http://localhost:8080`)
- `DATABASE_URL`: PostgreSQL connection string
- `CHROMA_URL`: ChromaDB endpoint

## Makefile Integration

All scripts can be run via Makefile:

```bash
make setup          # ./scripts/setup-midnight.sh
make start          # ./scripts/start-all.sh
make stop           # ./scripts/stop-all.sh
make status         # ./scripts/check-midnight-status.sh
make health         # ./scripts/health-check.sh
make compile        # ./scripts/compile-contract.sh
make deploy         # ./scripts/deploy-contract.sh
make test           # ./scripts/run-tests.sh
make reset          # ./scripts/reset-db.sh
```

## CI/CD Integration

Scripts are CI-friendly:

- Non-interactive mode
- Clear exit codes
- Structured output
- No user prompts (use `--yes` flags)

Example GitHub Actions:

```yaml
- name: Setup Midnight
  run: ./scripts/setup-all.sh

- name: Run tests
  run: ./scripts/run-tests.sh
```

## Security Notes

- **Never commit** `.env` files with credentials
- **Review deployment logs** before committing
- **Use testnet** for public repositories
- **Rotate keys** regularly
- **PID files** are gitignored

## Performance Tips

- **Parallel Docker builds**: `docker-compose build --parallel`
- **Skip Ollama pull**: If model already downloaded
- **Local npm cache**: Speeds up repeated installs
- **Docker volumes**: Persist data between restarts

## Support & Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in `docker-compose.yml` |
| Permission denied | Run with `chmod +x scripts/*.sh` |
| Network timeout | Check firewall, increase timeout values |
| Out of disk space | Run `docker system prune` |
| Contract compilation fails | Update `@midnight-ntwrk/compact-cli` |

### Debug Mode

Enable verbose output:

```bash
# Add to any script
set -x  # Print commands before execution
```

### Getting Help

1. Check script output for error messages
2. Review logs: `midnight-network.log`, `docker-compose logs`
3. Run status check: `./scripts/check-midnight-status.sh`
4. Consult [Midnight Documentation](https://docs.midnight.network)
5. Open GitHub issue with error output

## Contributing

When adding new scripts:

1. Follow existing naming conventions
2. Include color-coded output
3. Add error handling
4. Document in this README
5. Test on clean environment
6. Update Makefile targets

## License

MIT License - see LICENSE file for details.
