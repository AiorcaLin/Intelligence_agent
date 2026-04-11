from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.subscription_service import SubscriptionService

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────

class SubscriptionCreate(BaseModel):
    name: str = "AI情报"
    domain: str
    custom_keywords: list[str] | None = None
    density_level: str = "standard"
    formats: list[str] = ["text"]
    frequency: str = "daily"
    push_time_bucket: str = "09"
    template_id: uuid.UUID | None = None


class SubscriptionUpdate(BaseModel):
    name: str | None = None
    domain: str | None = None
    custom_keywords: list[str] | None = None
    density_level: str | None = None
    formats: list[str] | None = None
    frequency: str | None = None
    push_time_bucket: str | None = None
    template_id: uuid.UUID | None = None


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    name: str
    domain: str
    custom_keywords: list[str] | None
    density_level: str
    formats: list[str]
    frequency: str
    push_time_bucket: str
    template_id: uuid.UUID | None
    is_active: bool

    model_config = {"from_attributes": True}


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SubscriptionResponse]:
    svc = SubscriptionService(db)
    subs = await svc.list_subscriptions(user.id)
    return [SubscriptionResponse.model_validate(s) for s in subs]


@router.post("/", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    body: SubscriptionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    svc = SubscriptionService(db)
    sub = await svc.create_subscription(user.id, body.model_dump())
    return SubscriptionResponse.model_validate(sub)


@router.get("/{sub_id}", response_model=SubscriptionResponse)
async def get_subscription(
    sub_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    svc = SubscriptionService(db)
    sub = await svc.get_subscription(sub_id, user.id)
    if not sub:
        raise HTTPException(status_code=404, detail="订阅不存在")
    return SubscriptionResponse.model_validate(sub)


@router.put("/{sub_id}", response_model=SubscriptionResponse)
async def update_subscription(
    sub_id: uuid.UUID,
    body: SubscriptionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    svc = SubscriptionService(db)
    sub = await svc.update_subscription(sub_id, user.id, body.model_dump(exclude_unset=True))
    return SubscriptionResponse.model_validate(sub)


@router.patch("/{sub_id}/toggle", response_model=SubscriptionResponse)
async def toggle_subscription(
    sub_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubscriptionResponse:
    svc = SubscriptionService(db)
    sub = await svc.toggle_subscription(sub_id, user.id)
    return SubscriptionResponse.model_validate(sub)


@router.delete("/{sub_id}", status_code=204)
async def delete_subscription(
    sub_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    svc = SubscriptionService(db)
    await svc.delete_subscription(sub_id, user.id)
