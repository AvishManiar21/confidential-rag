# ConfidentialRAG

Privacy-Preserving Document Q&A System using Zero-Knowledge Proofs on Midnight Blockchain

## Overview

ConfidentialRAG is a privacy-first Retrieval-Augmented Generation (RAG) system that leverages Midnight's zero-knowledge proof capabilities to enable document querying without exposing sensitive content. Users can prove retrieval relevance and answer quality without revealing actual queries, embeddings, or document contents.

### Key Features

- **Private Embeddings**: Document embeddings stored as commitments on Midnight blockchain
- **Hybrid Retrieval**: BM25 + vector search fusion for superior retrieval quality
- **Quality Verification**: On-chain ZK proofs of RAGAS context precision metrics
- **Local LLM**: Ollama-based inference (no external API calls)
- **Selective Disclosure**: Prove facts about data without revealing the data itself

## Architecture

```
┌─────────────┐
│   Client    │ (Streamlit UI)
└──────┬──────┘
       │
┌──────▼──────────┐
│  FastAPI Backend│
│  - RAG Engine   │
│  - Proof Gen    │
└──────┬──────────┘
       │
┌──────▼──────────────────┐
│  Midnight Blockchain    │
│  - Compact Contract     │
│  - Commitment Storage   │
│  - Proof Verification   │
└─────────────────────────┘
```

## Use Case: Medical Knowledge Base

Demo scenario: Healthcare providers query medical literature while preserving patient privacy.

- Upload medical research papers
- Query symptoms/treatments privately
- Verify answers cite approved sources (ZK proof)
- Share diagnosis without exposing patient queries

## Technology Stack

### Blockchain Layer
- **Midnight Node**: Local devnet blockchain (Docker)
- **Midnight Indexer**: Query API for on-chain data (Docker)
- **Proof Server**: ZK proof generation service (Docker)
- **Compact Compiler**: Smart contract compiler (Docker)
- **Midnight.js SDK**: TypeScript SDK for contract interaction
- **ZK Proofs**: Commitment schemes, Merkle proofs, nullifiers

**Windows Compatibility**: Compact compiler runs in Docker for cross-platform support.

### Backend
- **FastAPI**: Python web framework
- **ChromaDB**: Vector database for embeddings
- **PostgreSQL**: Document registry and audit logs
- **sentence-transformers**: Embedding generation (all-MiniLM-L6-v2)
- **Ollama**: Local LLM inference (Llama2)
- **LangChain**: RAG orchestration

### Frontend
- **Streamlit**: Interactive Python UI

## Privacy Guarantees

| Data Type | Storage | Visibility |
|-----------|---------|------------|
| Document content | ChromaDB (off-chain) | Owner only |
| Document embeddings | Midnight (commitment) | Hidden (ZK proof only) |
| User query | Client-side only | User only |
| Query embedding | Commitment on-chain | User only |
| Retrieval results | Off-chain API | User only |
| Similarity score | ZK proof on-chain | Threshold met: YES/NO |
| RAGAS metrics | ZK proof on-chain | Above threshold: YES/NO |

## Quick Start

**Get up and running in 5 minutes:**

```bash
# Clone repository
git clone https://github.com/AvishManiar21/confidential-rag.git
cd confidential-rag

# Configure environment variables
cp .env.example .env
# Edit .env and set all required values (POSTGRES_PASSWORD, CHROMA_AUTH_TOKEN, SECRET_KEY)

# One-command setup (installs everything)
./scripts/setup-all.sh

# Start all services
make start

# Upload demo medical data
make demo-upload

# Run demo queries
make demo-query

# Access the UI
# http://localhost:8501
```

### Alternative: Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

**Prerequisites:**
- Docker & Docker Compose
- Node.js 18+ (for Midnight)
- Python 3.10+
- Git

**Step 1: Environment Setup**
```bash
# Configure environment variables (REQUIRED)
cp .env.example .env
# Edit .env and set all required values:
#   - POSTGRES_PASSWORD (strong password for database)
#   - CHROMA_AUTH_TOKEN (token for ChromaDB authentication)
#   - SECRET_KEY (generate with: openssl rand -hex 32)

# Install Midnight CLI
npm install -g @midnight-ntwrk/compact-cli @midnight-ntwrk/midnight-cli

# Start Docker services
docker-compose up -d

# Create Python virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 2: Database Setup**
```bash
# Run migrations
cd backend
alembic upgrade head

# Or use utility script
python setup_db.py
```

**Step 3: Compile & Deploy Contract**
```bash
cd contracts
compact compile ConfidentialRAG.compact
compact deploy --network local
```

**Step 4: Start Services**
```bash
# Backend (terminal 1)
cd backend
uvicorn app.main:app --reload --port 8001

