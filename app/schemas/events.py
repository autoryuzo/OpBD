from pydantic import BaseModel

class EventSchema(BaseModel):
    drone_id: str
    event_type: str
    severity: str = None
    message: str = None

    class Config:
        orm_mode = True