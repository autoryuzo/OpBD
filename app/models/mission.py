from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum


class MissionStatus(str, enum.Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"
    IN_FLIGHT = "IN_FLIGHT"
    CANCELLED = "CANCELLED"


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    drone_id = Column(Integer, ForeignKey("drones.id"), nullable=False)
    route = Column(String, nullable=False)
    status = Column(Enum(MissionStatus), default=MissionStatus.CREATED)

    drone = relationship("Drone")