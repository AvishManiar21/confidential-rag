# Midnight Compact Smart Contract Language - Research Summary

## Overview

Compact is Midnight Network's smart contract language designed for privacy-preserving applications. It abstracts away zero-knowledge proof complexity, providing TypeScript-like syntax with automatic ZK proof generation.

**Key Features:**
- Privacy-by-default model
- TypeScript-like syntax
- Automatic zero-knowledge proof generation
- Selective disclosure mechanism
- Three distinct execution contexts: ledger (public), circuits (ZK proofs), witnesses (private)

## 1. Basic Compact Contract Structure

### Minimal Counter Example

```compact
pragma language_version >= 0.20;
import CompactStandardLibrary;

// Public state stored on the on-chain ledger
export ledger round: Counter;

// Transition function that updates public state
export circuit increment(): [] {
  round.increment(1);
}
```

### Complete Contract Template

```compact
pragma language_version >= 0.20;
import CompactStandardLibrary;

// LEDGER (Public State) - visible on blockchain
export ledger authority: Bytes<32>;
export ledger value: Uint<64>;
export ledger state: State;
export ledger round: Counter;

// WITNESSES (Private Functions) - run locally in TypeScript/JavaScript
witness secretKey(): Bytes<32>;

// CIRCUITS (State Transitions) - generate ZK proofs
circuit publicKey(round: Field, sk: Bytes<32>): Bytes<32> {
    return persistentHash<Vector<3, Bytes<32>>>(
        [pad(32, "midnight:examples:lock:pk"), round as Bytes<32>, sk]
    );
}

export circuit set(v: Uint<64>): [] {
    assert(state == State.UNSET);
    const sk = secretKey();
    const pk = publicKey(round, sk);
    authority = disclose(pk);
    value = disclose(v);
    state = State.SET;
}
```

## 2. Defining Circuits in Compact

Circuits are functions that execute on-chain and generate zero-knowledge proofs. They define state transitions and validation logic.

### Circuit Syntax

```compact
export circuit functionName(param1: Type1, param2: Type2): ReturnType {
    // Circuit logic
    // Can call witnesses
    // Can use assertions
    // Must use disclose() for public outputs
}
```

### Circuit Examples

**Simple State Transition:**
```compact
export circuit increment(): [] {
    round.increment(1);
}
```

**With Witnesses and Assertions:**
```compact
export circuit post(customMessage: Opaque<"string">): [] {
    assert(state == State.VACANT, "Attempted to post to an occupied board");

    const sk = localSecretKey();
    const pk = publicKey(round, sk);

    authority = disclose(pk);
    message = disclose(customMessage);
    state = State.OCCUPIED;
    round.increment(1);
}
```

**Proof Verification in Circuits:**
```compact
export circuit proveOwnership(propertyId: Uint<32>): [] {
    const sk = localSecretKey();
    const commit = ownershipCommit(sk, propertyId);
    const path = findPath(commit);

    // Verify Merkle proof
    assert(merkleTreePathRoot(path) == ownershipCommitments.root(),
           "Invalid ownership proof");
}
```

## 3. Working with Commitments and Nullifiers

### Commitment Scheme Pattern

