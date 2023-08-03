from typing import Self
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base
from core.utils.mixins import TimeStampMixin


class UserModel(Base, TimeStampMixin):

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    @classmethod
    def create(cls, name: str) -> Self:
        return cls(id=uuid4(), name=name)
