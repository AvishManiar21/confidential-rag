# ConfidentialRAG Backend Architecture

## System Overview

The ConfidentialRAG backend is a production-grade FastAPI application that implements a Retrieval-Augmented Generation (RAG) pipeline with zero-knowledge proofs and blockchain integration.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│              (Frontend, API Clients, cURL)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Health   │  │ Documents  │  │   Query    │            │
│  │  Endpoint  │  │  Endpoint  │  │  Endpoint  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Embedding │  │ ChromaDB │  │   RAG    │  │Commitment│   │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐                                │
│  │  Merkle  │  │ Midnight │                                │
│  │ Service  │  │ Service  │                                │
│  └──────────┘  └──────────┘                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │   ChromaDB   │  │    Ollama    │      │
│  │  (Metadata)  │  │  (Vectors)   │  │    (LLM)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐                                           │
│  │   Midnight   │                                           │
│  │ (Blockchain) │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer (`app/api/`)

#### Health Endpoint (`health.py`)
- System health checks
- Service availability monitoring
- Returns status of all components

#### Documents Endpoint (`documents.py`)
- Document upload (multipart/form-data)
- PDF text extraction
- Document listing and retrieval
- Document deletion

#### Query Endpoint (`query.py`)
- RAG query processing
- ZK proof generation
- Query audit logging

### 2. Core Layer (`app/core/`)

#### Config (`config.py`)
- Environment-based configuration
- Pydantic Settings validation
- Type-safe configuration access

#### Database (`database.py`)
- Async SQLAlchemy setup
- Connection pooling
- Session management
- Database initialization

#### Logging (`logging.py`)
- Structured logging
- Log level configuration
- Third-party logger management

### 3. Models Layer (`app/models/`)

#### Document Model (`document.py`)
- SQLAlchemy ORM model
- Stores document metadata
- Tracks processing status
- Contains cryptographic commitments

Fields:
- `id`, `filename`, `file_hash`, `file_size`
- `text_content`, `num_chunks`
- `embedding_hash`, `commitment`, `merkle_root`, `merkle_proof`
- `processed`, `error_message`
- `tx_hash`, `block_number` (blockchain)
- Timestamps: `created_at`, `updated_at`, `processed_at`

#### Query Audit Model (`query.py`)
- SQLAlchemy ORM model
- Audit trail for queries
- Stores proof data
- Quality metrics

Fields:
- `id`, `query_text`, `query_hash`
- `num_results`, `retrieved_docs`, `relevance_scores`
- `response_text`, `response_hash`
- `proof_generated`, `proof_data`, `proof_verified`
- `ragas_score`, `avg_similarity`, `response_time_ms`
- `user_id`, `session_id`, `status`

#### Schemas (`schemas.py`)
- Pydantic models for validation
- Request/response schemas
- Type safety and documentation

### 4. Service Layer (`app/services/`)

#### Embedding Service (`embedding.py`)
**Purpose**: Generate text embeddings using sentence-transformers

**Key Methods**:
- `embed_text(text)`: Single text embedding
- `embed_batch(texts)`: Batch embedding with progress
- `compute_similarity(emb1, emb2)`: Cosine similarity
- `get_embedding_dimension()`: Vector dimension

**Features**:
- Lazy model loading
- Retry logic with exponential backoff
- Batch processing support
- GPU acceleration (if available)

#### ChromaDB Service (`chroma.py`)
**Purpose**: Vector database operations

**Key Methods**:
- `add_documents()`: Store embeddings
- `query_by_embedding()`: Vector search
- `query_by_text()`: Text-based search
- `delete_by_ids()`: Remove documents
- `count_documents()`: Get collection size

**Features**:
- HTTP client for remote ChromaDB
- Fallback to in-memory mode
- Metadata filtering
- Automatic collection creation

#### RAG Service (`rag.py`)
**Purpose**: Orchestrate RAG pipeline

**Key Methods**:
- `hybrid_retrieve()`: BM25 + vector fusion
- `generate_answer()`: LLM answer generation
- `query()`: Full RAG pipeline
- `evaluate_with_ragas()`: Quality metrics

**Hybrid Retrieval Algorithm**:
```python
hybrid_score = α * vector_score + (1-α) * bm25_score
```

**Features**:
- Configurable fusion weight (α)
- Top-K retrieval
- Similarity threshold filtering
- RAGAS evaluation integration

#### Commitment Service (`commitment.py`)
**Purpose**: Cryptographic hash and commitment generation

**Key Methods**:
- `hash_text(text)`: SHA-256 hash
- `hash_embedding(embedding)`: Embedding hash
- `generate_commitment()`: Combine hashes
- `verify_commitment()`: Validate commitment

**Commitment Formula**:
```
commitment = SHA256(doc_hash || embedding_hash || metadata)
```

#### Merkle Service (`merkle.py`)
**Purpose**: Merkle tree construction and proof generation

**Key Classes**:
- `MerkleNode`: Tree node
- `MerkleTree`: Tree construction
- `MerkleProof`: Proof data structure

**Key Methods**:
- `build_tree(leaves)`: Construct tree
- `generate_proof(leaf)`: Create proof
- `verify_proof(proof)`: Validate proof

