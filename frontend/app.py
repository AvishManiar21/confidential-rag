"""
ConfidentialRAG Frontend - Streamlit Application

A modern web interface for the ConfidentialRAG system with:
- Document upload and management
- RAG query interface with ZK proofs
- Document viewing and deletion
- System settings and health monitoring
"""

import streamlit as st
from datetime import datetime
import asyncio
from typing import Optional

# Import utilities
from utils import (
    init_session_state,
    check_backend_health,
    upload_document,
    query_rag,
    list_documents,
    delete_document,
    get_document,
    format_filesize,
    format_timestamp,
    copy_to_clipboard
)

# Page configuration
st.set_page_config(
    page_title="ConfidentialRAG",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 1rem;
    }

    /* Headers */
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
    }

    h2 {
        color: #2c3e50;
        margin-top: 1.5rem;
    }

    h3 {
        color: #34495e;
    }

    /* Status badges */
    .status-healthy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }

    .status-degraded {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }

    .status-unhealthy {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }

    /* Cards */
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }

    /* Code blocks */
    .stCodeBlock {
        background-color: #f8f9fa;
        border-radius: 0.25rem;
    }

    /* Success/Error messages */
    .success-message {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }

    .error-message {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }

    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 500;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #1f77b4;
        border-radius: 0.5rem;
        padding: 1rem;
    }

    /* Tables */
    .dataframe {
        width: 100%;
    }

    /* Info boxes */
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #0c5460;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with health status and settings."""
    with st.sidebar:
        st.title("🔒 ConfidentialRAG")
        st.markdown("---")

        # Health check
        st.subheader("System Status")
        health = asyncio.run(check_backend_health())

        if health:
            status = health.get("status", "unknown")
            if status == "healthy":
                st.markdown('<div class="status-healthy">✓ Healthy</div>', unsafe_allow_html=True)
            elif status == "degraded":
                st.markdown('<div class="status-degraded">⚠ Degraded</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-unhealthy">✗ Unhealthy</div>', unsafe_allow_html=True)

            st.caption(f"Version: {health.get('version', 'unknown')}")

            # Service status
            with st.expander("Service Details"):
                services = health.get("services", {})
                for service, status in services.items():
                    if "healthy" in status:
                        st.markdown(f"✓ **{service.title()}**: {status}")
                    else:
                        st.markdown(f"✗ **{service.title()}**: {status}")
        else:
            st.markdown('<div class="status-unhealthy">✗ Backend Offline</div>', unsafe_allow_html=True)
            st.error("Unable to connect to backend")

        st.markdown("---")

        # Quick settings
        st.subheader("Quick Settings")
        st.session_state.backend_url = st.text_input(
            "Backend URL",
            value=st.session_state.backend_url,
            help="Backend API endpoint"
        )

        if st.button("Test Connection"):
            with st.spinner("Testing..."):
                health = asyncio.run(check_backend_health())
                if health:
                    st.success("Connection successful!")
                else:
                    st.error("Connection failed!")

        st.markdown("---")
        st.caption("Built with Streamlit")
        st.caption("Zero-Knowledge RAG System")