```compact
// Ledger declarations
export sealed ledger authority: Bytes<32>;
export ledger commitments: HistoricMerkleTree<10, Bytes<32>>;
export ledger nullifiers: Set<Bytes<32>>;

// Witness for private key
witness localSecretKey(): Bytes<32>;

// Helper circuit to generate commitment
circuit ownershipCommit(sk: Bytes<32>, propertyId: Uint<32>): Bytes<32> {
    return persistentHash<Vector<3, Bytes<32>>>([
        pad(32, "domain:ownership:commit"),
        sk,
        propertyId as Bytes<32>
    ]);
}

// Helper circuit to generate nullifier
circuit yieldNullifier(sk: Bytes<32>, propertyId: Uint<32>, cycle: Uint<32>): Bytes<32> {
    return persistentHash<Vector<4, Bytes<32>>>([
        pad(32, "domain:yield:nullifier"),
        sk,
        propertyId as Bytes<32>,
        cycle as Bytes<32>
    ]);
}

// Insert commitment into Merkle tree
export circuit issueShare(investorCommit: Bytes<32>): [] {
    commitments.insert(disclose(investorCommit));
}

// Claim with nullifier to prevent replay
export circuit claimYield(propertyId: Uint<32>, cycle: Uint<32>): [] {
    const sk = localSecretKey();
    const commit = ownershipCommit(sk, propertyId);
    const path = findPath(commit);
    const nullifier = yieldNullifier(sk, propertyId, cycle);

    // Verify Merkle proof
    assert(merkleTreePathRoot(path) == commitments.root());

    // Check nullifier hasn't been used
    assert(!nullifiers.has(nullifier), "Yield already claimed");

    // Add nullifier to prevent replay
    nullifiers.insert(disclose(nullifier));

    // Transfer funds...
}
```

### Commitment Functions

**Transient (temporary use, not stored):**
```compact
circuit transientCommit<T>(value: T, rand: Field): Field;
circuit transientHash<T>(value: T): Field;
```

**Persistent (suitable for on-chain storage):**
```compact
circuit persistentCommit<T>(value: T, rand: Bytes<32>): Bytes<32>;
circuit persistentHash<T>(value: T): Bytes<32>;
```

**Security Best Practices:**
- Use domain separation with unique prefixes
- Use persistent functions for values stored in ledger state
- persistentCommit already includes randomness, no need for disclose()
- Always validate witness inputs in circuits

## 4. Example: Privacy-Preserving Real Estate Contract

This complete example shows all key patterns: commitments, nullifiers, Merkle proofs, and witnesses.

```compact
pragma language_version >= 0.20;
import CompactStandardLibrary;

enum State { VACANT, ACTIVE }

// PUBLIC LEDGER STATE
export sealed ledger sponsor: Bytes<32>;
export ledger ownershipCommitments: HistoricMerkleTree<10, Bytes<32>>;
export ledger yieldClaimNullifiers: Set<Bytes<32>>;
export ledger rentalPoolAvailable: Uint<64>;
export ledger propertyCount: Counter;
export ledger shareCount: Counter;
export ledger yieldClaimCount: Counter;
export ledger state: State;

// PRIVATE WITNESSES
witness localSecretKey(): Bytes<32>;
witness findPath(commit: Bytes<32>): MerkleTreePath<10, Bytes<32>>;

// HELPER CIRCUITS
circuit publicKey(sk: Bytes<32>): Bytes<32> {
    return persistentHash<Vector<2, Bytes<32>>>([
        pad(32, "realestate:sponsor:pk"),
        sk
    ]);
}

circuit ownershipCommit(sk: Bytes<32>, propertyId: Uint<32>): Bytes<32> {
    return persistentHash<Vector<3, Bytes<32>>>([
        pad(32, "realestate:ownership:commit"),
        sk,
        propertyId as Bytes<32>
    ]);
}

circuit yieldNullifier(sk: Bytes<32>, propertyId: Uint<32>, cycle: Uint<32>): Bytes<32> {
    return persistentHash<Vector<4, Bytes<32>>>([
        pad(32, "realestate:yield:nullifier"),
        sk,
        propertyId as Bytes<32>,
        cycle as Bytes<32>
    ]);
}

// SPONSOR OPERATIONS
export circuit initialize(): [] {
    assert(state == State.VACANT, "Already initialized");
    const sk = localSecretKey();
    sponsor = disclose(publicKey(sk));
    state = State.ACTIVE;
}

export circuit issueShare(investorCommit: Bytes<32>): [] {
    assert(state == State.ACTIVE, "Not initialized");
    ownershipCommitments.insert(disclose(investorCommit));
    shareCount.increment(1);
}

export circuit registerProperty(): [] {
    propertyCount.increment(1);
}

export circuit depositRent(amount: Uint<64>): [] {
    rentalPoolAvailable = rentalPoolAvailable + amount;
}

// INVESTOR OPERATIONS
export circuit proveOwnership(propertyId: Uint<32>): [] {
    const sk = localSecretKey();
    const commit = ownershipCommit(sk, propertyId);
    const path = findPath(commit);

    assert(merkleTreePathRoot(path) == ownershipCommitments.root(),
           "Invalid ownership proof");
}

export circuit claimYield(propertyId: Uint<32>, cycle: Uint<32>, amount: Uint<64>): [] {
    const sk = localSecretKey();
    const commit = ownershipCommit(sk, propertyId);
    const path = findPath(commit);
    const nullifier = yieldNullifier(sk, propertyId, cycle);

    // Verify ownership via Merkle proof
    assert(merkleTreePathRoot(path) == ownershipCommitments.root(),
           "Not an owner");

    // Check nullifier hasn't been used (prevent replay)
    assert(!yieldClaimNullifiers.has(nullifier),
           "Yield already claimed for this cycle");

    // Check sufficient funds
    assert(rentalPoolAvailable >= amount, "Insufficient pool balance");

    // Update state
    yieldClaimNullifiers.insert(disclose(nullifier));
    rentalPoolAvailable = rentalPoolAvailable - amount;
    yieldClaimCount.increment(1);

    // Payment would be handled via token transfer...
}
```

