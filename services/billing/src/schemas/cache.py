from pydantic import BaseModel

from core.settings import settings


class ExpireTime(BaseModel):
    time: int = settings.redis.record_expiration_time


class CacheReadDto(BaseModel):
    name: str


class CacheSetDto(CacheReadDto, ExpireTime):
    value: str


class CacheUpdateDto(CacheReadDto, ExpireTime): ...


class CacheFlushDto(CacheUpdateDto):
    time: int = 0
