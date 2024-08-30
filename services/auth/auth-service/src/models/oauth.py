from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.helpers.providers import SocialNetworksNames
from src.models.base import Base, pkid, str_50, str_256


class SocialNetworks(Base):
    def __repr__(self):
        return f"<SocialAccount {self.social_networks_name}:{self.user_id}>"

    __tablename__ = "social_networks"

    id: Mapped[pkid]
    user_id: Mapped[pkid] = mapped_column(ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False)
    social_network_id: Mapped[str_50] = mapped_column(nullable=False)
    social_network_email: Mapped[str_256] = mapped_column(nullable=False)
    social_networks_name: Mapped[SocialNetworksNames] = mapped_column(nullable=False)
