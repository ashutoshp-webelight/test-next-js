from typing import Optional

from fastapi import status

import constants


class CustomException(Exception):
    """
    A custom exception class to raise necessary exceptions in the app.
    """

    status_code = status.HTTP_502_BAD_GATEWAY

    def __init__(self, message: Optional[str] = constants.SOMETHING_WENT_WRONG) -> None:
        if message:
            self.message = message


class BadRequestError(CustomException):
    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedError(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(CustomException):
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(CustomException):
    status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsError(CustomException):
    status_code = status.HTTP_409_CONFLICT


class UnprocessableEntityError(CustomException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InvalidJWTTokenException(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidSQLQueryException(CustomException):
    pass
