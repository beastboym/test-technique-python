from fastapi import FastAPI

app = FastAPI(
    title="Antenna Management API",
    description="API REST de pilotage du réseau mobile: antennes et interventions terrain.",
    version="1.0.0",
)
