"""add superuser

Revision ID: 299fa7859f83
Revises: 9a394f38538e
Create Date: 2024-08-15 12:56:00.076066

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm
from src.core.api_settings import settings
from src.models import User

# revision identifiers, used by Alembic.
revision: str = "299fa7859f83"
down_revision: Union[str, None] = "9a394f38538e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    su = User(**settings.su.model_dump())
    session.add(su)
    session.commit()
    session.refresh(su)
    session.close()


def downgrade() -> None:
    op.execute("TRUNCATE TABLE public.users CASCADE")
