from fastapi import FastAPI
from app.api import telemetry, events
from app.services.db import init_db

init_db()

app = FastAPI(title="Telemetry & Event System")

app.include_router(telemetry.router, prefix="/log", tags=["Telemetry"])
app.include_router(events.router, prefix="/log", tags=["Events"])