from __future__ import annotations

from datetime import datetime  # noqa: TCH003

from pydantic import BaseModel


class PaymentResult(BaseModel):
    created_at: datetime | None = None
    message: str
