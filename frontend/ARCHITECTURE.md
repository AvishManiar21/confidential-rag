# ConfidentialRAG Frontend Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│                      (User Interface)                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (localhost:8501)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Streamlit Frontend                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    app.py                            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │  │
│  │  │  Upload  │ │  Query   │ │Documents │ │Settings│ │  │
│  │  │   Tab    │ │   Tab    │ │   Tab    │ │  Tab   │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │         Session State Management             │  │  │
│  │  │  - backend_url                               │  │  │
│  │  │  - top_k, similarity_threshold               │  │  │
│  │  │  - last_query_result                         │  │  │
│  │  │  - current_page                              │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │                 utils.py                             │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │          API Client Functions                │   │  │
│  │  │  - check_backend_health()                    │   │  │
│  │  │  - upload_document()                         │   │  │
│  │  │  - query_rag()                               │   │  │
│  │  │  - list_documents()                          │   │  │
│  │  │  - delete_document()                         │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │        Helper Functions                      │   │  │
│  │  │  - format_filesize()                         │   │  │
│  │  │  - format_timestamp()                        │   │  │
│  │  │  - validate_pdf_file()                       │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │              components.py                           │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │          UI Components                       │   │  │
│  │  │  - render_document_card()                    │   │  │
│  │  │  - render_proof_visualization()              │   │  │
│  │  │  - render_query_result_card()                │   │  │
│  │  │  - render_status_badge()                     │   │  │
│  │  │  - render_hash_display()                     │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON (httpx async)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                           │
│                    (localhost:8001)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                       │  │
│  │  - GET  /health                                      │  │
│  │  - POST /documents (upload)                          │  │
│  │  - GET  /documents (list)                            │  │
│  │  - GET  /documents/{id}                              │  │
│  │  - DELETE /documents/{id}                            │  │
│  │  - POST /query                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
app.py (Main Application)
│
├── Sidebar
│   ├── Health Status
│   ├── Service Details
│   └── Quick Settings
│
├── Tab 1: Upload Documents
│   ├── File Uploader
│   ├── Upload Button
│   ├── Progress Indicator
│   ├── Document Details
│   └── Commitment Display
│
├── Tab 2: Query RAG
│   ├── Query Input
│   ├── Settings (Top-K, Threshold)
│   ├── Submit Button
│   ├── Answer Display
│   ├── Metrics Row
│   ├── Retrieved Documents
│   └── ZK Proof Visualization
│       ├── Merkle Tree
│       ├── Hashes
│       └── Commitments
│
├── Tab 3: Documents
│   ├── Filters & Controls
│   ├── Document List
│   │   └── Document Card (for each)
│   │       ├── Metadata
│   │       ├── Hashes
│   │       └── Delete Button
│   └── Pagination Controls
│
└── Tab 4: Settings
    ├── Backend Configuration
    ├── Query Settings
    ├── Display Settings
    └── System Information
```

## Data Flow

### Document Upload Flow

```
User selects PDF
       │
       ▼
app.py: render_upload_tab()
       │
       ▼
utils.py: upload_document()
       │
       ├─── Validate file
       ├─── Prepare multipart data
       └─── POST /documents
              │
              ▼
       Backend processes:
         - Extract text
         - Create chunks
         - Generate embeddings
         - Create commitments
         - Build Merkle tree
         - Submit to Midnight
              │
              ▼
       Return document metadata
              │
              ▼
Display results:
  - Document ID
  - File hash
  - Commitment
  - Merkle root
  - Success message
```

### Query Flow

```
User enters query
       │
       ▼
app.py: render_query_tab()
       │
       ├─── Get query text
       ├─── Get settings (top_k, threshold)
       └─── Query button clicked
              │
              ▼
utils.py: query_rag()
       │
       ├─── Build query payload
       └─── POST /query
              │
              ▼
       Backend processes:
         - Generate query hash
         - Hybrid retrieval (BM25 + vector)
         - Generate answer (Ollama)
         - Create ZK proof
         - Calculate metrics
              │
              ▼
       Return query response:
         - Answer
         - Retrieved documents
         - Proof
         - Metrics
              │
              ▼
