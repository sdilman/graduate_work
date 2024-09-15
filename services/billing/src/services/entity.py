from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from uuid import UUID  # noqa: TCH003

from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from models.pg import Product, Transaction, UserProduct
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

    async def create_user_product(self, db: AsyncSession, user_id: UUID, product_id: UUID) -> str:
        new_user_product = UserProduct(
            product_id=product_id, user_id=user_id, active_from=datetime.now(), renewal_enabled=True
        )
        db.add(new_user_product)
        await db.commit()
        await db.refresh(new_user_product)
        return str(new_user_product.id)


@lru_cache
def get_entity_service() -> EntityService:
    return EntityService()
