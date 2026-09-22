from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class AuditEventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=120)
    actor_id: str | None = None
    entity_type: str = Field(min_length=1, max_length=80)
    entity_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

class AuditEventResponse(AuditEventCreate):
    audit_id: str
    created_at: datetime
