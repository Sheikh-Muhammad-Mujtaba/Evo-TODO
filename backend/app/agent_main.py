from fastapi import FastAPI, APIRouter
from .api.chat import router as chat_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Agent Service is running!"}

app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
