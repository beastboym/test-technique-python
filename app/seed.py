"""Seed de données de démonstration.

/!\ Ne fait rien si des antennes existent déjà.
Usage : python -m app.seed
"""
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.antenna import Antenna, AntennaStatus
from app.models.intervention import Intervention, Priority


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        count = (
            await session.execute(select(func.count()).select_from(Antenna))
        ).scalar_one()
        if count:
            print(f"Seed ignoré : {count} antenne(s) déjà en base.")
            return

        antennas = [
            Antenna(name="Tour Eiffel Nord", city="Paris",
                    status=AntennaStatus.UP),
            Antenna(name="Montmartre Relais 3",
                    city="Paris", status=AntennaStatus.UP),
            Antenna(name="Fourvière Sud", city="Lyon",
                    status=AntennaStatus.UP),
            Antenna(name="Vieux-Port Relais 1",
                    city="Marseille", status=AntennaStatus.UP),
            Antenna(name="Mériadeck Centre", city="Bordeaux",
                    status=AntennaStatus.UP),
        ]
        session.add_all(antennas)
        await session.flush()

        # Une intervention passée (clôturée) pour illustrer `last_intervention`
        # dans GET /antennas sans enfreindre la règle « antenne DOWN = intervention active ».
        started = datetime.now(timezone.utc) - timedelta(days=7)
        session.add(
            Intervention(
                antenna_id=antennas[0].id,
                description="Maintenance préventive — remplacement batterie de secours",
                technician_identity="Marie Curie",
                priority=Priority.MEDIUM,
                created_at=started,
                ended_at=started + timedelta(hours=2),
            )
        )

        await session.commit()
        print(
            f"Seed terminé : {len(antennas)} antennes et 1 intervention clôturée créées.")


if __name__ == "__main__":
    asyncio.run(seed())
