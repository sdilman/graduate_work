import asyncio

from core.logger import get_logger
from db.postgres import get_pg_session
from services.order_service import OrderService
from services.product_auto_renewal_service import ProductRenewalService

logger = get_logger(__name__)


async def run() -> None:
    try:
        async for session in get_pg_session():
            order_service = OrderService(session)
            product_renewal_service = ProductRenewalService(session, order_service)
            while True:
                await product_renewal_service.run_renewal()
                # TODO: use settings for sleep time
                await asyncio.sleep(3)
    except Exception as e:
        logger.exception("Exception:", exc_info=e)


if __name__ == "__main__":
    asyncio.run(run())
