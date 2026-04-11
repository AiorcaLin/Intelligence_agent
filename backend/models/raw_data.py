from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class RawData(Base):
    __tablename__ = "raw_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    raw_content: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fetched_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    embedding_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
