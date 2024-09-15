from __future__ import annotations

from datetime import datetime
from uuid import UUID  # noqa: TCH003

from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import get_logger
from models.pg import Product, Transaction, UserProduct
from schemas.entity import ProductSchema, TransactionSchema

logger = get_logger(__name__)


class EntityService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_product(self, product_schema: ProductSchema) -> ProductSchema:
        new_product = Product(**product_schema.model_dump())
        self._db.add(new_product)
        await self._db.commit()
        await self._db.refresh(new_product)
        return new_product.id

    async def create_transaction(self, transaction_schema: TransactionSchema) -> str:
        import logging

        logging.warning(transaction_schema.model_dump(exclude_unset=True))
        new_transaction = Transaction(**transaction_schema.model_dump(exclude_unset=True))
        self._db.add(new_transaction)
        await self._db.commit()
        return str(new_transaction.id)

    async def create_user_product(self, user_id: UUID, product_id: UUID) -> str:
        new_user_product = UserProduct(
            product_id=product_id, user_id=user_id, active_from=datetime.now(), renewal_enabled=True
        )
        self._db.add(new_user_product)
        await self._db.commit()
        await self._db.refresh(new_user_product)
        return str(new_user_product.id)
