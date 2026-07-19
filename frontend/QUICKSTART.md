# ConfidentialRAG Frontend - Quick Start Guide

Get the frontend running in under 5 minutes!

## Option 1: Docker Compose (Recommended)

The easiest way to run the entire stack:

```bash
# From project root
cd C:\dev\Midnight_Hackathon\confidential-rag

# Start all services (including frontend)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f frontend
```

**Access the app**: http://localhost:8501

## Option 2: Local Development

For frontend development with hot-reload:

### Prerequisites
- Python 3.11+
- Backend running (see backend README)

### Steps

1. **Navigate to frontend directory**
```bash
cd C:\dev\Midnight_Hackathon\confidential-rag\frontend
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the app**
```bash
streamlit run app.py
```

5. **Open browser**
- Navigate to: http://localhost:8501
- The app will auto-reload when you edit files

## Option 3: Docker (Frontend Only)

Run just the frontend container:

```bash
cd frontend

# Build image
docker build -t confidential-rag-frontend .

# Run container
docker run -p 8501:8501 \
  -e BACKEND_URL=http://localhost:8001 \
  confidential-rag-frontend
```

**Access the app**: http://localhost:8501

## First Steps

Once the app is running:

1. **Check Backend Connection**
   - Look at the sidebar
   - Should show "✓ Healthy" if backend is running
   - If "✗ Backend Offline", check:
     - Backend is running
     - Backend URL is correct (Settings tab)
     - Network connectivity

2. **Upload a Document**
   - Go to "Upload" tab
   - Click "Browse files"
   - Select a PDF file
   - Click "Upload and Process"
   - Wait for processing (1-5 minutes)

3. **Query the System**
   - Go to "Query" tab
   - Enter a question about your document
   - Click "Submit Query"
   - Review the answer and ZK proof

4. **Manage Documents**
   - Go to "Documents" tab
   - View all uploaded documents
   - Click to expand and see details
   - Delete documents if needed

## Troubleshooting

### Backend Offline
```bash
# Check if backend is running
curl http://localhost:8001/health

# If not running, start backend
cd ../backend
docker-compose up backend -d
```

### Port Already in Use
```bash
# Option 1: Stop other service on port 8501
# Windows
netstat -ano | findstr :8501

# Linux/Mac
lsof -i :8501

# Option 2: Use different port
streamlit run app.py --server.port=8502
```

### Module Not Found
```bash
# Ensure virtual environment is activated
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Docker Build Fails
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache frontend
```

## Configuration

### Backend URL

The frontend needs to know where the backend is:

**Docker Compose**: Automatically set to `http://backend:8000`

**Local Development**:
1. Go to Settings tab
2. Set Backend URL to `http://localhost:8001`
3. Click "Test Connection"

**Environment Variable**:
```bash
# Linux/Mac
export BACKEND_URL=http://localhost:8001
streamlit run app.py

# Windows
set BACKEND_URL=http://localhost:8001
streamlit run app.py
```

### Streamlit Settings

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Upload limits
- Server settings
- Browser options

## Development Tips

### Hot Reload
Streamlit automatically reloads when you save files. No need to restart!

### Debug Mode
Enable debug information:
1. Go to Settings tab
2. Check "Show debug information"
3. Now you'll see detailed error messages

### Testing API Calls
Use the Python shell to test API functions:

```python
import asyncio
from utils import check_backend_health

# Test health check
health = asyncio.run(check_backend_health())
print(health)
```

### Adding New Features
1. Edit `app.py` for new tabs/UI
2. Edit `utils.py` for new API calls
3. Edit `components.py` for reusable components
4. Streamlit will auto-reload changes

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check backend [API documentation](../backend/README.md)
- Review [docker-compose.yml](../docker-compose.yml) for service configuration
- Explore [Streamlit docs](https://docs.streamlit.io) for customization

## Support

- **Issues**: Open in main repository
- **Questions**: Check backend logs and frontend console
- **Updates**: Pull latest changes and rebuild

Happy querying with ConfidentialRAG! 🔒