def render_upload_tab():
    """Render document upload tab."""
    st.header("📤 Upload Documents")

    st.markdown("""
    Upload PDF documents to the ConfidentialRAG system. Documents are processed with:
    - Text extraction and chunking
    - Vector embeddings generation
    - Zero-knowledge commitment creation
    - Merkle tree construction
    - Midnight blockchain submission
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Select a PDF document to upload and process"
        )

        if uploaded_file:
            st.info(f"**File**: {uploaded_file.name} ({format_filesize(len(uploaded_file.getvalue()))})")

            if st.button("Upload and Process", type="primary"):
                with st.spinner("Processing document... This may take a few minutes."):
                    result = asyncio.run(upload_document(uploaded_file))

                    if result:
                        st.success("Document uploaded and processed successfully!")

                        # Display document details
                        doc = result.get("document", {})

                        with st.expander("Document Details", expanded=True):
                            col_a, col_b = st.columns(2)

                            with col_a:
                                st.metric("Document ID", doc.get("id"))
                                st.metric("File Size", format_filesize(doc.get("file_size", 0)))
                                st.metric("Chunks", doc.get("num_chunks", 0))

                            with col_b:
                                st.metric("Processed", "✓ Yes" if doc.get("processed") else "✗ No")
                                if doc.get("tx_hash"):
                                    st.metric("TX Hash", f"{doc.get('tx_hash')[:8]}...")
                                if doc.get("block_number"):
                                    st.metric("Block", doc.get("block_number"))

                        # Display commitments
                        with st.expander("Cryptographic Commitments"):
                            st.markdown("**File Hash**")
                            st.code(doc.get("file_hash", "N/A"))
                            copy_to_clipboard(doc.get("file_hash", ""), "file_hash")

                            st.markdown("**Document Commitment**")
                            st.code(doc.get("commitment", "N/A"))
                            copy_to_clipboard(doc.get("commitment", ""), "commitment")

                            st.markdown("**Merkle Root**")
                            st.code(doc.get("merkle_root", "N/A"))
                            copy_to_clipboard(doc.get("merkle_root", ""), "merkle_root")

                            st.markdown("**Embedding Hash**")
                            st.code(doc.get("embedding_hash", "N/A"))

                        st.balloons()
                    else:
                        st.error("Failed to upload document. Please check the logs.")

    with col2:
        st.subheader("Upload Guide")
        st.markdown("""
        **Steps:**
        1. Select PDF file
        2. Click Upload
        3. Wait for processing
        4. View commitments

        **Processing includes:**
        - Text extraction
        - Chunking (1000 chars)
        - Embedding generation
        - ZK commitment
        - Blockchain submission

        **Supported:**
        - PDF files only
        - Max size: 50MB
        - Multi-page docs
        """)


def render_query_tab():
    """Render RAG query tab."""
    st.header("🔍 Query RAG System")

    st.markdown("""
    Query the RAG system with natural language. Results include:
    - Retrieved document chunks
    - Generated answer with sources
    - Zero-knowledge proof of authenticity
    - Similarity scores and metrics
    """)

    # Query input
    query_text = st.text_area(
        "Enter your query",
        height=100,
        placeholder="Ask a question about your documents...",
        help="Enter a natural language question"
    )

    # Query settings
    col1, col2, col3 = st.columns(3)

    with col1:
        top_k = st.slider("Top-K Results", 1, 20, st.session_state.top_k)

    with col2:
        similarity_threshold = st.slider(
            "Similarity Threshold",
            0.0, 1.0,
            st.session_state.similarity_threshold,
            step=0.05
        )

    with col3:
        generate_proof = st.checkbox("Generate ZK Proof", value=True)

    # Submit button
    if st.button("Submit Query", type="primary", disabled=not query_text):
        with st.spinner("Processing query... Generating answer and proof..."):
            result = asyncio.run(query_rag(
                query_text,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                generate_proof=generate_proof
            ))

            if result:
                # Store in session state
                st.session_state.last_query_result = result

                st.success("Query processed successfully!")

                # Display answer
                st.subheader("📝 Answer")
                st.markdown(result.get("response", "No answer generated"))

                # Metrics
                col_a, col_b, col_c, col_d = st.columns(4)

                with col_a:
                    st.metric("Documents", len(result.get("retrieved_documents", [])))

                with col_b:
                    st.metric("Avg Similarity", f"{result.get('avg_similarity', 0):.3f}")

                with col_c:
                    ragas = result.get("ragas_score")
                    st.metric("RAGAS Score", f"{ragas:.3f}" if ragas else "N/A")

                with col_d:
                    st.metric("Response Time", f"{result.get('response_time_ms', 0)}ms")

                # Retrieved documents
                st.subheader("📚 Retrieved Documents")

                for idx, doc in enumerate(result.get("retrieved_documents", []), 1):
                    with st.expander(f"Document {idx} - Score: {doc.get('score', 0):.3f}"):
                        st.markdown(f"**Chunk ID**: `{doc.get('chunk_id')}`")
                        st.markdown(f"**Document ID**: {doc.get('document_id')}")
                        st.markdown(f"**Similarity Score**: {doc.get('score', 0):.4f}")

                        st.markdown("**Content**:")
                        st.text(doc.get("content", "")[:500] + "..." if len(doc.get("content", "")) > 500 else doc.get("content", ""))

                        metadata = doc.get("metadata", {})
                        if metadata:
                            st.markdown("**Metadata**:")
                            st.json(metadata)

                # ZK Proof
                if result.get("proof"):
                    st.subheader("🔐 Zero-Knowledge Proof")

                    proof = result["proof"]

                    col_p1, col_p2 = st.columns(2)

                    with col_p1:
                        verified = proof.get("verified", False)
                        if verified:
                            st.success("✓ Proof Verified")
                        else:
                            st.warning("⚠ Proof Not Verified")

                    with col_p2:
                        st.metric("Verification Time", f"{proof.get('verification_time_ms', 0)}ms")

                    with st.expander("Proof Details"):
                        st.markdown(f"**Proof Type**: {proof.get('proof_type')}")

                        proof_data = proof.get("proof_data", {})

                        st.markdown("**Query Hash**:")
                        st.code(proof_data.get("query_hash", "N/A"))

                        st.markdown("**Response Hash**:")
                        st.code(proof_data.get("response_hash", "N/A"))

                        st.markdown("**Merkle Root**:")
                        st.code(proof_data.get("merkle_root", "N/A"))

                        st.markdown("**Merkle Proof**:")
                        merkle_proof = proof_data.get("merkle_proof", [])
                        if merkle_proof:
                            for i, hash_val in enumerate(merkle_proof):
                                st.code(f"[{i}] {hash_val}")

                        st.markdown(f"**Number of Documents**: {proof_data.get('num_documents', 0)}")

                        commitments = proof_data.get("commitments", [])
                        if commitments:
                            st.markdown("**Document Commitments**:")
                            for i, commitment in enumerate(commitments[:5]):  # Show first 5
                                st.code(f"[{i}] {commitment}")
                            if len(commitments) > 5:
                                st.caption(f"... and {len(commitments) - 5} more")
            else:
                st.error("Failed to process query. Please try again.")

    # Show last result if available
    elif st.session_state.get("last_query_result"):
        st.info("Showing last query result. Submit a new query above.")
        result = st.session_state.last_query_result

        st.subheader("📝 Answer")
        st.markdown(result.get("response", ""))


def render_documents_tab():
    """Render document list and management tab."""
    st.header("📄 Document Management")

    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        processed_only = st.checkbox("Show processed only", value=False)

    with col2:
        page_size = st.selectbox("Items per page", [10, 25, 50, 100], index=0)

    with col3:
        if st.button("Refresh List"):
            st.rerun()

    # Fetch documents
    page = st.session_state.get("current_page", 1)

    with st.spinner("Loading documents..."):
        result = asyncio.run(list_documents(
            page=page,
            page_size=page_size,
            processed_only=processed_only
        ))

    if result:
        total = result.get("total", 0)
        documents = result.get("documents", [])
        total_pages = (total + page_size - 1) // page_size

        st.markdown(f"**Total Documents**: {total}")

        if documents:
            # Display documents
            for doc in documents:
                with st.expander(
                    f"📄 {doc.get('filename')} - ID: {doc.get('id')} - "
                    f"{'✓ Processed' if doc.get('processed') else '⏳ Processing'}"
                ):
                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        st.markdown(f"**ID**: {doc.get('id')}")
                        st.markdown(f"**Filename**: {doc.get('filename')}")
                        st.markdown(f"**Type**: {doc.get('content_type')}")
                        st.markdown(f"**Size**: {format_filesize(doc.get('file_size', 0))}")

                    with col_b:
                        st.markdown(f"**Chunks**: {doc.get('num_chunks', 0)}")
                        st.markdown(f"**Processed**: {'✓ Yes' if doc.get('processed') else '✗ No'}")
                        st.markdown(f"**Created**: {format_timestamp(doc.get('created_at'))}")
                        if doc.get('processed_at'):
                            st.markdown(f"**Processed At**: {format_timestamp(doc.get('processed_at'))}")

                    with col_c:
                        if doc.get('tx_hash'):
                            st.markdown(f"**TX Hash**: `{doc.get('tx_hash')[:16]}...`")
                        if doc.get('block_number'):
                            st.markdown(f"**Block**: {doc.get('block_number')}")
                        if doc.get('merkle_root'):
                            st.markdown(f"**Merkle Root**: `{doc.get('merkle_root')[:16]}...`")

                    # Show hashes
                    with st.expander("View Hashes"):
                        st.markdown("**File Hash**:")
                        st.code(doc.get('file_hash', 'N/A'))

                        if doc.get('commitment'):
                            st.markdown("**Commitment**:")
                            st.code(doc.get('commitment'))

                        if doc.get('embedding_hash'):
                            st.markdown("**Embedding Hash**:")
                            st.code(doc.get('embedding_hash'))

                    # Delete button
                    if st.button(f"Delete Document {doc.get('id')}", key=f"del_{doc.get('id')}"):
                        if st.session_state.get(f"confirm_delete_{doc.get('id')}"):
                            with st.spinner("Deleting..."):
                                success = asyncio.run(delete_document(doc.get('id')))
                                if success:
                                    st.success("Document deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete document")
                        else:
                            st.session_state[f"confirm_delete_{doc.get('id')}"] = True
                            st.warning("Click delete again to confirm")

            # Pagination
            st.markdown("---")
            col_p1, col_p2, col_p3 = st.columns([1, 2, 1])

            with col_p1:
                if page > 1:
                    if st.button("← Previous"):
                        st.session_state.current_page = page - 1
                        st.rerun()

            with col_p2:
                st.markdown(f"<center>Page {page} of {total_pages}</center>", unsafe_allow_html=True)

            with col_p3:
                if page < total_pages:
                    if st.button("Next →"):
                        st.session_state.current_page = page + 1
                        st.rerun()
        else:
            st.info("No documents found. Upload a document to get started!")
    else:
        st.error("Failed to load documents")


def render_settings_tab():
    """Render settings tab."""
    st.header("⚙️ Settings")

    st.markdown("Configure application settings and preferences.")

    # Backend settings
    st.subheader("Backend Configuration")

    backend_url = st.text_input(
        "Backend API URL",
        value=st.session_state.backend_url,
        help="URL of the backend API (e.g., http://localhost:8001)"
    )

    if backend_url != st.session_state.backend_url:
        st.session_state.backend_url = backend_url
        st.success("Backend URL updated!")

    # Query settings
    st.subheader("Query Settings")

    col1, col2 = st.columns(2)

    with col1:
        top_k = st.slider(
            "Default Top-K Results",
            min_value=1,
            max_value=20,
            value=st.session_state.top_k,
            help="Number of documents to retrieve per query"
        )

        if top_k != st.session_state.top_k:
            st.session_state.top_k = top_k
            st.success("Top-K updated!")

    with col2:
        similarity_threshold = st.slider(
            "Default Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.similarity_threshold,
            step=0.05,
            help="Minimum similarity score for retrieved documents"
        )

        if similarity_threshold != st.session_state.similarity_threshold:
            st.session_state.similarity_threshold = similarity_threshold
            st.success("Similarity threshold updated!")

    # Display settings
    st.subheader("Display Settings")

    show_debug_info = st.checkbox(
        "Show debug information",
        value=st.session_state.get("show_debug_info", False)
    )
    st.session_state.show_debug_info = show_debug_info

    # System info
    st.subheader("System Information")

    with st.spinner("Loading system info..."):
        health = asyncio.run(check_backend_health())

        if health:
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown(f"**Backend Status**: {health.get('status', 'unknown').title()}")
                st.markdown(f"**API Version**: {health.get('version', 'unknown')}")
                st.markdown(f"**Last Check**: {format_timestamp(health.get('timestamp'))}")

            with col_b:
                services = health.get('services', {})
                st.markdown("**Services**:")
                for service, status in services.items():
                    status_icon = "✓" if "healthy" in status else "✗"
                    st.markdown(f"{status_icon} {service.title()}: {status}")
        else:
            st.error("Unable to connect to backend")

    # Reset settings
    st.markdown("---")
    if st.button("Reset to Defaults", type="secondary"):
        st.session_state.backend_url = "http://localhost:8001"
        st.session_state.top_k = 5
        st.session_state.similarity_threshold = 0.6
        st.success("Settings reset to defaults!")
        st.rerun()


def main():
    """Main application."""
    # Initialize session state
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Main content
    st.title("🔒 ConfidentialRAG")
    st.markdown("**Zero-Knowledge Retrieval Augmented Generation System**")

    # Create tabs
    tabs = st.tabs(["📤 Upload", "🔍 Query", "📄 Documents", "⚙️ Settings"])

    with tabs[0]:
        render_upload_tab()

    with tabs[1]:
        render_query_tab()

    with tabs[2]:
        render_documents_tab()

    with tabs[3]:
        render_settings_tab()


if __name__ == "__main__":
    main()
