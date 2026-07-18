# Compact Smart Contract Quick Reference

## Basic Contract Template

```compact
pragma language_version >= 0.20;
import CompactStandardLibrary;

// Public state (on blockchain)
export ledger myState: Type;

// Private witness (runs locally)
witness getPrivateData(): Bytes<32>;

// State transition (generates ZK proof)
export circuit myFunction(): [] {
    const privateData = getPrivateData();
    myState = disclose(privateData);
}
```

## Essential Patterns for RAG Contract

### 1. Document Commitments in Merkle Tree

```compact
export ledger documentCommitments: HistoricMerkleTree<10, Bytes<32>>;

circuit documentCommit(docHash: Bytes<32>, embeddingHash: Bytes<32>): Bytes<32> {
    return persistentHash<Vector<3, Bytes<32>>>([
        pad(32, "rag:doc:commit"),
        docHash,
        embeddingHash
    ]);
}

export circuit addDocument(docHash: Bytes<32>, embeddingHash: Bytes<32>): [] {
    const commit = documentCommit(docHash, embeddingHash);
    documentCommitments.insert(disclose(commit));
}
```

### 2. Nullifiers for Replay Prevention

```compact
export ledger queryNullifiers: Set<Bytes<32>>;

circuit queryNullifier(sk: Bytes<32>, queryHash: Bytes<32>, timestamp: Uint<64>): Bytes<32> {
    return persistentHash<Vector<4, Bytes<32>>>([
        pad(32, "rag:query:nullifier"),
        sk,
        queryHash,
        timestamp as Bytes<32>
    ]);
}

export circuit processQuery(queryHash: Bytes<32>): [] {
    const sk = localSecretKey();
    const timestamp = getCurrentTimestamp();
    const nullifier = queryNullifier(sk, queryHash, timestamp);

    assert(!queryNullifiers.has(nullifier), "Query already processed");
    queryNullifiers.insert(disclose(nullifier));
}
```

### 3. Merkle Proof Verification

```compact
witness findPath(commit: Bytes<32>): MerkleTreePath<10, Bytes<32>>;

export circuit verifyMembership(docHash: Bytes<32>, embeddingHash: Bytes<32>): [] {
    const commit = documentCommit(docHash, embeddingHash);
    const path = findPath(commit);

    assert(
        merkleTreePathRoot(path) == documentCommitments.root(),
        "Document not found"
    );
}
```

### 4. Similarity Proof Verification

```compact
witness verifySimilarity(
    queryEmbed: Bytes<32>,
    docEmbed: Bytes<32>,
    threshold: Uint<8>
): Boolean;

export circuit querySimilar(
    queryEmbed: Bytes<32>,
    docEmbed: Bytes<32>,
    threshold: Uint<8>
): [] {
    const isValid = verifySimilarity(queryEmbed, docEmbed, threshold);
    assert(isValid, "Similarity verification failed");
}
```

## Data Types

### Primitives
```compact
Uint<8>         // 8-bit unsigned integer
Uint<32>        // 32-bit unsigned integer
Uint<64>        // 64-bit unsigned integer
Bytes<32>       // 32-byte array
Field           // ZK field element
Boolean         // true/false
```

### Collections
```compact
Vector<3, Bytes<32>>                    // Fixed-size array
Map<Bytes<32>, Uint<64>>               // Key-value map
Set<Bytes<32>>                          // Set (unique values)
List<Bytes<32>>                         // Dynamic list
MerkleTree<10, Bytes<32>>              // Merkle tree (depth 10)
HistoricMerkleTree<10, Bytes<32>>      // Historic Merkle tree
```

### Special Types
```compact
Counter                  // Auto-incrementing counter
Opaque<"string">        // JavaScript string (opaque to circuit)
Opaque<"Uint8Array">    // JavaScript Uint8Array (opaque to circuit)
```

## Standard Library Functions

### Hashing
```compact
// Circuit-optimized (not persistent across upgrades)
transientHash<T>(value: T): Field

// SHA-256 (persistent across upgrades)
persistentHash<T>(value: T): Bytes<32>
```

### Commitments
```compact
// Circuit-optimized commitment
transientCommit<T>(value: T, rand: Field): Field

// SHA-256 commitment (persistent)
persistentCommit<T>(value: T, rand: Bytes<32>): Bytes<32>
```

