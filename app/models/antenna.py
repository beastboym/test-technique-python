from __future__ import annotations
import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AntennaStatus(str, enum.Enum):
    UP = "UP"
    DOWN = "DOWN"


class Antenna(Base):
    __tablename__ = "antennas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[AntennaStatus] = mapped_column(
        Enum(AntennaStatus, name="antennastatus"), nullable=False, default=AntennaStatus.UP
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="antenna", lazy="noload"
    )
