import asyncio
import logging
from agents.mcp import MCPServerStreamableHttp
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_connection():
    mcp_url = "http://localhost:8003/mcp"
    print(f"Connecting to {mcp_url}...")
    
    try:
        async with MCPServerStreamableHttp(
            name="Test Client",
            params={"url": mcp_url},
        ) as client:
            print("Connected!")
            # Try to list tools
            tools = await client.list_tools()
            print(f"Tools: {len(tools)}")
            for tool in tools:
                print(f" - {tool.name}")
                
    except Exception as e:
        logger.exception("Connection failed")

if __name__ == "__main__":
    asyncio.run(test_connection())
