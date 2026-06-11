from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.antenna import Antenna, AntennaStatus
from app.models.intervention import Intervention
from app.schemas.antenna import AntennaOut, PaginatedAntennas


async def list_antennas(
    db: AsyncSession,
    city: str | None,
    status: AntennaStatus | None,
    limit: int,
    offset: int,
) -> PaginatedAntennas:
    base_q = select(Antenna)
    if city:
        base_q = base_q.where(Antenna.city.ilike(f"%{city}%"))
    if status:
        base_q = base_q.where(Antenna.status == status)

    total_result = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total = total_result.scalar_one()

    result = await db.execute(base_q.offset(offset).limit(limit))
    antennas = result.scalars().all()

    items = []
    for antenna in antennas:
        last_q = await db.execute(
            select(Intervention)
            .where(Intervention.antenna_id == antenna.id)
            .order_by(Intervention.created_at.desc())
            .limit(1)
        )
        last = last_q.scalar_one_or_none()
        items.append(
            AntennaOut(
                id=antenna.id,
                name=antenna.name,
                city=antenna.city,
                status=antenna.status,
                created_at=antenna.created_at,
                last_intervention=last,
            )
        )

    return PaginatedAntennas(total=total, items=items)
