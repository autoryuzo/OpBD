# Endpoint /log/telemetry

from fastapi import APIRouter, Depends
from app.schemas.telemetry import TelemetrySchema
from app.services.kafka_producer import send_telemetry
from app.services.db import SessionLocal
from app.models.telemetry import Telemetry as TelemetryModel
from app.security.api_key import verify_api_key

router = APIRouter()

@router.post("/telemetry")
def post_telemetry(data: TelemetrySchema, api_key: str = Depends(verify_api_key)):
    # Отправка в Kafka
    send_telemetry(data.dict())

    # Запись в Postgres
    db = SessionLocal()
    db_obj = TelemetryModel(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    db.close()
    return {"status": "ok", "id": db_obj.id}