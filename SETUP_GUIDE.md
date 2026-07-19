# ConfidentialRAG - Complete Setup Guide

Production-ready development environment for privacy-preserving RAG with Midnight blockchain.

## Overview

This guide covers the complete setup of ConfidentialRAG, including:

- Midnight blockchain local development network
- Smart contract compilation and deployment
- Backend services (PostgreSQL, ChromaDB, Ollama)
- Frontend Streamlit application
- Demo data and testing

## Prerequisites

### Required Software

- **Node.js 18+** - [Download](https://nodejs.org)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- **Docker Compose** - Included with Docker Desktop
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)

### Verify Installation

```bash
node --version    # Should be v18.0.0 or higher
docker --version  # Should be 20.10 or higher
python3 --version # Should be 3.10 or higher
git --version     # Any recent version
```

### System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows (with Git Bash/WSL)

## Quick Start (Automated)

### Option 1: One-Command Setup

```bash
# Clone repository
git clone <repo-url>
cd confidential-rag

# Complete automated setup
./scripts/setup-all.sh
```

This single command will:
1. Install Midnight CLI tools
2. Set up Python virtual environment
3. Start Docker services
4. Pull Ollama LLM model
5. Initialize database
6. Compile and deploy smart contract

**Duration**: 10-15 minutes (first run)

### Option 2: Using Makefile

```bash
# Alternative using make
make setup-all
```

## Step-by-Step Setup (Manual)

### 1. Install Midnight CLI

```bash
# Run Midnight setup script
./scripts/setup-midnight.sh
```

This installs:
- `@midnight-ntwrk/midnight-cli` (blockchain node)
- `@midnight-ntwrk/compact-cli` (smart contract compiler)

**Verify**:
```bash
midnight-cli --version
compact --version
```

### 2. Install Project Dependencies

```bash
# Install npm packages
npm install

# Create Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 3. Start Docker Services

```bash
# Start PostgreSQL, ChromaDB, Ollama
docker-compose up -d postgres chromadb ollama

# Check services are running
docker-compose ps
```

**Services**:
- PostgreSQL: `localhost:5432`
- ChromaDB: `localhost:8000`
- Ollama: `localhost:11434`

### 4. Initialize Database

```bash
# Wait for PostgreSQL to be ready
sleep 10

# Run database schema migration
cd backend
source venv/bin/activate
python setup_db.py
cd ..
```

### 5. Pull Ollama Model

```bash
# Download llama2 model (large download ~4GB)
docker exec confidential-rag-ollama ollama pull llama2
```

### 6. Start Midnight Network

```bash
# Start local blockchain
./scripts/start-local-network.sh

# Verify network is running
curl http://localhost:8080/health
```

### 7. Compile Smart Contract

```bash
# Compile Compact contract
./scripts/compile-contract.sh
```

**Output**: `contracts/ConfidentialRAG.compact.js`

### 8. Deploy Smart Contract

```bash
# Deploy to local network
./scripts/deploy-contract.sh local
```

**Output**: Contract address saved to `backend/.env`

### 9. Start Backend and Frontend

```bash
# Start all services with Docker Compose
docker-compose up -d backend frontend

# Or run manually:
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
cd frontend
streamlit run app.py
```

### 10. Verify Setup

```bash
# Comprehensive status check
./scripts/check-midnight-status.sh

# Quick health check
./scripts/health-check.sh
```

**Expected**: All services showing as healthy ✓

## Load Demo Data

### Upload Medical Abstracts

```bash
# Upload 15 medical research abstracts
python demo/upload-demo-data.py
```

**Expected Output**:
```
[SUCCESS] Loaded 15 medical abstracts
[SUCCESS] All documents uploaded successfully!
```

### Run Demo Queries

```bash
# Execute 10 sample queries
python demo/run-demo-queries.py
```

**Expected Output**:
```
Query Results Summary:
  Passed: 10/10
  All proofs verified successfully!
