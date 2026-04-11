from __future__ import annotations

import asyncio
import logging

from backend.tasks import celery_app

logger = logging.getLogger(__name__)


async def _reset_credits() -> int:
    """
    Reset daily free credits for all users.
    Free credits are tracked via daily TokenRecord entries, so resetting
    simply means a new day starts — no actual DB mutation needed.
    This task serves as a hook for any additional daily housekeeping.
    """
    from sqlalchemy import select, func

    from backend.database import async_session_factory
    from backend.models.user import User

    async with async_session_factory() as db:
        result = await db.execute(select(func.count(User.id)))
        user_count = result.scalar() or 0

    logger.info("Daily free credits reset for %d users", user_count)
    return user_count


@celery_app.task(name="backend.tasks.daily_free_credits.reset_daily_free_credits")
def reset_daily_free_credits() -> dict:
    """Celery beat task at 00:00 to reset daily free credits."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    count = loop.run_until_complete(_reset_credits())
    return {"users_processed": count}
