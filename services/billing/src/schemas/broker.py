from pydantic import BaseModel, Field


class MessageIn(BaseModel):
    topic: str = Field(..., description="Name of the Kafka topic")
    key: bytes = Field(..., description="Key of the message with idempotency key")
    value: bytes = Field(..., description="Value of the message")
