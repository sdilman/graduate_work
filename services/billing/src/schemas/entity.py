from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class UUIDMixinSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4)


class DatesMixinSchema(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = None
    closed_at: datetime | None = None


class CurrencySchema(StrEnum):
    RUB = auto()


class OrderStatusSchema(StrEnum):
    PENDING = auto()
    PAID = auto()
    REFUNDING = auto()
    REFUNDED = auto()


class TransactionTypeSchema(StrEnum):
    PAYMENT = auto()
    REFUND = auto()


class TransactionStatusSchema(StrEnum):
    PENDING = auto()
    SUCCEEDED = auto()
    CANCELLED = auto()


class PaymentMethodSchema(UUIDMixinSchema, DatesMixinSchema):
    user_id: UUID
    payment_token: str
    payment_method: str
    description: str | None
    is_active: bool = True


class ProductSchema(UUIDMixinSchema, DatesMixinSchema):
    title: str
    description: str | None
    basic_price: float
    basic_currency: CurrencySchema


class OrderSchema(UUIDMixinSchema, DatesMixinSchema):
    user_id: UUID | None = Field(default=None, description="Retrieved from access token")
    status: OrderStatusSchema = OrderStatusSchema.PENDING
    currency: CurrencySchema = CurrencySchema.RUB
    products_id: list[str]
    total_amount: float | None = None


class UserProductSchema(UUIDMixinSchema, DatesMixinSchema):
    product_id: str
    user_id: str
    active_from: datetime | None
    active_till: datetime | None
    renewal_enabled: bool = False


class OrderProductSchema(UUIDMixinSchema, DatesMixinSchema):
    order_id: str
    product_id: str


class TransactionSchema(UUIDMixinSchema, DatesMixinSchema):
    order_id: str
    type: TransactionTypeSchema
    status: TransactionStatusSchema
    amount: float
    currency: CurrencySchema
