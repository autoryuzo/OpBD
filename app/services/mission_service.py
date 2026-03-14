from app.models.mission import Mission, MissionStatus
from app.services.audit_service import log_action
from app.models.drone import Drone
from app.core.db import SessionLocal


def create_mission(drone_serial: str, route: str):
    db = SessionLocal()

    drone = db.query(Drone).filter(Drone.serial_number == drone_serial).first()
    if not drone:
        db.close()
        raise Exception("Drone not registered")

    mission = Mission(drone_id=drone.id, route=route)
    db.add(mission)
    db.commit()
    db.refresh(mission)

    log_action(
        action="MISSION_CREATED",
        entity="Mission",
        entity_id=mission.id,
        performed_by=drone.owner_id
    )

    db.close()
    return mission


def authorize_mission(mission_id: int):
    db = SessionLocal()
    mission = db.query(Mission).filter(Mission.id == mission_id).first()

    if not mission:
        db.close()
        raise Exception("Mission not found")

    mission.status = MissionStatus.AUTHORIZED
    db.commit()
    db.refresh(mission)

    log_action(
        action="MISSION_AUTHORIZED",
        entity="Mission",
        entity_id=mission.id,
        performed_by="SYSTEM"
    )

    db.close()
    return mission