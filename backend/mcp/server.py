from fastmcp import FastMCP
from app.models import Todo, SessionLocal
from app.schemas.todo import TodoCreate, TodoUpdate
from typing import List
from uuid import UUID

mcp = FastMCP("Todo MCP Server")

@mcp.tool
def get_user_stats(user_id: str) -> dict:
    """Get user task stats (pending/completed)."""
    with SessionLocal() as db:
        pending = db.query(Todo).filter(Todo.user_id == user_id, Todo.is_complete == False).count()
        completed = db.query(Todo).filter(Todo.user_id == user_id, Todo.is_complete == True).count()
        return {"pending": pending, "completed": completed}

@mcp.tool
def todo_crud(action: str, user_id: str, **kwargs) -> dict:
    """Todo CRUD: add/list/update/delete/complete."""
    with SessionLocal() as db:
        if action == "list":
            todos = db.query(Todo).filter(Todo.user_id == user_id).all()
            return [{"id": t.id, "title": t.title, "is_complete": t.is_complete} for t in todos]
        elif action == "add":
            todo = Todo(**kwargs, user_id=user_id)
            db.add(todo)
            db.commit()
            return {"id": todo.id, "status": "added"}
        elif action == "update":
            todo = db.query(Todo).filter(Todo.id == kwargs["id"], Todo.user_id == user_id).first()
            if todo:
                for k, v in kwargs.items():
                    setattr(todo, k, v)
                db.commit()
                return {"status": "updated"}
        elif action == "delete":
            todo = db.query(Todo).filter(Todo.id == kwargs["id"], Todo.user_id == user_id).delete()
            db.commit()
            return {"status": "deleted"}
        elif action == "complete":
            todo = db.query(Todo).filter(Todo.id == kwargs["id"], Todo.user_id == user_id).first()
            if todo:
                todo.is_complete = True
                db.commit()
                return {"status": "completed"}
    return {"error": "not found"}

# T302: MCP server with CRUD/stats tools (user_id injection)
if __name__ == "__main__":
    mcp.run()
