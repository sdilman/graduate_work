from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class UserIdMixin(BaseModel):
    user_id: UUID | None = Field(default=None, description="Expecting from access token")


class IdempotencyKeyMixin(BaseModel):
    idempotency_key: str = Field(default_factory=lambda: uuid4().hex, description="Expecting from request")


class UUIDMixin(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class CreatedAtMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now, description="Created at timestamp")


class TimestampsMixin(CreatedAtMixin):
    updated_at: datetime | None = None
    closed_at: datetime | None = None