```

### Run E2E Tests

```bash
# Complete end-to-end workflow test
python demo/test-e2e.py
```

**Expected Output**:
```
Test Summary: 9/9 passed
All tests passed!
```

## Access Services

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8501 | Streamlit UI |
| **Backend API** | http://localhost:8001 | FastAPI server |
| **API Docs** | http://localhost:8001/docs | Swagger UI |
| **ChromaDB** | http://localhost:8000 | Vector database |
| **Midnight RPC** | http://localhost:8080 | Blockchain node |
| **PostgreSQL** | localhost:5432 | Database |

## Common Commands

### Using Scripts

```bash
# Start all services
./scripts/start-all.sh

# Stop all services
./scripts/stop-all.sh

# Check status
./scripts/check-midnight-status.sh

# Health check
./scripts/health-check.sh

# Reset databases
./scripts/reset-db.sh

# Run tests
./scripts/run-tests.sh
```

### Using Makefile

```bash
# Start services
make start

# Stop services
make stop

# Check status
make status

# Health check
make health

# Run tests
make test

# Upload demo data
make demo-upload

# Run demo queries
make demo-query

# Complete demo workflow
make demo
```

### Using npm Scripts

```bash
# Compile contract
npm run compile

# Deploy contract
npm run deploy

# Start Midnight network
npm run start:network

# Check status
npm run status
```

## Troubleshooting

### Midnight CLI Installation Fails

**Issue**: `npm install -g @midnight-ntwrk/midnight-cli` fails

**Solutions**:
1. Update Node.js to v18+
2. Clear npm cache: `npm cache clean --force`
3. Try with sudo (Linux/Mac): `sudo npm install -g ...`
4. Check internet connection

### Docker Services Won't Start

**Issue**: `docker-compose up` fails

**Solutions**:
1. Check Docker is running: `docker ps`
2. Free up ports: `docker-compose down`
3. Remove old volumes: `docker volume prune`
4. Check disk space: `df -h`

### Midnight Network Not Starting

**Issue**: Network fails to start or times out

**Solutions**:
1. Check port 8080 is free: `lsof -i :8080` (kill conflicting process)
2. Review logs: `cat midnight-network.log`
3. Restart: `./scripts/stop-all.sh && ./scripts/start-local-network.sh`
4. Update Midnight CLI: `npm update -g @midnight-ntwrk/midnight-cli`

### Contract Compilation Fails

**Issue**: `compact compile` errors

**Solutions**:
1. Check contract syntax in `contracts/ConfidentialRAG.compact`
2. Update Compact CLI: `npm update -g @midnight-ntwrk/compact-cli`
3. Review error messages for specific issues
4. Consult [Compact docs](https://docs.midnight.network/develop/compact)

### Contract Deployment Fails

**Issue**: Deployment times out or errors

**Solutions**:
1. Ensure network is running: `curl http://localhost:8080/health`
2. Check account has funds (testnet): Use faucet
3. Recompile contract: `./scripts/compile-contract.sh`
4. Try deploying again: `./scripts/deploy-contract.sh`

### Backend API Errors

**Issue**: FastAPI returns 500 errors

**Solutions**:
1. Check PostgreSQL: `docker exec -it confidential-rag-postgres pg_isready`
2. Check ChromaDB: `curl http://localhost:8000/api/v1/heartbeat`
3. Review logs: `docker-compose logs backend`
4. Restart backend: `docker-compose restart backend`

### Ollama Model Not Found

**Issue**: Queries fail with "model not found"

**Solutions**:
1. Pull model: `docker exec confidential-rag-ollama ollama pull llama2`
2. List models: `docker exec confidential-rag-ollama ollama list`
3. Check Ollama logs: `docker-compose logs ollama`

### Demo Data Upload Fails

**Issue**: `upload-demo-data.py` errors

**Solutions**:
1. Ensure backend is running: `./scripts/health-check.sh`
2. Check ChromaDB is healthy: `curl http://localhost:8000/api/v1/heartbeat`
3. Reset database: `./scripts/reset-db.sh`
4. Try uploading again

### Proofs Not Verifying

**Issue**: `proof_verified: false` in query results

**Solutions**:
1. Check Midnight network: `curl http://localhost:8080/health`
2. Verify contract is deployed: Check `contracts/deployment-info.json`
3. Check contract address in backend: `cat backend/.env | grep MIDNIGHT_CONTRACT_ADDRESS`
4. Redeploy contract: `./scripts/deploy-contract.sh`

## Development Workflow

