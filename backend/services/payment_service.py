from __future__ import annotations

import uuid

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User
from backend.services.credits_service import CreditsService

RECHARGE_TIERS: dict[int, int] = {
    10: 1000,
    30: 3500,
    100: 13000,
}

_mock_orders: dict[str, dict] = {}


class RechargeResponse(BaseModel):
    payment_url: str
    order_id: str


class PaymentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_payment(self, user_id: uuid.UUID, tier: int) -> RechargeResponse:
        credits_amount = RECHARGE_TIERS.get(tier)
        if not credits_amount:
            raise HTTPException(
                status_code=400,
                detail=f"无效的充值档位: {tier}，可选: {list(RECHARGE_TIERS.keys())}",
            )

        order_id = str(uuid.uuid4())

        _mock_orders[order_id] = {
            "user_id": str(user_id),
            "tier": tier,
            "credits": credits_amount,
            "status": "paid",
        }

        credits_svc = CreditsService(self.db)
        await credits_svc.add_credits(
            user_id=user_id,
            amount=credits_amount,
            record_type="recharge",
            description=f"充值 ¥{tier} 获得 {credits_amount} 积分",
        )

        return RechargeResponse(
            payment_url=f"mock://payment/success?order={order_id}",
            order_id=order_id,
        )

    async def handle_callback(self, payment_data: dict) -> None:
        order_id = payment_data.get("order_id", "")
        order = _mock_orders.get(order_id)

        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if order["status"] != "paid":
            raise HTTPException(status_code=400, detail="订单状态异常")

        order["status"] = "completed"
