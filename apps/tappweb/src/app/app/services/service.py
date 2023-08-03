from typing import Any, Dict

from fastapi import Depends

from app.app.models.user import UserModel
from app.app.repositories.repository import Repository


class Service:
    """
    Service with methods to set and get values.
    """

    def __init__(self, repo: Repository = Depends(Repository)) -> None:
        """
        Call method to inject Service as a dependency.
        This method also calls a Repo instance which is injected here.

        :param repo: Repository instance.
        :return: Service Generator.
        """
        self.repo = repo

    async def create_user(self, name: str) -> Dict[str, Any]:
        """
        Create a user.

        :param name: Name of the user.

        :return: Created user model instance.
        """
        return await self.repo.save(UserModel.create(name=name))
