from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.feedback import ReportItemFeedback
from backend.models.report import IntelReport
from backend.models.subscription import Subscription
from backend.services.credits_service import CreditsService
from backend.services.history_service import HistoryService


class IntelService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_today_reports(self, user_id: uuid.UUID) -> list[IntelReport]:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(IntelReport)
            .where(
                and_(
                    IntelReport.user_id == user_id,
                    IntelReport.created_at >= today_start,
                )
            )
            .order_by(IntelReport.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_report_detail(
        self, report_id: uuid.UUID, user_id: uuid.UUID
    ) -> IntelReport | None:
        result = await self.db.execute(
            select(IntelReport).where(
                and_(IntelReport.id == report_id, IntelReport.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        domain: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[IntelReport], int]:
        query = select(IntelReport).where(IntelReport.user_id == user_id)
        count_query = select(func.count(IntelReport.id)).where(IntelReport.user_id == user_id)

        if domain:
            query = query.where(IntelReport.domain == domain)
            count_query = count_query.where(IntelReport.domain == domain)
        if date_from:
            query = query.where(IntelReport.created_at >= datetime.combine(date_from, datetime.min.time()))
            count_query = count_query.where(
                IntelReport.created_at >= datetime.combine(date_from, datetime.min.time())
            )
        if date_to:
            query = query.where(IntelReport.created_at <= datetime.combine(date_to, datetime.max.time()))
            count_query = count_query.where(
                IntelReport.created_at <= datetime.combine(date_to, datetime.max.time())
            )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        result = await self.db.execute(
            query.order_by(IntelReport.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    async def get_report_history(
        self, report_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[dict]:
        report = await self.get_report_detail(report_id, user_id)
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")

        if not report.embedding_id:
            return []

        history_svc = HistoryService()
        try:
            results = await history_svc.get_related_history(
                embedding_id=report.embedding_id,
                user_id=user_id,
                domain=report.domain,
            )
            return results
        except Exception:
            return []

    async def regenerate_report(
        self, report_id: uuid.UUID, user_id: uuid.UUID, feedback_text: str | None
    ) -> IntelReport:
        original = await self.get_report_detail(report_id, user_id)
        if not original:
            raise HTTPException(status_code=404, detail="报告不存在")

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        regen_count = await self.db.execute(
            select(func.count(IntelReport.id)).where(
                and_(
                    IntelReport.user_id == user_id,
                    IntelReport.is_regenerated.is_(True),
                    IntelReport.created_at >= today_start,
                )
            )
        )
        if (regen_count.scalar() or 0) >= 3:
            raise HTTPException(status_code=429, detail="今日重新生成次数已达上限")

        credits_svc = CreditsService(self.db)
        estimated_cost = 10.0
        balance = await credits_svc.get_balance(user_id)
        if balance.total_balance + balance.free_credits_remaining < estimated_cost:
            raise HTTPException(status_code=402, detail="积分不足")

        new_report = IntelReport(
            subscription_id=original.subscription_id,
            user_id=user_id,
            template_id=original.template_id,
            domain=original.domain,
            title=f"{original.title} (重新生成)",
            items=original.items,
            action_items=original.action_items,
            density_level=original.density_level,
            formats_generated=original.formats_generated,
            sources=original.sources,
            is_regenerated=True,
            original_report_id=original.id,
        )
        self.db.add(new_report)
        await self.db.flush()
        await self.db.refresh(new_report)

        await credits_svc.consume_credits(
            user_id=user_id,
            amount=estimated_cost,
            cost_breakdown={"type": "regenerate", "original_report_id": str(original.id)},
            related_report_id=new_report.id,
        )

        return new_report

    async def toggle_feedback(
        self, report_id: uuid.UUID, item_index: int, user_id: uuid.UUID, is_important: bool
    ) -> None:
        existing = await self.db.execute(
            select(ReportItemFeedback).where(
                and_(
                    ReportItemFeedback.report_id == report_id,
                    ReportItemFeedback.item_index == item_index,
                    ReportItemFeedback.user_id == user_id,
                )
            )
        )
        feedback = existing.scalar_one_or_none()

        if feedback:
            feedback.is_important = is_important
        else:
            feedback = ReportItemFeedback(
                report_id=report_id,
                item_index=item_index,
                user_id=user_id,
                is_important=is_important,
            )
            self.db.add(feedback)
