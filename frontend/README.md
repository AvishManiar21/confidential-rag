# ConfidentialRAG Frontend

A modern, user-friendly web interface for the ConfidentialRAG system built with Streamlit.

## Features

### Document Management
- **Upload PDFs**: Upload and process PDF documents with real-time progress tracking
- **View Documents**: Browse all uploaded documents with detailed metadata
- **Delete Documents**: Remove documents and their associated embeddings
- **Cryptographic Commitments**: View document hashes, commitments, and Merkle roots

### RAG Query Interface
- **Natural Language Queries**: Ask questions about your documents
- **Similarity Search**: Hybrid retrieval with BM25 and vector search
- **Answer Generation**: LLM-powered answer synthesis with source attribution
- **Zero-Knowledge Proofs**: Cryptographic proof of answer authenticity
- **Performance Metrics**: RAGAS scores, similarity metrics, and response times

### Zero-Knowledge Features
- **Merkle Proofs**: Hierarchical proof structure for document authenticity
- **Commitment Verification**: Verify document commitments against blockchain
- **Proof Visualization**: Interactive display of proof components
- **Nullifier Tracking**: Query privacy through nullifiers

### System Monitoring
- **Health Status**: Real-time backend service health checks
- **Service Status**: Monitor database, ChromaDB, Midnight, and Ollama
- **Performance Tracking**: Response times and system metrics

## Quick Start

### Prerequisites
- Python 3.11+
- Backend API running (see backend README)
- Docker (optional)

### Local Development

1. **Install Dependencies**
```bash
cd frontend
pip install -r requirements.txt
```

2. **Configure Backend URL**

Edit the backend URL in the Settings tab or set it in session:
- Default: `http://localhost:8001`
- Docker: `http://backend:8000`

3. **Run Application**
```bash
streamlit run app.py
```

4. **Access Interface**

Open your browser to: http://localhost:8501

### Docker Deployment

1. **Build Image**
```bash
docker build -t confidential-rag-frontend .
```

2. **Run Container**
```bash
docker run -p 8501:8501 \
  -e BACKEND_URL=http://backend:8000 \
  confidential-rag-frontend
```

### Using Docker Compose

The frontend is included in the main docker-compose.yml:

```bash
# From project root
docker-compose up frontend
```

Access at: http://localhost:8501

## Usage Guide

### Uploading Documents

1. Navigate to the **Upload** tab
2. Click **Browse files** and select a PDF
3. Click **Upload and Process**
4. Wait for processing to complete (may take 1-5 minutes)
5. View the generated commitments and Merkle root

**Processing Steps:**
- Text extraction from PDF
- Chunking (1000 chars with 200 char overlap)
- Embedding generation (384-dim vectors)
- Commitment creation for each chunk
- Merkle tree construction
- Blockchain submission to Midnight

### Querying Documents

1. Navigate to the **Query** tab
2. Enter your question in natural language
3. Adjust settings:
   - **Top-K**: Number of documents to retrieve (1-20)
   - **Similarity Threshold**: Minimum score (0.0-1.0)
   - **Generate ZK Proof**: Enable/disable proof generation
4. Click **Submit Query**
5. Review results:
   - Generated answer
   - Retrieved documents with scores
   - Zero-knowledge proof (if enabled)
   - Performance metrics

**Query Features:**
- Hybrid retrieval (BM25 + vector search)
- Source attribution with chunk IDs
- Similarity scoring
- RAGAS quality metrics
- Cryptographic proof of authenticity

### Managing Documents

1. Navigate to the **Documents** tab
2. View all uploaded documents
3. Filter by processed status
4. Adjust pagination (10-100 items per page)
5. Expand documents to view details:
   - Metadata (filename, size, chunks)
   - Processing status
   - Blockchain transaction info
   - Cryptographic hashes
6. Delete documents (requires confirmation)

### Configuring Settings

1. Navigate to the **Settings** tab
2. Configure:
   - **Backend URL**: API endpoint
   - **Default Top-K**: Results per query
   - **Default Similarity Threshold**: Minimum score
   - **Debug Mode**: Show detailed errors
3. View system information
4. Test backend connection
5. Reset to defaults if needed

## Configuration

### Backend URL

The frontend connects to the backend API via HTTP. Configure the URL in:

1. **Settings Tab**: Change at runtime
2. **Session State**: `st.session_state.backend_url`
3. **Environment Variable**: Set `BACKEND_URL` (future enhancement)

**Default URLs:**
- Local development: `http://localhost:8001`
- Docker compose: `http://backend:8000`
- Production: Your deployed backend URL

### Query Settings

**Top-K Results (1-20)**
- Number of document chunks to retrieve
- Higher values: More context, slower processing
- Lower values: Faster, less context
- Recommended: 5-10

