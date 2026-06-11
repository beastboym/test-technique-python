from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.antenna import Antenna, AntennaStatus


async def _create_antenna(db: AsyncSession, name: str = "Tour A", city: str = "Paris") -> Antenna:
    antenna = Antenna(name=name, city=city, status=AntennaStatus.UP)
    db.add(antenna)
    await db.commit()
    await db.refresh(antenna)
    return antenna


async def test_create_intervention_nominal(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    antenna = await _create_antenna(db)
    resp = await client.post(
        "/api/v1/intervention",
        json={"antenna_id": antenna.id, "description": "Panne secteur", "technician_identity": "Jean Dupont", "priority": "HIGH"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["ended_at"] is None
    await db.refresh(antenna)
    assert antenna.status == AntennaStatus.DOWN


async def test_create_intervention_double_active(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    antenna = await _create_antenna(db)
    payload = {"antenna_id": antenna.id, "description": "Panne", "technician_identity": "Alice", "priority": "LOW"}
    r1 = await client.post("/api/v1/intervention", json=payload, headers=auth_headers)
    assert r1.status_code == 201
    r2 = await client.post("/api/v1/intervention", json=payload, headers=auth_headers)
    assert r2.status_code == 409
    assert "active intervention" in r2.json()["detail"].lower()


async def test_close_intervention(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    antenna = await _create_antenna(db)
    r = await client.post(
        "/api/v1/intervention",
        json={"antenna_id": antenna.id, "description": "P", "technician_identity": "Bob", "priority": "MEDIUM"},
        headers=auth_headers,
    )
    iid = r.json()["id"]
    resp = await client.patch(f"/api/v1/intervention/{iid}/close", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["ended_at"] is not None
    await db.refresh(antenna)
    assert antenna.status == AntennaStatus.UP


async def test_close_already_closed(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    antenna = await _create_antenna(db)
    r = await client.post(
        "/api/v1/intervention",
        json={"antenna_id": antenna.id, "description": "P", "technician_identity": "Bob", "priority": "LOW"},
        headers=auth_headers,
    )
    iid = r.json()["id"]
    await client.patch(f"/api/v1/intervention/{iid}/close", headers=auth_headers)
    resp = await client.patch(f"/api/v1/intervention/{iid}/close", headers=auth_headers)
    assert resp.status_code == 409


async def test_create_intervention_no_auth(client: AsyncClient, db: AsyncSession):
    antenna = await _create_antenna(db)
    resp = await client.post(
        "/api/v1/intervention",
        json={"antenna_id": antenna.id, "description": "P", "technician_identity": "X", "priority": "LOW"},
    )
    assert resp.status_code in (401, 403)


async def test_create_intervention_antenna_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/intervention",
        json={"antenna_id": 99999, "description": "P", "technician_identity": "X", "priority": "LOW"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_get_antennas_with_filters(client: AsyncClient, db: AsyncSession):
    await _create_antenna(db, name="Tour Paris 1", city="Paris")
    await _create_antenna(db, name="Tour Lyon 1", city="Lyon")
    resp = await client.get("/api/v1/antennas?city=Paris")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["city"] == "Paris"
    resp2 = await client.get("/api/v1/antennas?status=UP")
    assert resp2.status_code == 200
    assert resp2.json()["total"] == 2
