import datetime

from uuid import uuid4

from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, relationship

from models.enums import Currency, OrderStatus, TransactionStatus, TransactionType


class Base(DeclarativeBase): ...


class BaseMixin:
    __abstract__ = True
    __slots__ = ()


class UUIDMixin(BaseMixin):
    """Add UUID field to the model."""

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()), unique=True, nullable=False)


class DatesMixin(BaseMixin):
    """Add timestamp fields to the model."""

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), nullable=False)
    updated_at = Column(DateTime)
    closed_at = Column(DateTime)


class PaymentMethod(UUIDMixin, DatesMixin, Base):
    __tablename__ = "payment_method"

    user_id = Column(UUID, nullable=False)
    payment_token = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)


class Product(UUIDMixin, DatesMixin, Base):
    __tablename__ = "product"

    title = Column(String, nullable=False)
    description = Column(String)
    basic_price = Column(Float, nullable=False)
    basic_currency = Column(String, nullable=False)

    user_products = relationship("UserProduct", back_populates="product")
    order_products = relationship("OrderProduct", back_populates="product")


class UserProduct(UUIDMixin, DatesMixin, Base):
    __tablename__ = "user_product"

    product_id = Column(UUID, ForeignKey("product.id"), nullable=False)
    user_id = Column(UUID, nullable=False)
    active_from = Column(DateTime)
    active_till = Column(DateTime)
    renewal_enabled = Column(Boolean, default=False)

    product = relationship("Product", back_populates="user_products")


class Order(UUIDMixin, DatesMixin, Base):
    __tablename__ = "order"

    user_id = Column(UUID, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(Enum(Currency), nullable=False)

    order_products = relationship("OrderProduct", back_populates="order")
    transactions = relationship("Transaction", back_populates="order")


class OrderProduct(UUIDMixin, DatesMixin, Base):
    __tablename__ = "order_product"

    order_id = Column(UUID, ForeignKey("order.id"), nullable=False)
    product_id = Column(UUID, ForeignKey("product.id"), nullable=False)

    order = relationship("Order", back_populates="order_products")
    product = relationship("Product", back_populates="order_products")


class Transaction(UUIDMixin, DatesMixin, Base):
    __tablename__ = "transaction"

    order_id = Column(UUID, ForeignKey("order.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(Enum(Currency), nullable=False)

    order = relationship("Order", back_populates="transactions")
