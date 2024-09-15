from __future__ import annotations

from typing import cast

from functools import lru_cache

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from models.pg import Order, OrderProduct, Product
from schemas.entity import OrderSchema

logger = get_logger(__name__)


class OrderServiceError(Exception):
    pass


class OrderService:
    def __init__(self, db: AsyncSession):
        self._db = db

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
    async def create_order(self, order_schema: OrderSchema) -> OrderSchema:
        non_existing_products_ids = await self._get_nonexists_products(order_schema)

        if non_existing_products_ids:
            raise OrderServiceError("Products does not exist: %s", non_existing_products_ids)

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

        return new_order.id

    async def get_order(self, order_id: str) -> OrderSchema:
        result = await self._db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()


@lru_cache
def get_order_service(db: AsyncSession) -> OrderService:
    return OrderService(db)
