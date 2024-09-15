from enum import StrEnum, auto


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
