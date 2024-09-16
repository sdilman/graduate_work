from enum import StrEnum, auto


class YookassaObjectTypes(StrEnum):
    PAYMENT = auto()
    REFUND = auto()


class YookassaPaymentStatuses(StrEnum):
    PENDING = auto()
    WAITING_FOR_CAPTURE = auto()
    SUCCEEDED = auto()
    CANCELED = auto()


class YookassaRefundStatuses(StrEnum):
    PENDING = auto()
    SUCCEEDED = auto()
    CANCELED = auto()
