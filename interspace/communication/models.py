from datetime import datetime
from pydantic import BaseModel, Field

class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    agent_id: str | None = None
    payload: dict = Field(default_factory=dict)

class EventResponse(EventCreate):
    event_id: str
    created_at: datetime
