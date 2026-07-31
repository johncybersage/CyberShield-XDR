from fastapi import APIRouter, HTTPException

from backend.auth.dependencies import CurrentUser
from backend.config.logging_config import get_logger
from backend.schemas.ai import ChatRequest, ChatResponse
from backend.services.ai.service import ai_service

logger = get_logger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse, summary="Chat with AI Assistant")
async def chat_with_assistant(
    request: ChatRequest,
    current_user: CurrentUser
):
    """
    Send a message to the AI SOC Assistant.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
    try:
        # Convert pydantic models to dict
        messages_dict = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # If context_alert_id is provided, we could fetch alert details and inject them into the system prompt or first message
        # For MVP, we'll just pass the messages directly
        
        response_data = await ai_service.chat(messages_dict)
        return ChatResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
