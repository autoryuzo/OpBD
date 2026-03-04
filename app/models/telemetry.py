# SQLAlchemy модели для PostgreSQL

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    drone_id = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    pitch = Column(Float)
    roll = Column(Float)
    course = Column(Float)
    battery = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)