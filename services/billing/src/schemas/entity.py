from __future__ import annotations

from typing import TYPE_CHECKING

from uuid import UUID  # noqa:TCH003

from core.constraints import Currency, OrderStatus, TransactionStatus, TransactionType
from schemas.mixins import IdempotencyKeyMixin, TimestampsMixin, UserIdMixin, UUIDMixin

if TYPE_CHECKING:
    from datetime import datetime


class PaymentMethodSchema(UUIDMixin, TimestampsMixin):
    user_id: UUID
    payment_token: str
    payment_method: str
    description: str | None
    is_active: bool = True


class ProductSchema(UUIDMixin, TimestampsMixin):
    title: str
    description: str | None
    basic_price: float
    basic_currency: Currency


class OrderSchema(UUIDMixin, TimestampsMixin, UserIdMixin, IdempotencyKeyMixin):
    status: OrderStatus = OrderStatus.PENDING
    currency: Currency = Currency.RUB
    products_id: list[str]
    total_amount: float | None = None


class UserProductSchema(UUIDMixin, TimestampsMixin):
    product_id: str
    user_id: str
    active_from: datetime | None
    active_till: datetime | None
    renewal_enabled: bool = False


class OrderProductSchema(UUIDMixin, TimestampsMixin):
    order_id: str
    product_id: str


class TransactionSchema(UUIDMixin, TimestampsMixin):
    order_id: str
    type: TransactionType
    status: TransactionStatus
    amount: float
    currency: Currency
