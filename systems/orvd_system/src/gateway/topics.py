"""Топики и actions для Gateway orvd_system."""
import os

_NS = os.environ.get("SYSTEM_NAMESPACE", "")
_P = f"{_NS}." if _NS else ""


class SystemTopics:
    ORVD_SYSTEM = f"{_P}systems.orvd_system"


class ComponentTopics:
    ORVD_COMPONENT = f"{_P}components.orvd_component"

    @classmethod
    def all(cls) -> list:
        return [cls.ORVD_COMPONENT]


class GatewayActions:

    REGISTER_MISSION = "register_mission"
    AUTHORIZE_MISSION = "authorize_mission"
    REQUEST_TAKEOFF = "request_takeoff"
    FORCE_LAND = "force_land"
    GET_REQUESTS = "get_requests"
