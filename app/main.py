from fastapi import FastAPI
import threading

from app.core.db import init_db
from app.api import audit, missions,telemetry
#from app.kafka.consumer import consumer
#from app.kafka.handlers import handle_message

init_db()

app = FastAPI(title="OrVD Drone System")

app.include_router(audit.router, prefix="/audit", tags=["Audit"])
app.include_router(missions.router, prefix="/missions", tags=["Missions"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])



# def kafka_listener():
#     for msg in consumer:
#         handle_message(msg.topic, msg.value)


# @app.on_event("startup")
# def start_kafka():
#     thread = threading.Thread(target=kafka_listener)
#     thread.start()