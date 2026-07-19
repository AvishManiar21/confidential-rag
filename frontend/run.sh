#!/bin/bash
# Startup script for ConfidentialRAG Frontend

set -e

echo "Starting ConfidentialRAG Frontend..."

# Set default backend URL if not provided
export BACKEND_URL=${BACKEND_URL:-http://localhost:8001}

echo "Backend URL: $BACKEND_URL"

# Run Streamlit
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
