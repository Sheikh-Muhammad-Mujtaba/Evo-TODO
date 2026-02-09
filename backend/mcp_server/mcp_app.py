import logging
import json
from typing import List, Optional, Dict, Annotated
from uuid import UUID

from mcp.server.fastmcp import FastMCP, Context
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


def get_auth_headers_from_context(ctx: Optional[Context], user_id: str) -> Dict[str, str]:
    """Extract authentication headers from MCP request context.
    
    This function is CRITICAL for multi-user concurrent request handling.
    Each HTTP request to the MCP server includes user-specific headers that MUST
    be extracted and passed to Dapr services to maintain proper authorization.
    
    In stateless_http mode, FastMCP creates a new context for each request,
    ensuring thread-safe isolation between concurrent users.
    
    Args:
        ctx: MCP Context object containing request metadata and headers
        user_id: Fallback user_id if context is unavailable
        
    Returns:
        Dictionary of headers to pass to Dapr service invocations
    """
    # Default fallback headers (should only be used in testing/development)
    headers = {
        "X-User-ID": user_id,
        "X-Internal-Secret": settings.MCP_INTERNAL_SECRET,
        "Authorization": "",
    }
    
    if ctx is None:
        logger.warning(
            f"No MCP context available for user {user_id}. "
            "Using fallback headers. This should only happen in tests."
        )
        return headers
    
    # Try to access HTTP headers from the context's request_context
    # The request_context may contain HTTP headers in some MCP SDK versions
    try:
        # Check if context has request_context with headers
        if hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
            meta = ctx.request_context.meta
            if isinstance(meta, dict):
                # Extract user-specific headers (case-insensitive)
                extracted_user_id = meta.get("x-user-id") or meta.get("X-User-ID")
                extracted_secret = meta.get("x-internal-secret") or meta.get("X-Internal-Secret")
                extracted_auth = meta.get("authorization") or meta.get("Authorization")

                if extracted_user_id:
                    headers["X-User-ID"] = extracted_user_id
                    logger.debug(f"Extracted user_id from context: {extracted_user_id}")

                if extracted_secret:
                    headers["X-Internal-Secret"] = extracted_secret

                if extracted_auth:
                    headers["Authorization"] = extracted_auth
                    logger.debug(f"Extracted authorization token for user {extracted_user_id}")
            else:
                logger.debug(
                    f"Context meta is not a dict for user {user_id}. "
                    "Using fallback headers."
                )
        else:
            logger.debug(
                f"Context does not have request_context.meta for user {user_id}. "
                "Using fallback headers."
            )
    except Exception as e:
        logger.warning(
            f"Error extracting headers from context for user {user_id}: {e}. "
            "Using fallback headers."
        )
    
    return headers


# Create a global FastMCP instance to register tools
# stateless_http=True is CRITICAL for Dockerized microservices to prevent session termination
# In stateless mode, each request is independent and doesn't rely on RAM-based session IDs
mcp_app_instance = FastMCP(
    name="Todo MCP Server",
    stateless_http=False,  # Re-enable SSE for compatibility with agents.mcp.MCPServerStreamableHttp
    json_response=True,   # Ensure JSON-RPC compatible responses
)
logger.debug(
    f"FastMCP instance '{mcp_app_instance.name}' initialized globally with stateless_http=False (SSE Enabled)."
)

# Tool context provided by the MCP client will contain authentication headers
# The MCP_INTERNAL_SECRET is directly available via settings


@mcp_app_instance.tool()
async def get_user_stats(
    user_id: str,
    ctx: Annotated[Context, "MCP request context"] = None
) -> List[TextContent]:
    """Get user task stats (pending/completed)."""
    logger.debug(f"Calling get_user_stats for user_id: {user_id}")

    # Extract headers from the current HTTP request context
    # This ensures each concurrent user gets their own authentication
    headers = get_auth_headers_from_context(ctx, user_id)

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
    user_id: str,
    title: str,
    ctx: Annotated[Context, "MCP request context"] = None
) -> List[TextContent]:
    """Check if a similar task already exists (case-insensitive, whitespace-trimmed)."""
    logger.debug(f"Calling check_duplicate_task for user_id: {user_id}, title: {title}")

    validate_required_args({"title": title}, ["title"], "check_duplicate_task")

    # Extract headers from the current HTTP request context
    headers = get_auth_headers_from_context(ctx, user_id)

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
    user_id: str,
    title: str,
    description: Optional[str] = None,
    ctx: Annotated[Context, "MCP request context"] = None
) -> List[TextContent]:
    """Adds a new task to the database. Automatically checks for duplicates using case-insensitive title matching."""
    logger.debug(f"Calling add_task for user_id: {user_id}, title: {title}")

    validate_required_args({"title": title}, ["title"], "add_task")

    # Extract headers from the current HTTP request context
    headers = get_auth_headers_from_context(ctx, user_id)

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
async def list_tasks(
    user_id: str,
    ctx: Annotated[Context, "MCP request context"] = None
) -> List[TextContent]:
    """Lists all tasks for a user."""
    logger.debug(f"Calling list_tasks for user_id: {user_id}")

    # Extract headers from the current HTTP request context
    headers = get_auth_headers_from_context(ctx, user_id)

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
    ctx: Annotated[Context, "MCP request context"] = None
) -> List[TextContent]:
    """Updates a task."""
    logger.debug(f"Calling update_task for user_id: {user_id}, task_id: {task_id}")

    validate_required_args({"task_id": task_id}, ["task_id"], "update_task")

    # Extract headers from the current HTTP request context
    headers = get_auth_headers_from_context(ctx, user_id)

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
    user_id: str,
    task_id: str,
    ctx: Annotated[Context, "MCP request context"] = None
) -> List[TextContent]:
    """Deletes a task."""
    logger.debug(f"Calling delete_task for user_id: {user_id}, task_id: {task_id}")

    validate_required_args({"task_id": task_id}, ["task_id"], "delete_task")

    # Extract headers from the current HTTP request context
    headers = get_auth_headers_from_context(ctx, user_id)

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
    user_id: str,
    task_id: str,
    ctx: Annotated[Context, "MCP request context"] = None
) -> List[TextContent]:
    """Marks a task as completed."""
    logger.debug(f"Calling complete_task for user_id: {user_id}, task_id: {task_id}")

    validate_required_args({"task_id": task_id}, ["task_id"], "complete_task")

    # Extract headers from the current HTTP request context
    headers = get_auth_headers_from_context(ctx, user_id)

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
