# Pydantic схемы для валидации запросов/ответов
from pydantic import BaseModel, Field

class TelemetrySchema(BaseModel):
    drone_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    pitch: float = None
    roll: float = None
    course: float = None
    battery: float = None

    class Config:
        orm_mode = True