Display results:
  - Answer text
  - Metrics (RAGAS, similarity, time)
  - Retrieved documents
  - ZK proof visualization
```

### Document List Flow

```
User navigates to Documents tab
       │
       ▼
app.py: render_documents_tab()
       │
       ├─── Get page number
       ├─── Get page size
       └─── Get filters
              │
              ▼
utils.py: list_documents()
       │
       ├─── Build query params
       └─── GET /documents?page=1&page_size=10
              │
              ▼
       Backend queries:
         - PostgreSQL for documents
         - Apply filters
         - Paginate results
              │
              ▼
       Return document list:
         - Total count
         - Documents array
         - Page info
              │
              ▼
Display results:
  - For each document:
    └─── components.py: render_document_card()
  - Pagination controls
```

## State Management

### Session State Variables

```python
st.session_state = {
    # Configuration
    "backend_url": "http://localhost:8001",
    "top_k": 5,
    "similarity_threshold": 0.6,
    "show_debug_info": False,

    # UI State
    "current_page": 1,
    "last_query_result": None,

    # Temporary State
    "confirm_delete_<id>": False,
    "show_doc_<id>": False
}
```

### State Lifecycle

1. **Initialization** (utils.py: init_session_state())
   - Set default values
   - Check for existing state
   - Preserve user preferences

2. **Updates** (throughout app.py)
   - User interactions modify state
   - Widget callbacks update state
   - API responses cached in state

3. **Persistence**
   - State persists during session
   - Lost on browser refresh
   - No server-side storage

## API Communication

### HTTP Client Architecture

```
Streamlit App (Sync)
       │
       ▼
asyncio.run()
       │
       ▼
Async Function (utils.py)
       │
       ▼
httpx.AsyncClient
       │
       ├─── Connection pooling
       ├─── Timeout handling
       ├─── Retry logic
       └─── Error handling
              │
              ▼
Backend API (FastAPI)
```

### Error Handling Strategy

```
API Call
   │
   ├─── Success
   │       └─── Return data
   │
   ├─── HTTPStatusError
   │       ├─── 400: Show validation error
   │       ├─── 404: Show not found
   │       └─── 500: Show server error
   │
   ├─── ConnectError
   │       └─── Show "Backend offline"
   │
   ├─── TimeoutError
   │       └─── Show "Request timeout"
   │
   └─── Generic Exception
           └─── Show generic error + debug info
```

## File Structure

```
frontend/
│
├── Core Application
│   ├── app.py              # Main Streamlit app
│   ├── utils.py            # API client & helpers
│   └── components.py       # Reusable UI components
│
├── Configuration
│   ├── .streamlit/
│   │   └── config.toml     # Streamlit config
│   ├── requirements.txt    # Python dependencies
│   └── .gitignore         # Git exclusions
│
├── Docker
│   ├── Dockerfile         # Container definition
│   ├── .dockerignore      # Docker build exclusions
│   └── run.sh            # Startup script
│
├── Documentation
│   ├── README.md          # Full documentation
│   ├── QUICKSTART.md      # Quick start guide
│   ├── DEVELOPMENT.md     # Developer guide
│   ├── ARCHITECTURE.md    # This file
│   └── IMPLEMENTATION_SUMMARY.md  # Implementation details
│
└── Testing
    └── test_connection.py  # Backend connection test
```

## Technology Stack

### Frontend Framework
- **Streamlit 1.39.0**
  - Web framework
  - UI components
  - State management
  - Real-time updates

### HTTP Client
- **httpx 0.27.0**
  - Async HTTP requests
  - Connection pooling
  - Timeout handling
  - Error handling

### Data Processing
- **pandas 2.2.0**
  - Data manipulation
  - Table display
  - Data formatting

### Utilities
- **python-dateutil 2.9.0**
  - Date/time parsing
  - Timestamp formatting

- **typing-extensions 4.12.0**
  - Type hints
  - Type checking

### Runtime
- **Python 3.11+**
  - Async/await support
  - Performance optimizations
  - Modern syntax

## Design Patterns

### 1. Separation of Concerns

- **app.py**: UI and user interactions
- **utils.py**: API communication and data processing
- **components.py**: Reusable UI elements

### 2. Async/Await Pattern

```python
async def api_call():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Called from sync Streamlit context
result = asyncio.run(api_call())
```

### 3. Component Pattern

```python
def render_component(data):
    with st.container():
        # Render UI
        pass

