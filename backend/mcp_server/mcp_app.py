import logging
import json
from typing import List, Optional, Dict
from uuid import UUID

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Dapr sidecar address - usually localhost:3500 within the container
DAPR_HOST = "http://localhost"
DAPR_HTTP_PORT = 3500
DAPR_URL = f"{DAPR_HOST}:{DAPR_HTTP_PORT}"
TODO_APP_ID = "todo-service"  # Dapr app-id for the todo-service


async def invoke_dapr_service(
    app_id: str,
    method_name: str,
    http_method: str = "GET",
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
) -> Dict:
    """Invokes a Dapr service using its app ID and method name."""
    url = f"{DAPR_URL}/v1.0/invoke/{app_id}/method/{method_name}"

    async with httpx.AsyncClient() as client:
        try:
            if http_method == "POST":
                response = await client.post(url, json=data, headers=headers)
            elif http_method == "PUT":
                response = await client.put(url, json=data, headers=headers)
            elif http_method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:  # Default to GET
                response = await client.get(url, headers=headers)

            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Dapr invocation failed: {e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Dapr invocation request error: {e}")
            raise


def validate_required_args(
    arguments: dict, required: list[str], tool_name: str
) -> None:
    """Validate that required arguments are present and non-empty.

    Raises:
        ValueError: If any required argument is missing or empty.
    """
    missing = [arg for arg in required if not arguments.get(arg)]
    if missing:
        raise ValueError(
            f"Missing required arguments for {tool_name}: {', '.join(missing)}"
        )


# Create a global FastMCP instance to register tools
mcp_app_instance = FastMCP(
    "Todo MCP Server",
    json_response=True,  # Ensure JSON-RPC compatible responses
)
logger.debug(f"FastMCP instance '{mcp_app_instance.name}' initialized globally.")

# Tool context provided by the MCP client will contain authentication headers
# The MCP_INTERNAL_SECRET is directly available via settings


@mcp_app_instance.tool()
async def get_user_stats(user_id: str, context: Dict) -> List[TextContent]:
    """Get user task stats (pending/completed)."""
    logger.debug(f"Calling get_user_stats for user_id: {user_id}")

    headers = {
        "Authorization": f"Bearer {context['token']}",
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
    }

    try:
        response = await invoke_dapr_service(
            TODO_APP_ID, "api/todos/stats", http_method="GET", headers=headers
        )
        pending = response.get("pending", 0)
        completed = response.get("completed", 0)
        total = response.get("total", 0)
        return [
            TextContent(
                type="text",
                text=f"Pending tasks: {pending}, Completed tasks: {completed}, Total tasks: {total}",
            )
        ]
    except Exception as e:
        logger.error(f"Error getting user stats for user {user_id}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error getting user stats: {e}")]


@mcp_app_instance.tool()
async def check_duplicate_task(
    user_id: str, title: str, context: Dict
) -> List[TextContent]:
    """Check if a similar task already exists (case-insensitive, whitespace-trimmed)."""
    logger.debug(f"Calling check_duplicate_task for user_id: {user_id}, title: {title}")

    validate_required_args({"title": title}, ["title"], "check_duplicate_task")

    headers = {
        "Authorization": f"Bearer {context['token']}",
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
    }

    try:
        response = await invoke_dapr_service(
            TODO_APP_ID,
            f"api/todos/check_duplicate?title={title}",
            http_method="GET",
            headers=headers,
        )
        if response.get("is_duplicate"):
            return [
                TextContent(
                    type="text",
                    text=f"DUPLICATE FOUND: A task with similar title already exists: '{response['existing_title']}' (ID: {response['existing_id']}, Completed: {response['is_complete']})",
                )
            ]
        return [
            TextContent(
                type="text", text="NO DUPLICATE: No similar task found. Safe to create."
            )
        ]
    except Exception as e:
        logger.error(
            f"Error checking duplicate task for user {user_id}, title {title}: {e}",
            exc_info=True,
        )
        return [TextContent(type="text", text=f"Error checking duplicate task: {e}")]


