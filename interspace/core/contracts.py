from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ContractPublish(BaseModel):
    contract_id: str = Field(min_length=1, max_length=150)
    name: str = Field(min_length=1, max_length=200)
    definition: dict[str, Any]
    created_by: str = Field(min_length=1, max_length=100)


class ContractVersionResponse(BaseModel):
    contract_id: str
    name: str
    version: int
    definition: dict[str, Any]
    created_by: str
    created_at: datetime


class ContractSummary(BaseModel):
    contract_id: str
    name: str
    latest_version: int
    updated_at: datetime


class ContractDiffResponse(BaseModel):
    contract_id: str
    from_version: int
    to_version: int
    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)
    changed: list[str] = Field(default_factory=list)
