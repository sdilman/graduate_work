from enum import StrEnum, auto


class Currency(StrEnum):
    RUB = auto()


class TransactionStatus(StrEnum):
    PENDING = auto()
    SUCCEEDED = auto()
    CANCELLED = auto()


class TransactionType(StrEnum):
    PAYMENT = auto()
    REFUND = auto()


class OrderStatus(StrEnum):
    PENDING = auto()
    PAID = auto()
    REFUNDING = auto()
    REFUNDED = auto()
