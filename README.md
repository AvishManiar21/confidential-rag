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
- **Midnight**: Privacy-preserving blockchain
- **Compact**: TypeScript-based smart contract language
- **ZK Proofs**: Commitment schemes, Merkle proofs, nullifiers

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

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for Midnight)
- Python 3.10+
- Git

### Installation

```bash
# Clone repository
git clone <repo-url>
cd confidential-rag

# Install Midnight local dev environment
npm install -g @midnight-ntwrk/midnight-cli
midnight-cli init

# Start services
docker-compose up -d

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload

# Run frontend (new terminal)
cd frontend
streamlit run app.py
```

### Deploy Smart Contract

```bash
cd contracts
compact compile ConfidentialRAG.compact
compact deploy --network local
```

## Development Roadmap

### Phase 1: Foundation (MVP)
- [x] Project structure
- [ ] Midnight local dev setup
- [ ] Docker Compose configuration
- [ ] Basic Compact contract (commitment storage)

### Phase 2: RAG Core
- [ ] Document ingestion API
- [ ] Embedding generation (sentence-transformers)
- [ ] Hybrid retrieval (BM25 + vector)
- [ ] RAGAS evaluation

### Phase 3: ZK Integration
- [ ] Commitment generation service
- [ ] Merkle tree construction
- [ ] Proof generation (similarity + quality)
- [ ] Contract integration

### Phase 4: UI & Demo
- [ ] Streamlit interface
- [ ] Medical dataset preparation
- [ ] Demo queries and scenarios

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
