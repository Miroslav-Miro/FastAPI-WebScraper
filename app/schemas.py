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


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: UUID
    username: str

    model_config = ConfigDict(from_attributes=True)
