from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app.models import WebhookUrl
from core.db import db_session
from core.utils.schema import SuccessResponse


router = APIRouter()


@router.post("/set-webhook-url")
async def set_webhook_url(url: str = Query(), session: AsyncSession = Depends(db_session)) -> SuccessResponse:
    """
    Set webhook url.
    :param url: Url for webhook.
    :param session: An asynchronous database connection.
    :return: Json response.
    """
    query = await session.scalars(select(WebhookUrl))
    _url = query.first()
    if _url:
        _url.url = url
    else:
        session.add(WebhookUrl.create(url))
    return SuccessResponse()
