from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.db import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True)

    drone_id = Column(Integer, ForeignKey("drones.id"))
    mission_id = Column(Integer, ForeignKey("missions.id"))

    latitude = Column(Float)
    longitude = Column(Float)

    speed = Column(Float)
    status = Column(String)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())