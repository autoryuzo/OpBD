from pydantic import BaseModel
from datetime import datetime


class AuditResponse(BaseModel):
    id: int
    action: str
    entity: str
    entity_id: int
    performed_by: str | None
    timestamp: datetime

    class Config:
        from_attributes = True