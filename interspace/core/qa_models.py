from datetime import datetime
from pydantic import BaseModel, Field

class QARunCreate(BaseModel):
    test_path: str | None = None
    timeout_seconds: int = Field(default=60, ge=1, le=300)
    requested_by: str = Field(min_length=1, max_length=100)

class QARunResponse(BaseModel):
    qa_run_id: str
    requested_by: str
    status: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    created_at: datetime
