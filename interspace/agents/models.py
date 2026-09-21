from datetime import datetime, timezone
from pydantic import BaseModel, Field

class AgentRegistration(BaseModel):
    agent_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=200)
    capabilities: list[str] = Field(default_factory=list)

class AgentHeartbeat(BaseModel):
    status: str = Field(default="online", pattern="^(online|busy|idle|offline)$")

class AgentResponse(AgentRegistration):
    status: str
    last_heartbeat: datetime | None = None

def utc_now() -> datetime:
    return datetime.now(timezone.utc)
