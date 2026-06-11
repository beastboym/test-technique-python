from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.antenna import AntennaStatus
from app.schemas.antenna import PaginatedAntennas
from app.services.antenna_service import list_antennas

router = APIRouter(prefix="/api/v1/antennas", tags=["antennas"])


@router.get("", response_model=PaginatedAntennas)
async def get_antennas(
    city: Optional[str] = Query(None),
    status: Optional[AntennaStatus] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await list_antennas(db, city=city, status=status, limit=limit, offset=offset)
