from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.subscription import Subscription

VALID_DOMAINS = {"AI", "Crypto", "custom"}
VALID_DENSITY = {"quick_scan", "standard", "research"}
VALID_FREQUENCY = {"daily", "weekly", "major_only"}
VALID_BUCKETS = {"00", "03", "06", "09", "12", "15", "18", "21"}


class SubscriptionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_subscriptions(self, user_id: uuid.UUID) -> list[Subscription]:
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_subscription(
        self, sub_id: uuid.UUID, user_id: uuid.UUID
    ) -> Subscription | None:
        result = await self.db.execute(
            select(Subscription).where(
                and_(Subscription.id == sub_id, Subscription.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def create_subscription(
        self, user_id: uuid.UUID, data: dict
    ) -> Subscription:
        count_result = await self.db.execute(
            select(func.count(Subscription.id)).where(Subscription.user_id == user_id)
        )
        current_count = count_result.scalar() or 0
        if current_count >= 50:
            raise HTTPException(status_code=400, detail="订阅数量已达上限(50)")

        domain = data.get("domain", "")
        if domain not in VALID_DOMAINS:
            raise HTTPException(status_code=400, detail=f"无效的领域: {domain}")

        density = data.get("density_level", "standard")
        if density not in VALID_DENSITY:
            raise HTTPException(status_code=400, detail=f"无效的密度级别: {density}")

        frequency = data.get("frequency", "daily")
        if frequency not in VALID_FREQUENCY:
            raise HTTPException(status_code=400, detail=f"无效的频率: {frequency}")

        bucket = data.get("push_time_bucket", "09")
        if bucket not in VALID_BUCKETS:
            raise HTTPException(status_code=400, detail=f"无效的推送时段: {bucket}")

        sub = Subscription(user_id=user_id, **data)
        self.db.add(sub)
        await self.db.flush()
        await self.db.refresh(sub)
        return sub

    async def update_subscription(
        self, sub_id: uuid.UUID, user_id: uuid.UUID, data: dict
    ) -> Subscription:
        sub = await self.get_subscription(sub_id, user_id)
        if not sub:
            raise HTTPException(status_code=404, detail="订阅不存在")

        for key, value in data.items():
            if hasattr(sub, key):
                setattr(sub, key, value)

        await self.db.flush()
        await self.db.refresh(sub)
        return sub

    async def toggle_subscription(
        self, sub_id: uuid.UUID, user_id: uuid.UUID
    ) -> Subscription:
        sub = await self.get_subscription(sub_id, user_id)
        if not sub:
            raise HTTPException(status_code=404, detail="订阅不存在")

        sub.is_active = not sub.is_active
        await self.db.flush()
        await self.db.refresh(sub)
        return sub

    async def delete_subscription(
        self, sub_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        sub = await self.get_subscription(sub_id, user_id)
        if not sub:
            raise HTTPException(status_code=404, detail="订阅不存在")
        await self.db.delete(sub)