## 5. Verifying Proofs in Compact

### Merkle Proof Verification

```compact
// Witness provides the path
witness findPath(commit: Bytes<32>): MerkleTreePath<10, Bytes<32>>;

// Circuit verifies the proof
export circuit verifyMembership(value: Bytes<32>): [] {
    const path = findPath(value);
    const computedRoot = merkleTreePathRoot(path);

    assert(computedRoot == commitments.root(),
           "Membership proof failed");
}
```

**MerkleTreePath Structure:**
```compact
struct MerkleTreePath<#n, T> {
    leaf: T;
    path: Vector<n, MerkleTreePathEntry>;
}
```

**Standard Library Functions:**
```compact
circuit merkleTreePathRoot<#n, T>(path: MerkleTreePath<n, T>): MerkleTreeDigest;
circuit merkleTreePathRootNoLeafHash<#n, T>(path: MerkleTreePath<n, T>): MerkleTreeDigest;
```

### Assertion-Based Verification

```compact
export circuit verify(condition: Boolean): [] {
    assert(condition, "Verification failed");
}
```

### Nullifier-Based Replay Prevention

```compact
export ledger nullifiers: Set<Bytes<32>>;

export circuit consumeProof(proof: Bytes<32>): [] {
    const nullifier = persistentHash(proof);

    assert(!nullifiers.has(nullifier), "Proof already consumed");

    nullifiers.insert(disclose(nullifier));
}
```

## 6. Data Types and Standard Library

### Primitive Types

**Unsigned Integers:**
```compact
Uint<8>    // 8-bit unsigned integer
Uint<16>   // 16-bit unsigned integer
Uint<32>   // 32-bit unsigned integer
Uint<64>   // 64-bit unsigned integer
Uint<256>  // 256-bit unsigned integer
```

**Bytes:**
```compact
Bytes<32>  // 32-byte array
Bytes<64>  // 64-byte array
Bytes<n>   // n-byte array (generic)
```

**Field:**
```compact
Field      // Native ZK field element (large prime order)
```

**Boolean:**
```compact
Boolean    // true or false
```

**Vector:**
```compact
Vector<3, Bytes<32>>   // Fixed-size vector of 3 elements
Vector<n, T>           // Generic vector of n elements of type T
```

**Opaque Types (for external data):**
```compact
Opaque<"string">       // JavaScript string, opaque to circuits
Opaque<"Uint8Array">   // JavaScript Uint8Array, opaque to circuits
```

### Ledger State Types (from CompactStandardLibrary)

**Counter:**
```compact
export ledger count: Counter;

count.increment(1);      // Increment by 1
count.increment(n);      // Increment by n
```

