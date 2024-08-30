from dataclasses import dataclass


@dataclass(frozen=True)
class UserAuthInfoRequest:
    input_token: str


@dataclass(frozen=True)
class UserAuthInfoResponce:
    sso_id: str


@dataclass(frozen=True)
class UserAuthError:
    message: str
