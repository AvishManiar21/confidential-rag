# Quick Start Guide

Get the ConfidentialRAG backend running in minutes.

## Prerequisites

Make sure you have these services running:

1. **PostgreSQL** (port 5432)
2. **ChromaDB** (port 8000)
3. **Ollama** with llama2 model (port 11434)

## Step 1: Install Dependencies

```bash
cd confidential-rag/backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
# Minimum required:
# - DATABASE_URL
# - CHROMA_URL
# - OLLAMA_URL
```

## Step 3: Setup Database

Using Alembic (recommended):
```bash
alembic upgrade head
```

Or using the setup script:
```bash
python setup_db.py
```

## Step 4: Start the Server

```bash
# Development mode (with auto-reload)
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

## Step 5: Test the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

Or use the test script:
```bash
python test_api.py
```

## Quick Test with cURL

### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -F "file=@your_document.pdf"
```

### List Documents
```bash
curl "http://localhost:8000/api/v1/documents"
```

### Query RAG
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "top_k": 5,
    "generate_proof": true
  }'
```

## Troubleshooting

### PostgreSQL not running?
```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
createdb confidentialrag
```

### ChromaDB not running?
```bash
# Install ChromaDB
pip install chromadb

# Run ChromaDB server
chroma run --host localhost --port 8000
```

### Ollama not installed?
```bash
# Install Ollama from https://ollama.ai

# Pull llama2 model
ollama pull llama2

# Verify it's running
curl http://localhost:11434/api/tags
```

### Port already in use?
Change the port in `run.py` or use:
```bash
uvicorn app.main:app --port 8001
```

## Next Steps

1. **Upload Documents**: Use the `/documents` endpoint to upload PDFs
2. **Query RAG**: Use the `/query` endpoint to ask questions
3. **Check Proofs**: Verify ZK proofs are generated
4. **Monitor Logs**: Watch the console for processing details
5. **Explore API**: Visit `/docs` for interactive documentation

## Development Workflow

```bash
# Format code
black app/

# Run tests
pytest tests/ -v

# Check types
mypy app/

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Production Deployment

```bash
# Build Docker image
docker build -t confidential-rag-backend .

# Run container
docker run -p 8000:8000 --env-file .env confidential-rag-backend

# Or use docker-compose
docker-compose up -d
```

## Support

- Check logs for errors
- Verify all services are running
- Check `.env` configuration
- Review API documentation at `/docs`
- See full README.md for detailed information