**Map:**
```compact
export ledger balances: Map<Bytes<32>, Uint<64>>;

balances.set(key, value);
let val = balances.get(key);
let exists = balances.has(key);
```

**Set:**
```compact
export ledger nullifiers: Set<Bytes<32>>;

nullifiers.insert(value);
let exists = nullifiers.has(value);
```

**List:**
```compact
export ledger items: List<Bytes<32>>;

items.push(value);
let item = items.get(index);
let len = items.length();
```

**MerkleTree:**
```compact
export ledger tree: MerkleTree<10, Bytes<32>>;  // Depth 10

tree.insert(value);
let root = tree.root();
```

**HistoricMerkleTree (preserves history for proofs):**
```compact
export ledger commitments: HistoricMerkleTree<10, Bytes<32>>;

commitments.insert(value);
let root = commitments.root();
```

### Standard Library Hash and Commitment Functions

**Hash Functions:**
```compact
// Circuit-optimized hash (not persistent across upgrades)
circuit transientHash<T>(value: T): Field;

// SHA-256 hash (persistent across upgrades)
circuit persistentHash<T>(value: T): Bytes<32>;
```

**Commitment Functions:**
```compact
// Circuit-optimized commitment
circuit transientCommit<T>(value: T, rand: Field): Field;

// SHA-256 commitment (persistent)
circuit persistentCommit<T>(value: T, rand: Bytes<32>): Bytes<32>;
```

**Utility Functions:**
```compact
// Pad string to fixed byte length
pad(32, "my-domain-separator"): Bytes<32>

// Type casting
value as Bytes<32>
round as Field
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
assert(state == State.VACANT, "Wrong state");
```

### Structs

```compact
struct Record {
    id: Uint<32>;
    owner: Bytes<32>;
    value: Uint<64>;
}

export ledger records: List<Record>;
```

## 7. Privacy Model: The Three Contexts

### 1. Ledger (Public)
- Stored on blockchain
- Visible to everyone
- Requires `export ledger` declaration
- Must use `disclose()` to write witness/circuit data

```compact
export ledger balance: Uint<64>;
```

### 2. Circuits (Zero-Knowledge Proofs)
- Execute on-chain with ZK proofs
- Private inputs/outputs unless disclosed
- Can call witnesses
- Can assert conditions

```compact
export circuit transfer(amount: Uint<64>): [] {
    const sk = secretKey();  // Private
    balance = disclose(amount);  // Public
}
```

### 3. Witnesses (Local/Private)
- Execute off-chain in TypeScript/JavaScript
- Never exposed on-chain
- Provide private data to circuits
- Cannot modify ledger directly

```compact
witness secretKey(): Bytes<32>;
witness findPath(commit: Bytes<32>): MerkleTreePath<10, Bytes<32>>;
```

## 8. The `disclose()` Function

The `disclose()` function is Compact's privacy mechanism. It explicitly marks when private data becomes public.

**Rules:**
- All circuit inputs are private by default
- All witness outputs are private by default
- To store in ledger: must `disclose()`
- To return from exported circuit: must `disclose()`
- To pass to another contract: must `disclose()`

**Examples:**

```compact
// CORRECT: Disclosing witness output before storing
export circuit storeBalance(): [] {
    const bal = getBalance();  // Private witness output
    balance = disclose(bal);   // Disclosed for public storage
}

// ERROR: Cannot store witness output without disclose
export circuit storeBalance(): [] {
    const bal = getBalance();
    balance = bal;  // COMPILATION ERROR!
}

// Commitment doesn't need disclose (has randomness)
export circuit commit(value: Uint<64>, salt: Bytes<32>): [] {
    const commitment = persistentCommit(value, salt);
    commitments.insert(commitment);  // No disclose needed
}

// Hash of witness needs disclose
export circuit storeHash(): [] {
    const secret = getSecret();  // From witness
    const hash = transientHash(secret);
    hashes.insert(disclose(hash));  // Must disclose
}
```

## 9. Complete RAG Contract Pattern

Based on the research, here's how to structure a privacy-preserving RAG contract:

