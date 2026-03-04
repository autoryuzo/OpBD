from fastapi import APIRouter, Depends
from app.schemas.events import EventSchema
from app.services.kafka_producer import send_event
from app.services.db import SessionLocal
from app.models.events import Event as EventModel
from app.security.api_key import verify_api_key

router = APIRouter()

@router.post("/event")
def post_event(data: EventSchema, api_key: str = Depends(verify_api_key)):
    # Отправка в Kafka
    send_event(data.dict())

    # Запись в Postgres
    db = SessionLocal()
    db_obj = EventModel(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    db.close()
    return {"status": "ok", "id": db_obj.id}