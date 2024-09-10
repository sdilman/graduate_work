from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from models.pg import Order, OrderProduct, Product, Transaction
from schemas.entity import OrderSchema, ProductSchema, TransactionSchema


class EntityService:
    async def create_product(self, db: AsyncSession, product_schema: ProductSchema) -> ProductSchema:
        new_product = Product(**product_schema.dict())
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product.id

    async def create_order(self, db: AsyncSession, order_schema: OrderSchema) -> OrderSchema:
        new_order = Order(
            user_id=order_schema.user_id,
            status=order_schema.status,
            currency=order_schema.currency,
            created_at=order_schema.created_at,
            total_amount=order_schema.total_amount,
        )
        db.add(new_order)
        await db.commit()

        op_list = []
        for product_id in order_schema.products_id:
            new_order_product = OrderProduct(
                order_id=new_order.id, product_id=product_id, created_at=order_schema.created_at
            )
            db.add(new_order_product)
            op_list.append(new_order_product)
        await db.commit()

        return new_order.id

    async def get_order(self, db: AsyncSession, order_id: str) -> OrderSchema:
        result = await db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def create_transaction(self, db: AsyncSession, transaction_schema: TransactionSchema) -> str:
        import logging

        logging.warning(transaction_schema.model_dump(exclude_unset=True))
        new_transaction = Transaction(**transaction_schema.model_dump(exclude_unset=True))
        db.add(new_transaction)
        await db.commit()
        return str(new_transaction.id)


@lru_cache
def get_entity_service() -> EntityService:
    return EntityService()