**Similarity Threshold (0.0-1.0)**
- Minimum similarity score for results
- Higher values: More relevant, fewer results
- Lower values: More results, lower quality
- Recommended: 0.6-0.7

**ZK Proof Generation**
- Enable: Generate cryptographic proof (adds ~100-500ms)
- Disable: Faster queries without proof

## Architecture

### Frontend Stack
- **Streamlit**: Web framework
- **httpx**: Async HTTP client
- **Python 3.11**: Runtime environment

### Communication
- **REST API**: JSON over HTTP
- **Async Operations**: Non-blocking I/O
- **Timeout Handling**: Configurable timeouts
- **Error Recovery**: Retry logic with backoff

### State Management
- **Session State**: User preferences and cache
- **Query Results**: Cached for reuse
- **Health Status**: Periodic checks

## API Endpoints Used

### Health Check
```
GET /health
```
Returns backend status and service availability.

### Upload Document
```
POST /documents
multipart/form-data: file
```
Uploads and processes a PDF document.

### List Documents
```
GET /documents?page=1&page_size=10&processed_only=false
```
Returns paginated document list.

### Get Document
```
GET /documents/{id}
```
Returns specific document details.

### Delete Document
```
DELETE /documents/{id}
```
Deletes document and embeddings.

### Query RAG
```
POST /query
{
  "query": "string",
  "top_k": 5,
  "similarity_threshold": 0.6,
  "generate_proof": true
}
```
Processes RAG query with optional ZK proof.

## Troubleshooting

### Cannot Connect to Backend

**Problem**: Health check fails, "Backend Offline" status

**Solutions:**
1. Verify backend is running: `docker-compose ps`
2. Check backend URL in Settings
3. Ensure network connectivity
4. Review backend logs: `docker-compose logs backend`

### Upload Fails

**Problem**: Document upload returns error

**Solutions:**
1. Check file format (PDF only)
2. Verify file size (max 50MB)
3. Ensure sufficient backend resources
4. Check backend logs for errors
5. Verify ChromaDB and Ollama are running

### Query Returns No Results

**Problem**: Query completes but returns empty results

**Solutions:**
1. Lower similarity threshold
2. Increase Top-K value
3. Rephrase query
4. Verify documents are processed
5. Check document content relevance

### Proof Verification Fails

**Problem**: ZK proof generated but not verified

**Solutions:**
1. Check Midnight connection in health status
2. Verify document commitments exist
3. Review backend logs for verification errors
4. Ensure Midnight network is accessible

### Slow Performance

**Problem**: Queries take too long to process

**Solutions:**
1. Reduce Top-K value
2. Increase similarity threshold
3. Disable proof generation for testing
4. Check backend resource usage
5. Verify Ollama model is loaded

## Development

### Project Structure
```
frontend/
├── app.py                 # Main Streamlit application
├── utils.py              # Utility functions and API calls
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container definition
├── .streamlit/
│   └── config.toml      # Streamlit configuration
└── README.md            # This file
```

### Adding Features

1. **New Tab**: Add to `st.tabs()` and create `render_*_tab()` function
2. **New API Call**: Add async function to `utils.py`
3. **New Component**: Create reusable component in `utils.py`
4. **Styling**: Update CSS in `app.py` markdown block

### Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run app.py

# Access at http://localhost:8501
```

### Building Docker Image

```bash
# Build
docker build -t confidential-rag-frontend:latest .

# Run
docker run -p 8501:8501 confidential-rag-frontend:latest

# Test
curl http://localhost:8501/_stcore/health
```

## Security Considerations

### Data Privacy
- No document content stored in frontend
- All data transmitted via HTTPS in production
- Session state cleared on browser close

### Authentication
- Currently no authentication (development only)
- Add authentication middleware for production
- Use secure session tokens

### Input Validation
- File type validation (PDF only)
- File size limits (50MB)
- Query length limits (2000 chars)
- SQL injection prevention via API

## Performance Optimization

### Frontend
- Async API calls for non-blocking UI
- Cached query results in session state
- Pagination for large document lists
- Lazy loading of document details

### Backend Communication
- Configurable timeouts
- Connection pooling via httpx
- Retry logic with exponential backoff
- Request compression

## Contributing

When adding features to the frontend:

1. Follow Streamlit best practices
2. Use async functions for API calls
3. Add error handling with user-friendly messages
4. Update this README with new features
5. Test with backend API
6. Ensure mobile responsiveness

## License

Part of the ConfidentialRAG project. See main repository for license information.

## Support

For issues, questions, or contributions:
- Open an issue in the main repository
- Check backend README for API documentation
- Review Streamlit documentation for UI customization
