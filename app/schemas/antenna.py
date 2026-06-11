from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.antenna import AntennaStatus
from app.schemas.intervention import InterventionOut


class AntennaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
    status: AntennaStatus
    created_at: datetime
    last_intervention: Optional[InterventionOut]


class PaginatedAntennas(BaseModel):
    total: int
    items: list[AntennaOut]
