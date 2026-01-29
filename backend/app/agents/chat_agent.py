from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, RunConfig

# Disable tracing globally
set_tracing_disabled(True)
from agents.mcp import MCPServerStreamableHttp
from app.models.database import Session, engine
from app.models.chat import Conversation, Message
from uuid import UUID
from sqlmodel import select
from app.core.config import settings
from typing import Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

# Create a custom AsyncOpenAI client
client = AsyncOpenAI(api_key=settings.GEMINI_API_KEY, base_url=settings.GEMINI_BASE_URL)


async def get_initialized_triage_agent(mcp_http_server: MCPServerStreamableHttp) -> Agent:
    """
    Initializes and returns the TriageAgent with all its specialist agents and tools.
    This function is asynchronous because it needs to await the MCP server's tools.
    """
    # Define the Gemini model using OpenAIChatCompletionsModel
    gemini_model = OpenAIChatCompletionsModel(
        model=settings.MODEL_NAME,
        openai_client=client,
    )

    # Specialist Agents
    chat_agent = Agent(
        name="ChatAgent",
        instructions="""You are a proactive Task Manager. Help users manage their task list using the available MCP tools.

IMPORTANT TOOL USAGE:
- Use 'get_user_stats' to show task statistics (pending/completed counts)
- Use 'add_task' to create new tasks (requires title, optional description)
- Use 'list_tasks' to show all user's tasks
- Use 'update_task' to modify existing tasks (requires task_id)
- Use 'delete_task' to remove tasks (requires task_id)

RESPONSE GUIDELINES:
- After successfully using a tool, confirm the action to the user with details
- If a tool returns an error, explain what went wrong clearly
- Always acknowledge when tasks are created, updated, or deleted
- Be concise but informative in your responses""",
        model=gemini_model,
        mcp_servers=[mcp_http_server],
    )

    summarizer_agent = Agent(
        name="SummarizerAgent",
        instructions="You are a summarization expert. Condense the following conversation into a concise summary.",
        model=gemini_model,
    )

    # Orchestrator Agent
    triage_agent = Agent(
        name="TriageAgent",
        instructions="""You are a triage agent. Your job is to determine which specialist agent to use.
If the conversation has 5 or more messages, you must first call the summarizer agent.
Then, you must call the chat agent to respond to the user.""",
        model=gemini_model,
        tools=[
            chat_agent.as_tool(
                tool_name="chat",
                tool_description="Use this tool to chat with the user.",
            ),
            summarizer_agent.as_tool(
                tool_name="summarize",
                tool_description="Use this tool to summarize the conversation.",
            ),
        ],
    )
    return triage_agent


async def get_agent_response(triage_agent: Agent, user_input: str, user_id: str, conversation_id: UUID) -> str:
    # Validate conversation_id is not None
    if conversation_id is None:
        raise ValueError("conversation_id is required and cannot be None")
    
    with Session(engine) as session:
        conversation = session.exec(select(Conversation).where(Conversation.id == conversation_id)).first()
        if not conversation:
            # Handle new conversation
            conversation = Conversation(id=conversation_id, user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Retrieve messages for the current conversation
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()

        # Prepare messages for the agent
        formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
        
        # Add context summary if available
        if conversation.context_summary:
            formatted_messages.insert(0, {"role": "system", "content": f"Current summary: {conversation.context_summary}"})

        # Add the user input
        formatted_messages.append({"role": "user", "content": user_input})

        # Create a string representation of the messages
        message_history = "\n".join([f"{m['role']}: {m['content']}" for m in formatted_messages])

        # Run the triage agent with timeout and error handling
        try:
            # Configure run with increased max turns for complex tool operations
            run_config = RunConfig(
                max_turns=15,  # Allow more turns for tool calls and responses
            )

            result = await asyncio.wait_for(
                Runner.run(
                    triage_agent,
                    message_history,
                    context={"user_id": user_id},
                    run_config=run_config,
                ),
                timeout=180.0  # 3 minute timeout for entire agent run
            )
            assistant_response = result.final_output

            # Log successful completion
            logger.info(f"Agent completed successfully for user {user_id[:8]}...")

        except asyncio.TimeoutError:
            logger.error(f"Agent timed out for user {user_id[:8]}...")
            assistant_response = "I'm sorry, the request took too long to process. Your task may have been created - please use 'list tasks' to check, or try again."

        except Exception as e:
            error_str = str(e)
            logger.error(f"Agent error for user {user_id[:8]}...: {error_str}")

            if "RateLimitError" in error_str:
                assistant_response = "I'm sorry, I'm a bit overwhelmed right now. Please try again in a few moments."
            elif "timeout" in error_str.lower() or "timed out" in error_str.lower():
                assistant_response = "The operation took longer than expected. Your task may have been processed - please check your task list."
            elif "connection" in error_str.lower():
                assistant_response = "I'm having trouble connecting to the task service. Please try again in a moment."
            elif "MCP" in error_str or "tool" in error_str.lower():
                assistant_response = f"There was an issue processing your request: {error_str}. Please try again."
            else:
                assistant_response = "I encountered an unexpected error. Please try again or rephrase your request."

        # We also need to save the assistant's response to the database.
        if assistant_response:
            # Ensure conversation_id is set before creating the message
            new_message = Message(
                conversation_id=conversation_id,  # Always use the validated conversation_id
                role="assistant",
                content=assistant_response,
            )
            session.add(new_message)
            session.commit()

        return assistant_response
