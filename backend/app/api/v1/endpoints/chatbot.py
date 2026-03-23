from fastapi import APIRouter, Depends
from ....services.chatbot_service import chatbot_service
from ....core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/message")
async def send_message(req: ChatRequest, user: dict = Depends(get_current_user)):
    result = chatbot_service.process_message(req.message, user["username"])
    return result

@router.get("/history")
async def get_history(user: dict = Depends(get_current_user)):
    return {"messages": [], "note": "Chat history is session-based in this version."}
