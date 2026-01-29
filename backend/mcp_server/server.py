import asyncio
import json
import mcp.types as types
from mcp.server import Server
from app.models.todo import Todo
from app.models.database import Session, engine
from typing import List, Optional
from uuid import UUID
from sqlmodel import select
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP Server instance
mcp_server = Server("Todo MCP Server")


@mcp_server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_user_stats",
            description="Get user task stats (pending/completed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user."}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="add_task",
            description="Adds a new task to the database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user."},
                    "title": {"type": "string", "description": "The title of the task."},
                    "description": {"type": "string", "description": "The description of the task."}
                },
                "required": ["user_id", "title"]
            }
        ),
        types.Tool(
            name="list_tasks",
            description="Lists all tasks for a user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user."}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="update_task",
            description="Updates a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user."},
                    "task_id": {"type": "string", "description": "The ID of the task."},
                    "title": {"type": "string", "description": "The new title of the task."},
                    "description": {"type": "string", "description": "The new description of the task."}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        types.Tool(
            name="delete_task",
            description="Deletes a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user."},
                    "task_id": {"type": "string", "description": "The ID of the task."}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        types.Tool(
            name="complete_task",
            description="Marks a task as complete.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user."},
                    "task_id": {"type": "string", "description": "The ID of the task."}
                },
                "required": ["user_id", "task_id"]
            }
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    user_id = arguments.get("user_id")
    if not user_id:
        raise ValueError("user_id is required for all tool calls.")

    if name == "get_user_stats":
        with Session(engine) as session:
            pending = len(session.exec(select(Todo).where(Todo.user_id == user_id, Todo.is_complete == False)).all())
            completed = len(session.exec(select(Todo).where(Todo.user_id == user_id, Todo.is_complete == True)).all())
            return [types.TextContent(text=f"Pending tasks: {pending}, Completed tasks: {completed}")]
    elif name == "add_task":
        title = arguments.get("title")
        description = arguments.get("description")
        if not title:
            raise ValueError("Title is required for adding a task.")
        with Session(engine) as session:
            todo = Todo(user_id=user_id, title=title, description=description)
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return [types.TextContent(text=f"Task '{todo.title}' added with ID: {todo.id}")]
    elif name == "list_tasks":
        with Session(engine) as session:
            todos = session.exec(select(Todo).where(Todo.user_id == user_id)).all()
            if not todos:
                return [types.TextContent(text="No tasks found.")]
            task_list = "\n".join([f"- {t.title} (ID: {t.id}, Completed: {t.is_complete})" for t in todos])
            return [types.TextContent(text=f"Your tasks:\n{task_list}")]
    elif name == "update_task":
        task_id = arguments.get("task_id")
        title = arguments.get("title")
        description = arguments.get("description")
        if not task_id:
            raise ValueError("Task ID is required for updating a task.")
        with Session(engine) as session:
            todo = session.exec(select(Todo).where(Todo.id == UUID(task_id), Todo.user_id == user_id)).first()
            if todo:
                if title is not None:
                    todo.title = title
                if description is not None:
                    todo.description = description
                session.add(todo)
                session.commit()
                session.refresh(todo)
                return [types.TextContent(text=f"Task '{todo.id}' updated.")]
            return [types.TextContent(text=f"Task with ID '{task_id}' not found.")]
    elif name == "delete_task":
        task_id = arguments.get("task_id")
        if not task_id:
            raise ValueError("Task ID is required for deleting a task.")
        with Session(engine) as session:
            todo = session.exec(select(Todo).where(Todo.id == UUID(task_id), Todo.user_id == user_id)).first()
            if todo:
                session.delete(todo)
                session.commit()
                return [types.TextContent(text=f"Task '{task_id}' deleted.")]
            return [types.TextContent(text=f"Task with ID '{task_id}' not found.")]
    elif name == "complete_task":
        task_id = arguments.get("task_id")
        if not task_id:
            raise ValueError("Task ID is required for completing a task.")
        with Session(engine) as session:
            todo = session.exec(select(Todo).where(Todo.id == UUID(task_id), Todo.user_id == user_id)).first()
            if todo:
                todo.is_complete = True
                session.add(todo)
                session.commit()
                session.refresh(todo)
                return [types.TextContent(text=f"Task '{todo.id}' marked as complete.")]
            return [types.TextContent(text=f"Task with ID '{task_id}' not found.")]
    
    raise ValueError(f"Tool not found: {name}")


# Create a FastAPI app instance to host the MCP server as HTTP
mcp_host_app = FastAPI(
    title="Todo MCP Host",
    description="Hosts the MCP Server instance via HTTP",
    version="1.0.0",
)


@mcp_host_app.post("/mcp")
async def handle_mcp_request(request: Request):
    """
    Handle MCP protocol requests via HTTP using JSON-RPC format.
    """
    try:
        body = await request.json()
        logger.info(f"MCP request: {body.get('method', 'unknown')}")
        
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        # Handle MCP protocol methods
        if method == "initialize":
            # Initialize request - return server capabilities
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "Todo MCP Server",
                    "version": "1.0.0"
                }
            }
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })
        
        elif method == "tools/list":
            tools = await list_tools()
            # Convert tool objects to dictionaries for JSON serialization
            tools_data = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ]
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {"tools": tools_data},
                "id": request_id
            })
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = await call_tool(tool_name, tool_args)
            # Convert TextContent objects to text
            result_text = result[0].text if result else ""
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": result_text}]},
                "id": request_id
            })
        
        else:
            logger.warning(f"Unknown MCP method: {method}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": request_id
            }, status_code=200)
    
    except Exception as e:
        logger.error(f"Error handling MCP request: {str(e)}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": body.get("id", None)
        }, status_code=200)


@mcp_host_app.get("/health")
async def health_check():
    """Health check endpoint for the MCP server."""
    return {"status": "healthy", "service": "Todo MCP Server"}


if __name__ == "__main__":
    uvicorn.run(mcp_host_app, host="0.0.0.0", port=8001)
