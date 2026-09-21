from datetime import datetime

from pydantic import BaseModel, Field


class ContractSubscriptionCreate(BaseModel):
    contract_id: str = Field(min_length=1, max_length=150)
    agent_id: str = Field(min_length=1, max_length=100)


class ContractSubscriptionResponse(BaseModel):
    contract_id: str
    agent_id: str
    created_at: datetime


class NotificationResponse(BaseModel):
    notification_id: str
    agent_id: str
    notification_type: str
    contract_id: str
    from_version: int
    to_version: int
    payload: dict
    status: str
    created_at: datetime
