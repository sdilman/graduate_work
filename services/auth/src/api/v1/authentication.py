from typing import Annotated, Dict

import logging

from urllib.parse import urljoin

import httpx

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import settings
from db.postgres import get_pg_session
from helpers.providers import SocialNetworksNames
from models.db_entity import User
from schemas.cookie import AccessTokenCookie, RefreshTokenCookie
from schemas.model import AccessTokenData, SNUserRegisteredResp, SNUserRegistrationReq, UserLoginReq
from services.authentication import AuthenticationService, get_authentication_service
from services.base import BaseService, get_base_service
from services.jwt_token import JWTService, get_jwt_service
from services.registration import RegistrationService, UserRegisteredResp, UserRegistrationReq, get_registration_service

router = APIRouter()


async def check_access_token(
    input_token: str = Cookie(alias=AccessTokenCookie.name), jwt_service: JWTService = Depends(get_jwt_service)
) -> dict:
    """
    Function to check access jwt token from the Cookie.
    """
    if not input_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised")

    result = await jwt_service.verify_token(token=input_token)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised")

    return result


async def get_user(
    db: Annotated[AsyncSession, Depends(get_pg_session)],
    base_service: Annotated[BaseService, Depends(get_base_service)],
    access_token_dict: Annotated[Dict, Depends(check_access_token)],
) -> User:
    """
    Checks if user_id, received in JWT token exists in DB.
    Depends on func 'check_access_token'.
    Returns User DB model.
    """

    access_token = AccessTokenData(**access_token_dict)

    db_user = await base_service.get_user_by_uuid(db, user_id=access_token.user_id)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_user


async def get_current_active_user(user: Annotated[User, Depends(get_user)]) -> User:
    """
    Checks if received from DB user is active.
    Depends on func 'get_user'.
    """
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


async def get_superuser(user: Annotated[User, Depends(get_current_active_user)]) -> User:
    """
    Checks if received from DB user is superuser.
    Depends on func 'get_current_active_user'.
    """
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


async def check_refresh_token(
    input_token: str = Cookie(alias=RefreshTokenCookie.name), jwt_service: JWTService = Depends(get_jwt_service)
) -> dict:
    """
    Function to check access jwt token from the Cookie
    """
    if not input_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised")

    result = await jwt_service.verify_token(token=input_token)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised")

    return result


