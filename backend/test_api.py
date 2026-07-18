#!/usr/bin/env python
"""Example API client to test the ConfidentialRAG backend."""

import asyncio
import httpx
from pathlib import Path


BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


async def test_health():
    """Test health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/health")
        print(f"Health Check: {response.status_code}")
        print(response.json())
        print()


async def test_upload_document(file_path: str):
    """Test document upload."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "application/pdf")}
            response = await client.post(f"{API_URL}/documents", files=files)

        print(f"Upload Document: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Document ID: {data['document']['id']}")
            print(f"File Hash: {data['document']['file_hash']}")
            print(f"Commitment: {data['document']['commitment']}")
            print(f"Merkle Root: {data['document']['merkle_root']}")
            print(f"Processed: {data['document']['processed']}")
            return data["document"]["id"]
        else:
            print(response.text)
        print()


async def test_list_documents():
    """Test listing documents."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/documents?page=1&page_size=10")
        print(f"List Documents: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Documents: {data['total']}")
            for doc in data["documents"]:
                print(f"  - {doc['filename']} (ID: {doc['id']}, Processed: {doc['processed']})")
        print()


async def test_query(query_text: str):
    """Test RAG query."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "query": query_text,
            "top_k": 5,
            "similarity_threshold": 0.6,
            "generate_proof": True
        }
        response = await client.post(f"{API_URL}/query", json=payload)

        print(f"Query: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data['query']}")
            print(f"Response: {data['response'][:200]}...")
            print(f"Retrieved Documents: {data['num_results']}")
            print(f"Avg Similarity: {data['avg_similarity']:.3f}")
            print(f"Response Time: {data['response_time_ms']}ms")

            if data.get("proof"):
                print(f"Proof Generated: Yes")
                print(f"Proof Verified: {data['proof']['verified']}")
                print(f"Proof Type: {data['proof']['proof_type']}")

            print("\nRetrieved Documents:")
            for doc in data["retrieved_documents"]:
                print(f"  - Chunk {doc['chunk_id']}: Score {doc['score']:.3f}")
                print(f"    {doc['content'][:100]}...")

            return data["query_id"]
        else:
            print(response.text)
        print()


async def test_get_query_audit(query_id: int):
    """Test getting query audit record."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/query/{query_id}")
        print(f"Get Query Audit: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Query ID: {data['id']}")
            print(f"Status: {data['status']}")
            print(f"Proof Generated: {data['proof_generated']}")
            print(f"Proof Verified: {data['proof_verified']}")
        print()


async def main():
    """Run all tests."""
    print("=" * 60)
    print("ConfidentialRAG Backend API Tests")
    print("=" * 60)
    print()

    # Test health
    print("1. Testing Health Check...")
    await test_health()

    # Test document upload (if you have a PDF file)
    # Uncomment and provide path to test
    # print("2. Testing Document Upload...")
    # doc_id = await test_upload_document("path/to/your/document.pdf")

    # Test listing documents
    print("2. Testing List Documents...")
    await test_list_documents()

    # Test query (requires documents to be uploaded first)
    # print("3. Testing RAG Query...")
    # query_id = await test_query("What is the main topic discussed in the documents?")

    # Test getting query audit
    # if query_id:
    #     print("4. Testing Get Query Audit...")
    #     await test_get_query_audit(query_id)

    print("=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
