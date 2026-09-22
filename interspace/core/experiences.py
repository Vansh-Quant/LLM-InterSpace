from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class ExperienceCreate(BaseModel):
    problem: str = Field(min_length=1)
    action: str = Field(min_length=1)
    result: str = Field(min_length=1)
    verification: str = Field(min_length=1)
    created_by: str = Field(min_length=1, max_length=100)
    status: str = Field(default="UNVERIFIED", pattern="^(UNVERIFIED|OBSERVED|TESTED|VERIFIED|REUSED|RECONFIRMED|REVIEW|REVISED|INVALIDATED)$")
    metadata: dict[str, Any] = Field(default_factory=dict)

class ExperienceResponse(ExperienceCreate):
    experience_id: str
    created_at: datetime
    updated_at: datetime

class ExperienceSearch(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
