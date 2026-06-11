from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.antenna import Antenna, AntennaStatus
from app.models.intervention import Intervention
from app.schemas.intervention import InterventionCreate, InterventionOut


async def create_intervention(db: AsyncSession, data: InterventionCreate) -> InterventionOut:
    antenna = await db.get(Antenna, data.antenna_id)
    if antenna is None:
        raise ValueError("antenna_not_found")

    existing = await db.execute(
        select(Intervention)
        .where(
            Intervention.antenna_id == data.antenna_id,
            Intervention.ended_at.is_(None),
        )
        .with_for_update()
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError("active_intervention_exists")

    intervention = Intervention(
        antenna_id=data.antenna_id,
        description=data.description,
        technician_identity=data.technician_identity,
        priority=data.priority,
    )
    db.add(intervention)
    antenna.status = AntennaStatus.DOWN

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("active_intervention_exists")

    await db.refresh(intervention)
    return InterventionOut.model_validate(intervention)


async def close_intervention(db: AsyncSession, intervention_id: int) -> InterventionOut:
    intervention = await db.get(Intervention, intervention_id)
    if intervention is None:
        raise ValueError("intervention_not_found")
    if intervention.ended_at is not None:
        raise ValueError("already_closed")

    intervention.ended_at = datetime.now(timezone.utc)

    antenna = await db.get(Antenna, intervention.antenna_id)
    antenna.status = AntennaStatus.UP

    await db.commit()
    await db.refresh(intervention)
    return InterventionOut.model_validate(intervention)
