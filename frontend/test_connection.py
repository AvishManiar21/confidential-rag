#!/usr/bin/env python3
"""
Test script to verify frontend can connect to backend.

Run this before starting the Streamlit app to check connectivity.
"""

import asyncio
import httpx
import sys
from datetime import datetime


async def test_health_check(backend_url: str):
    """Test health check endpoint."""
    print(f"\n🔍 Testing backend connection: {backend_url}")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"\n⏱️  Sending request to {backend_url}/health")
            response = await client.get(f"{backend_url}/health")
            response.raise_for_status()

            data = response.json()

            print(f"\n✅ Connection successful!")
            print(f"\n📊 Backend Status:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'unknown')}")

            print(f"\n🔧 Services:")
            services = data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if "healthy" in status else "❌"
                print(f"   {status_icon} {service.title()}: {status}")

            # Check if all services are healthy
            all_healthy = all("healthy" in s for s in services.values())

            if all_healthy:
                print(f"\n✅ All services are healthy!")
                return True
            else:
                print(f"\n⚠️  Some services are degraded or unhealthy")
                return False

    except httpx.ConnectError as e:
        print(f"\n❌ Connection Error: Cannot connect to backend")
        print(f"   Error: {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check if backend is running: docker-compose ps")
        print(f"   2. Verify backend URL is correct")
        print(f"   3. Check if backend port is exposed")
        return False

    except httpx.TimeoutException:
        print(f"\n❌ Timeout Error: Backend took too long to respond")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Backend might be starting up - wait a moment and retry")
        print(f"   2. Check backend logs: docker-compose logs backend")
        return False

    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        return False


async def test_documents_endpoint(backend_url: str):
    """Test documents list endpoint."""
    print(f"\n🔍 Testing documents endpoint")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{backend_url}/documents",
                params={"page": 1, "page_size": 1}
            )
            response.raise_for_status()

            data = response.json()
            total = data.get('total', 0)

            print(f"\n✅ Documents endpoint working!")
            print(f"   Total documents: {total}")

            return True

    except Exception as e:
        print(f"\n⚠️  Documents endpoint error: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("  ConfidentialRAG Frontend - Backend Connection Test")
    print("=" * 60)
    print(f"\n⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Default backend URLs to try
    backend_urls = [
        "http://localhost:8001",  # Local development
        "http://backend:8000",    # Docker compose
    ]

    # Allow custom URL from command line
    if len(sys.argv) > 1:
        backend_urls = [sys.argv[1]]
        print(f"\n🎯 Using custom backend URL: {backend_urls[0]}")

    success = False

    for url in backend_urls:
        health_ok = await test_health_check(url)

        if health_ok:
            success = True
            await test_documents_endpoint(url)
            print(f"\n✅ Backend URL verified: {url}")
            break

    print("\n" + "=" * 60)

    if success:
        print("✅ All tests passed! You can now start the frontend.")
        print("\n📝 Next steps:")
        print("   1. Run: streamlit run app.py")
        print("   2. Open: http://localhost:8501")
        print("   3. Start uploading documents and querying!")
        sys.exit(0)
    else:
        print("❌ Connection tests failed!")
        print("\n💡 Make sure the backend is running:")
        print("   docker-compose up backend -d")
        print("\n   Then run this test again:")
        print("   python test_connection.py")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
