# ConfidentialRAG Smart Contract

Privacy-preserving RAG verification contract written in Midnight's Compact language.

## Overview

This contract enables privacy-preserving document retrieval with zero-knowledge proofs. Users can query a knowledge base and prove they found relevant documents **without revealing**:

- The query text
- The query embedding
- Which specific documents matched
- Document content or embeddings

## Contract Architecture

### Ledger State (On-Chain)

```compact
export ledger documentCommitments: HistoricMerkleTree<10, Bytes<32>>;
export ledger queryNullifiers: Set<Bytes<32>>;
export ledger documentCount: Counter;
export ledger queryCount: Counter;
export ledger similarityThreshold: Uint<8>;
```

- **documentCommitments**: Merkle tree of document hashes (max 1,024 docs)
- **queryNullifiers**: Prevents replay attacks
- **Counters**: Track usage statistics
- **similarityThreshold**: Minimum similarity score (0-100)

### Core Operations

#### 1. Add Document
```compact
export circuit addDocument(
    docHash: Bytes<32>,
    embeddingHash: Bytes<32>
): []
```

Owner adds document commitment to knowledge base.

**Privacy**: Only commitment stored on-chain, full document stays off-chain.

#### 2. Query with Similarity Proof
```compact
export circuit querySimilarDocument(
    queryHash: Bytes<32>,
    queryEmbedding: Bytes<32>,
    docHash: Bytes<32>,
    docEmbedding: Bytes<32>,
    similarityScore: Uint<8>
): []
```

User queries knowledge base with ZK proof of similarity.

**Verification Steps**:
1. Document exists in Merkle tree
2. Similarity ≥ threshold
3. Similarity proof valid (via witness)
4. No replay attack (nullifier check)

**Privacy**: Contract verifies without seeing actual query or documents.

#### 3. Batch Query
```compact
export circuit queryMultipleDocuments(
    queryHash: Bytes<32>,
    docHashes: Vector<3, Bytes<32>>,
    docEmbeddings: Vector<3, Bytes<32>>
): []
```

Query multiple documents at once (up to 3).

**Use case**: Top-k retrieval with ZK proof for each.

### Privacy Guarantees

| Data | Storage | Visibility |
|------|---------|------------|
| Document content | Off-chain | Owner only |
| Document embedding | Off-chain | Owner only |
| Query text | Client-side | User only |
| Query embedding | Client-side | User only |
| Document commitment | On-chain | Public (hash only) |
| Query nullifier | On-chain | Public (hash only) |
| Similarity score | Private input | Hidden (ZK proof) |

## Workflow

### Document Indexing (Owner)

```
1. Hash document → docHash
2. Generate embedding → embed
3. Hash embedding → embeddingHash
4. Call addDocument(docHash, embeddingHash)
5. Store full document off-chain (ChromaDB)
```

### Query Execution (User)

```
1. Hash query → queryHash
2. Generate query embedding locally (sentence-transformers)
3. Search local index for similar docs (ChromaDB)
4. For each similar document:
   a. Compute similarity score
   b. Call querySimilarDocument(...) on-chain
   c. Get ZK proof of valid query
5. Retrieve actual documents off-chain
6. Generate response with local LLM (Ollama)
```

### What Gets Proven (Zero-Knowledge)

✅ Document exists in knowledge base
✅ Similarity exceeds threshold
✅ Query is not a replay attack
✅ User has valid credentials

❌ What the query was
❌ Which document matched
❌ Actual similarity score
❌ Document content

## Compilation & Deployment

### Prerequisites

```bash
npm install -g @midnight-ntwrk/compact-cli
```

### Compile

```bash
cd contracts
compact compile ConfidentialRAG.compact
```

Output: `ConfidentialRAG.compiled.json`

### Deploy to Local Network

```bash
# Start Midnight local dev
midnight-cli start-local

# Deploy contract
compact deploy ConfidentialRAG.compiled.json --network local
```

### Deploy to Testnet

```bash
compact deploy ConfidentialRAG.compiled.json --network testnet
```

## Testing

```bash
# Unit tests
compact test ConfidentialRAG.compact

# Integration tests (with backend)
cd ../backend
pytest tests/test_contract_integration.py
```

## Security Considerations

1. **Replay Protection**: Nullifiers prevent same query twice
2. **Merkle Proof**: Ensures document authenticity
3. **Threshold Enforcement**: Prevents low-quality matches
4. **Owner Controls**: Only owner can pause/update threshold
5. **Historic Merkle Tree**: Preserves proof validity after updates

## Extensions (Future Work)

- [ ] Access control (whitelist/blacklist users)
- [ ] Document versioning (update embeddings)
- [ ] Document removal (soft delete)
- [ ] Query cost (pay-per-query)
- [ ] Reputation system (query quality scoring)
- [ ] Result caching (recent query optimization)

## Resources

- [Compact Language Docs](https://docs.midnight.network/develop/compact)
- [Standard Library](https://docs.midnight.network/compact/standard-library)
- [Example Contracts](https://github.com/midnightntwrk/example-counter)
- [Compact by Example](https://compact-by-example.org)

## License

MIT License
