"""Simple test to verify MCP server connection"""
import asyncio
import httpx

async def test_mcp_connection():
    """Test basic connection to MCP server"""
    try:
        # Test health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8003/health")
            print(f"Health check: {response.status_code} - {response.json()}")

            # Test MCP endpoint exists
            response = await client.get("http://localhost:8003/mcp")
            print(f"MCP endpoint: {response.status_code}")

        print("✓ Server is accessible")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
