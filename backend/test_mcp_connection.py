import httpx
import asyncio

async def test_mcp():
    try:
        print("Checking health...")
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8003/health", timeout=2.0)
            print(f"Health: {resp.status_code} {resp.text}")

        # Minimal MCP initialize request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        print("Sending request to http://localhost:8003/mcp...")
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8003/mcp", json=payload, timeout=5.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp())
