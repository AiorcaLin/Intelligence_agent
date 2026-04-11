from __future__ import annotations

import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.feedback import ReportItemFeedback, ReportSatisfaction


class FeedbackService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def toggle_important(
        self, report_id: uuid.UUID, item_index: int, user_id: uuid.UUID
    ) -> ReportItemFeedback:
        result = await self.db.execute(
            select(ReportItemFeedback).where(
                and_(
                    ReportItemFeedback.report_id == report_id,
                    ReportItemFeedback.item_index == item_index,
                    ReportItemFeedback.user_id == user_id,
                )
            )
        )
        feedback = result.scalar_one_or_none()

        if feedback:
            feedback.is_important = not feedback.is_important
        else:
            feedback = ReportItemFeedback(
                report_id=report_id,
                item_index=item_index,
                user_id=user_id,
                is_important=True,
            )
            self.db.add(feedback)

        await self.db.flush()
        await self.db.refresh(feedback)
        return feedback

    async def submit_satisfaction(
        self,
        report_id: uuid.UUID,
        user_id: uuid.UUID,
        is_satisfied: bool,
        feedback_text: str | None = None,
    ) -> ReportSatisfaction:
        existing = await self.db.execute(
            select(ReportSatisfaction).where(
                and_(
                    ReportSatisfaction.report_id == report_id,
                    ReportSatisfaction.user_id == user_id,
                )
            )
        )
        sat = existing.scalar_one_or_none()

        if sat:
            sat.is_satisfied = is_satisfied
            sat.feedback_text = feedback_text
        else:
            sat = ReportSatisfaction(
                report_id=report_id,
                user_id=user_id,
                is_satisfied=is_satisfied,
                feedback_text=feedback_text,
            )
            self.db.add(sat)

        await self.db.flush()
        await self.db.refresh(sat)
        return sat
