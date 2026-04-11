from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.credits_service import CreditsService
from backend.services.payment_service import PaymentService

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────

class BalanceResponse(BaseModel):
    total_balance: float
    free_credits_remaining: int


class RechargeRequest(BaseModel):
    tier: int  # 10, 30, 100


class RechargeResponse(BaseModel):
    payment_url: str
    order_id: str


class PaymentCallbackRequest(BaseModel):
    order_id: str
    status: str
    amount: float


class TokenRecordResponse(BaseModel):
    id: uuid.UUID
    amount: float
    type: str
    description: str | None
    cost_breakdown: dict | None
    created_at: str | None

    model_config = {"from_attributes": True}


class PaginatedRecords(BaseModel):
    items: list[TokenRecordResponse]
    total: int
    page: int
    size: int


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BalanceResponse:
    svc = CreditsService(db)
    return await svc.get_balance(user.id)


@router.post("/recharge", response_model=RechargeResponse)
async def recharge(
    body: RechargeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RechargeResponse:
    svc = PaymentService(db)
    return await svc.create_payment(user.id, body.tier)


@router.post("/recharge/callback")
async def recharge_callback(
    body: PaymentCallbackRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = PaymentService(db)
    await svc.handle_callback(body.model_dump())
    return {"ok": True}


@router.get("/records", response_model=PaginatedRecords)
async def get_records(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    record_type: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedRecords:
    svc = CreditsService(db)
    items, total = await svc.get_records(
        user_id=user.id,
        page=page,
        size=size,
        record_type=record_type,
    )
    return PaginatedRecords(
        items=[TokenRecordResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/earnings", response_model=PaginatedRecords)
async def get_earnings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedRecords:
    svc = CreditsService(db)
    items, total = await svc.get_records(
        user_id=user.id,
        page=page,
        size=size,
        record_type="creator_revenue",
    )
    return PaginatedRecords(
        items=[TokenRecordResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        size=size,
    )
