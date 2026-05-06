"""No-fly zones domain component.

The component owns static no-fly zones and temporary local "carpet" zones.
Other domains can request a snapshot through the component topic and subscribe
to ComponentTopics.NOFLYZONES_UPDATES for change events.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from broker.system_bus import SystemBus
from sdk.base_component import BaseComponent

try:
    from systems.orvd_system.src.noflyzones_component.topics import (
        ComponentTopics,
        NoFlyZonesActions,
    )
except ModuleNotFoundError:
    from src.noflyzones_component.topics import ComponentTopics, NoFlyZonesActions


class NoFlyZonesComponent(BaseComponent):
    def __init__(
        self,
        component_id: str,
        name: str,
        bus: SystemBus,
        topic: str = ComponentTopics.NOFLYZONES_COMPONENT,
    ):
        self.name = name
        self._zones: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []

        super().__init__(
            component_id=component_id,
            component_type="noflyzones_component",
            topic=topic,
            bus=bus,
        )

        print(f"NoFlyZonesComponent '{name}' initialized")

    def _register_handlers(self):
        self.register_handler(NoFlyZonesActions.ADD_ZONE, self._handle_add_zone)
        self.register_handler(NoFlyZonesActions.UPDATE_ZONE, self._handle_update_zone)
        self.register_handler(NoFlyZonesActions.REMOVE_ZONE, self._handle_remove_zone)
        self.register_handler(NoFlyZonesActions.GET_ZONES, self._handle_get_zones)
        self.register_handler(NoFlyZonesActions.CHECK_POINT, self._handle_check_point)
        self.register_handler(NoFlyZonesActions.CHECK_ROUTE, self._handle_check_route)
        self.register_handler(NoFlyZonesActions.ACTIVATE_CARPET, self._handle_activate_carpet)
        self.register_handler(NoFlyZonesActions.DEACTIVATE_CARPET, self._handle_deactivate_carpet)

    def _now(self) -> str:
        return datetime.utcnow().isoformat()

    def _log(self, event: str, **kwargs):
        self._history.append({"event": event, "timestamp": self._now(), **kwargs})

    def _publish_update(self, event: str, zone: Optional[Dict[str, Any]] = None):
        self.bus.publish(
            ComponentTopics.NOFLYZONES_UPDATES,
            {
                "action": "no_fly_zones_updated",
                "sender": self.component_id,
                "payload": {
                    "event": event,
                    "zone": zone,
                    "zones": list(self._zones.values()),
                    "timestamp": self._now(),
                },
            },
        )

    def _normalize_zone(self, payload: Dict[str, Any], existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        zone = dict(existing or {})
        zone.update(payload)
        zone.setdefault("active", True)
        zone.setdefault("kind", "no_fly")
        zone["updated_at"] = self._now()
        zone.setdefault("created_at", zone["updated_at"])
        return zone

    def _validate_zone(self, zone: Dict[str, Any]) -> Optional[str]:
        if not zone.get("zone_id"):
            return "zone_id required"

        bounds = zone.get("bounds")
        if not isinstance(bounds, dict):
            return "bounds required"

        required = ("min_lat", "max_lat", "min_lon", "max_lon")
        if any(bounds.get(key) is None for key in required):
            return "bounds must include min_lat, max_lat, min_lon, max_lon"

        if bounds["min_lat"] > bounds["max_lat"] or bounds["min_lon"] > bounds["max_lon"]:
            return "invalid bounds"

        return None

    def _handle_add_zone(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = message.get("payload", {})
        zone = self._normalize_zone(payload)
        error = self._validate_zone(zone)
        if error:
            return {"status": "error", "message": error}

        zone_id = zone["zone_id"]
        if zone_id in self._zones:
            return {"status": "error", "message": "zone already exists"}

        self._zones[zone_id] = zone
        self._log("zone_added", zone_id=zone_id)
        self._publish_update("zone_added", zone)
        return {"status": "zone_added", "zone_id": zone_id, "zone": zone}

    def _handle_update_zone(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = message.get("payload", {})
        zone_id = payload.get("zone_id")
        if zone_id not in self._zones:
            return {"status": "error", "message": "zone not found"}

        zone = self._normalize_zone(payload, self._zones[zone_id])
        error = self._validate_zone(zone)
        if error:
            return {"status": "error", "message": error}

        self._zones[zone_id] = zone
        self._log("zone_updated", zone_id=zone_id)
        self._publish_update("zone_updated", zone)
        return {"status": "zone_updated", "zone_id": zone_id, "zone": zone}

    def _handle_remove_zone(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = message.get("payload", {})
        zone_id = payload.get("zone_id")
        if not zone_id:
            return {"status": "error", "message": "zone_id required"}

        zone = self._zones.pop(zone_id, None)
        self._log("zone_removed", zone_id=zone_id)
        self._publish_update("zone_removed", zone)
        return {"status": "zone_removed", "zone_id": zone_id}

    def _handle_get_zones(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = message.get("payload", {})
        include_inactive = payload.get("include_inactive", False)
        zones = [
            zone for zone in self._zones.values()
            if include_inactive or zone.get("active", True)
        ]
        return {"status": "ok", "zones": zones, "history": self._history}

    def _handle_check_point(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = message.get("payload", {})
        point = payload.get("coords", payload)
        zone = self._find_zone_for_point(point)
        return {
            "status": "ok",
            "violates": zone is not None,
            "zone": zone,
            "command": "LAND" if zone and zone.get("kind") == "carpet" else None,
        }

    def _handle_check_route(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = message.get("payload", {})
        for point in payload.get("route", []):
            zone = self._find_zone_for_point(point)
            if zone:
                return {"status": "ok", "violates": True, "zone": zone}

        return {"status": "ok", "violates": False, "zone": None}

    def _handle_activate_carpet(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(message.get("payload", {}))
        payload.setdefault("zone_id", f"carpet:{payload.get('area_id', 'default')}")
        payload["kind"] = "carpet"
        payload["active"] = True

        zone = self._normalize_zone(payload, self._zones.get(payload["zone_id"]))
        error = self._validate_zone(zone)
        if error:
            return {"status": "error", "message": error}

        self._zones[zone["zone_id"]] = zone
        self._log("carpet_activated", zone_id=zone["zone_id"])
        self._publish_update("carpet_activated", zone)
        return {
            "status": "carpet_activated",
            "zone_id": zone["zone_id"],
            "zone": zone,
            "command": "LAND_IN_ZONE",
        }

    def _handle_deactivate_carpet(self, message: Dict[str, Any]) -> Dict[str, Any]:
        payload = message.get("payload", {})
        zone_id = payload.get("zone_id") or f"carpet:{payload.get('area_id', 'default')}"
        zone = self._zones.get(zone_id)
        if not zone:
            return {"status": "error", "message": "carpet zone not found"}

        zone = self._normalize_zone({"zone_id": zone_id, "active": False}, zone)
        self._zones[zone_id] = zone
        self._log("carpet_deactivated", zone_id=zone_id)
        self._publish_update("carpet_deactivated", zone)
        return {"status": "carpet_deactivated", "zone_id": zone_id, "zone": zone}

    def _find_zone_for_point(self, coords: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        lat = coords.get("lat")
        lon = coords.get("lon")
        if lat is None or lon is None:
            return None

        for zone in self._zones.values():
            if not zone.get("active", True):
                continue

            bounds = zone.get("bounds", {})
            if (
                bounds.get("min_lat") <= lat <= bounds.get("max_lat")
                and bounds.get("min_lon") <= lon <= bounds.get("max_lon")
            ):
                return zone

        return None
