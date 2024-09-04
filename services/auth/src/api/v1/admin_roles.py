from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.authentication import get_superuser
from db.postgres import get_pg_session
from models.db_entity import User
from schemas.model import (
    PermissionCreateReq,
    PermissionInfoResp,
    PermissionsListResp,
    RoleCreateReq,
    RoleInfoResp,
    RolesListResp,
)
from services.admin_roles import AdminRolesService, get_admin_roles_service

router = APIRouter()


@router.get("/admin/permissions", response_model=PermissionsListResp, status_code=status.HTTP_200_OK)
async def get_permissions(
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> PermissionsListResp:
    return await admin_roles_service.get_all_permissions(db=db)


@router.post("/admin/permissions", response_model=PermissionInfoResp, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreateReq,
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> PermissionInfoResp:
    return await admin_roles_service.create_permission(db=db, permission_data=permission_data)


@router.delete("/admin/permissions/{permission_name}")
async def delete_permission(
    permission_name: str,
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> None:
    return await admin_roles_service.delete_permission(db=db, permission_name=permission_name)


@router.get("/admin/roles", response_model=RolesListResp, status_code=status.HTTP_200_OK)
async def get_roles(
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> RolesListResp:
    return await admin_roles_service.get_all_roles(db=db)


@router.post("/admin/roles", response_model=RoleInfoResp, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreateReq,
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> RoleInfoResp:
    return await admin_roles_service.create_role(db=db, role_data=role_data)


@router.get("/admin/roles/{role_name}", response_model=PermissionsListResp, status_code=status.HTTP_200_OK)
async def get_role_permissions(
    role_name: str,
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> PermissionsListResp:
    return await admin_roles_service.get_permissions_by_role(db=db, role_name=role_name)


@router.put("/admin/roles/{role_name}")
async def update_role_permissions(
    role_name: str,
    permissions: List[str],
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> RoleInfoResp:
    return await admin_roles_service.update_role_permissions(db=db, role_name=role_name, permissions=permissions)


@router.delete("/admin/roles/{role_name}")
async def delete_permission(
    role_name: str,
    db: AsyncSession = Depends(get_pg_session),
    admin_roles_service: AdminRolesService = Depends(get_admin_roles_service),
    su_user: User = Depends(get_superuser),
) -> None:
    return await admin_roles_service.delete_role(db=db, role_name=role_name)