@router.post("/user", status_code=status.HTTP_200_OK, summary="Get user ID", description="Get user ID")
async def get_user_id(
    payload: dict[str, str],
    jwt_service: JWTService = Depends(get_jwt_service),
    db: AsyncSession = Depends(get_pg_session),
    base_service: BaseService = Depends(get_base_service),
):
    input_token_value = payload["input_token"]
    access_token_dict = await check_access_token(input_token=input_token_value, jwt_service=jwt_service)
    user = await get_user(db=db, base_service=base_service, access_token_dict=access_token_dict)
    return {"sso_id": user.id}


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login by username and password",
    description="Login by username and password",
)
async def login_user_for_access_token_cookie(
    request: Request,
    response: Response,
    form_data: Annotated[UserLoginReq, Body()],
    db: AsyncSession = Depends(get_pg_session),
    base_service: BaseService = Depends(get_base_service),
    authentication_service: AuthenticationService = Depends(get_authentication_service),
):
    """
    User login endpoint
    """
    try:
        user = await authentication_service.authenticate_user(db, form_data.email, form_data.password)
    except Exception as excp:
        logging.exception("Unable to get user %s. The following error occured: %s", form_data.email, excp)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal server error")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is inactive")

    try:
        user_roles_list = await base_service.get_user_roles(db, user.id)
        user_roles = [jsonable_encoder(role) for role in user_roles_list]

    except Exception as excp:
        logging.exception("Unable to get roles for user %s. The following error occured: %s", form_data.email, excp)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal server error")

    access_token, refresh_token = await authentication_service.get_tokens(user_id=str(user.id), user_roles=user_roles)

    response.set_cookie(key=AccessTokenCookie.name, value=access_token, httponly=True)
    response.set_cookie(key=RefreshTokenCookie.name, value=refresh_token, httponly=True)

    try:
        await authentication_service.save_login_history(
            db,
            user_id=str(user.id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            location=request.headers.get("location"),
        )
    except Exception as excp:
        logging.exception("DB. Unable to save user login history: %s", excp)

    response.headers["Authorization"] = f"Bearer {access_token}"


@router.get(
    "/authentication_callback_yandex",
    status_code=status.HTTP_200_OK,
    summary="Callback handle for Yandex authentication",
    description="Callback handle for Yandex authentication",
)
async def authentication_callback_yandex(
    request: Request,
    response: Response,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_pg_session),
    authentication_service: AuthenticationService = Depends(get_authentication_service),
    get_registration_service: RegistrationService = Depends(get_registration_service),
):
    authorization_details = await authentication_service.get_external_authorization_details(
        sn=SocialNetworksNames.yandex
    )
    external_auth_service_url = authorization_details.external_auth_service_url
    data = {
        "client_id": authorization_details.client_id,
        "grant_type": authorization_details.grant_type,
        "client_secret": authorization_details.client_secret,
        "code": code,
    }
    headers = {"Content-type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        auth_response = await client.post(external_auth_service_url, data=data, headers=headers)
        auth_response_json = auth_response.json()
        external_access_token = auth_response_json["access_token"]
        external_refresh_token = auth_response_json["refresh_token"]

    external_get_user_info_service_url = authorization_details.external_get_user_info_service_url
    headers = {"Authorization": "OAuth " + external_access_token}

    async with httpx.AsyncClient() as client:
        auth_response = await client.get(external_get_user_info_service_url, headers=headers)
        auth_response_json = auth_response.json()
        external_user_id = auth_response_json["id"]
        external_user_email = auth_response_json["default_email"]

    internal_user = await authentication_service.get_user(db, external_user_email)
    if not internal_user:
        user_info = UserRegistrationReq(email=external_user_email, password="", request_password_change=True)
        user_response = await get_registration_service.add_user(db, user_info)
        user_id = user_response.user_id
    else:
        user_id = internal_user.id

    sn_user = await authentication_service.get_extretrnal_user(db, external_user_id, SocialNetworksNames.yandex)
    if not sn_user:
        sn_user_info = SNUserRegistrationReq(
            internal_user_id=user_id,
            social_network_id=external_user_id,
            social_network_email=external_user_email,
            social_network_name=SocialNetworksNames.yandex,
        )
        sn_user_response = await get_registration_service.add_social_network_user(db, sn_user_info)

    access_token, refresh_token = await authentication_service.get_tokens(user_id=str(user_id), user_roles=[])
    response.set_cookie(key=AccessTokenCookie.name, value=access_token, httponly=True)
    response.set_cookie(key=RefreshTokenCookie.name, value=refresh_token, httponly=True)

    try:
        await authentication_service.save_login_history(
            db,
            user_id=str(user_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            location=request.headers.get("location"),
        )
    except Exception as excp:
        logging.exception("DB. Unable to save user login history: %s", excp)

    response.headers["Authorization"] = f"Bearer {access_token}"
    return user_id


@router.get(
    "/login_external",
    status_code=status.HTTP_200_OK,
    summary="Login with external authentication",
    description="Login with external authentication",
)
async def get_external_login_link(
    request: Request,
    response: Response,
    social_network: SocialNetworksNames,
    db: AsyncSession = Depends(get_pg_session),
    authentication_service: AuthenticationService = Depends(get_authentication_service),
):
    """
    External user login endpoint
    """

    authentication_details = await authentication_service.get_external_authentication_details(social_network)

    params = {
        "response_type": authentication_details.response_type,
        "client_id": authentication_details.client_id,
        "redirect_uri": urljoin(str(request.base_url), authentication_details.redirect_uri),
        "scope": authentication_details.scope,
        "state": authentication_details.state,
    }

    async with httpx.AsyncClient() as client:
        auth_response = await client.get(authentication_details.external_auth_service_url, params=params)
        return (auth_response.request.method, str(auth_response.request.url))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout", description="Logout")
async def logout_user(
    response: Response,
    access_token: dict = Depends(check_access_token),
    token_input_dict: dict = Depends(check_refresh_token),
    authentication_service: AuthenticationService = Depends(get_authentication_service),
):
    """
    User logout endpoint
    """

    try:
        await authentication_service.logout_user(token_input_dict)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal server error")

    response.delete_cookie(key=AccessTokenCookie.name)
    response.delete_cookie(key=RefreshTokenCookie.name)


@router.post(
    "/token-refresh", status_code=status.HTTP_200_OK, summary="Refresh token pair", description="Refresh token pair"
)
async def refresh_user_tokens_cookie_pair(
    response: Response,
    token_input_dict: dict = Depends(check_refresh_token),
    authentication_service: AuthenticationService = Depends(get_authentication_service),
):
    """
    User jwt token pair refresh endpoint
    """

    access_token, refresh_token = await authentication_service.refresh_tokens(token_input_dict)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised")

    response.set_cookie(key=AccessTokenCookie.name, value=access_token, httponly=True)
    response.set_cookie(key=RefreshTokenCookie.name, value=refresh_token, httponly=True)
