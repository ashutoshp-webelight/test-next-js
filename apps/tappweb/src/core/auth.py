from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jwt import DecodeError, ExpiredSignatureError, decode, encode

import constants
from config import settings
from core.exceptions import InvalidJWTTokenException
from core.types import RoleType


class JWToken(HTTPBearer):
    """
    A class inheriting from :class:`HTTPBearer` to inherit the methods necessary for
    token extraction from the request.
    """

    def __init__(self, role: Optional[RoleType] = None, *args: Any, **kwargs: Any) -> None:
        super(JWToken, self).__init__(*args, **kwargs)
        self.role = role

    def encode(self, payload: dict, expire_period: int) -> str:
        """
        Creates a JWT access token.

        :param payload: Claims to be included in the _token.
        :param expire_period: Expiry period of the _token.
        :return: JWT Token
        """
        _token = encode(
            payload={**payload, "role": self.role, "exp": datetime.utcnow() + timedelta(seconds=expire_period)},
            key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return _token

    def decode(self, _token: str) -> Dict[str, Any]:
        """
        Decode a JWT access token.

        :param _token: A JWT token.
        :return: Claims included in the token.
        """
        try:
            payload = decode(
                jwt=_token,
                key=settings.JWT_SECRET_KEY,
                algorithms=settings.JWT_ALGORITHM,
                option={"verify_signature": True, "verify_exp": True},
            )
            if self.role is not None:
                if payload.get("role") != self.role:
                    raise InvalidJWTTokenException(constants.UNAUTHORIZED)
            return payload
        except DecodeError:
            raise InvalidJWTTokenException(constants.INVALID_TOKEN)
        except ExpiredSignatureError:
            raise InvalidJWTTokenException(constants.EXPIRED_TOKEN)

    async def __call__(self, request: Request) -> Dict[str, Any]:
        """
        A magic method intercepts the request and extracts token from it.
        allowing us to access the token in the request context.

        :param request: FastAPI Request.
        :return: Claims included in the token.
        """
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            raise InvalidJWTTokenException(constants.UNAUTHORIZED)
        if scheme.lower() != "bearer":
            raise InvalidJWTTokenException(constants.INVALID_TOKEN)
        return self.decode(credentials)


token = JWToken(role=RoleType.USER)
admin_token = JWToken(role=RoleType.ADMIN)
