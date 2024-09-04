import uuid

from sqlalchemy import UUID, Column


class UUIDMixin:
    """
    Adds UUID field to the model
    """

    __abstract__ = True
    __slots__ = ()

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
