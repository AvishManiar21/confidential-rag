# ConfidentialRAG Backend

FastAPI backend for Confidential RAG with Zero-Knowledge Proofs and Midnight Blockchain integration.

## Features

- **Document Ingestion**: Upload PDF documents, extract text, chunk, and generate embeddings
- **Hybrid Retrieval**: Combines BM25 (sparse) and vector search (dense) for optimal retrieval
- **RAG Pipeline**: Query answering using Ollama LLM with retrieved context
- **Zero-Knowledge Proofs**: Generate cryptographic commitments and Merkle proofs
- **Midnight Integration**: Submit commitments to Midnight blockchain
- **RAGAS Evaluation**: Quality metrics for RAG responses
- **Audit Logging**: Complete query and document audit trail

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLAlchemy async
- **Vector Store**: ChromaDB
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **LLM**: Ollama (llama2)
- **Retrieval**: BM25 + Vector Search fusion
- **Cryptography**: eth-hash for Keccak-256
- **Blockchain**: Midnight (placeholder integration)

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── documents.py  # Document upload/list endpoints
│   │   ├── query.py      # RAG query endpoint
│   │   └── health.py     # Health check
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings from env vars
│   │   ├── database.py   # PostgreSQL connection
│   │   └── logging.py    # Logging setup
│   ├── models/           # Data models
│   │   ├── document.py   # Document SQLAlchemy model
│   │   ├── query.py      # Query audit model
│   │   └── schemas.py    # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── embedding.py  # Embedding generation
│   │   ├── chroma.py     # ChromaDB client
│   │   ├── rag.py        # RAG orchestration
│   │   ├── commitment.py # Hash/commitment generation
│   │   ├── merkle.py     # Merkle tree operations
│   │   └── midnight.py   # Blockchain integration
│   └── main.py           # FastAPI app
├── alembic/              # Database migrations
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- ChromaDB server
- Ollama with llama2 model

### Installation

1. **Clone and navigate**:
   ```bash
   cd confidential-rag/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

### Running the Server

**Development**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Docker**:
```bash
docker build -t confidential-rag-backend .
docker run -p 8000:8000 --env-file .env confidential-rag-backend
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - System health status

### Documents
- `POST /api/v1/documents` - Upload document (multipart/form-data)
- `GET /api/v1/documents` - List documents (paginated)
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document

### Query
- `POST /api/v1/query` - RAG query with ZK proof
- `GET /api/v1/query/{id}` - Get query audit record

### Documentation
- `GET /docs` - Interactive API documentation (Swagger)
- `GET /redoc` - Alternative API documentation

## API Usage Examples

### Upload Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -F "file=@document.pdf"
```

### Query RAG

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the document?",
    "top_k": 5,
    "generate_proof": true
  }'
```

### List Documents

```bash
curl "http://localhost:8000/api/v1/documents?page=1&page_size=10"
```

## Configuration

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# ChromaDB
CHROMA_URL=http://localhost:8000

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Midnight
MIDNIGHT_RPC_URL=http://localhost:8080
MIDNIGHT_CONTRACT_ADDRESS=0x...

# RAG Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.6
```

## Development

### Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

### Testing

```bash
pytest tests/ -v --cov=app
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Architecture

### Document Ingestion Flow

1. Upload PDF → Extract text → Chunk into segments
2. Generate embeddings for each chunk
3. Store embeddings in ChromaDB with metadata
4. Compute chunk hashes and embedding hashes
5. Generate commitments: `hash(chunk_hash || embedding_hash)`
6. Build Merkle tree from commitments
7. Submit Merkle root to Midnight contract
8. Store document metadata in PostgreSQL

### RAG Query Flow

1. Receive query → Generate query embedding
2. Hybrid retrieval:
   - Vector search: ChromaDB similarity search
   - BM25: Sparse keyword matching
   - Fusion: Weighted combination of scores
3. Generate answer using Ollama with retrieved context
4. Generate ZK proof:
   - Build Merkle tree from retrieved doc commitments
   - Generate Merkle proof for each document
   - Verify proof on Midnight contract
5. Evaluate with RAGAS metrics
6. Log to audit table
7. Return response with proof

### Cryptographic Components

- **Hashing**: SHA-256 for content, Keccak-256 for blockchain
- **Commitments**: `hash(doc_hash || embedding_hash || metadata)`
- **Merkle Tree**: Binary tree with leaf commitments
- **ZK Proof**: Merkle proof + on-chain verification

## Troubleshooting

**Database connection errors**:
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify network connectivity

**ChromaDB errors**:
- Start ChromaDB server: `chroma run --host localhost --port 8000`
- Check CHROMA_URL in .env

**Ollama errors**:
- Install Ollama and pull model: `ollama pull llama2`
- Check OLLAMA_URL in .env

**Slow embeddings**:
- Use GPU if available
- Reduce batch_size in embedding service
- Consider lighter embedding model

## License

MIT
