# ConfidentialRAG Frontend - Development Guide

This guide covers development workflows, architecture, and best practices for the ConfidentialRAG frontend.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip and virtualenv
- Git
- Docker (for backend services)
- Code editor (VS Code recommended)

### Initial Setup

1. **Clone and navigate**
```bash
cd C:\dev\Midnight_Hackathon\confidential-rag\frontend
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate environment**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Verify installation**
```bash
pip list | grep streamlit
```

6. **Test backend connection**
```bash
python test_connection.py
```

7. **Run development server**
```bash
streamlit run app.py
```

## Project Structure

```
frontend/
├── app.py                    # Main Streamlit application
├── utils.py                  # API client and helper functions
├── components.py             # Reusable UI components
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container definition
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── .dockerignore            # Docker build exclusions
├── .gitignore               # Git exclusions
├── run.sh                   # Startup script
├── test_connection.py       # Backend connection test
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
└── DEVELOPMENT.md           # This file
```

### File Responsibilities

**app.py**
- Main application entry point
- Tab navigation and routing
- Page layouts and UI structure
- Event handling and user interactions

**utils.py**
- Backend API communication
- Data formatting helpers
- Error handling
- Session state management

**components.py**
- Reusable UI components
- Consistent styling
- Common patterns
- Visual elements

## Architecture

### Communication Flow

```
┌─────────────┐
│   Browser   │
│  (User UI)  │
└──────┬──────┘
       │
       │ HTTP (localhost:8501)
       │
┌──────▼──────────┐
│   Streamlit     │
│   Frontend      │
│   (app.py)      │
└──────┬──────────┘
       │
       │ HTTP/JSON (httpx)
       │
┌──────▼──────────┐
│   FastAPI       │
│   Backend       │
│   (port 8001)   │
└─────────────────┘
```

### State Management

Streamlit uses session state to persist data across reruns:

```python
# Initialize state
st.session_state.backend_url = "http://localhost:8001"

# Read state
url = st.session_state.backend_url

# Update state
st.session_state.backend_url = new_url
```

**Session State Variables:**
- `backend_url`: Backend API endpoint
- `top_k`: Default number of results
- `similarity_threshold`: Default similarity threshold
- `current_page`: Document list pagination
- `last_query_result`: Cached query result
- `show_debug_info`: Debug mode toggle

### API Integration

All backend calls use `httpx.AsyncClient` for async operations:

```python
async def api_call():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{backend_url}/endpoint")
        response.raise_for_status()
        return response.json()

# Call from Streamlit
result = asyncio.run(api_call())
```

**Error Handling Pattern:**
```python
try:
    # API call
    response = await client.post(url, json=data)
    response.raise_for_status()
    return response.json()

except httpx.HTTPStatusError as e:
    st.error(f"API error: {e.response.status_code}")
    return None

except httpx.ConnectError:
    st.error("Cannot connect to backend")
    return None

except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
    return None
```

## Development Workflow

### Hot Reload

Streamlit automatically reloads when you save files. Just edit and save!

**Auto-reload triggers:**
- Editing Python files (.py)
- Changing config.toml
- Modifying requirements.txt

**Does NOT auto-reload:**
- Installing new packages (restart required)
- Environment variables (restart required)

### Testing Changes

1. **Edit code**
   - Modify app.py, utils.py, or components.py
   - Save file
   - Streamlit auto-reloads

2. **Test in browser**
   - Changes appear immediately
   - Check console for errors
   - Use Streamlit debug menu (top-right)

3. **Debug errors**
   - Enable debug mode in Settings tab
   - Check browser console (F12)
   - Review Streamlit logs in terminal

### Adding Features

#### New Tab

1. Add tab to `st.tabs()` in `app.py`:
```python
tabs = st.tabs(["Upload", "Query", "Documents", "Settings", "New Tab"])
```

2. Create render function:
```python
def render_new_tab():
    st.header("New Feature")
    # Your code here
```

3. Call in tab block:
```python
with tabs[4]:
    render_new_tab()
```

#### New API Endpoint

1. Add function to `utils.py`:
```python
async def new_api_call(param: str) -> Optional[Dict]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{get_backend_url()}/new-endpoint",
                json={"param": param}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        st.error(f"API error: {str(e)}")
        return None
```

2. Call from UI:
```python
result = asyncio.run(new_api_call("value"))
if result:
    st.success("Success!")
```

#### New Component

1. Add to `components.py`:
```python
def render_custom_component(data: Dict):
    with st.expander("Custom Component"):
        st.json(data)
```

2. Import and use:
```python
from components import render_custom_component

