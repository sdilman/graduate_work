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


class PaymentObjectMetadata(BaseModel):
    transaction_id: str | None = None


class YoukassaPaymentObject(BaseModel):
    id: str
    status: YoukassaPaymentStatuses
    description: str | None = None
    payment_method: dict[str, Any] | None = None
    captured_at: str | None = None
    created_at: str | None = None
    expires_at: str | None = None
    paid: bool
    cancellation_details: dict[str, Any] | None = None
    metadata: PaymentObjectMetadata | None = None


class YoukassaEventNotification(BaseModel):
    type: str
    event: str
    object: dict[str, Any]
