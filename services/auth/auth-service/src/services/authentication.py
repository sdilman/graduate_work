import logging
import uuid

from datetime import datetime
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import and_, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from src.core.api_settings import settings
from src.db.redis_db import get_redis
from src.helpers.providers import SocialNetworksNames
from src.models.db_entity import LoginHistory, User
from src.models.oauth import SocialNetworks
from src.schema.model import ExternalAuthenticationDetails, ExternalAuthorizationDetails, RefreshTokenData
from src.services.jwt_token import JWTService, get_jwt_service
from src.services.redis import RedisService, get_redis_service

from .helper import AsyncCache


class AuthenticationService:
    def __init__(self, cache: AsyncCache, redis_service: RedisService, jwt_service: JWTService):
        self.cache = cache
        self.redis_service: RedisService = redis_service
        self.jwt_service: JWTService = jwt_service

    @staticmethod
    async def get_user(db: AsyncSession, email: str) -> [User | None]:
        """
        Searching for a user in the DB
        """
        statement = select(User).where(User.email == email)
        statement_result = await db.execute(statement=statement)
        user = statement_result.scalar_one_or_none()
        if not user:
            return None
        return user

    @staticmethod
    async def get_extretrnal_user(
        db: AsyncSession, social_network_id: str, social_network_name: str
    ) -> [SocialNetworks | None]:
        """
        Searching for a social network user in the DB
        """
        statement = select(SocialNetworks).where(
            and_(
                SocialNetworks.social_network_id == social_network_id,
                SocialNetworks.social_networks_name == social_network_name,
            )
        )
        statement_result = await db.execute(statement=statement)
        sn_user = statement_result.scalar_one_or_none()
        if not sn_user:
            return None
        return sn_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> [User | None]:
        """
        Searching for a user in the DB, check password
        """
        user = await AuthenticationService.get_user(db, email)
        if not user:
            return None
        if not await user.check_password(password):
            return None
        return user

    @staticmethod
    async def save_login_history(
        db: AsyncSession, user_id: str, ip_address: str, location: str, user_agent: str
    ) -> None:
        """
        Save user login info in the DB
        """
        statement = insert(LoginHistory).values(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            location=location,
            user_agent=user_agent,
        )
        await db.execute(statement=statement)
        await db.commit()

    @staticmethod
    async def generate_session_id() -> str:
        return str(uuid.uuid4())

    async def logout_user(self, token_input_dict: dict) -> None:
        logging.debug("Refresh token: %s", token_input_dict)

        token = RefreshTokenData(**token_input_dict)

        await self.redis_service.del_refresh_token(user_id=token.user_id, session_id=token.session_id)

    async def get_tokens(self, user_id: str, user_roles: list | None) -> (str, str):
        session_id = await self.generate_session_id()
        access_token, refresh_token = await self.jwt_service.get_token_pair(
            user_id=user_id, session_id=session_id, roles=user_roles
        )

        try:
            await self.redis_service.save_refresh_token(
                user_id=user_id, session_id=session_id, expire_time_sec=JWTService.refresh_token_expire * 60
            )
        except Exception as excp:
            logging.exception("Unable to save refresh_token %s:%s to Redis. %s", user_id, session_id, excp)

        return access_token, refresh_token

    async def refresh_tokens(self, rt_input_dict: dict) -> (str, str):
        logging.debug('Received "refresh_token": %s', rt_input_dict)

        token = RefreshTokenData(**rt_input_dict)
        redis_key = await self.redis_service.get_redis_key(user_id=token.user_id, session_id=token.session_id)

        redis_refresh_token = await self.redis_service.redis.get(name=redis_key)
        # For now, we use refresh token white list.
        if not redis_refresh_token:
            return None, None

        await self.redis_service.redis.expire(name=redis_key, time=0)

        access_token, refresh_token = await self.get_tokens(user_id=token.user_id, user_roles=token.roles)

        return access_token, refresh_token

    async def get_external_authentication_details(self, sn: SocialNetworksNames):
        if sn == SocialNetworksNames.yandex:
            return ExternalAuthenticationDetails(
                external_auth_service_url=settings.yauth_authorize_url,
                response_type="code",
                client_id=settings.yauth_client_id,
                redirect_uri=settings.yauth_authenticate_redirect_uri,
                scope="login:email",
                state=settings.yauth_authenticate_state,
            )
        if sn == SocialNetworksNames.google or sn == SocialNetworksNames.vk:
            raise NotImplemented
        raise ValueError

    async def get_external_authorization_details(self, sn: SocialNetworksNames):
        if sn == SocialNetworksNames.yandex:
            return ExternalAuthorizationDetails(
                external_auth_service_url=settings.yauth_token_url,
                external_get_user_info_service_url=settings.yauth_user_info_url,
                client_id=settings.yauth_client_id,
                grant_type="authorization_code",
                client_secret=settings.yauth_secret_key,
            )
        if sn == SocialNetworksNames.google or sn == SocialNetworksNames.vk:
            raise NotImplemented
        raise ValueError


@lru_cache
def get_authentication_service(
    cache: AsyncCache = Depends(get_redis),
    redis_service: RedisService = Depends(get_redis_service),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> AuthenticationService:
    return AuthenticationService(cache, redis_service, jwt_service)
