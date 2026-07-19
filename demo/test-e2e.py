#!/usr/bin/env python3
"""
End-to-End Test Suite for ConfidentialRAG

Tests the complete workflow:
1. Upload documents
2. Generate embeddings and ZK commitments
3. Run queries
4. Verify ZK proofs
5. Validate retrieval quality
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

import requests
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration
BACKEND_URL = "http://localhost:8001"
DEMO_DIR = Path(__file__).parent


class TestResult:
    """Track test results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_pass(self, name: str, message: str = ""):
        self.passed += 1
        self.tests.append({"name": name, "status": "PASS", "message": message})
        print(f"{Fore.GREEN}[PASS]{Style.RESET_ALL} {name}")
        if message:
            print(f"       {message}")

    def add_fail(self, name: str, message: str = ""):
        self.failed += 1
        self.tests.append({"name": name, "status": "FAIL", "message": message})
        print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} {name}")
        if message:
            print(f"       {message}")

    def summary(self):
        total = self.passed + self.failed
        print()
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"Test Summary: {self.passed}/{total} passed")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print()
        return self.failed == 0


def test_backend_health(results: TestResult):
    """Test: Backend is healthy and reachable."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        health = response.json()

        if health.get("status") == "healthy":
            results.add_pass("Backend health check", f"Version: {health.get('version')}")
        else:
            results.add_fail("Backend health check", f"Status: {health.get('status')}")

    except Exception as e:
        results.add_fail("Backend health check", str(e))


def test_document_upload(results: TestResult):
    """Test: Upload a test document."""
    test_doc = {
        "title": "E2E Test Document",
        "content": "This is a test document for end-to-end testing of the ConfidentialRAG system. It contains information about diabetes treatment with metformin.",
        "metadata": {"test": True, "keywords": ["test", "diabetes", "metformin"]},
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/documents",
            json=test_doc,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        doc_id = result.get("document_id")
        if doc_id:
            results.add_pass("Document upload", f"Document ID: {doc_id}")
            return doc_id
        else:
            results.add_fail("Document upload", "No document ID returned")
            return None

    except Exception as e:
        results.add_fail("Document upload", str(e))
        return None


def test_document_retrieval(results: TestResult, doc_id: str):
    """Test: Retrieve uploaded document."""
    if not doc_id:
        results.add_fail("Document retrieval", "No document ID to retrieve")
        return

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/documents/{doc_id}",
            timeout=10,
        )
        response.raise_for_status()
        doc = response.json()

        if doc.get("id") == doc_id:
            results.add_pass("Document retrieval", f"Retrieved: {doc.get('title')}")
        else:
            results.add_fail("Document retrieval", "Document ID mismatch")

    except Exception as e:
        results.add_fail("Document retrieval", str(e))


def test_query_execution(results: TestResult):
    """Test: Execute a query and get results."""
    query = "What medications treat diabetes?"

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/query",
            json={"query": query, "top_k": 3},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        docs = result.get("documents", [])
        answer = result.get("answer", "")

        if len(docs) > 0 and len(answer) > 0:
            results.add_pass("Query execution", f"Retrieved {len(docs)} docs, answer length: {len(answer)}")
            return result
        else:
            results.add_fail("Query execution", "No documents or answer returned")
            return None

    except Exception as e:
        results.add_fail("Query execution", str(e))
        return None


def test_proof_generation(results: TestResult, query_result: Dict):
    """Test: ZK proof generation for query."""
    if not query_result:
        results.add_fail("Proof generation", "No query result to verify")
        return

    proof_info = query_result.get("proof", {})

    if proof_info.get("proof_hash"):
        results.add_pass("Proof generation", f"Proof hash: {proof_info['proof_hash'][:16]}...")
    else:
        results.add_fail("Proof generation", "No proof hash generated")


def test_proof_verification(results: TestResult, query_result: Dict):
    """Test: ZK proof verification."""
    if not query_result:
        results.add_fail("Proof verification", "No query result to verify")
        return

    proof_info = query_result.get("proof", {})
    verified = proof_info.get("verified", False)

    if verified:
        results.add_pass("Proof verification", "Proof verified on-chain")
    else:
        results.add_fail("Proof verification", "Proof verification failed")


def test_retrieval_quality(results: TestResult, query_result: Dict):
    """Test: Retrieval quality using RAGAS metrics."""
    if not query_result:
        results.add_fail("Retrieval quality", "No query result to evaluate")
        return

    metrics = query_result.get("metrics", {})
    context_precision = metrics.get("context_precision", 0)

    if context_precision > 0.5:
        results.add_pass("Retrieval quality", f"Context precision: {context_precision:.2f}")
    else:
        results.add_fail("Retrieval quality", f"Low context precision: {context_precision:.2f}")


def test_embedding_storage(results: TestResult):
    """Test: Embeddings are stored in ChromaDB."""
    try:
        # Check if ChromaDB is reachable
        response = requests.get("http://localhost:8000/api/v1/heartbeat", timeout=5)

        if response.status_code == 200:
            results.add_pass("ChromaDB connectivity", "Vector database accessible")
        else:
            results.add_fail("ChromaDB connectivity", f"Status: {response.status_code}")

    except Exception as e:
        results.add_fail("ChromaDB connectivity", str(e))


def test_midnight_network(results: TestResult):
    """Test: Midnight network is running."""
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)

        if response.status_code == 200:
            results.add_pass("Midnight network", "Blockchain node accessible")
        else:
            results.add_fail("Midnight network", f"Status: {response.status_code}")

    except Exception as e:
        results.add_fail("Midnight network", str(e))


def cleanup_test_data(doc_id: str):
    """Clean up test document."""
    if not doc_id:
        return

    try:
        requests.delete(f"{BACKEND_URL}/api/v1/documents/{doc_id}", timeout=10)
        print(f"\n{Fore.BLUE}[INFO]{Style.RESET_ALL} Cleaned up test document: {doc_id}")
    except:
        pass


def main():
    """Run all E2E tests."""
    print()
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ConfidentialRAG - End-to-End Test Suite{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print()

    results = TestResult()
    doc_id = None
    query_result = None

    try:
        # Test 1: Backend health
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing backend health...")
        test_backend_health(results)
        print()

        # Test 2: Infrastructure connectivity
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing infrastructure...")
        test_embedding_storage(results)
        test_midnight_network(results)
        print()

        # Test 3: Document upload
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing document upload...")
        doc_id = test_document_upload(results)
        print()

        # Test 4: Document retrieval
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing document retrieval...")
        test_document_retrieval(results, doc_id)
        print()

        # Test 5: Query execution
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing query execution...")
        query_result = test_query_execution(results)
        print()

        # Test 6: Proof generation
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing ZK proof generation...")
        test_proof_generation(results, query_result)
        print()

        # Test 7: Proof verification
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing ZK proof verification...")
        test_proof_verification(results, query_result)
        print()

        # Test 8: Retrieval quality
        print(f"{Fore.YELLOW}[TEST]{Style.RESET_ALL} Testing retrieval quality...")
        test_retrieval_quality(results, query_result)
        print()

    finally:
        # Cleanup
        if doc_id:
            cleanup_test_data(doc_id)

    # Summary
    all_passed = results.summary()

    if all_passed:
        print(f"{Fore.GREEN}All tests passed!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"{Fore.RED}Some tests failed!{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
