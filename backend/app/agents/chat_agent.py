from openai_agents import Agent, Runner
from backend.mcp.server import mcp  # MCP tools
from typing import List, Dict

agent = Agent(
    name="Todo Chat Agent",
    instructions="""Proactive task assistant (Phase III constitution XI).
- Greet with stats (use get_user_stats).
- Natural language CRUD via tools (todo_crud).
- Confirm destructive actions.
- Context: Last 5 msgs only (IX).
- Summarize every 5 (X).""",
    tools=mcp.tools,  # MCP todo/stats
    model="gpt-4o-mini",
)

async def run_chat_agent(messages: List[Dict], user_id: str) -> str:
    """Runner for stateless chat cycle (VIII stateless)."""
    context = {"user_id": user_id}  # XII tool isolation
    result = await Runner.run(agent, messages[-5:], context=context)  # IX 5-msg window
    return result.final_output

# T303: Agents runner (summary trigger in endpoint)
