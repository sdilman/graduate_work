from __future__ import annotations

from typing import Protocol, TypeVar

In_contra = TypeVar("In_contra", contravariant=True)
Out_co = TypeVar("Out_co", covariant=True)


class RepositoryProtocol(Protocol[In_contra, Out_co]):
    """Base CRUD repository interface"""

    async def create(self, obj: In_contra) -> Out_co: ...
    async def read(self, obj: In_contra) -> Out_co | None: ...
    async def update(self, obj: In_contra) -> Out_co: ...
    async def delete(self, obj: In_contra) -> Out_co: ...


class RedisRepositoryProtocol(RepositoryProtocol[In_contra, Out_co]): ...
