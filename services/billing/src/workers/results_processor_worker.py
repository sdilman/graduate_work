import asyncio

import pydantic

from aiokafka import AIOKafkaConsumer

from core.constraints.yookassa import YookassaObjectTypes
from core.logger import get_logger
from core.settings import settings
from db.postgres import get_pg_session
from schemas.yookassa import YookassaEventNotification, YookassaPaymentObject
from services.payment_processing_service import PaymentResultsProcessingService

logger = get_logger(__name__)


async def run() -> None:
    kafka_client = AIOKafkaConsumer(
        settings.kafka.topic_name,
        bootstrap_servers=settings.kafka.bootstrap_servers,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id=settings.kafka.group_id,
    )
    await kafka_client.start()

    try:
        async for message in kafka_client:
            async for session in get_pg_session():
                payment_results_service = PaymentResultsProcessingService(session)

                try:
                    # TODO: why error catched by outside try ?
                    parsed_message = YookassaEventNotification.parse_raw(message.value)
                except pydantic.ValidationError:
                    logger.info("Can't parse message. Skip it")
                    continue

                object_type, status = parsed_message.event.split(".")

                if object_type == YookassaObjectTypes.PAYMENT:
                    object_ = YookassaPaymentObject.parse_obj(parsed_message.object)
                    await payment_results_service.process_payment_result(object_)
                elif object_type == YookassaObjectTypes.REFUND:
                    # TODO: add handler in future
                    continue
                else:
                    continue

                await session.commit()
                await kafka_client.commit()
    except BaseException as e:
        logger.exception("Something went wrong")
    finally:
        await kafka_client.stop()


if __name__ == "__main__":
    asyncio.run(run())
