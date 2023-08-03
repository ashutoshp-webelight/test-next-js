import asyncio
from typing import Any, Dict

from sqlalchemy import select

import constants
from app.app.models.webhook import WebhookUrl
from core.db import async_session
from core.utils import HTTPClient, logger


async def send_webhook(headers: Dict[Any, Any] = None, payload: str = None) -> bool:
    async with async_session() as session:
        async with session.begin():
            webhook_url = await session.execute(select(WebhookUrl).first())
            if webhook_url:
                client = HTTPClient(base_url=webhook_url.base_url)
                await client.post(headers=headers, json=payload)
                return True
    return False


def webhook_handler(payload: str = None) -> None:
    task = asyncio.create_task(send_webhook(payload=payload))
    task.add_done_callback(
        lambda _: logger.exception(constants.WEBHOOK_FAILED)
        if _.exception() or _.result() is False
        else logger.info(constants.WEBHOOK_SUCCESSFUL + payload)
    )
    return None