# Frontend (terminal 2)
cd frontend
streamlit run app.py --server.port 8501

# Midnight local network (terminal 3)
./scripts/start-local-network.sh
```

</details>

## Project Status

### ✅ Completed

#### Infrastructure
- [x] Docker Compose configuration (PostgreSQL, ChromaDB, Ollama, Midnight services)
- [x] Midnight Node + Indexer + Proof Server (Docker-based devnet)
- [x] Compact Compiler Docker service (Windows-compatible)
- [x] Database schema and migrations
- [x] Environment configuration with secrets externalization

#### Smart Contract (Midnight/Compact)
- [x] ConfidentialRAG.compact contract (418 lines)
- [x] Merkle tree-based document commitment verification
- [x] Nullifier-based replay protection
- [x] Similarity proof verification circuit
- [x] Batch query support circuits
- [x] Docker-based compilation pipeline
- [x] Deployment scripts (`midnight/scripts/deploy.mjs`)
- [x] Interaction scripts (`midnight/scripts/interact.mjs`)

#### Backend (FastAPI)
- [x] Document ingestion API with PDF processing
- [x] Hybrid retrieval (BM25 + vector search)
- [x] Embedding generation (sentence-transformers)
- [x] RAG orchestration with LangChain
- [x] Cryptographic commitment service
- [x] Merkle tree construction and proof generation
- [x] Midnight blockchain integration (HTTP health checks + service connections)
- [x] Health monitoring and audit logging
- [x] RAGAS evaluation framework

#### Frontend (Streamlit)
- [x] Document upload interface
- [x] Privacy-preserving query interface
- [x] Interactive ZK proof visualization
- [x] Document management with pagination
- [x] Settings and configuration
- [x] Real-time health monitoring

#### Development Tools
- [x] One-command setup script
- [x] Service management scripts (start/stop/health)
- [x] Database reset and cleanup utilities
- [x] Comprehensive test suite
- [x] Demo dataset (15 medical abstracts)
- [x] Demo queries with validation
- [x] End-to-end testing script
- [x] Makefile with convenient commands
- [x] npm scripts for Midnight operations

#### Documentation
- [x] Comprehensive README
- [x] QUICKSTART guide
- [x] SETUP_GUIDE with troubleshooting
- [x] Contract documentation
- [x] Backend architecture docs
- [x] Frontend development guide
- [x] Script reference guide
- [x] Demo testing scenarios

### ✅ Midnight Blockchain Integration

**Fully Integrated Infrastructure:**
- ✅ Midnight Node (localhost:8080) - Blockchain RPC running in Docker
- ✅ Midnight Indexer (localhost:8081) - Query API for on-chain data
- ✅ Proof Server (localhost:6300) - ZK proof generation service
- ✅ Compact Compiler - Docker service for contract compilation (Windows-compatible)
- ✅ Backend health checks - Real HTTP calls to all Midnight services
- ✅ Contract deployment scripts - `midnight/scripts/deploy.mjs`
- ✅ Interaction scripts - `midnight/scripts/interact.mjs` for proof submission demo

**Midnight.js SDK Ready:**
The project includes `midnight/package.json` with all Midnight.js dependencies configured. To complete the integration:
1. `cd midnight && npm install` - Install SDK packages
2. Generate wallet key for contract deployment
3. Run `npm run compile` - Compile Compact contract via Docker
4. Run `npm run deploy` - Deploy to local devnet

**Current Status:**
- Docker Compose runs complete Midnight devnet ✅
- Contract compiles successfully via Docker ✅
- Backend connects to all Midnight services ✅
- SDK integration structured, awaiting `npm install` and wallet setup ⏳

## Hackathon Submission

**Track**: AI - Privacy-Preserving AI Applications

**Problem**: Traditional RAG systems expose sensitive queries and documents to:
- OpenAI/Anthropic APIs (privacy leak)
- Vector database operators (data access)
- Blockchain explorers (public ledger)

**Solution**: ConfidentialRAG uses:
1. **Local embeddings** (sentence-transformers, no API calls)
2. **ZK commitments** (embeddings hidden on-chain)
3. **Merkle proofs** (document authenticity without revealing content)
4. **RAGAS verification** (prove retrieval quality cryptographically)

**Differentiators**:
- Hybrid retrieval (BM25 + vector) - not naive cosine search
- On-chain quality metrics (RAGAS context precision)
- Production-grade architecture (local LLM, proper RAG patterns)

## License

MIT License - see LICENSE file for details

## Resources

- [Midnight Documentation](https://docs.midnight.network)
- [Compact Language Guide](https://docs.midnight.network/develop/compact)
- [Midnight Academy](https://academy.midnight.network)
- [Hackathon Details](https://mlh.io/midnight-hackathon)

## Team

Built for Midnight Foundation Hackathon (MLH)
