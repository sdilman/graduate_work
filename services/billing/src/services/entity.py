from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from models.pg import Product, Transaction
from schemas.entity import ProductSchema, TransactionSchema

logger = get_logger(__name__)


class EntityService:
    async def create_product(self, db: AsyncSession, product_schema: ProductSchema) -> ProductSchema:
        new_product = Product(**product_schema.dict())
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product.id

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
