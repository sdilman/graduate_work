from typing import Annotated

import uuid

from sqlalchemy.orm import DeclarativeBase, mapped_column

str_50 = Annotated[str, 50]
str_256 = Annotated[str, 256]
pkid = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]


class Base(DeclarativeBase):
    """
    Base ORM class for all models
    """
