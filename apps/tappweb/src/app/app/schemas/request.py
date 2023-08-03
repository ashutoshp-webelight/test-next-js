from core.utils import CamelCaseModel


class UserCreateRequest(CamelCaseModel):
    name: str
