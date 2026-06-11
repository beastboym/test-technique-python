from __future__ import annotations
import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Intervention(Base):
    __tablename__ = "interventions"
    __table_args__ = (
        Index(
            "uq_one_active_intervention",
            "antenna_id",
            unique=True,
            postgresql_where="ended_at IS NULL",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    antenna_id: Mapped[int] = mapped_column(
        ForeignKey("antennas.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technician_identity: Mapped[str] = mapped_column(
        String(255), nullable=False)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

    antenna: Mapped["Antenna"] = relationship(
        back_populates="interventions", lazy="noload")
