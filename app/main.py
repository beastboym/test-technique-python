from fastapi import FastAPI

from app.routers import antennas, interventions

app = FastAPI(
    title="Antenna Management API",
    description="API REST de pilotage du réseau mobile — antennes et interventions terrain.",
    version="1.0.0",
)

app.include_router(antennas.router)
app.include_router(interventions.router)
