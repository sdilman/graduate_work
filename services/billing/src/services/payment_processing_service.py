from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from core.constraints import OrderStatus
from core.logger import get_logger
from models.pg import Order, OrderProduct, PaymentMethod, Product, Transaction, UserProduct
from schemas.youkassa import YoukassaPaymentObject, YoukassaPaymentStatuses

logger = get_logger(__name__)


class PaymentResultsProcessingService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _update_transaction(self, payment_object: YoukassaPaymentObject) -> Transaction | None:
        stmt = select(Transaction).where(Transaction.id == payment_object.metadata.transaction_id)
        result = await self._session.execute(stmt)
        transaction = result.scalar_one_or_none()
        if transaction:
            # TODO: add mapping from payment obj status to order and transaction status
            transaction.status = payment_object.status.value
            self._session.add(transaction)
        return transaction

    async def _update_order(self, transaction: Transaction) -> Order | None:
        order_stmt = select(Order).where(Order.id == transaction.order_id)
        result = await self._session.execute(order_stmt)
        order = result.scalar_one_or_none()
        if order:
            order.status = OrderStatus.PAID
            self._session.add(order)
        return order

    async def _save_payment_method(self, payment_token: str, user_id: str) -> None:
        payment_method = PaymentMethod(user_id=user_id, payment_token=payment_token, payment_method="", description="")
        self._session.add(payment_method)

    async def _get_products(self, payment_object: YoukassaPaymentObject, user_id: str, order_id: str) -> None:
        user_products_stmt = select(UserProduct).where(UserProduct.user_id == user_id)
        result = await self._session.execute(user_products_stmt)
        user_products = result.scalars()
        user_products = {p.product_id: p for p in user_products}

        order_products_stmt = (
            select(Product)
            .join(OrderProduct, Product.id == OrderProduct.product_id)
            .where(OrderProduct.order_id == order_id)
        )

        results = await self._session.execute(order_products_stmt)
        order_products = results.scalars()

        products_to_add = []
        products_to_edit = []

        for product in order_products:
            if product.id in user_products:
                product.active_till = product.active_till + timedelta(days=30)
                products_to_edit.append(product)
            else:
                now = datetime.now()
                new_product = UserProduct(
                    user_id=user_id,
                    product_id=product.id,
                    # check if payment method save
                    renewal_enabled=payment_object.payment_method.get("saved", False),
                    active_from=now,
                    # TODO; remove hardcode
                    active_till=now + timedelta(days=30),
                )
                products_to_add.append(new_product)

        self._session.add_all(products_to_add + products_to_edit)

    async def process_payment_result(self, payment_object: YoukassaPaymentObject) -> None:
        if payment_object.status == YoukassaPaymentStatuses.SUCCEEDED:
            await self.process_success_payment_result(payment_object)
        elif payment_object.status == YoukassaPaymentStatuses.CANCELED:
            await self.process_canceled_payment_result(payment_object)
        else:
            logger.info("Can't handle payment object with status '%s'. Skip it", payment_object.status)

    async def process_success_payment_result(self, payment_object: YoukassaPaymentObject) -> None:
        transaction = await self._update_transaction(payment_object)
        order = await self._update_order(transaction)
        user_id = order.user_id  # type: ignore # noqa: PGH003

        if payment_object.payment_method and payment_object.payment_method.get("saved", False):
            await self._save_payment_method(payment_object.payment_method["id"], user_id)

        await self._get_products(payment_object, user_id, order.id)  # type: ignore # noqa: PGH003

    async def process_canceled_payment_result(self, payment_object: YoukassaPaymentObject) -> None:
        await self._update_transaction(payment_object)
