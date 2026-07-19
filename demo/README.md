# ConfidentialRAG Demo & Testing

Demo data, sample queries, and end-to-end testing for the ConfidentialRAG system.

## Overview

This directory contains:

- **Medical Abstracts**: 15 realistic medical research abstracts (demo dataset)
- **Sample Queries**: 10 pre-defined queries with expected results
- **Upload Script**: Automated demo data ingestion
- **Query Runner**: Execute queries and verify ZK proofs
- **E2E Tests**: Complete workflow validation

## Files

### Data Files

#### `medical-abstracts.json`

15 medical research abstracts covering diverse topics:

| ID | Topic | Keywords |
|----|-------|----------|
| med_001 | Metformin for Type 2 Diabetes | diabetes, metformin, HbA1c |
| med_002 | Antibiotic Resistance in HAP | MRSA, pneumonia, resistance |
| med_003 | ML for Sepsis Detection | machine learning, sepsis, ICU |
| med_004 | Mediterranean Diet & CVD | diet, cardiovascular, prevention |
| med_005 | Melanoma Immunotherapy | PD-1, CTLA-4, checkpoint inhibitors |
| med_006 | Ketogenic Diet for Epilepsy | epilepsy, ketogenic, pediatric |
| med_007 | CRISPR for Sickle Cell | CRISPR, gene editing, stem cell |
| med_008 | Long COVID Neurology | PASC, cognitive impairment, rehab |
| med_009 | Artificial Pancreas Systems | type 1 diabetes, closed-loop insulin |
| med_010 | Gut Microbiome & IBD | microbiome, FMT, ulcerative colitis |
| med_011 | Telemedicine Cost Analysis | telemedicine, chronic disease |
| med_012 | Temperature Management Post-Arrest | cardiac arrest, hypothermia |
| med_013 | Vitamin D & Respiratory Infection | vitamin D, immune function |
| med_014 | DOACs vs Warfarin | anticoagulation, stroke prevention |
| med_015 | Mindfulness for Chronic Pain | MBSR, pain management, fMRI |

**Structure**:
```json
{
  "id": "med_001",
  "title": "Paper title",
  "authors": ["Author 1", "Author 2"],
  "journal": "Journal name",
  "year": 2024,
  "abstract": "Full abstract text...",
  "keywords": ["keyword1", "keyword2"]
}
```

#### `sample-queries.json`

10 test queries with varying complexity:

| ID | Query Type | Description |
|----|------------|-------------|
| query_001 | Simple keyword | "Treatment options for type 2 diabetes" |
| query_002 | Medical terminology | "Immunotherapy for melanoma" |
| query_003 | Conceptual match | "Dietary interventions for CVD" |
| query_004 | Multi-concept | "ML predict sepsis in ICU" |
| query_005 | Yes/no question | "Antibiotic-resistant bacteria in hospitals" |
| query_006 | Current topic | "Long-term neurological effects of COVID-19" |
| query_007 | Specific population | "Drug-resistant epilepsy in children" |
| query_008 | Cutting-edge therapy | "Gene editing cure sickle cell" |
| query_009 | Microbiome-focused | "Role of gut bacteria in IBD" |
| query_010 | Supplement + prevention | "Vitamin D prevent respiratory infections" |

**Structure**:
```json
{
  "id": "query_001",
  "query": "What are the treatment options for type 2 diabetes?",
  "expected_docs": ["med_001"],
  "description": "Simple keyword match",
  "expected_concepts": ["metformin", "HbA1c"]
}
```

### Python Scripts

#### `upload-demo-data.py`

**Purpose**: Upload medical abstracts to backend for indexing.

**Features**:
- Color-coded progress output
- Health check before upload
- Rate limiting (500ms between uploads)
- Upload verification
- Success/failure tracking

**Usage**:
```bash
# Ensure backend is running
./scripts/start-all.sh

# Upload data
python demo/upload-demo-data.py

# Or via make
make demo-upload
```

**Output**:
```
[INFO] Checking backend health...
[SUCCESS] Backend is healthy!
[INFO] Loading demo data from medical-abstracts.json...
[SUCCESS] Loaded 15 medical abstracts
[INFO] Uploading 15 documents...

[1/15] Uploading: Efficacy of Metformin in Type 2 Diabetes...
  [SUCCESS] med_001: Efficacy of Metformin in Type 2 Diabetes... (ID: doc_abc123)

...

[SUCCESS] All documents uploaded successfully!
```

**Requirements**:
- Backend running at `http://localhost:8001`
- Python 3.10+
- `requests`, `colorama` packages

---

#### `run-demo-queries.py`

**Purpose**: Execute sample queries and verify ZK proofs.

**Features**:
- Runs all 10 sample queries
- Validates retrieval accuracy
- Verifies ZK proof generation
- Checks proof verification
- Measures execution time
- Saves results to `query-results.json`

