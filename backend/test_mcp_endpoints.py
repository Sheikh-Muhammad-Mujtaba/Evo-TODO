import httpx
import asyncio
import sys

async def probe():
    base = "http://localhost:8003"
    paths = ["/mcp", "/mcp/sse", "/mcp/messages", "/sse", "/messages"]
    
    print(f"Probing {base}...", flush=True)
    async with httpx.AsyncClient() as client:
        
        # Check health
        try:
            resp = await client.get(f"{base}/health", timeout=2.0)
            print(f"GET /health: {resp.status_code}", flush=True)
        except Exception as e:
            print(f"GET /health: Error {e}", flush=True)

        for path in paths:
            url = f"{base}{path}"
            
            # GET probe (for SSE)
            try:
                resp = await client.get(url, timeout=2.0)
                print(f"GET {path}: {resp.status_code}", flush=True)
            except httpx.ReadTimeout:
                print(f"GET {path}: Timeout (Possible SSE stream!)", flush=True)
            except Exception as e:
                print(f"GET {path}: Error {e}", flush=True)

            # POST probe (for messages)
            try:
                # Need valid Session ID for POST? Or maybe just try?
                # Usually POST to /messages requires ?sessionId=...
                resp = await client.post(url, json={}, timeout=2.0)
                print(f"POST {path}: {resp.status_code}", flush=True)
            except Exception as e:
                print(f"POST {path}: Error {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(probe())
