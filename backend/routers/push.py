from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.push_service import PushService

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────

class PushStatusResponse(BaseModel):
    report_id: uuid.UUID
    channel: str
    status: str
    sent_at: str | None
    error_msg: str | None

    model_config = {"from_attributes": True}


class TestPushRequest(BaseModel):
    report_id: uuid.UUID
    channels: list[str]


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/status", response_model=list[PushStatusResponse])
async def get_push_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PushStatusResponse]:
    svc = PushService(db)
    logs = await svc.get_push_status(user.id)
    return [PushStatusResponse.model_validate(log) for log in logs]


@router.post("/test")
async def test_push(
    body: TestPushRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = PushService(db)
    await svc.push_report(user.id, body.report_id, body.channels)
    return {"ok": True, "message": "推送已发起"}
