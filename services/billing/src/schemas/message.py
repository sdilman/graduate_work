from __future__ import annotations

from schemas.mixins import CreatedAtMixin


class PaymentResult(CreatedAtMixin):
    message: str
