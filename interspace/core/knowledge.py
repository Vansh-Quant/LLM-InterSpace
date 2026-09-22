from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class ProjectStateUpsert(BaseModel):
    key: str = Field(min_length=1, max_length=150)
    value: Any
    updated_by: str = Field(min_length=1, max_length=100)

class ProjectStateResponse(ProjectStateUpsert):
    updated_at: datetime

class KnowledgeCreate(BaseModel):
    key: str = Field(min_length=1, max_length=150)
    value: Any
    scope: str = Field(default="project", pattern="^(project|shared_agent)$")
    created_by: str = Field(min_length=1, max_length=100)
    status: str = Field(default="VERIFIED", pattern="^(UNVERIFIED|VERIFIED|INVALIDATED)$")

class KnowledgeResponse(KnowledgeCreate):
    knowledge_id: str
    created_at: datetime
