from __future__ import annotations

from typing import cast

import itertools

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.constraints import TransactionStatus, TransactionType
from core.logger import get_logger
from core.settings import settings as cfg
from interfaces.repositories import RedisRepositoryProtocol
from models.pg import Order, OrderProduct, Product, Transaction
from schemas.cache import CacheReadDto, CacheSetDto
from schemas.entity import OrderSchema
from services.payment import PaymentService

logger = get_logger(__name__)


class OrderService:
    def __init__(self, db: AsyncSession, redis_repo: RedisRepositoryProtocol, payment_service: PaymentService):
        self._db = db
        self._repo = redis_repo
        self._payment_service = payment_service

    async def _check_idempotency_key(self, order_schema: OrderSchema) -> None:
        key = f"{cfg.redis.prefix}{order_schema.idempotency_key}"
        result = await self._repo.read(CacheReadDto(name=key))
        if result:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Duplicate request: idempotency key already used."
            )

    async def _store_argument_pairs_in_cache(self, *args: str) -> None:
        pairs = itertools.combinations(args, 2)
        for name, value in pairs:
            name_ = f"{cfg.redis.prefix}{name}"
            await self._repo.create(CacheSetDto(name=name_, value=value))

    async def _get_nonexists_products(self, order_schema: OrderSchema) -> set[str]:
        products_stmt = select(Product).where(Product.id.in_(order_schema.products_id))
        res = await self._db.execute(products_stmt)
        products = res.scalars()
        existing_product_ids = {str(p.id) for p in products}
        return set(order_schema.products_id).difference(existing_product_ids)

    async def _calculate_total_order_price(self, order_schema: OrderSchema) -> float:
        total_amount_stmt = select(func.sum(Product.basic_price)).where(Product.id.in_(order_schema.products_id))
        res = await self._db.execute(total_amount_stmt)
        total_amount = res.scalar_one_or_none()
        if total_amount is None:
            total_amount = 0
        return cast(float, total_amount)

    async def _create_order_products(self, new_order: Order, order_schema: OrderSchema) -> list[OrderProduct]:
        order_products = []
        for product_id in order_schema.products_id:
            new_order_product = OrderProduct(
                order_id=new_order.id, product_id=product_id, created_at=order_schema.created_at
            )
            order_products.append(new_order_product)
        return order_products

    # TODO: add transaction
    async def create_order(self, order_schema: OrderSchema) -> Order:
        await self._check_idempotency_key(order_schema)

        non_existing_products_ids = await self._get_nonexists_products(order_schema)

        if non_existing_products_ids:
            detail = f"Products do not exist: {non_existing_products_ids}"
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

        total_price = await self._calculate_total_order_price(order_schema)

        new_order = Order(
            user_id=order_schema.user_id,
            status=order_schema.status,
            currency=order_schema.currency,
            created_at=order_schema.created_at,
            total_amount=total_price,
        )
        self._db.add(new_order)
        await self._db.commit()

        order_products = await self._create_order_products(new_order, order_schema)
        self._db.add_all(order_products)
        await self._db.commit()

        await self._store_argument_pairs_in_cache(order_schema.idempotency_key, new_order.id)

        return new_order

    async def get_order(self, order_id: str) -> Order:
        result = await self._db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    # TODO: add transaction rollback
    async def get_payment_link_for_order(self, order_id: str, base_url: str) -> str:
        cached_link = await self._repo.read(CacheReadDto(name=order_id))

        if cached_link:
            return cast(str, cached_link)

        order = await self.get_order(order_id)
        if order is None:
            detail = f"No order found with ID {order_id}"
            raise HTTPException(status_code=404, detail=detail)

        succeeded_transactions_exists = await self._db.execute(
            select(func.count()).where(
                and_(Transaction.status == TransactionStatus.SUCCEEDED, Transaction.order_id == order.id)
            )
        )
        succeeded_transactions_exists = succeeded_transactions_exists.scalar()
        if succeeded_transactions_exists:
            return ""

        transaction = Transaction(
            order_id=order_id,
            type=TransactionType.PAYMENT,
            status=TransactionStatus.PENDING,
            amount=order.total_amount,
            currency=order.currency,
        )
        self._db.add(transaction)
        await self._db.commit()

        key = f"{cfg.redis.prefix}{order_id}"
        idempotency_key = await self._repo.read(CacheReadDto(name=key))

        link, external_id = await self._payment_service.create_payment_link(
            base_url=base_url,
            amount=order.total_amount,
            currency=order.currency.value.upper(),
            description=f"Payment for order № {order_id}",
            transaction_id=transaction.id,
            idempotency_key=idempotency_key,
        )
        await self._repo.create(CacheSetDto(name=order_id, value=link))

        transaction.external_id = external_id
        self._db.add(transaction)
        await self._db.commit()

        return cast(str, link)

    # TODO: add transaction rollback
    async def refund_order(self, order_id: str) -> bool:
        order = await self.get_order(order_id)
        if order is None:
            return False

        transaction_to_return = await self._db.execute(
            select(Transaction).where(
                and_(Transaction.status == TransactionStatus.SUCCEEDED, Transaction.order_id == order.id)
            )
        )

        transaction_to_return = transaction_to_return.scalar_one_or_none()
        logger.info(transaction_to_return.amount)

        if not transaction_to_return:
            return False

        refund_tr = Transaction(
            status=TransactionStatus.PENDING,
            type=TransactionType.REFUND,
            amount=transaction_to_return.amount,
            currency=transaction_to_return.currency,
            order_id=transaction_to_return.order_id,
        )

        self._db.add(refund_tr)
        await self._db.commit()
        external_id = await self._payment_service.create_refund_object(
            transaction_to_return.external_id, transaction_to_return.amount, transaction_to_return.currency
        )
        refund_tr.external_id = external_id
        self._db.add(refund_tr)
        await self._db.commit()

        return True
