from pydantic import BaseModel
from pydantic.utils import to_lower_camel  # noqa

import constants


class CamelCaseModel(BaseModel):
    """
    A schemas for Camelcase.
    """

    class Config:
        alias_generator = to_lower_camel
        allow_population_by_field_name = True


class SuccessResponse(CamelCaseModel):
    """
    A schemas model success response.
    """

    message = constants.SUCCESS
