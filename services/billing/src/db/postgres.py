from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.logger import get_logger

logger = get_logger(__name__)


async def get_pg_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a session for database operations."""

    from core.settings import settings

    engine = create_async_engine(url=settings.pg.dsn, echo=settings.debug, future=True)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


async def get_pg_session_for_sequence() -> AsyncGenerator[AsyncSession, None]:
    """Get a session for sequence of database operations."""
    from core.settings import settings

    engine = create_async_engine(url=settings.pg.dsn, echo=settings.debug, future=True)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(msg="Database error", exc_info=e)
                raise
