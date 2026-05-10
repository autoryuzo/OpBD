from unittest.mock import MagicMock

import pytest

from src.noflyzones_component import NoFlyZonesComponent
from src.noflyzones_component.topics import ComponentTopics, NoFlyZonesActions


@pytest.fixture
def component_and_bus():
    bus = MagicMock()
    component = NoFlyZonesComponent(
        component_id="noflyzones_component_1",
        name="NoFlyZones",
        bus=bus,
    )
    return component, bus


def test_add_zone_publishes_update(component_and_bus):
    component, bus = component_and_bus

    result = component._handle_add_zone({
        "payload": {
            "zone_id": "Z1",
            "bounds": {"min_lat": 0, "max_lat": 10, "min_lon": 0, "max_lon": 10},
        }
    })

    assert result["status"] == "zone_added"
    assert result["zone_id"] == "Z1"
    bus.publish.assert_called_once()
    assert bus.publish.call_args[0][0] == ComponentTopics.NOFLYZONES_UPDATES


def test_add_zone_validates_bounds(component_and_bus):
    component, _ = component_and_bus

    result = component._handle_add_zone({
        "payload": {
            "zone_id": "Z1",
            "bounds": {"min_lat": 10, "max_lat": 0, "min_lon": 0, "max_lon": 10},
        }
    })

    assert result["status"] == "error"


def test_get_zones_returns_active_zones(component_and_bus):
    component, _ = component_and_bus
    component._zones["Z1"] = {"zone_id": "Z1", "active": True}
    component._zones["Z2"] = {"zone_id": "Z2", "active": False}

    result = component._handle_get_zones({"payload": {}})

    assert result["status"] == "ok"
    assert [zone["zone_id"] for zone in result["zones"]] == ["Z1"]


def test_check_point_detects_zone(component_and_bus):
    component, _ = component_and_bus
    component._zones["Z1"] = {
        "zone_id": "Z1",
        "active": True,
        "kind": "no_fly",
        "bounds": {"min_lat": 0, "max_lat": 10, "min_lon": 0, "max_lon": 10},
    }

    result = component._handle_check_point({
        "action": NoFlyZonesActions.CHECK_POINT,
        "payload": {"coords": {"lat": 5, "lon": 5}},
    })

    assert result["status"] == "ok"
    assert result["violates"] is True
    assert result["zone"]["zone_id"] == "Z1"


def test_check_route_detects_zone(component_and_bus):
    component, _ = component_and_bus
    component._zones["Z1"] = {
        "zone_id": "Z1",
        "active": True,
        "kind": "no_fly",
        "bounds": {"min_lat": 0, "max_lat": 10, "min_lon": 0, "max_lon": 10},
    }

    result = component._handle_check_route({
        "payload": {"route": [{"lat": 20, "lon": 20}, {"lat": 5, "lon": 5}]}
    })

    assert result["violates"] is True
    assert result["zone"]["zone_id"] == "Z1"


def test_carpet_mode_creates_landing_zone(component_and_bus):
    component, _ = component_and_bus

    result = component._handle_activate_carpet({
        "payload": {
            "area_id": "A1",
            "bounds": {"min_lat": 0, "max_lat": 10, "min_lon": 0, "max_lon": 10},
        }
    })

    assert result["status"] == "carpet_activated"
    assert result["command"] == "LAND_IN_ZONE"
    assert component._zones["carpet:A1"]["kind"] == "carpet"
