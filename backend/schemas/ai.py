from typing import List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_alert_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: str
    model_used: str
    is_mock: bool = False