render_custom_component({"key": "value"})
```

## Styling

### Custom CSS

Add custom styles in `app.py`:

```python
st.markdown("""
    <style>
    .custom-class {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)
```

### Theme Configuration

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"        # Primary accent color
backgroundColor = "#ffffff"      # Main background
secondaryBackgroundColor = "#f0f2f6"  # Sidebar/secondary
textColor = "#262730"           # Text color
font = "sans serif"             # Font family
```

### Icons and Emojis

Use Unicode emojis for visual appeal:

```python
st.header("📤 Upload Documents")
st.success("✓ Success!")
st.error("✗ Error!")
st.warning("⚠ Warning")
st.info("ℹ Information")
```

Common icons:
- 📄 Document
- 🔍 Search
- 🔐 Security
- ⚙️ Settings
- 📊 Metrics
- 🌳 Tree
- 🔑 Key
- ✓ Success
- ✗ Error

## Best Practices

### Performance

**Do:**
- Use `@st.cache_data` for expensive computations
- Implement pagination for large lists
- Load data only when needed
- Use session state for caching

**Don't:**
- Load all documents at once
- Make API calls on every rerun
- Process large datasets in frontend
- Store large objects in session state

### User Experience

**Do:**
- Show loading spinners for async operations
- Provide clear error messages
- Use progress bars for long operations
- Confirm destructive actions
- Provide helpful tooltips

**Don't:**
- Leave users waiting without feedback
- Show technical error messages
- Allow destructive actions without confirmation
- Use jargon in UI text

### Code Quality

**Do:**
- Add type hints to functions
- Write docstrings for complex functions
- Handle errors gracefully
- Use meaningful variable names
- Keep functions focused and small

**Don't:**
- Catch and silence errors
- Use global variables
- Write monolithic functions
- Hardcode configuration values

### Security

**Do:**
- Validate user inputs
- Use HTTPS in production
- Sanitize displayed data
- Implement rate limiting (backend)

**Don't:**
- Store secrets in code
- Trust user input blindly
- Display sensitive information
- Expose backend errors to users

## Debugging

### Enable Debug Mode

1. Go to Settings tab
2. Check "Show debug information"
3. Detailed errors will appear

### Browser Console

Open browser dev tools (F12):
- Console tab shows JavaScript errors
- Network tab shows API requests
- Elements tab shows rendered HTML

### Streamlit Debugging

**Rerun button**: Top-right corner, forces manual reload

**Clear cache**: Settings → Clear cache

**Always rerun**: Settings → Run on save

### Common Issues

**State not persisting**
```python
# Wrong - uses local variable
value = "test"

# Right - uses session state
st.session_state.value = "test"
```

**Async function not working**
```python
# Wrong - calling async directly
result = my_async_function()

# Right - using asyncio.run
result = asyncio.run(my_async_function())
```

**Widget key conflicts**
```python
# Wrong - duplicate keys
st.button("Click", key="btn")
st.button("Click", key="btn")

# Right - unique keys
st.button("Click", key="btn1")
st.button("Click", key="btn2")
```

## Testing

### Manual Testing Checklist

- [ ] Health check shows all services healthy
- [ ] Document upload works with sample PDF
- [ ] Query returns results and generates proof
- [ ] Document list shows uploaded documents
- [ ] Document deletion works
- [ ] Settings update and persist
- [ ] Error messages are user-friendly
- [ ] Loading spinners appear during operations
- [ ] Pagination works correctly
- [ ] UI is responsive on different screen sizes

### Backend Connection Test

```bash
python test_connection.py
```

Should output:
```
✅ Connection successful!
✅ All services are healthy!
✅ All tests passed!
```

### API Testing

Use Python shell to test individual API calls:

```python
import asyncio
from utils import *

# Test health
asyncio.run(check_backend_health())

# Test document list
asyncio.run(list_documents(page=1, page_size=10))
```

## Deployment

### Docker Build

```bash
docker build -t confidential-rag-frontend:latest .
```

### Docker Run

```bash
docker run -p 8501:8501 \
  -e BACKEND_URL=http://backend:8000 \
  confidential-rag-frontend:latest
```

### Docker Compose

```bash
# From project root
docker-compose up frontend -d
```

### Production Checklist

- [ ] Set appropriate backend URL
- [ ] Configure HTTPS
- [ ] Add authentication
- [ ] Set file upload limits
- [ ] Enable CORS correctly
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Test error handling
- [ ] Optimize performance
- [ ] Document deployment

## Contributing

### Code Style

- Follow PEP 8 for Python code
- Use 4 spaces for indentation
- Keep lines under 100 characters
- Add docstrings to public functions
- Use type hints

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Update documentation
6. Submit PR with description

### Commit Messages

```
feat: Add document search functionality
fix: Correct pagination bug in document list
docs: Update development guide
style: Improve UI spacing and colors
refactor: Simplify API error handling
```

## Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [httpx Documentation](https://www.python-httpx.org)
- [Backend API Documentation](../backend/README.md)
- [Project README](../README.md)

## Support

For questions or issues:
1. Check this guide first
2. Review backend documentation
3. Check Streamlit docs
4. Open issue in repository
5. Contact development team

Happy developing! 🚀
