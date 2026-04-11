from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), default="AI情报")
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    custom_keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    density_level: Mapped[str] = mapped_column(
        String(20),
        default="standard",
        server_default=text("'standard'"),
    )
    formats: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=["text"],
        server_default=text("'{text}'"),
    )
    frequency: Mapped[str] = mapped_column(
        String(20),
        default="daily",
        server_default=text("'daily'"),
    )
    push_time_bucket: Mapped[str] = mapped_column(
        String(2),
        default="09",
        server_default=text("'09'"),
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="subscriptions")
    template = relationship("Template", lazy="selectin")
    reports = relationship("IntelReport", back_populates="subscription", lazy="selectin")
