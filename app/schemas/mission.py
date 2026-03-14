from pydantic import BaseModel


class MissionCreate(BaseModel):
    drone_serial: str
    route: str


class MissionResponse(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True