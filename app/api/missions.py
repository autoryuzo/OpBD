from fastapi import APIRouter, HTTPException
from app.schemas.mission import MissionCreate, MissionResponse
from app.services.mission_service import create_mission, authorize_mission

router = APIRouter()


@router.post("/", response_model=MissionResponse)
def register_mission(data: MissionCreate):
    try:
        mission = create_mission(data.drone_serial, data.route)
        return mission
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{mission_id}/authorize", response_model=MissionResponse)
def authorize(mission_id: int):
    try:
        mission = authorize_mission(mission_id)
        return mission
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))