### Utilities
```compact
// Pad string to fixed length
pad(32, "domain-separator"): Bytes<32>

// Type casting
value as Bytes<32>
counter as Field
```

### Merkle Tree Operations
```compact
tree.insert(value)           // Insert into tree
tree.root()                  // Get current root
merkleTreePathRoot(path)     // Compute root from path
```

### Map Operations
```compact
map.set(key, value)          // Set key-value pair
map.get(key)                 // Get value by key
map.has(key)                 // Check if key exists
```

### Set Operations
```compact
set.insert(value)            // Add to set
set.has(value)               // Check membership
```

### Counter Operations
```compact
counter.increment(1)         // Increment by 1
counter.increment(n)         // Increment by n
```

## Key Concepts

### disclose() - Privacy Control
```compact
// Private by default
const privateValue = getPrivateData();

// Explicit disclosure for public storage
publicState = disclose(privateValue);

// No disclose needed for commitments (already have randomness)
const commit = persistentCommit(value, salt);
commitments.insert(commit);  // OK without disclose
```

### Witnesses - Private Functions
```compact
// Declared in contract
witness localSecretKey(): Bytes<32>;
witness findPath(commit: Bytes<32>): MerkleTreePath<10, Bytes<32>>;

// Implemented in TypeScript (off-chain)
// Provides private data to circuits
// Never exposed on blockchain
```

### Circuits - ZK Proof Functions
```compact
// Helper circuit (internal)
circuit publicKey(sk: Bytes<32>): Bytes<32> {
    return persistentHash(/* ... */);
}

// Exported circuit (callable from dApp)
export circuit transfer(amount: Uint<64>): [] {
    // Generates ZK proof automatically
}
```

### Assertions
```compact
assert(condition, "Error message");
assert(state == State.ACTIVE, "Contract not active");
assert(!nullifiers.has(n), "Replay attack detected");
```

### Enums
```compact
enum State {
    VACANT,
    OCCUPIED,
    LOCKED
}

export ledger state: State;
state = State.VACANT;
```

## Domain Separation Pattern

Always use unique domain prefixes for different purposes:

```compact
// Different domains for different purposes
pad(32, "myapp:ownership:commit")
pad(32, "myapp:query:nullifier")
pad(32, "myapp:user:pk")
pad(32, "myapp:doc:hash")

// Prevents collision attacks
```

## Security Best Practices

1. **Always validate witness inputs**
   ```compact
   const sk = localSecretKey();
   const pk = publicKey(sk);
   assert(authority == pk, "Invalid secret key");
   ```

2. **Use persistent hashing for storage**
   ```compact
   // Good: Survives protocol upgrades
   persistentHash(value)

   // Bad: May change in upgrades
   transientHash(value)
   ```

3. **Use domain separation**
   ```compact
   // Good
   persistentHash([pad(32, "unique:domain"), value])

   // Bad
   persistentHash(value)
   ```

4. **Check nullifiers before processing**
   ```compact
   assert(!nullifiers.has(n), "Already processed");
   nullifiers.insert(disclose(n));
   ```

5. **Verify Merkle proofs**
   ```compact
   assert(merkleTreePathRoot(path) == tree.root(), "Invalid proof");
   ```

## Common Errors

### Error: "Cannot store witness output without disclose"
```compact
// Wrong
const data = getPrivateData();
publicState = data;

// Correct
const data = getPrivateData();
publicState = disclose(data);
```

### Error: "Compilation error - private value stored publicly"
```compact
// Wrong
export circuit store(): [] {
    const hash = transientHash(secretKey());
    stored = hash;  // Error!
}

// Correct
export circuit store(): [] {
    const hash = transientHash(secretKey());
    stored = disclose(hash);
}
```

## Testing Pattern

Tests in TypeScript:
```typescript
import { Counter } from './managed/counter/contract';

describe('Counter', () => {
    it('should increment', async () => {
        const contract = new Counter(/* ... */);
        await contract.increment();
        expect(await contract.ledger.round).toBe(1);
    });
});
```

## Deployment

```bash
# Compile contract
yarn compile

# Deploy to testnet
yarn deploy

# Interact via CLI
yarn cli increment
```

## Resources

- Docs: https://docs.midnight.network/develop/compact
- Reference: https://docs.midnight.network/develop/reference/compact/lang-ref
- Examples: https://github.com/midnightntwrk/example-counter
- Community: https://forum.midnight.network
