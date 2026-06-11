from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.intervention import Priority


class InterventionCreate(BaseModel):
    antenna_id: int
    description: str
    technician_identity: str
    priority: Priority


class InterventionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    antenna_id: int
    description: str
    technician_identity: str
    priority: Priority
    created_at: datetime
    ended_at: Optional[datetime]