@mcp_app_instance.tool()
async def add_task(
    user_id: str, title: str, description: Optional[str] = None, context: Dict = {}
) -> List[TextContent]:
    """Adds a new task to the database. Automatically checks for duplicates using case-insensitive title matching."""
    logger.debug(f"Calling add_task for user_id: {user_id}, title: {title}")

    validate_required_args({"title": title}, ["title"], "add_task")

    headers = {
        "Authorization": f"Bearer {context['token']}",
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
    }

    data = {"title": title, "description": description}

    try:
        response = await invoke_dapr_service(
            TODO_APP_ID, "api/todos", http_method="POST", data=data, headers=headers
        )
        return [
            TextContent(
                type="text",
                text=f"Task '{response['title']}' added with ID: {response['id']}",
            )
        ]
    except Exception as e:
        logger.error(
            f"Error adding task for user {user_id}, title {title}: {e}", exc_info=True
        )
        return [TextContent(type="text", text=f"Error adding task: {e}")]


@mcp_app_instance.tool()
async def list_tasks(user_id: str, context: Dict = {}) -> List[TextContent]:
    """Lists all tasks for a user."""
    logger.debug(f"Calling list_tasks for user_id: {user_id}")

    headers = {
        "Authorization": f"Bearer {context['token']}",
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
    }

    try:
        todos_response = await invoke_dapr_service(
            TODO_APP_ID, "api/todos", http_method="GET", headers=headers
        )
        todos = todos_response.get("todos", [])

        if not todos:
            return [TextContent(type="text", text="No tasks found.")]

        task_list = "\n".join(
            [
                f"- {t['title']} (ID: {t['id']}, Completed: {t['is_complete']})"
                for t in todos
            ]
        )
        return [TextContent(type="text", text=f"Your tasks:\n{task_list}")]
    except Exception as e:
        logger.error(f"Error listing tasks for user {user_id}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error listing tasks: {e}")]


@mcp_app_instance.tool()
async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_complete: Optional[bool] = None,
    context: Dict = {},
) -> List[TextContent]:
    """Updates a task."""
    logger.debug(f"Calling update_task for user_id: {user_id}, task_id: {task_id}")

    validate_required_args({"task_id": task_id}, ["task_id"], "update_task")

    headers = {
        "Authorization": f"Bearer {context['token']}",
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
    }

    data = {}
    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if is_complete is not None:
        data["is_complete"] = is_complete

    if not data:
        return [TextContent(type="text", text="No fields provided to update.")]

    try:
        response = await invoke_dapr_service(
            TODO_APP_ID,
            f"api/todos/{task_id}",
            http_method="PUT",
            data=data,
            headers=headers,
        )
        return [TextContent(type="text", text=f"Task '{response['id']}' updated.")]
    except Exception as e:
        logger.error(
            f"Error updating task {task_id} for user {user_id}: {e}", exc_info=True
        )
        return [TextContent(type="text", text=f"Error updating task: {e}")]


@mcp_app_instance.tool()
async def delete_task(
    user_id: str, task_id: str, context: Dict = {}
) -> List[TextContent]:
    """Deletes a task."""
    logger.debug(f"Calling delete_task for user_id: {user_id}, task_id: {task_id}")

    validate_required_args({"task_id": task_id}, ["task_id"], "delete_task")

    headers = {
        "Authorization": f"Bearer {context['token']}",
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
    }

    try:
        response = await invoke_dapr_service(
            TODO_APP_ID, f"api/todos/{task_id}", http_method="DELETE", headers=headers
        )
        return [TextContent(type="text", text=f"Task '{task_id}' deleted.")]
    except Exception as e:
        logger.error(
            f"Error deleting task {task_id} for user {user_id}: {e}", exc_info=True
        )
        return [TextContent(type="text", text=f"Error deleting task: {e}")]


@mcp_app_instance.tool()
async def complete_task(
    user_id: str, task_id: str, context: Dict = {}
) -> List[TextContent]:
    """Marks a task as completed."""
    logger.debug(f"Calling complete_task for user_id: {user_id}, task_id: {task_id}")

    validate_required_args({"task_id": task_id}, ["task_id"], "complete_task")

    headers = {
        "Authorization": f"Bearer {context['token']}",
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
    }

    data = {"is_complete": True}

    try:
        response = await invoke_dapr_service(
            TODO_APP_ID,
            f"api/todos/{task_id}",
            http_method="PATCH",
            data=data,
            headers=headers,
        )  # Use PATCH for partial update
        return [TextContent(type="text", text=f"Task '{task_id}' marked as completed.")]
    except Exception as e:
        logger.error(
            f"Error completing task {task_id} for user {user_id}: {e}", exc_info=True
        )
        return [TextContent(type="text", text=f"Error completing task: {e}")]


