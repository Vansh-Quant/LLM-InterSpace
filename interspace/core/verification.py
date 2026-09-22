from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class VerificationCreate(BaseModel):
    fact_type: str = Field(min_length=1, max_length=80)
    fact_id: str = Field(min_length=1, max_length=150)
    created_by: str = Field(min_length=1, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)

class VerificationTransition(BaseModel):
    target_state: str
    actor_id: str = Field(min_length=1, max_length=100)
    note: str = ""

class VerificationResponse(VerificationCreate):
    verification_id: str
    state: str
    created_at: datetime
    updated_at: datetime
