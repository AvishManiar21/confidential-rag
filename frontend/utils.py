"""
Utility functions for the ConfidentialRAG frontend.

Handles API communication, data formatting, and helper functions.
"""

import httpx
import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio


def init_session_state():
    """Initialize session state variables."""
    if "backend_url" not in st.session_state:
        st.session_state.backend_url = "http://localhost:8001"

    if "top_k" not in st.session_state:
        st.session_state.top_k = 5

    if "similarity_threshold" not in st.session_state:
        st.session_state.similarity_threshold = 0.6

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    if "last_query_result" not in st.session_state:
        st.session_state.last_query_result = None

    if "show_debug_info" not in st.session_state:
        st.session_state.show_debug_info = False


def get_backend_url() -> str:
    """Get the current backend URL from session state."""
    return st.session_state.backend_url.rstrip("/")


async def check_backend_health() -> Optional[Dict[str, Any]]:
    """
    Check backend health status.

    Returns:
        Dictionary with health information or None if unavailable
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{get_backend_url()}/health")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        if st.session_state.show_debug_info:
            st.error(f"Health check error: {str(e)}")
        return None


async def upload_document(file) -> Optional[Dict[str, Any]]:
    """
    Upload a document to the backend.

    Args:
        file: Streamlit UploadedFile object

    Returns:
        Upload response dictionary or None on error
    """
    try:
        # Prepare file for upload
        files = {
            "file": (file.name, file.getvalue(), file.type or "application/pdf")
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{get_backend_url()}/documents",
                files=files
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        st.error(f"Upload failed: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None


async def query_rag(
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.6,
    generate_proof: bool = True,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Submit a query to the RAG system.

    Args:
        query: Query text
        top_k: Number of documents to retrieve
        similarity_threshold: Minimum similarity score
        generate_proof: Whether to generate ZK proof
        user_id: Optional user ID
        session_id: Optional session ID

    Returns:
        Query response dictionary or None on error
    """
    try:
        payload = {
            "query": query,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "generate_proof": generate_proof
        }

        if user_id:
            payload["user_id"] = user_id
        if session_id:
            payload["session_id"] = session_id

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{get_backend_url()}/query",
                json=payload
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        st.error(f"Query failed: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return None


async def list_documents(
    page: int = 1,
    page_size: int = 10,
    processed_only: bool = False
) -> Optional[Dict[str, Any]]:
    """
    List documents with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        processed_only: Only return processed documents

    Returns:
        Document list response or None on error
    """
    try:
        params = {
            "page": page,
            "page_size": page_size,
            "processed_only": processed_only
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{get_backend_url()}/documents",
                params=params
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        st.error(f"Failed to list documents: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error listing documents: {str(e)}")
        return None


async def get_document(document_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific document by ID.

    Args:
        document_id: Document ID

    Returns:
        Document details or None on error
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{get_backend_url()}/documents/{document_id}"
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            st.error("Document not found")
        else:
            st.error(f"Failed to get document: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error getting document: {str(e)}")
        return None


async def delete_document(document_id: int) -> bool:
    """
    Delete a document.

    Args:
        document_id: Document ID to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{get_backend_url()}/documents/{document_id}"
            )
            response.raise_for_status()
            return True

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            st.error("Document not found")
        else:
            st.error(f"Failed to delete document: {e.response.status_code}")
        return False
    except Exception as e:
        st.error(f"Error deleting document: {str(e)}")
        return False


def format_filesize(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_timestamp(timestamp: Any) -> str:
    """
    Format timestamp in human-readable format.

    Args:
        timestamp: Timestamp string or datetime object

    Returns:
        Formatted string
    """
    if timestamp is None:
        return "N/A"

    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return str(timestamp)

        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(timestamp)


def copy_to_clipboard(text: str, key: str):
    """
    Add a copy-to-clipboard button.

    Args:
        text: Text to copy
        key: Unique key for the button
    """
    if text and text != "N/A":
        if st.button(f"📋 Copy", key=f"copy_{key}"):
            st.code(text)
            st.info("Text displayed above - copy manually")


def format_score(score: float) -> str:
    """
    Format similarity score.

    Args:
        score: Score value (0-1)

    Returns:
        Formatted string with color coding
    """
    if score >= 0.8:
        return f"🟢 {score:.3f} (High)"
    elif score >= 0.6:
        return f"🟡 {score:.3f} (Medium)"
    else:
        return f"🔴 {score:.3f} (Low)"


def display_proof_data(proof_data: Dict[str, Any]):
    """
    Display ZK proof data in a formatted way.

    Args:
        proof_data: Proof data dictionary
    """
    st.markdown("**Query Hash**:")
    st.code(proof_data.get("query_hash", "N/A"))

    st.markdown("**Response Hash**:")
    st.code(proof_data.get("response_hash", "N/A"))

    st.markdown("**Merkle Root**:")
    st.code(proof_data.get("merkle_root", "N/A"))

    merkle_proof = proof_data.get("merkle_proof", [])
    if merkle_proof:
        st.markdown("**Merkle Proof Path**:")
        for idx, hash_val in enumerate(merkle_proof):
            st.code(f"Level {idx}: {hash_val}")

    commitments = proof_data.get("commitments", [])
    if commitments:
        st.markdown(f"**Document Commitments** ({len(commitments)} total):")
        # Show first 3 commitments
        for idx, commitment in enumerate(commitments[:3]):
            st.code(f"{idx + 1}. {commitment}")
        if len(commitments) > 3:
            st.caption(f"... and {len(commitments) - 3} more commitments")


def create_metric_card(label: str, value: Any, delta: Optional[str] = None):
    """
    Create a styled metric card.

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
    """
    st.metric(label, value, delta)


def show_error_message(message: str, details: Optional[str] = None):
    """
    Show formatted error message.

    Args:
        message: Error message
        details: Optional error details
    """
    st.error(f"**Error**: {message}")
    if details and st.session_state.show_debug_info:
        with st.expander("Error Details"):
            st.code(details)


def show_success_message(message: str):
    """
    Show formatted success message.

    Args:
        message: Success message
    """
    st.success(f"✓ {message}")


def show_info_message(message: str):
    """
    Show formatted info message.

    Args:
        message: Info message
    """
    st.info(f"ℹ {message}")


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def validate_pdf_file(file) -> bool:
    """
    Validate uploaded PDF file.

    Args:
        file: Uploaded file object

    Returns:
        True if valid, False otherwise
    """
    if not file:
        st.error("No file selected")
        return False

    if not file.name.lower().endswith('.pdf'):
        st.error("Only PDF files are supported")
        return False

    # Check file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB
    if len(file.getvalue()) > max_size:
        st.error(f"File too large. Maximum size is {format_filesize(max_size)}")
        return False

    return True


def validate_query(query: str) -> bool:
    """
    Validate query text.

    Args:
        query: Query text

    Returns:
        True if valid, False otherwise
    """
    if not query or not query.strip():
        st.error("Query cannot be empty")
        return False

    if len(query) > 2000:
        st.error("Query too long. Maximum 2000 characters")
        return False

    return True


def get_status_color(status: str) -> str:
    """
    Get color for status indicator.

    Args:
        status: Status string

    Returns:
        Color code
    """
    status_colors = {
        "healthy": "#28a745",
        "degraded": "#ffc107",
        "unhealthy": "#dc3545",
        "unknown": "#6c757d"
    }
    return status_colors.get(status.lower(), "#6c757d")


def render_loading_spinner(message: str = "Loading..."):
    """
    Render a loading spinner with message.

    Args:
        message: Loading message
    """
    with st.spinner(message):
        pass
