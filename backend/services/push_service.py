from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.push_log import PushLog


class PushService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def push_report(
        self, user_id: uuid.UUID, report_id: uuid.UUID, channels: list[str]
    ) -> list[PushLog]:
        logs: list[PushLog] = []
        for channel in channels:
            log = PushLog(
                user_id=user_id,
                report_id=report_id,
                channel=channel,
                status="pending",
            )
            self.db.add(log)
            logs.append(log)

        await self.db.flush()

        for log in logs:
            try:
                await self._send(log)
                log.status = "sent"
                log.sent_at = datetime.now(timezone.utc)
            except Exception as e:
                log.status = "failed"
                log.error_msg = str(e)
                log.retry_count += 1

        await self.db.flush()
        return logs

    async def get_push_status(self, user_id: uuid.UUID) -> list[PushLog]:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(PushLog).where(
                and_(
                    PushLog.user_id == user_id,
                    PushLog.sent_at >= today_start,
                )
            ).order_by(PushLog.sent_at.desc())
        )
        return list(result.scalars().all())

    async def _send(self, log: PushLog) -> None:
        """Dispatch to channel-specific sender. MVP stubs."""
        if log.channel == "web":
            pass
        elif log.channel == "email":
            pass
        elif log.channel == "telegram":
            pass
        elif log.channel == "wechat":
            pass
        else:
            raise ValueError(f"未知推送渠道: {log.channel}")
