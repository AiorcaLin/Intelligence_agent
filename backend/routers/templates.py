from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.template_service import TemplateService

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────

class ContributorResponse(BaseModel):
    user_id: uuid.UUID
    contribution_description: str | None
    contribution_score: float

    model_config = {"from_attributes": True}


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    domain: str
    parent_template_id: uuid.UUID | None
    creator_type: str
    creator_id: uuid.UUID | None
    adoption_count: int
    quality_score: float | None
    version: int
    is_active: bool

    model_config = {"from_attributes": True}


class TemplateDetailResponse(TemplateResponse):
    prompt_config: dict | None
    contributors: list[ContributorResponse]


class LineageNode(BaseModel):
    id: uuid.UUID
    name: str
    creator_type: str
    creator_id: uuid.UUID | None
    depth: int


class ForkRequest(BaseModel):
    name: str
    description: str | None = None
    prompt_config: dict | None = None


class PaginatedTemplates(BaseModel):
    items: list[TemplateResponse]
    total: int
    page: int
    size: int


# ── Endpoints ─────────────────────────────────────────────────

@router.get("/", response_model=PaginatedTemplates)
async def list_templates(
    domain: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedTemplates:
    svc = TemplateService(db)
    items, total = await svc.list_templates(domain=domain, page=page, size=size)
    return PaginatedTemplates(
        items=[TemplateResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TemplateDetailResponse:
    svc = TemplateService(db)
    template = await svc.get_template_detail(template_id)
    contributors = [
        ContributorResponse.model_validate(c) for c in (template.contributors or [])
    ]
    data = TemplateResponse.model_validate(template).model_dump()
    data["prompt_config"] = template.prompt_config
    data["contributors"] = contributors
    return TemplateDetailResponse(**data)


@router.get("/{template_id}/lineage", response_model=list[LineageNode])
async def get_lineage(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[LineageNode]:
    svc = TemplateService(db)
    return await svc.get_lineage(template_id)


@router.post("/{template_id}/try")
async def try_template(
    template_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = TemplateService(db)
    result = await svc.try_template(template_id, user.id)
    return result


@router.post("/{template_id}/adopt")
async def adopt_template(
    template_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    svc = TemplateService(db)
    await svc.adopt_template(template_id, user.id)
    return {"ok": True}


@router.post("/{template_id}/fork", response_model=TemplateResponse)
async def fork_template(
    template_id: uuid.UUID,
    body: ForkRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TemplateResponse:
    svc = TemplateService(db)
    new_template = await svc.fork_template(template_id, user.id, body.model_dump())
    return TemplateResponse.model_validate(new_template)
