from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class WebhookUrl(Base):
    """
    A Webhook-url model class defining Columns and table name of the stored webhook-url values.
    """

    __tablename__ = "webhook_url"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column()

    @classmethod
    def create(cls, url: str) -> "WebhookUrl":
        """
        Create webhook url

        :param url: url

        :return: Created webhook url model instance.
        """
        return cls(id=uuid4(), url=url)
