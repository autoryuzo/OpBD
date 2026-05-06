"""Topics and actions for ORVD components."""
import os

_NS = os.environ.get("SYSTEM_NAMESPACE", "")
_P = f"{_NS}." if _NS else ""


class ComponentTopics:
    ORVD_COMPONENT = f"{_P}components.orvd_component"
    NOFLYZONES_COMPONENT = f"{_P}components.noflyzones_component"
    NOFLYZONES_UPDATES = f"{_P}components.noflyzones.updates"

    @classmethod
    def all(cls) -> list:
        return [cls.ORVD_COMPONENT, cls.NOFLYZONES_COMPONENT, cls.NOFLYZONES_UPDATES]


class ExternalTopics:
    REGULATOR = f"{_P}systems.regulator"


class OrvdActions:
    REGISTER_DRONE = "register_drone"
    REGISTER_MISSION = "register_mission"
    REQUEST_TAKEOFF = "request_takeoff"
    REVOKE_TAKEOFF = "revoke_takeoff"
    SEND_TELEMETRY = "send_telemetry"
    REQUEST_TELEMETRY = "request_telemetry"
    AUTHORIZE_MISSION = "authorize_mission"
    GET_HISTORY = "get_history"

    ADD_NO_FLY_ZONE = "add_no_fly_zone"
    UPDATE_NO_FLY_ZONE = "update_no_fly_zone"
    REMOVE_NO_FLY_ZONE = "remove_no_fly_zone"
    GET_NO_FLY_ZONES = "get_no_fly_zones"
    CHECK_NO_FLY_POINT = "check_no_fly_point"
    CHECK_NO_FLY_ROUTE = "check_no_fly_route"
    ACTIVATE_CARPET_MODE = "activate_carpet_mode"
    DEACTIVATE_CARPET_MODE = "deactivate_carpet_mode"
