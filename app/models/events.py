from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    drone_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    severity = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)