from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.token_record import TokenRecord
from backend.models.user import User
from backend.utils.pricing import calculate_credits

MODEL_PRICES = {
    "deepseek_v3": {"input": 0.001, "output": 0.002},
    "claude_sonnet": {"input": 0.015, "output": 0.060},
}


class BalanceInfo(BaseModel):
    total_balance: float
    free_credits_remaining: int


class CreditsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_balance(self, user_id: uuid.UUID) -> BalanceInfo:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        free_used_result = await self.db.execute(
            select(func.coalesce(func.sum(TokenRecord.amount), 0)).where(
                and_(
                    TokenRecord.user_id == user_id,
                    TokenRecord.type == "free_daily",
                    TokenRecord.created_at >= today_start,
                )
            )
        )
        free_used = abs(float(free_used_result.scalar() or 0))
        free_remaining = max(0, settings.DAILY_FREE_CREDITS - int(free_used))

        return BalanceInfo(
            total_balance=float(user.token_balance),
            free_credits_remaining=free_remaining,
        )

    async def consume_credits(
        self,
        user_id: uuid.UUID,
        amount: float,
        cost_breakdown: dict | None = None,
        related_report_id: uuid.UUID | None = None,
    ) -> None:
        balance = await self.get_balance(user_id)

        free_to_use = min(amount, balance.free_credits_remaining)
        paid_to_use = amount - free_to_use

        if paid_to_use > balance.total_balance:
            raise HTTPException(status_code=402, detail="积分不足")

        if free_to_use > 0:
            free_record = TokenRecord(
                user_id=user_id,
                amount=-free_to_use,
                type="free_daily",
                description="每日免费积分消耗",
                cost_breakdown=cost_breakdown,
                related_report_id=related_report_id,
            )
            self.db.add(free_record)

        if paid_to_use > 0:
            paid_record = TokenRecord(
                user_id=user_id,
                amount=-paid_to_use,
                type="consume",
                description="付费积分消耗",
                cost_breakdown=cost_breakdown,
                related_report_id=related_report_id,
            )
            self.db.add(paid_record)

            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one()
            user.token_balance = float(user.token_balance) - paid_to_use

        await self.db.flush()

    async def add_credits(
        self,
        user_id: uuid.UUID,
        amount: float,
        record_type: str,
        description: str,
        related_template_id: uuid.UUID | None = None,
    ) -> None:
        record = TokenRecord(
            user_id=user_id,
            amount=amount,
            type=record_type,
            description=description,
            related_template_id=related_template_id,
        )
        self.db.add(record)

        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()
        user.token_balance = float(user.token_balance) + amount

        await self.db.flush()

    async def get_records(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        record_type: str | None = None,
    ) -> tuple[list[TokenRecord], int]:
        query = select(TokenRecord).where(TokenRecord.user_id == user_id)
        count_query = select(func.count(TokenRecord.id)).where(TokenRecord.user_id == user_id)

        if record_type:
            query = query.where(TokenRecord.type == record_type)
            count_query = count_query.where(TokenRecord.type == record_type)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        result = await self.db.execute(
            query.order_by(TokenRecord.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(result.scalars().all()), total

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
        density_level: str,
    ) -> int:
        return calculate_credits(input_tokens, output_tokens, model, density_level)