```compact
pragma language_version >= 0.20;
import CompactStandardLibrary;

// Document commitments stored in Merkle tree
export ledger documentCommitments: HistoricMerkleTree<10, Bytes<32>>;

// Query nullifiers to prevent replay
export ledger queryNullifiers: Set<Bytes<32>>;

// Similarity proof verification results
export ledger verifiedQueries: Counter;

// Witnesses
witness localSecretKey(): Bytes<32>;
witness findDocPath(docCommit: Bytes<32>): MerkleTreePath<10, Bytes<32>>;
witness verifySimilarityProof(queryEmbed: Bytes<32>, docEmbed: Bytes<32>): Boolean;

// Helper: Create document commitment
circuit documentCommit(docHash: Bytes<32>, embedding: Bytes<32>): Bytes<32> {
    return persistentHash<Vector<3, Bytes<32>>>([
        pad(32, "rag:doc:commit"),
        docHash,
        embedding
    ]);
}

// Helper: Create query nullifier
circuit queryNullifier(sk: Bytes<32>, queryHash: Bytes<32>, timestamp: Uint<64>): Bytes<32> {
    return persistentHash<Vector<4, Bytes<32>>>([
        pad(32, "rag:query:nullifier"),
        sk,
        queryHash,
        timestamp as Bytes<32>
    ]);
}

// Store document commitment
export circuit addDocument(docCommit: Bytes<32>): [] {
    documentCommitments.insert(disclose(docCommit));
}

// Verify similarity proof and check document membership
export circuit querySimilar(
    docCommit: Bytes<32>,
    queryHash: Bytes<32>,
    timestamp: Uint<64>
): [] {
    const sk = localSecretKey();

    // Verify document is in the tree
    const path = findDocPath(docCommit);
    assert(merkleTreePathRoot(path) == documentCommitments.root(),
           "Document not found");

    // Create and check nullifier
    const nullifier = queryNullifier(sk, queryHash, timestamp);
    assert(!queryNullifiers.has(nullifier),
           "Query already processed");

    // Mark query as processed
    queryNullifiers.insert(disclose(nullifier));
    verifiedQueries.increment(1);
}
```

## Key Resources

### Official Documentation
- Main Docs: https://docs.midnight.network/develop/compact
- Language Reference: https://docs.midnight.network/develop/reference/compact/lang-ref
- Standard Library: https://docs.midnight.network/compact/standard-library/exports
- Tutorials: https://docs.midnight.network/getting-started/hello-world

### GitHub Examples
- Counter: https://github.com/midnightntwrk/example-counter
- Bulletin Board: https://github.com/midnightntwrk/example-bboard
- Community Examples: https://github.com/Olanetsoft/compact-by-example
- OpenZeppelin Contracts: https://github.com/OpenZeppelin/compact-contracts
- Real-World dApps: https://github.com/ayushsingh82/Midnight-dApps

### Community Resources
- Compact by Example: https://compact-by-example.org
- DEV.to Tutorials: Search "Midnight Compact"
- Midnight Forum: https://forum.midnight.network

## Summary

Midnight's Compact language provides powerful privacy-preserving capabilities through:

1. **Automatic ZK Proof Generation**: Write normal code, compiler generates proofs
2. **Privacy by Default**: Everything private unless explicitly disclosed
3. **Three-Context Model**: Clear separation of public ledger, ZK circuits, and private witnesses
4. **Rich Standard Library**: Built-in Merkle trees, sets, maps for privacy patterns
5. **Commitment Schemes**: Easy-to-use persistent hashing and commitments
6. **Nullifier Support**: Built-in replay attack prevention
7. **TypeScript Integration**: Seamless integration with TypeScript/JavaScript ecosystem

For a privacy-preserving RAG contract, the key patterns are:
- Store document commitments in HistoricMerkleTree
- Use Set for query nullifiers (replay prevention)
- Implement similarity proofs in witness functions (off-chain ML)
- Verify Merkle proofs in circuits for document membership
- Use persistent hashing for commitments with domain separation
