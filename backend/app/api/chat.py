from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import os
import jwt
import google.generativeai as genai

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: str

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Gemini-2.5-flash alias/exp

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, authorization: str = Header(None)):
    print(f"[Backend Chat] User {request.user_id}: {request.message[:50]}...")

    # JWT Auth (Better Auth)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]
    try:
        secret = os.getenv("BETTER_AUTH_SECRET")
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if payload.get('sub') != request.user_id:
            raise HTTPException(status_code=401, detail="Token mismatch")
        print(f"[Backend Chat] Verified user: {payload.get('sub')}")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        response = model.generate_content(request.message)
        ai_response = response.text
        print(f"[Backend Chat] Gemini response length: {len(ai_response)}")
        conv_id = request.conversation_id or str(hash(request.message + str(request.user_id)))
        return {
            "response": ai_response,
            "conversation_id": conv_id
        }
    except Exception as e:
        print(f"[Backend Chat] Gemini error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
