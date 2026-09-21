from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "LLM InterSpace"
    database_path: str = "storage/interspace.db"
    heartbeat_timeout_seconds: int = 30

settings = Settings()
