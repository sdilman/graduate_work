from functools import lru_cache

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from src.db.redis_db import get_redis
from src.models.db_entity import User
from src.models.oauth import SocialNetworks, SocialNetworksNames
from src.schema.model import SNUserRegisteredResp, SNUserRegistrationReq, UserRegisteredResp, UserRegistrationReq

from .helper import AsyncCache


class RegistrationService:
    def __init__(self, cache: AsyncCache):
        self.cache = cache

    async def register_user(self, db: AsyncSession, user_info: UserRegistrationReq) -> UserRegisteredResp:
        user_exists = await self.check_user_exists(db=db, email=user_info.email)
        if user_exists:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Пользователь уже существует")

        result = await self.add_user(db, user_info)
        return result

    async def check_user_exists(self, db: AsyncSession, email: str) -> bool:
        statement = select(User).where(User.email == email)
        statement_result = await db.execute(statement=statement)
        user = statement_result.scalar_one_or_none()
        return user is not None

    async def add_user(self, db: AsyncSession, user_info: UserRegistrationReq) -> UserRegisteredResp:
        user = User(email=user_info.email, hashed_password=user_info.password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserRegisteredResp(result="success", user_id=str(user.id), email=user.email, is_active=user.is_active)

    async def add_social_network_user(
        self, db: AsyncSession, sn_user_info: SNUserRegistrationReq
    ) -> UserRegisteredResp:
        sn_user = SocialNetworks(
            user_id=sn_user_info.internal_user_id,
            social_network_id=sn_user_info.social_network_id,
            social_network_email=sn_user_info.social_network_email,
            social_networks_name=sn_user_info.social_network_name,
        )
        db.add(sn_user)
        await db.commit()
        await db.refresh(sn_user)
        return SNUserRegisteredResp(
            result="success",
            internal_user_id=str(sn_user.user_id),
            social_network_id=sn_user.social_network_id,
            social_network_email=sn_user.social_network_email,
            social_networks_name=sn_user.social_networks_name,
        )


@lru_cache
def get_registration_service(cache: AsyncCache = Depends(get_redis)) -> RegistrationService:
    return RegistrationService(cache=cache)
