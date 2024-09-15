from __future__ import annotations

from mixins import CreatedAtMixin


class PaymentResult(CreatedAtMixin):
    message: str
