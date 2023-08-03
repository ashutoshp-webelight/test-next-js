from typing import Optional

import constants
from core.exceptions import BadRequestError


class RequestFailedException(BadRequestError):
    def __init__(self, message: Optional[str] = constants.REQUEST_FAILED) -> None:
        super().__init__(message)


class UserNotFound(BadRequestError):
    def __init__(self, message: Optional[str] = constants.SOMETHING_WENT_WRONG) -> None:
        super().__init__(message)
