from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class TimeStampMixin:
    """
    A mixin class to add timestamp fields in a model.
    """

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now(), onupdate=datetime.utcnow, nullable=False
    )