**Algorithm**:
1. Build binary tree from leaf hashes
2. Hash pairs: `parent = SHA256(left || right)`
3. Generate proof path to root
4. Verify by recomputing root

#### Midnight Service (`midnight.py`)
**Purpose**: Blockchain integration (placeholder)

**Key Methods**:
- `submit_commitment()`: Submit to chain
- `verify_proof()`: On-chain verification
- `get_commitment()`: Retrieve commitment
- `check_connection()`: Health check

**Note**: Currently a placeholder implementation. In production, would use actual Midnight SDK.

## Data Flow

### Document Ingestion Flow

```
1. Upload PDF
   └─> Extract text (pypdf)
       └─> Chunk text (overlapping windows)
           └─> Generate embeddings (sentence-transformers)
               └─> Store in ChromaDB
               └─> Compute hashes
                   └─> Generate commitments
                       └─> Build Merkle tree
                           └─> Submit to Midnight
                           └─> Save to PostgreSQL
```

### Query Processing Flow

```
1. Receive query
   └─> Generate query embedding
       └─> Hybrid retrieval
           ├─> Vector search (ChromaDB)
           └─> BM25 scoring
           └─> Fusion and ranking
               └─> Generate answer (Ollama)
                   └─> Generate ZK proof
                       ├─> Build Merkle tree
                       ├─> Generate proof
                       └─> Verify on-chain
                   └─> Evaluate (RAGAS)
                   └─> Save audit log
                   └─> Return response
```

## Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    text_content TEXT,
    num_chunks INTEGER DEFAULT 0,
    embedding_hash VARCHAR(64),
    commitment VARCHAR(64),
    merkle_root VARCHAR(64),
    merkle_proof JSONB,
    metadata JSONB,
    tags JSONB,
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    tx_hash VARCHAR(66),
    block_number INTEGER,
    contract_address VARCHAR(42),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
```

### Query Audit Table
```sql
CREATE TABLE query_audit (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    num_results INTEGER DEFAULT 0,
    retrieved_docs JSONB,
    relevance_scores JSONB,
    response_text TEXT,
    response_hash VARCHAR(64),
    proof_generated BOOLEAN DEFAULT FALSE,
    proof_data JSONB,
    proof_verified BOOLEAN DEFAULT FALSE,
    ragas_score FLOAT,
    avg_similarity FLOAT,
    response_time_ms INTEGER,
    metadata JSONB,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    error_message TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

## Security Considerations

### Cryptographic Commitments
- SHA-256 for content hashing
- Keccak-256 for blockchain compatibility
- Deterministic commitment generation
- Merkle proofs for efficient verification

### Data Privacy
- Document hashes prevent content leakage
- Embeddings are not directly reversible
- ZK proofs enable verification without revealing data

### API Security
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- Error message sanitization

## Performance Optimizations

### Async/Await Pattern
- Non-blocking I/O operations
- Concurrent request handling
- Efficient database queries

### Batch Processing
- Batch embedding generation
- Bulk ChromaDB operations
- Connection pooling

### Caching
- Model lazy loading
- Embedding model reuse
- Database connection pool

### Indexing
- Database indexes on common queries
- ChromaDB vector indexes
- File hash uniqueness constraint

## Monitoring and Logging

### Logging Levels
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages with stack traces

### Health Checks
- Database connectivity
- ChromaDB availability
- Ollama status
- Midnight blockchain connection

### Metrics
- Response times
- Document processing time
- Embedding generation time
- Query latency
- Proof generation time

## Error Handling

### Error Categories
1. **Validation Errors**: Invalid input (400)
2. **Not Found Errors**: Resource not found (404)
3. **Processing Errors**: PDF extraction, embedding failures (500)
4. **External Service Errors**: ChromaDB, Ollama, Midnight (500)
5. **Database Errors**: Connection, constraint violations (500)

### Error Response Format
```json
{
  "error": "Error type",
  "detail": "Detailed message",
  "timestamp": "2026-07-18T..."
}
```

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- External state in PostgreSQL/ChromaDB
- Load balancer compatible

### Vertical Scaling
- GPU acceleration for embeddings
- Connection pool tuning
- Worker process configuration

### Database Scaling
- Read replicas for queries
- Partitioning for large datasets
- Index optimization

## Future Enhancements

1. **Authentication**: JWT-based auth
2. **Rate Limiting**: Request throttling
3. **Caching Layer**: Redis for frequently accessed data
4. **Async Processing**: Celery for background tasks
5. **Monitoring**: Prometheus metrics, Grafana dashboards
6. **Testing**: Comprehensive test suite
7. **CI/CD**: Automated testing and deployment
8. **Real Midnight Integration**: Actual blockchain SDK
9. **Advanced RAG**: Multi-query, re-ranking, query expansion
10. **Document Types**: Support for more file formats

## Deployment

### Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker
```bash
docker build -t confidential-rag .
docker run -p 8000:8000 confidential-rag
```

### Kubernetes
- Deployment manifests
- Service definitions
- ConfigMaps for configuration
- Secrets for sensitive data
