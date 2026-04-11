from __future__ import annotations

import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )
    subscription_limit: Mapped[int] = mapped_column(Integer, default=50, server_default=text("50"))
    vip_level: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    token_balance: Mapped[float] = mapped_column(
        Numeric(precision=12, scale=2),
        default=0,
        server_default=text("0"),
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    subscriptions = relationship("Subscription", back_populates="user", lazy="selectin")
    token_records = relationship("TokenRecord", back_populates="user", lazy="selectin")
    reports = relationship("IntelReport", back_populates="user", lazy="selectin")
    feedbacks = relationship("ReportSatisfaction", back_populates="user", lazy="selectin")
    template_trials = relationship("TemplateTrial", back_populates="user", lazy="selectin")
