from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PaymentResult(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    message: str