**Usage**:
```bash
python demo/run-demo-queries.py

# Or via make
make demo-query
```

**Output**:
```
[INFO] Loading queries from sample-queries.json...
[SUCCESS] Loaded 10 sample queries

[1/10] Simple keyword match - should retrieve metformin study
  Query: 'What are the treatment options for type 2 diabetes?'
  [✓] Retrieved: ['med_001', 'med_009']
  [✓] Proof verified: True
  [✓] Execution time: 287ms

...

Query Results Summary:
  [SUCCESS] Passed: 10/10
```

**Verification Logic**:
1. Checks if expected documents are in top-k results
2. Validates ZK proof hash is generated
3. Confirms proof verification succeeded
4. Measures query latency

**Output File**: `demo/query-results.json`

---

#### `test-e2e.py`

**Purpose**: End-to-end testing of complete RAG workflow.

**Test Coverage**:
1. Backend health check
2. ChromaDB connectivity
3. Midnight network availability
4. Document upload
5. Document retrieval
6. Query execution
7. ZK proof generation
8. ZK proof verification
9. RAGAS quality metrics

**Usage**:
```bash
python demo/test-e2e.py

# Or via make
make demo-e2e
```

**Output**:
```
=== ConfidentialRAG - End-to-End Test Suite ===

[TEST] Testing backend health...
[PASS] Backend health check
       Version: 1.0.0

[TEST] Testing infrastructure...
[PASS] ChromaDB connectivity
[PASS] Midnight network

[TEST] Testing document upload...
[PASS] Document upload
       Document ID: doc_test123

[TEST] Testing query execution...
[PASS] Query execution
       Retrieved 3 docs, answer length: 245

[TEST] Testing ZK proof generation...
[PASS] Proof generation
       Proof hash: a3f5e8c9d2b4...

[TEST] Testing ZK proof verification...
[PASS] Proof verification
       Proof verified on-chain

Test Summary: 9/9 passed
All tests passed!
```

**Exit Codes**:
- `0`: All tests passed
- `1`: Some tests failed

**Cleanup**: Automatically deletes test documents

---

## Quick Start

### 1. Setup Environment

```bash
# Complete setup
./scripts/setup-all.sh

# Or manual setup
./scripts/setup-midnight.sh
./scripts/start-all.sh
```

### 2. Upload Demo Data

```bash
python demo/upload-demo-data.py
```

**Expected**: 15 documents uploaded successfully

### 3. Run Demo Queries

```bash
python demo/run-demo-queries.py
```

**Expected**: 10/10 queries passed with verified proofs

### 4. Run E2E Tests

```bash
python demo/test-e2e.py
```

**Expected**: 9/9 tests passed

### 5. Access Frontend

```bash
# Open in browser
http://localhost:8501

# Try queries:
# - "What medications treat diabetes?"
# - "How effective is immunotherapy for melanoma?"
# - "Can machine learning predict sepsis?"
```

## Testing Scenarios

### Scenario 1: Simple Keyword Match

**Query**: "What are the treatment options for type 2 diabetes?"

**Expected**:
- Retrieves `med_001` (Metformin study)
- Answer mentions metformin, HbA1c
- ZK proof verified
- Execution < 500ms

### Scenario 2: Complex Medical Terminology

**Query**: "How effective is immunotherapy for melanoma patients?"

**Expected**:
- Retrieves `med_005` (Melanoma immunotherapy)
- Answer mentions PD-1, CTLA-4, nivolumab
- High similarity score (>0.8)

### Scenario 3: Multi-Document Synthesis

**Query**: "What are cutting-edge treatments for genetic diseases?"

**Expected**:
- Retrieves `med_007` (CRISPR for sickle cell)
- May also retrieve related papers
- Answer synthesizes multiple sources

### Scenario 4: Zero-Knowledge Proof Verification

**What's Proven**:
1. **Similarity Threshold**: Query-document similarity > 0.6 (without revealing exact score)
2. **Document Authenticity**: Retrieved doc exists in commitment tree
3. **Context Quality**: RAGAS precision > threshold

**What's Hidden**:
- Actual query text
- Document embeddings
- Exact similarity scores
- User identity

## Verification Checklist

After running demo scripts, verify:

- [ ] All 15 documents uploaded without errors
- [ ] Documents indexed in ChromaDB (check logs)
- [ ] PostgreSQL contains document metadata
- [ ] Midnight blockchain has commitments
- [ ] All 10 queries return results
- [ ] ZK proofs generated for each query
- [ ] Proofs verified on-chain
- [ ] RAGAS metrics calculated
- [ ] Frontend displays results correctly

## Performance Benchmarks

Expected performance on modest hardware (4 CPU, 8GB RAM):

