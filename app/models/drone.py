from sqlalchemy import Column, Integer, String, Boolean
from app.core.db import Base

class Drone(Base):
    __tablename__ = "drones"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, nullable=False)
    owner_id = Column(String, nullable=False)
    is_registered = Column(Boolean, default=True)