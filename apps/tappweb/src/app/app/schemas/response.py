from uuid import UUID

from core.utils import CamelCaseModel


class UserCreateRequest(CamelCaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True
