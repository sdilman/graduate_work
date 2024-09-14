from pydantic import BaseModel, Field


class MessageIn(BaseModel):
    topic: str = Field(..., description="Name of the Kafka topic")
    key: str = Field(..., description="Key of the message with idempotency key")
    value: str = Field(..., description="Value of the message")
