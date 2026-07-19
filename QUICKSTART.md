# ConfidentialRAG - Quick Start

Get up and running in 5 minutes!

## Prerequisites

- Node.js 18+
- Docker Desktop (running)
- Python 3.10+
- Git

## One-Command Setup

```bash
# Complete automated setup (10-15 minutes)
./scripts/setup-all.sh
```

This installs everything:
- Midnight CLI tools
- Python dependencies
- Docker services
- Database initialization
- Smart contract compilation & deployment

## Start Services

```bash
# Start all services
make start

# Or
./scripts/start-all.sh
```

## Upload Demo Data

```bash
# Upload 15 medical research abstracts
make demo-upload

# Or
python demo/upload-demo-data.py
```

## Run Demo Queries

```bash
# Execute 10 sample queries
make demo-query

# Or
python demo/run-demo-queries.py
```

## Access UI

Open in browser: **http://localhost:8501**

## Run Tests

```bash
# Complete test suite
make test

# Or end-to-end tests only
python demo/test-e2e.py
```

## Check Status

```bash
# Comprehensive status
make status

# Quick health check
make health
```

## Stop Services

```bash
make stop
```

## Troubleshooting

### Services won't start?
```bash
# Check Docker is running
docker ps

# Restart all
make stop
make start
```

### Demo upload fails?
```bash
# Ensure backend is running
make health

# Reset database if needed
make reset
```

### Proofs not verifying?
```bash
# Check Midnight network
curl http://localhost:8080/health

# Restart network
./scripts/start-local-network.sh
```

## Useful Commands

```bash
# Using Make (recommended)
make setup-all      # Complete setup
make start          # Start all services
make stop           # Stop all services
make status         # Check status
make health         # Health check
make test           # Run tests
make demo           # Upload data + run queries
make reset          # Reset databases
make clean          # Clean everything

# Using npm
npm run compile     # Compile contract
npm run deploy      # Deploy contract
npm run status      # Check status

# Using scripts directly
./scripts/setup-midnight.sh          # Install Midnight
./scripts/compile-contract.sh        # Compile contract
./scripts/deploy-contract.sh         # Deploy contract
./scripts/check-midnight-status.sh   # Full status
```

## Service Endpoints

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8501 |
| Backend API | http://localhost:8001 |
| API Docs | http://localhost:8001/docs |
| ChromaDB | http://localhost:8000 |
| Midnight | http://localhost:8080 |

## What's Next?

1. **Try custom queries** in the frontend
2. **Read the docs**:
   - `SETUP_GUIDE.md` - Complete setup guide
   - `scripts/README.md` - Script reference
   - `demo/README.md` - Demo data guide
3. **Add your own documents** via API
4. **Modify smart contract** in `contracts/`
5. **Deploy to testnet**

## Getting Help

- Check `SETUP_GUIDE.md` for detailed troubleshooting
- Review logs: `make logs-backend`
- Check status: `make status`
- Consult [Midnight Docs](https://docs.midnight.network)

## Common Issues

| Issue | Solution |
|-------|----------|
| Port conflict | Change ports in `docker-compose.yml` |
| Network timeout | Check firewall settings |
| Out of disk space | `docker system prune` |
| Contract fails | Update Midnight CLI: `npm update -g @midnight-ntwrk/compact-cli` |

---

**Pro Tip**: Use `make` commands for everything - they're shorter and easier to remember!

```bash
make setup-all  # First time
make start      # Every day
make demo       # Test it
make stop       # When done
```
