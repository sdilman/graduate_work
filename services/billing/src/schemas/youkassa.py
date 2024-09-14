from __future__ import annotations

from typing import Any

from enum import StrEnum, auto

from pydantic import BaseModel


class YoukassaObjectTypes(StrEnum):
    PAYMENT = auto()
    REFUND = auto()


class YoukassaPaymentStatuses(StrEnum):
    PENDING = auto()
    WAITING_FOR_CAPTURE = auto()
    SUCCEEDED = auto()
    CANCELED = auto()


class YoukassaRefundStatuses(StrEnum):
    PENDING = auto()
    SUCCEEDED = auto()
    CANCELED = auto()


class YoukassaPaymentObject(BaseModel):
    id: str
    status: YoukassaPaymentStatuses
    description: str | None
    payment_method: dict[str, Any] | None
    captured_at: str | None
    created_at: str
    expires_at: str
    paid: bool
    cancellation_details: dict[str, Any] | None


class YoukassaEventNotification(BaseModel):
    type: str
    event: str
    object: dict[str, Any]
