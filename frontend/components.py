"""
Reusable UI components for the ConfidentialRAG frontend.

This module contains custom Streamlit components for consistent UI/UX.
"""

import streamlit as st
from typing import Optional, Dict, Any, List


def render_document_card(doc: Dict[str, Any], show_actions: bool = True):
    """
    Render a document information card.

    Args:
        doc: Document dictionary
        show_actions: Whether to show action buttons
    """
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"**📄 {doc.get('filename', 'Unknown')}**")
            st.caption(f"ID: {doc.get('id', 'N/A')} | Type: {doc.get('content_type', 'N/A')}")

        with col2:
            status = "✓ Processed" if doc.get('processed') else "⏳ Processing"
            status_color = "green" if doc.get('processed') else "orange"
            st.markdown(f"**Status**: :{status_color}[{status}]")
            st.caption(f"Chunks: {doc.get('num_chunks', 0)}")

        with col3:
            if show_actions:
                if st.button("View", key=f"view_{doc.get('id')}"):
                    st.session_state[f"show_doc_{doc.get('id')}"] = True


def render_metric_row(metrics: List[tuple]):
    """
    Render a row of metrics.

    Args:
        metrics: List of (label, value, delta) tuples
    """
    cols = st.columns(len(metrics))

    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            if delta:
                st.metric(label, value, delta)
            else:
                st.metric(label, value)


def render_status_badge(status: str, label: Optional[str] = None):
    """
    Render a status badge with appropriate color.

    Args:
        status: Status string (healthy, degraded, unhealthy, etc.)
        label: Optional custom label
    """
    status_lower = status.lower()
    display_label = label or status.title()

    if "healthy" in status_lower:
        st.success(f"✓ {display_label}")
    elif "degraded" in status_lower:
        st.warning(f"⚠ {display_label}")
    elif "unhealthy" in status_lower or "error" in status_lower or "failed" in status_lower:
        st.error(f"✗ {display_label}")
    else:
        st.info(f"ℹ {display_label}")


def render_hash_display(hash_value: str, label: str, truncate: bool = False):
    """
    Render a hash value with copy button.

    Args:
        hash_value: Hash string
        label: Label for the hash
        truncate: Whether to truncate the display
    """
    st.markdown(f"**{label}**")

    if truncate and len(hash_value) > 32:
        display_value = f"{hash_value[:16]}...{hash_value[-16:]}"
        st.code(display_value)
    else:
        st.code(hash_value)

    if st.button(f"📋 Copy {label}", key=f"copy_{label}_{hash_value[:8]}"):
        st.info(f"Copy manually: {hash_value}")


def render_proof_visualization(proof: Dict[str, Any]):
    """
    Render an interactive visualization of a ZK proof.

    Args:
        proof: Proof dictionary
    """
    st.subheader("🔐 Zero-Knowledge Proof")

    # Verification status
    verified = proof.get("verified", False)

    col1, col2 = st.columns(2)

    with col1:
        if verified:
            st.success("✓ Proof Verified")
        else:
            st.warning("⚠ Proof Not Verified")

    with col2:
        st.metric("Verification Time", f"{proof.get('verification_time_ms', 0)}ms")

    # Proof data
    proof_data = proof.get("proof_data", {})

    # Merkle tree visualization
    with st.expander("🌳 Merkle Tree Structure", expanded=True):
        merkle_root = proof_data.get("merkle_root", "N/A")
        merkle_proof = proof_data.get("merkle_proof", [])

        st.markdown("**Merkle Root**")
        st.code(merkle_root)

        if merkle_proof:
            st.markdown("**Proof Path** (leaf to root)")

            # Create a simple tree visualization
            for level, hash_val in enumerate(merkle_proof):
                indent = "  " * level
                st.markdown(f"{indent}└─ Level {level}")
                st.code(f"{indent}   {hash_val}")

            st.markdown(f"{'  ' * len(merkle_proof)}└─ **Root**")
            st.code(f"{'  ' * len(merkle_proof)}   {merkle_root}")

    # Query and response hashes
    with st.expander("🔑 Cryptographic Hashes"):
        query_hash = proof_data.get("query_hash", "N/A")
        response_hash = proof_data.get("response_hash", "N/A")

        render_hash_display(query_hash, "Query Hash")
        st.markdown("---")
        render_hash_display(response_hash, "Response Hash")

    # Document commitments
    with st.expander("📜 Document Commitments"):
        commitments = proof_data.get("commitments", [])
        num_docs = proof_data.get("num_documents", 0)

        st.markdown(f"**Total Documents**: {num_docs}")

        if commitments:
            for idx, commitment in enumerate(commitments[:5]):
                st.markdown(f"**Document {idx + 1}**")
                st.code(commitment)

            if len(commitments) > 5:
                st.caption(f"... and {len(commitments) - 5} more commitments")


