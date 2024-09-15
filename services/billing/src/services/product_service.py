from __future__ import annotations

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, update

from core.logger import get_logger
from models.pg import UserProduct

logger = get_logger(__name__)


class ProductService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def disable_renewal(self, user_id: str, product_id: str) -> None:
        q_user_product_select = select(UserProduct).where(
            and_(UserProduct.product_id == product_id, UserProduct.user_id == user_id)
        )
        q_user_product_update = (
            update(UserProduct)
            .values(renewal_enabled=False)
            .where(and_(UserProduct.product_id == product_id, UserProduct.user_id == user_id))
        )
        statement_res = await self._db.execute(q_user_product_select)
        statement_res.scalar_one()
        await self._db.execute(q_user_product_update)
        await self._db.commit()
