import asyncio

from core.logger import get_logger
from db import get_redis
from db.postgres import get_pg_session
from db.redis import redis_manager
from repositories import get_redis_service
from services import get_order_service, get_payment_service
from services.product_auto_renewal_service import ProductRenewalService

logger = get_logger(__name__)


async def run() -> None:
    try:
        await redis_manager.initialize()
        async for session in get_pg_session():
            order_service = get_order_service(
                db=session, redis=get_redis_service(get_redis()), payment_service=get_payment_service()
            )
            product_renewal_service = ProductRenewalService(session, order_service)
            while True:
                await product_renewal_service.run_renewal()
                # TODO: use settings for sleep time
                await asyncio.sleep(3)
    except Exception as e:
        logger.exception("Exception:", exc_info=e)


if __name__ == "__main__":
    asyncio.run(run())