def render_query_result_card(doc: Dict[str, Any], index: int):
    """
    Render a retrieved document result card.

    Args:
        doc: Retrieved document dictionary
        index: Index in results
    """
    score = doc.get("score", 0)

    # Score color coding
    if score >= 0.8:
        score_color = "green"
        score_emoji = "🟢"
    elif score >= 0.6:
        score_color = "orange"
        score_emoji = "🟡"
    else:
        score_color = "red"
        score_emoji = "🔴"

    with st.expander(
        f"Result {index} - {score_emoji} Score: {score:.3f}",
        expanded=(index == 1)
    ):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"**Chunk ID**: `{doc.get('chunk_id')}`")
            st.markdown(f"**Document ID**: {doc.get('document_id')}")

        with col2:
            st.markdown(f"**Score**: :{score_color}[{score:.4f}]")

        # Content preview
        st.markdown("**Content**")
        content = doc.get("content", "")
        if len(content) > 500:
            st.text(content[:500] + "...")
            if st.button(f"Show full content", key=f"expand_{index}"):
                st.text(content)
        else:
            st.text(content)

        # Metadata
        metadata = doc.get("metadata", {})
        if metadata:
            with st.expander("Metadata"):
                st.json(metadata)


def render_upload_progress(filename: str, status: str = "processing"):
    """
    Render upload progress indicator.

    Args:
        filename: Name of file being uploaded
        status: Current status
    """
    st.markdown(f"**Uploading**: {filename}")

    if status == "processing":
        with st.spinner("Processing document..."):
            st.progress(0.5)
    elif status == "success":
        st.progress(1.0)
        st.success("Upload complete!")
    elif status == "error":
        st.error("Upload failed")


def render_settings_section(title: str, description: str):
    """
    Render a settings section header.

    Args:
        title: Section title
        description: Section description
    """
    st.subheader(title)
    st.markdown(description)
    st.markdown("---")


def render_info_box(message: str, icon: str = "ℹ"):
    """
    Render an information box.

    Args:
        message: Info message
        icon: Icon emoji
    """
    st.info(f"{icon} {message}")


def render_warning_box(message: str, icon: str = "⚠"):
    """
    Render a warning box.

    Args:
        message: Warning message
        icon: Icon emoji
    """
    st.warning(f"{icon} {message}")


def render_error_box(message: str, details: Optional[str] = None):
    """
    Render an error box with optional details.

    Args:
        message: Error message
        details: Optional error details
    """
    st.error(f"✗ {message}")

    if details:
        with st.expander("Error Details"):
            st.code(details)


def render_success_box(message: str):
    """
    Render a success box.

    Args:
        message: Success message
    """
    st.success(f"✓ {message}")


def render_service_status_grid(services: Dict[str, str]):
    """
    Render a grid of service statuses.

    Args:
        services: Dictionary of service name to status
    """
    cols = st.columns(len(services))

    for col, (service, status) in zip(cols, services.items()):
        with col:
            st.markdown(f"**{service.title()}**")

            if "healthy" in status.lower():
                st.success("✓ Healthy")
            elif "degraded" in status.lower():
                st.warning("⚠ Degraded")
            else:
                st.error("✗ Unhealthy")

            st.caption(status)


def render_confirmation_dialog(
    title: str,
    message: str,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    key: str = "confirm"
) -> Optional[bool]:
    """
    Render a confirmation dialog.

    Args:
        title: Dialog title
        message: Confirmation message
        confirm_text: Confirm button text
        cancel_text: Cancel button text
        key: Unique key for the dialog

    Returns:
        True if confirmed, False if cancelled, None if not clicked
    """
    st.markdown(f"**{title}**")
    st.warning(message)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(confirm_text, key=f"{key}_confirm", type="primary"):
            return True

    with col2:
        if st.button(cancel_text, key=f"{key}_cancel"):
            return False

    return None


def render_loading_state(message: str = "Loading..."):
    """
    Render a loading state indicator.

    Args:
        message: Loading message
    """
    with st.spinner(message):
        st.empty()


def render_empty_state(
    title: str,
    message: str,
    icon: str = "📭",
    action_text: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """
    Render an empty state placeholder.

    Args:
        title: Empty state title
        message: Empty state message
        icon: Icon emoji
        action_text: Optional action button text
        action_callback: Optional action button callback
    """
    st.markdown(f"<div style='text-align: center; padding: 2rem;'>", unsafe_allow_html=True)
    st.markdown(f"<h1>{icon}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>{message}</p>", unsafe_allow_html=True)

    if action_text and action_callback:
        if st.button(action_text, key="empty_state_action"):
            action_callback()

    st.markdown("</div>", unsafe_allow_html=True)
