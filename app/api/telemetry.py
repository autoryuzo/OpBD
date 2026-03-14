from fastapi import APIRouter
from app.core.db import SessionLocal
from app.models.telemetry import Telemetry

router = APIRouter()


@router.get("/latest")
def get_latest_positions():
    db = SessionLocal()

    telemetry = (
        db.query(Telemetry)
        .order_by(Telemetry.timestamp.desc())
        .limit(50)
        .all()
    )

    db.close()

    return telemetry