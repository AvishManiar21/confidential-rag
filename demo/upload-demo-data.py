#!/usr/bin/env python3
"""
Upload Demo Medical Data to ConfidentialRAG

This script uploads medical abstracts from medical-abstracts.json
to the backend API for indexing and ZK commitment generation.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

import requests
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Configuration
BACKEND_URL = "http://localhost:8001"
DEMO_DIR = Path(__file__).parent
DATA_FILE = DEMO_DIR / "medical-abstracts.json"


def log_info(msg: str):
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {msg}")


def log_success(msg: str):
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {msg}")


def log_warning(msg: str):
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {msg}")


def log_error(msg: str):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")


def check_backend():
    """Check if backend is running and healthy."""
    log_info("Checking backend health...")

    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        health = response.json()

        log_success("Backend is healthy!")
        log_info(f"  Version: {health.get('version', 'unknown')}")

        return True

    except requests.exceptions.RequestException as e:
        log_error(f"Backend not reachable: {e}")
        log_info("Start backend with: ./scripts/start-all.sh")
        return False


def load_demo_data() -> List[Dict]:
    """Load medical abstracts from JSON file."""
    log_info(f"Loading demo data from {DATA_FILE}...")

    if not DATA_FILE.exists():
        log_error(f"Demo data file not found: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    log_success(f"Loaded {len(data)} medical abstracts")
    return data


def upload_document(doc: Dict) -> bool:
    """Upload a single document to the backend."""
    try:
        # Prepare document payload
        payload = {
            "title": doc["title"],
            "content": doc["abstract"],
            "metadata": {
                "authors": doc["authors"],
                "journal": doc["journal"],
                "year": doc["year"],
                "keywords": doc["keywords"],
                "doc_id": doc["id"],
            },
        }

        # Upload document
        response = requests.post(
            f"{BACKEND_URL}/api/v1/documents",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        doc_id = result.get("document_id")
        log_success(f"  {doc['id']}: {doc['title'][:60]}... (ID: {doc_id})")

        # Small delay to avoid overwhelming the API
        time.sleep(0.5)

        return True

    except requests.exceptions.RequestException as e:
        log_error(f"  Failed to upload {doc['id']}: {e}")
        return False


def upload_all_documents(documents: List[Dict]):
    """Upload all documents and track progress."""
    log_info(f"Uploading {len(documents)} documents...")
    print()

    success_count = 0
    failed_count = 0

    for i, doc in enumerate(documents, 1):
        print(f"{Fore.CYAN}[{i}/{len(documents)}]{Style.RESET_ALL} Uploading: {doc['title'][:50]}...")

        if upload_document(doc):
            success_count += 1
        else:
            failed_count += 1

    print()
    log_info("Upload Summary:")
    log_success(f"  Successfully uploaded: {success_count}")

    if failed_count > 0:
        log_error(f"  Failed uploads: {failed_count}")
    else:
        log_success("  All documents uploaded successfully!")


def verify_uploads():
    """Verify documents were indexed correctly."""
    log_info("Verifying document indexing...")

    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/documents", timeout=10)
        response.raise_for_status()
        docs = response.json()

        count = len(docs.get("documents", []))
        log_success(f"Found {count} documents in database")

        return True

    except requests.exceptions.RequestException as e:
        log_warning(f"Could not verify uploads: {e}")
        return False


def show_next_steps():
    """Show next steps after upload."""
    print()
    log_info("=" * 60)
    log_success("Demo data upload complete!")
    log_info("=" * 60)
    print()

    log_info("Next steps:")
    print("  1. Run demo queries:       python demo/run-demo-queries.py")
    print("  2. Run E2E tests:          python demo/test-e2e.py")
    print("  3. Access frontend:        http://localhost:8501")
    print("  4. View API docs:          http://localhost:8001/docs")
    print()


def main():
    """Main upload flow."""
    print()
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ConfidentialRAG - Demo Data Upload{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print()

    # Check backend health
    if not check_backend():
        sys.exit(1)

    print()

    # Load demo data
    documents = load_demo_data()
    print()

    # Upload all documents
    upload_all_documents(documents)
    print()

    # Verify uploads
    verify_uploads()

    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main()
