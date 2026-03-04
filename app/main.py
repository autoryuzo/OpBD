from fastapi import FastAPI
from app.api import missions
from app.core.db import init_db
from app.api import audit

init_db()

app = FastAPI(title="OrVD Drone System")

app.include_router(audit.router, prefix="/audit", tags=["Audit"])

app.include_router(missions.router, prefix="/missions", tags=["Missions"])