| Operation | Time | Notes |
|-----------|------|-------|
| Document upload | 500-800ms | Per document (with embedding) |
| Full dataset upload | 10-15s | 15 documents |
| Simple query | 200-400ms | BM25 + vector search |
| Complex query | 400-800ms | Multiple retrieval passes |
| ZK proof generation | 100-300ms | Commitment + Merkle proof |
| Proof verification | 50-150ms | On-chain verification |
| E2E test suite | 15-25s | All 9 tests |

## Troubleshooting

### Upload Fails

**Symptom**: `Backend not reachable`

**Solution**:
```bash
# Check backend is running
./scripts/health-check.sh

# Start if needed
./scripts/start-all.sh

# Check logs
docker-compose logs backend
```

### Queries Return No Results

**Symptom**: Empty `documents` array

**Solution**:
```bash
# Verify documents were indexed
curl http://localhost:8001/api/v1/documents

# Check ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Reinitialize if needed
./scripts/reset-db.sh
python demo/upload-demo-data.py
```

### Proof Verification Fails

**Symptom**: `proof_verified: false`

**Solution**:
```bash
# Check Midnight network
curl http://localhost:8080/health

# Restart network
./scripts/start-local-network.sh

# Redeploy contract
./scripts/deploy-contract.sh

# Check contract address in backend/.env
cat backend/.env | grep MIDNIGHT_CONTRACT_ADDRESS
```

### Slow Query Performance

**Symptom**: Execution time > 1 second

**Possible causes**:
1. **Ollama model not loaded**: First query loads model (slow)
2. **ChromaDB not indexed**: Rebuild index
3. **CPU throttling**: Check system resources
4. **Network latency**: Midnight RPC delays

**Solution**:
```bash
# Warm up Ollama
curl http://localhost:11434/api/generate \
  -d '{"model":"llama2","prompt":"test"}'

# Check ChromaDB status
curl http://localhost:8000/api/v1/collections

# Monitor resources
docker stats
```

## Advanced Usage

### Custom Dataset

```python
# Create custom abstracts
custom_data = [
    {
        "id": "custom_001",
        "title": "Your research title",
        "authors": ["Your Name"],
        "journal": "Your Journal",
        "year": 2024,
        "abstract": "Your abstract text...",
        "keywords": ["keyword1", "keyword2"]
    }
]

# Upload
import requests
for doc in custom_data:
    requests.post(
        "http://localhost:8001/api/v1/documents",
        json={
            "title": doc["title"],
            "content": doc["abstract"],
            "metadata": doc
        }
    )
```

### Batch Query Testing

```python
import json
from run_demo_queries import run_query

# Load custom queries
with open("custom-queries.json") as f:
    queries = json.load(f)

# Run batch
results = [run_query(q) for q in queries]

# Analyze
avg_time = sum(r["execution_time"] for r in results) / len(results)
success_rate = sum(r["success"] for r in results) / len(results)
```

### Proof Analysis

```bash
# Extract proof hashes
cat demo/query-results.json | jq '.[] | .proof_hash'

# Check on-chain
curl http://localhost:8080/api/v1/proofs/{proof_hash}

# Verify manually
curl http://localhost:8001/api/v1/proof/verify \
  -d '{"proof_hash": "abc123..."}'
```

## Integration with Frontend

The demo data is designed to work with the Streamlit UI:

1. **Document Browser**: View all 15 medical abstracts
2. **Query Interface**: Try sample queries
3. **Proof Viewer**: Inspect ZK proofs
4. **Metrics Dashboard**: RAGAS scores, retrieval quality

Access at: `http://localhost:8501`

## CI/CD Integration

Use demo scripts in automated testing:

```yaml
# GitHub Actions example
- name: Upload demo data
  run: python demo/upload-demo-data.py

- name: Run demo queries
  run: python demo/run-demo-queries.py

- name: E2E tests
  run: python demo/test-e2e.py

- name: Check results
  run: |
    if [ $? -eq 0 ]; then
      echo "Demo passed!"
    else
      echo "Demo failed!"
      exit 1
    fi
```

## Data Attribution

Medical abstracts are **synthetic but realistic**, based on:
- Public PubMed abstracts (public domain)
- Medical research summaries
- Clinical trial reports

**Not real research papers** - for demo purposes only.

## Privacy Considerations

This demo dataset:
- Contains **no real patient data**
- Uses **synthetic medical content**
- Simulates **privacy-preserving queries**

In production:
- Replace with real documents
- Implement access control
- Audit all queries
- Encrypt at rest
- Use testnet for development

## Next Steps

After running demos:

1. **Explore Frontend**: Try custom queries in UI
2. **Read Code**: Review RAG pipeline implementation
3. **Modify Dataset**: Add your own documents
4. **Tune Parameters**: Adjust similarity thresholds
5. **Stress Test**: Upload 100+ documents
6. **Deploy Testnet**: Use real Midnight testnet

## Support

Issues with demo scripts:
1. Check prerequisites installed
2. Review script output for errors
3. Consult main README troubleshooting
4. Open GitHub issue with logs

## License

MIT License - see LICENSE file for details.
