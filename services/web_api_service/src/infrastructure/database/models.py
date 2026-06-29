from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base

class HttpLogModel(Base):
    __tablename__="http_logs"
    __table_args__ = (
        Index("ix_http_logs_created_at", "created_at"),
        Index("ix_http_logs_method", "method"),
        Index("ix_http_logs_status_code", "status_code"),
    )

    id: Mapped[UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    ip: Mapped[str]=mapped_column(String(45), nullable=False)
    method: Mapped[str]=mapped_column(String(10), nullable=False)
    uri: Mapped[str]=mapped_column(String(2048), nullable=False)
    status_code: Mapped[int]=mapped_column(Integer, nullable=False)
    raw_log: Mapped[str]=mapped_column(Text, nullable=False)