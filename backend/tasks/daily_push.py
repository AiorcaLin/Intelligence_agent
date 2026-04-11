from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, select

from backend.database import async_session_factory
from backend.models.subscription import Subscription
from backend.services.push_service import PushService
from backend.tasks import celery_app

logger = logging.getLogger(__name__)


def _get_current_bucket() -> str:
    """Return the current 3-hour time bucket as a zero-padded string."""
    hour = datetime.now(timezone.utc).hour
    bucket = (hour // 3) * 3
    return f"{bucket:02d}"


async def _process_push() -> int:
    """Query subscriptions matching the current time bucket and push reports."""
    bucket = _get_current_bucket()
    pushed = 0

    async with async_session_factory() as db:
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.is_active.is_(True),
                    Subscription.push_time_bucket == bucket,
                )
            )
        )
        subscriptions = result.scalars().all()

        push_svc = PushService(db)

        for sub in subscriptions:
            try:
                from sqlalchemy import select as sel
                from backend.models.report import IntelReport

                today_start = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                report_result = await db.execute(
                    sel(IntelReport).where(
                        and_(
                            IntelReport.subscription_id == sub.id,
                            IntelReport.created_at >= today_start,
                        )
                    ).order_by(IntelReport.created_at.desc()).limit(1)
                )
                report = report_result.scalar_one_or_none()

                if report:
                    channels = sub.formats if sub.formats else ["web"]
                    await push_svc.push_report(sub.user_id, report.id, channels)
                    pushed += 1

            except Exception:
                logger.exception("Failed to push for subscription %s", sub.id)
                continue

        await db.commit()

    return pushed


@celery_app.task(name="backend.tasks.daily_push.run_hourly_push", bind=True, max_retries=3)
def run_hourly_push(self) -> dict:
    """Celery beat task running every hour to push intel reports."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    count = loop.run_until_complete(_process_push())
    logger.info("Hourly push completed: %d subscriptions pushed", count)
    return {"pushed": count, "bucket": _get_current_bucket()}
