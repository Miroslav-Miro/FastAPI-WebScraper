from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class ItemRead(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    url: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
