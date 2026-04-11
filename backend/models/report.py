from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class IntelReport(Base):
    __tablename__ = "intel_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id"),
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    items: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    action_items: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    density_level: Mapped[str] = mapped_column(String(20), nullable=False)
    formats_generated: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tokens_consumed: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    cost_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_regenerated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )
    original_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intel_reports.id"),
        nullable=True,
    )
    embedding_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    subscription = relationship("Subscription", back_populates="reports")
    user = relationship("User", back_populates="reports")
    template = relationship("Template", lazy="selectin")
    original_report = relationship("IntelReport", remote_side="IntelReport.id", lazy="selectin")
