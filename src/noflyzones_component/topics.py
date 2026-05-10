"""Topics and actions for the no-fly zones component."""
import os

_NS = os.environ.get("SYSTEM_NAMESPACE", "")
_P = f"{_NS}." if _NS else ""


class ComponentTopics:
    NOFLYZONES_COMPONENT = f"{_P}components.noflyzones_component"
    NOFLYZONES_UPDATES = f"{_P}components.noflyzones.updates"

    @classmethod
    def all(cls) -> list:
        return [cls.NOFLYZONES_COMPONENT, cls.NOFLYZONES_UPDATES]


class NoFlyZonesActions:
    ADD_ZONE = "add_no_fly_zone"
    UPDATE_ZONE = "update_no_fly_zone"
    REMOVE_ZONE = "remove_no_fly_zone"
    GET_ZONES = "get_no_fly_zones"
    CHECK_POINT = "check_no_fly_point"
    CHECK_ROUTE = "check_no_fly_route"
    ACTIVATE_CARPET = "activate_carpet_mode"
    DEACTIVATE_CARPET = "deactivate_carpet_mode"
