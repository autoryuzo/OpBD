from app.kafka.producer import send_message
from app.kafka.topics import ORDV_TAKEOFF_AUTHORIZATION
from app.services.mission_service import authorize_mission
from app.models.telemetry import Telemetry
from app.core.db import SessionLocal
from app.kafka.topics import DRONE_TAKEOFF_REQUEST, DRONE_TELEMETRY


def handle_message(topic, data):

    if topic == DRONE_TAKEOFF_REQUEST:
        handle_takeoff_request(data)

    elif topic == DRONE_TELEMETRY:
        handle_telemetry(data)

def handle_takeoff_request(data):

    mission_id = data["mission_id"]

    # проверяем миссию в БД
    mission = authorize_mission(mission_id)

    send_message(
        ORDV_TAKEOFF_AUTHORIZATION,
        {
            "mission_id": mission.id,
            "authorized": True
        }
    )

def handle_telemetry(data):

    db = SessionLocal()

    telemetry = Telemetry(
        drone_id=data["drone_id"],
        mission_id=data["mission_id"],
        latitude=data["lat"],
        longitude=data["lon"],
        speed=data["speed"],
        status=data["status"]
    )

    db.add(telemetry)
    db.commit()
    db.close()