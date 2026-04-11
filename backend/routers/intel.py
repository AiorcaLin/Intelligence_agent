from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.intel_service import IntelService

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────

class IntelItemResponse(BaseModel):
    index: int
    title: str
    summary: str
    importance_score: float | None = None
    domain: str | None = None
    sources: list[dict] | None = None
    action_items: list[str] | None = None
    is_important: bool = False


class ReportResponse(BaseModel):
    id: uuid.UUID
    domain: str
    title: str
    items: list[dict] | None
    action_items: list[dict] | None
    density_level: str
    formats_generated: list[str] | None
    audio_url: str | None
    video_url: str | None
    sources: list[dict] | None
    tokens_consumed: float | None
    is_regenerated: bool
    created_at: str | None

    model_config = {"from_attributes": True}


class FeedbackRequest(BaseModel):
    is_important: bool


class RegenerateRequest(BaseModel):
    feedback_text: str | None = None


class HistoryItem(BaseModel):
    report_id: uuid.UUID
    title: str
    domain: str
    similarity: float
    created_at: str | None


class PaginatedReports(BaseModel):
    items: list[ReportResponse]
    total: int
    page: int
    size: int


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/today", response_model=list[ReportResponse])
async def get_today_intel(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ReportResponse]:
    svc = IntelService(db)
    reports = await svc.get_today_reports(user.id)
    return [ReportResponse.model_validate(r) for r in reports]


@router.get("/list", response_model=PaginatedReports)
async def list_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    domain: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedReports:
    svc = IntelService(db)
    items, total = await svc.list_reports(
        user_id=user.id,
        page=page,
        size=size,
        domain=domain,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedReports(
        items=[ReportResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    svc = IntelService(db)
    report = await svc.get_report_detail(report_id, user.id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return ReportResponse.model_validate(report)


@router.get("/{report_id}/history", response_model=list[HistoryItem])
async def get_report_history(
    report_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[HistoryItem]:
    svc = IntelService(db)
    return await svc.get_report_history(report_id, user.id)


@router.post("/{report_id}/regenerate", response_model=ReportResponse)
async def regenerate_report(
    report_id: uuid.UUID,
    body: RegenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    svc = IntelService(db)
    report = await svc.regenerate_report(report_id, user.id, body.feedback_text)
    return ReportResponse.model_validate(report)


@router.post("/{report_id}/items/{item_index}/feedback")
async def toggle_item_feedback(
    report_id: uuid.UUID,
    item_index: int,
    body: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = IntelService(db)
    await svc.toggle_feedback(report_id, item_index, user.id, body.is_important)
    return {"ok": True}