### Daily Development

```bash
# Morning: Start services
make start

# Work on code...

# Recompile contract if changed
make compile
make deploy

# Test changes
make test

# Evening: Stop services
make stop
```

### Testing Changes

```bash
# 1. Make code changes

# 2. Restart affected service
docker-compose restart backend

# 3. Run tests
./scripts/run-tests.sh

# 4. Test manually in frontend
# Open http://localhost:8501
```

### Debugging

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
cat midnight-network.log

# Shell into containers
docker exec -it confidential-rag-backend /bin/bash
docker exec -it confidential-rag-postgres psql -U raguser -d confidentialrag

# Check database
psql -h localhost -U raguser -d confidentialrag
# Password: ragpass

# Check ChromaDB collections
curl http://localhost:8000/api/v1/collections
```

## Performance Optimization

### Speed Up First Start

```bash
# Pre-pull Docker images
docker-compose pull

# Pre-download Ollama model
docker pull ollama/ollama:latest
docker run -d --name ollama-temp ollama/ollama:latest
docker exec ollama-temp ollama pull llama2
docker commit ollama-temp ollama/ollama:latest-with-llama2
docker rm -f ollama-temp
```

### Reduce Resource Usage

```bash
# Use smaller Ollama model
docker exec confidential-rag-ollama ollama pull llama2:7b-chat

# Limit Docker memory
# Edit docker-compose.yml:
# services:
#   backend:
#     deploy:
#       resources:
#         limits:
#           memory: 2G
```

## Production Deployment

### Testnet Deployment

```bash
# 1. Get testnet tokens from faucet
# Visit: https://faucet.midnight.network

# 2. Configure testnet RPC
export MIDNIGHT_RPC_URL=https://testnet-rpc.midnight.network

# 3. Deploy contract
./scripts/deploy-contract.sh testnet

# 4. Update backend config
# Edit backend/.env with testnet contract address
```

### Security Checklist

- [ ] Change default database passwords
- [ ] Enable SSL/TLS for API endpoints
- [ ] Use environment variables for secrets
- [ ] Enable authentication on ChromaDB
- [ ] Rotate Midnight account keys
- [ ] Set up firewall rules
- [ ] Enable Docker security scanning
- [ ] Review and audit smart contract code

## Advanced Configuration

### Custom Ollama Model

```bash
# Pull different model
docker exec confidential-rag-ollama ollama pull mistral

# Update backend config
# Edit backend/app/config.py:
# OLLAMA_MODEL = "mistral"
```

### Custom Embedding Model

```python
# Edit backend/app/services/embeddings.py
from sentence_transformers import SentenceTransformer

# Use different model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
```

### Midnight Network Configuration

```bash
# Edit .midnight/config.json
{
  "network": "local",
  "rpc": "http://localhost:8080",
  "chainId": "midnight-local-1"
}
```

## Next Steps

After successful setup:

1. **Explore Frontend**: http://localhost:8501
   - Try sample queries
   - View document browser
   - Inspect ZK proofs

2. **Read Documentation**:
   - `scripts/README.md` - Script reference
   - `demo/README.md` - Demo data guide
   - `backend/README.md` - Backend architecture
   - `contracts/README.md` - Smart contract docs

3. **Customize**:
   - Add your own documents
   - Modify retrieval parameters
   - Tune embedding models
   - Extend smart contract

4. **Deploy**:
   - Test on Midnight testnet
   - Deploy to production
   - Set up monitoring
   - Configure backups

## Resources

### Documentation

- [Midnight Documentation](https://docs.midnight.network)
- [Compact Language Guide](https://docs.midnight.network/develop/compact)
- [Midnight Academy](https://academy.midnight.network)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [LangChain Docs](https://python.langchain.com)

### Community

- [Midnight Discord](https://discord.gg/midnight)
- [Midnight GitHub](https://github.com/midnight-ntwrk)
- [Hackathon Page](https://mlh.io/midnight-hackathon)

### Support

For issues:
1. Check this guide's troubleshooting section
2. Review script/demo README files
3. Consult Midnight documentation
4. Ask in Midnight Discord
5. Open GitHub issue

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built for Midnight Foundation Hackathon (MLH) - Privacy-Preserving AI Track.
