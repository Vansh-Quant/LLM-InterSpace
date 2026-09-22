from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class MessageCreate(BaseModel):
    sender_id: str = Field(min_length=1, max_length=100)
    recipient_id: str = Field(min_length=1, max_length=100)
    message_type: str = Field(min_length=1, max_length=100)
    payload: dict[str, Any] = Field(default_factory=dict)

class MessageResponse(MessageCreate):
    message_id: str
    created_at: datetime
