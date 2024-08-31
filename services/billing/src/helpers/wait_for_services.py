import asyncio

from logging import getLogger

import backoff

from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings

logger = getLogger(__name__)


@backoff.on_exception(backoff.expo, Exception, max_time=300, max_tries=10)
async def wait_for_postgres() -> None:
    logger.info("Pinging Postgres...")
    dsn = settings.pg.dsn
    engine = create_async_engine(dsn, echo=True, future=True)

    async with engine.begin() as conn:
        await conn.get_raw_connection()
        logger.info("Postgres is up!")


async def main() -> None:
    await wait_for_postgres()


if __name__ == "__main__":
    logger.info("Waiting for Postgres to start...")
    asyncio.run(main())
