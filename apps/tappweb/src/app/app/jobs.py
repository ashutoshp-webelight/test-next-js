from core.db import async_session
from core.utils import logger


async def job() -> None:
    """
    Check subscription status.
    :return: Subscription state.
    """
    logger.info("Running cron job!")
    async with async_session() as session:
        async with session.begin():
            await session.execute()
    logger.info("Finished cron job!")
    return None