# Used in app
render_component(data)
```

### 4. Error Handling Pattern

```python
try:
    result = api_call()
    if result:
        # Success path
    else:
        # Error path
except Exception as e:
    # Handle error
```

### 5. State Management Pattern

```python
# Initialize
if "key" not in st.session_state:
    st.session_state.key = default_value

# Read
value = st.session_state.key

# Update
st.session_state.key = new_value
```

## Security Architecture

### Input Validation

```
User Input
    │
    ├── File Upload
    │   ├── Type check (PDF only)
    │   ├── Size check (max 50MB)
    │   └── Content validation
    │
    ├── Query Text
    │   ├── Length check (max 2000 chars)
    │   └── Content sanitization
    │
    └── Settings
        ├── URL validation
        └── Range validation
```

### Data Flow Security

```
Browser
   │ HTTPS (production)
   ▼
Streamlit
   │ Internal API
   ▼
Utils (Validation)
   │ HTTP/JSON
   ▼
Backend API
   │ Database queries
   ▼
PostgreSQL/ChromaDB
```

## Performance Considerations

### 1. Async Operations
- Non-blocking API calls
- Concurrent requests possible
- Better resource utilization

### 2. Pagination
- Limit data transfer
- Server-side pagination
- Lazy loading

### 3. Caching
- Session state for results
- No redundant API calls
- User preference persistence

### 4. Progressive Loading
- Load data on demand
- Show loading states
- Stream large results

## Scalability

### Current Limitations
- Single instance
- No load balancing
- Session state in memory
- No distributed caching

### Future Improvements
- Multiple frontend instances
- Redis for session storage
- Load balancer (nginx)
- CDN for static assets

## Monitoring & Observability

### Current Monitoring
- Backend health checks
- Service status display
- Error logging (console)
- Performance metrics (response time)

### Future Enhancements
- Application monitoring (Sentry)
- Usage analytics
- Performance tracking
- Error aggregation

## Deployment Architecture

### Docker Compose Deployment

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────┐    ┌──────────┐         │
│  │ Frontend │◄───┤ Backend  │         │
│  │  :8501   │    │  :8000   │         │
│  └────┬─────┘    └────┬─────┘         │
│       │               │                │
│       │               ├──► PostgreSQL  │
│       │               ├──► ChromaDB    │
│       │               ├──► Ollama      │
│       │               └──► Midnight    │
│       │                                │
└───────┼────────────────────────────────┘
        │
        ▼
   Host :8501
```

### Production Deployment

```
Internet
    │
    ▼
Load Balancer (nginx)
    │
    ├──► Frontend Instance 1
    ├──► Frontend Instance 2
    └──► Frontend Instance 3
            │
            ▼
    Backend API (load balanced)
            │
            ├──► PostgreSQL (primary + replicas)
            ├──► ChromaDB (clustered)
            └──► Ollama (distributed)
```

## Integration Points

### Backend API
- RESTful JSON API
- Health checks
- Document operations
- Query processing
- Proof generation

### Services (via Backend)
- PostgreSQL: Document metadata
- ChromaDB: Vector embeddings
- Ollama: LLM inference
- Midnight: Blockchain verification

## Summary

The frontend architecture is designed for:

1. **Simplicity**: Easy to understand and maintain
2. **Modularity**: Separated concerns, reusable components
3. **Scalability**: Ready for horizontal scaling
4. **Security**: Input validation, error handling
5. **Performance**: Async operations, caching, pagination
6. **User Experience**: Responsive, intuitive, informative
7. **Maintainability**: Well-documented, tested, organized

The architecture supports the current requirements while being flexible enough to accommodate future enhancements.
