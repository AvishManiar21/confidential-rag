#!/usr/bin/env python3
"""
Run Demo Queries and Verify ZK Proofs

This script runs sample queries from sample-queries.json and verifies
that the RAG system returns correct documents with valid ZK proofs.
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
QUERIES_FILE = DEMO_DIR / "sample-queries.json"
RESULTS_FILE = DEMO_DIR / "query-results.json"


def log_info(msg: str):
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {msg}")


def log_success(msg: str):
    print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} {msg}")


def log_warning(msg: str):
    print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")


def log_error(msg: str):
    print(f"{Fore.RED}[✗]{Style.RESET_ALL} {msg}")


def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        return True
    except:
        log_error("Backend not reachable at http://localhost:8001")
        log_info("Start with: ./scripts/start-all.sh")
        return False


def load_queries() -> List[Dict]:
    """Load sample queries from JSON file."""
    log_info(f"Loading queries from {QUERIES_FILE}...")

    if not QUERIES_FILE.exists():
        log_error(f"Queries file not found: {QUERIES_FILE}")
        sys.exit(1)

    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)

    log_success(f"Loaded {len(queries)} sample queries")
    return queries


def run_query(query_spec: Dict) -> Dict:
    """Run a single query and return results with ZK proof info."""
    query_text = query_spec["query"]

    try:
        # Run RAG query
        response = requests.post(
            f"{BACKEND_URL}/api/v1/query",
            json={"query": query_text, "top_k": 3},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        # Extract results
        retrieved_docs = result.get("documents", [])
        answer = result.get("answer", "")
        proof_info = result.get("proof", {})

        return {
            "query_id": query_spec["id"],
            "query": query_text,
            "success": True,
            "retrieved_docs": [doc.get("metadata", {}).get("doc_id") for doc in retrieved_docs],
            "expected_docs": query_spec["expected_docs"],
            "answer_length": len(answer),
            "proof_verified": proof_info.get("verified", False),
            "proof_hash": proof_info.get("proof_hash"),
            "execution_time": result.get("execution_time_ms", 0),
        }

    except requests.exceptions.RequestException as e:
        log_error(f"Query failed: {e}")
        return {
            "query_id": query_spec["id"],
            "query": query_text,
            "success": False,
            "error": str(e),
        }


def verify_results(query_spec: Dict, result: Dict) -> bool:
    """Verify that query results match expectations."""
    if not result["success"]:
        return False

    expected = set(query_spec["expected_docs"])
    retrieved = set(result["retrieved_docs"])

    # Check if expected docs are in top-k results
    matches = expected.intersection(retrieved)

    if len(matches) > 0:
        return True
    else:
        log_warning(f"  Expected {expected}, got {retrieved}")
        return False


def run_all_queries(queries: List[Dict]):
    """Run all queries and track results."""
    log_info(f"Running {len(queries)} demo queries...")
    print()

    results = []
    passed = 0
    failed = 0

    for i, query_spec in enumerate(queries, 1):
        print(f"{Fore.CYAN}[{i}/{len(queries)}]{Style.RESET_ALL} {query_spec['description']}")
        print(f"  Query: '{query_spec['query']}'")

        # Run query
        result = run_query(query_spec)
        results.append(result)

        # Verify results
        if result["success"]:
            if verify_results(query_spec, result):
                log_success(f"  Retrieved: {result['retrieved_docs']}")
                log_success(f"  Proof verified: {result['proof_verified']}")
                log_success(f"  Execution time: {result['execution_time']:.0f}ms")
                passed += 1
            else:
                log_warning("  Results don't match expectations")
                failed += 1
        else:
            log_error(f"  Query failed: {result.get('error')}")
            failed += 1

        print()
        time.sleep(1)  # Rate limiting

    # Save results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    log_info(f"Results saved to {RESULTS_FILE}")

    # Summary
    print()
    log_info("=" * 60)
    log_info("Query Results Summary:")
    log_success(f"  Passed: {passed}/{len(queries)}")

    if failed > 0:
        log_warning(f"  Failed: {failed}/{len(queries)}")

    log_info("=" * 60)
    print()

    return passed == len(queries)


def analyze_proof_verification(results: List[Dict]):
    """Analyze ZK proof verification statistics."""
    print()
    log_info("ZK Proof Verification Analysis:")

    verified_count = sum(1 for r in results if r.get("proof_verified", False))
    total_count = len([r for r in results if r.get("success", False)])

    if total_count > 0:
        verification_rate = (verified_count / total_count) * 100
        log_info(f"  Verification rate: {verification_rate:.1f}% ({verified_count}/{total_count})")

        if verification_rate == 100:
            log_success("  All proofs verified successfully!")
        else:
            log_warning("  Some proofs failed verification")
    else:
        log_warning("  No successful queries to analyze")

    print()


def show_next_steps():
    """Show next steps."""
    log_info("Next steps:")
    print("  1. Run E2E tests:      python demo/test-e2e.py")
    print("  2. View results:       cat demo/query-results.json")
    print("  3. Access frontend:    http://localhost:8501")
    print("  4. Check proofs:       http://localhost:8080 (Midnight explorer)")
    print()


def main():
    """Main query execution flow."""
    print()
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ConfidentialRAG - Demo Query Runner{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print()

    # Check backend
    if not check_backend():
        sys.exit(1)

    print()

    # Load queries
    queries = load_queries()
    print()

    # Run all queries
    all_passed = run_all_queries(queries)

    # Analyze proof verification
    with open(RESULTS_FILE, "r") as f:
        results = json.load(f)
    analyze_proof_verification(results)

    # Show next steps
    show_next_steps()

    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
