from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStreamableHttp
from app.models.database import Session, engine
from app.models.chat import Conversation, Message
from uuid import UUID
from sqlmodel import select
from app.core.config import settings
from typing import Optional

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
        instructions="""You are a proactive Task Manager. Greet users with their current task stats and help them manage their list using tools.
Use the 'get_user_stats' tool to greet the user with their task statistics on the first turn of a session.
Use 'add_task', 'list_tasks', 'update_task', 'delete_task', 'complete_task' tools to manage tasks.""",
        model=gemini_model,
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
        mcp_servers=[mcp_http_server],
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

        # Run the triage agent
        result = await Runner.run(triage_agent, message_history, context={"user_id": user_id})

        # We also need to save the assistant's response to the database.
        assistant_response = result.final_output
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
