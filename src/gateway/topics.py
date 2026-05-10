"""
Топики и actions для Gateway orvd_system.
Поддерживает внешний API Agrodron (v1.*).
"""
import os

_NS = os.environ.get("SYSTEM_NAMESPACE", "")
_P = f"{_NS}." if _NS else ""


class SystemTopics:
    # Внутренний системный топик
    ORVD_SYSTEM = f"{_P}systems.orvd_system"

    # ВНЕШНИЙ API топик (Agrodron контракт)
    ORVD_EXTERNAL = os.environ.get(
        "ORVD_EXTERNAL_TOPIC",
        "v1.ORVD.ORVD001.main",
    )


class ComponentTopics:
    ORVD_COMPONENT = f"{_P}components.orvd_component"
    NOFLYZONES_COMPONENT = f"{_P}components.noflyzones_component"

    @classmethod
    def all(cls) -> list:
        return [cls.ORVD_COMPONENT, cls.NOFLYZONES_COMPONENT]


class GatewayActions:

    # внутренние
    REGISTER_DRONE = "register_drone"
    REGISTER_MISSION = "register_mission"
    AUTHORIZE_MISSION = "authorize_mission"
    REQUEST_TAKEOFF = "request_takeoff"
    REVOKE_TAKEOFF = "revoke_takeoff"
    COMPLETE_MISSION = "complete_mission"
    REPORT_INCIDENT = "report_incident"
    GET_MISSION_STATUS = "get_mission_status"
    SEND_TELEMETRY = "send_telemetry"
    REQUEST_TELEMETRY = "request_telemetry"
    ADD_NO_FLY_ZONE = "add_no_fly_zone"
    UPDATE_NO_FLY_ZONE = "update_no_fly_zone"
    REMOVE_NO_FLY_ZONE = "remove_no_fly_zone"
    GET_NO_FLY_ZONES = "get_no_fly_zones"
    CHECK_NO_FLY_POINT = "check_no_fly_point"
    CHECK_NO_FLY_ROUTE = "check_no_fly_route"
    ACTIVATE_CARPET_MODE = "activate_carpet_mode"
    DEACTIVATE_CARPET_MODE = "deactivate_carpet_mode"
    GET_HISTORY = "get_history"
