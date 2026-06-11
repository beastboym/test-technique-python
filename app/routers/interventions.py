from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_api_key
from app.schemas.intervention import InterventionCreate, InterventionOut
from app.services.intervention_service import close_intervention, create_intervention

router = APIRouter(prefix="/api/v1/intervention", tags=["interventions"])

_auth = [Depends(require_api_key)]


@router.post("", response_model=InterventionOut, status_code=status.HTTP_201_CREATED, dependencies=_auth)
async def post_intervention(data: InterventionCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_intervention(db, data)
    except ValueError as e:
        msg = str(e)
        if msg == "antenna_not_found":
            raise HTTPException(status_code=404, detail="Antenna not found")
        if msg == "active_intervention_exists":
            raise HTTPException(status_code=409, detail="An active intervention already exists for this antenna")
        raise


@router.patch("/{intervention_id}/close", response_model=InterventionOut, dependencies=_auth)
async def patch_close(intervention_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await close_intervention(db, intervention_id)
    except ValueError as e:
        msg = str(e)
        if msg == "intervention_not_found":
            raise HTTPException(status_code=404, detail="Intervention not found")
        if msg == "already_closed":
            raise HTTPException(status_code=409, detail="Intervention is already closed")
        raise
