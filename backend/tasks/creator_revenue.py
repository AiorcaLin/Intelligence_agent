from __future__ import annotations

import asyncio
import logging
import uuid

from backend.tasks import celery_app

logger = logging.getLogger(__name__)


async def _distribute(template_id: uuid.UUID, credits_consumed: float) -> dict:
    from backend.database import async_session_factory
    from backend.services.credits_service import CreditsService
    from backend.services.template_service import TemplateService

    async with async_session_factory() as db:
        tmpl_svc = TemplateService(db)
        credits_svc = CreditsService(db)

        lineage = await tmpl_svc.get_lineage(template_id)
        distribution = TemplateService.calculate_revenue_split(credits_consumed, lineage)

        for recipient_id, amount in distribution.items():
            if recipient_id in ("platform", "operations") or amount <= 0:
                continue

            try:
                uid = uuid.UUID(recipient_id)
            except ValueError:
                continue

            await credits_svc.add_credits(
                user_id=uid,
                amount=amount,
                record_type="creator_revenue",
                description=f"模板收益分成 (模板链贡献)",
                related_template_id=template_id,
            )

        await db.commit()

    logger.info(
        "Revenue distributed for template %s: %s",
        template_id,
        distribution,
    )
    return distribution


@celery_app.task(name="backend.tasks.creator_revenue.distribute_revenue")
def distribute_revenue(template_id: str, credits_consumed: float) -> dict:
    """Distribute creator revenue for a template usage."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(
        _distribute(uuid.UUID(template_id), credits_consumed)
    )
    return {k: float(v) for k, v in result.items()}
