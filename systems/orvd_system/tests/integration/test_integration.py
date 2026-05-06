from itertools import count

import pytest

from src.gateway.src.gateway import OrvdGateway
from src.gateway.topics import GatewayActions, SystemTopics
from src.noflyzones_component import NoFlyZonesComponent
from src.noflyzones_component.topics import ComponentTopics as NoFlyZonesTopics
from src.orvd_component import OrvdComponent
from src.orvd_component.topics import ComponentTopics as OrvdTopics


class InProcessBus:
    def __init__(self):
        self.subscribers = {}
        self.published = []
        self._ids = count(1)

    def start(self):
        pass

    def stop(self):
        pass

    def subscribe(self, topic, handler):
        self.subscribers[topic] = handler

    def unsubscribe(self, topic):
        self.subscribers.pop(topic, None)

    def publish(self, topic, message):
        self.published.append((topic, message))

    def request(self, topic, message, timeout=10.0):
        handler = self.subscribers.get(topic)
        if handler is None:
            return None

        reply_to = f"tests.reply.{next(self._ids)}"
        correlation_id = f"corr-{next(self._ids)}"
        request = {
            **message,
            "reply_to": reply_to,
            "correlation_id": correlation_id,
        }

        before = len(self.published)
        handler(request)

        for published_topic, published_message in self.published[before:]:
            if (
                published_topic == reply_to
                and published_message.get("correlation_id") == correlation_id
            ):
                return published_message

        return None


@pytest.fixture
def running_system():
    bus = InProcessBus()

    orvd = OrvdComponent(
        component_id="orvd_component",
        name="ORVD",
        bus=bus,
        topic=OrvdTopics.ORVD_COMPONENT,
    )
    zones = NoFlyZonesComponent(
        component_id="noflyzones_component",
        name="NoFlyZones",
        bus=bus,
        topic=NoFlyZonesTopics.NOFLYZONES_COMPONENT,
    )
    gateway = OrvdGateway(system_id="orvd_gateway", bus=bus)

    orvd.start()
    zones.start()
    gateway.start()

    yield bus, orvd, zones, gateway

    gateway.stop()
    zones.stop()
    orvd.stop()


def request_gateway(bus, action, payload=None):
    response = bus.request(
        SystemTopics.ORVD_SYSTEM,
        {
            "action": action,
            "sender": "test_client",
            "payload": payload or {},
        },
    )
    assert response is not None
    assert response["success"] is True
    return response["payload"]


def test_orvd_full_lifecycle_via_gateway(running_system):
    bus, _, _, _ = running_system

    assert request_gateway(
        bus,
        GatewayActions.REGISTER_DRONE,
        {"drone_id": "D1"},
    )["status"] == "registered"

    assert request_gateway(
        bus,
        GatewayActions.REGISTER_MISSION,
        {"mission_id": "M1", "drone_id": "D1", "route": []},
    )["status"] == "mission_registered"

    assert request_gateway(
        bus,
        GatewayActions.AUTHORIZE_MISSION,
        {"mission_id": "M1"},
    )["status"] == "authorized"

    assert request_gateway(
        bus,
        GatewayActions.REQUEST_TAKEOFF,
        {"drone_id": "D1", "mission_id": "M1"},
    )["status"] == "takeoff_authorized"


def test_mission_rejected_when_route_crosses_nofly_zone(running_system):
    bus, _, _, _ = running_system

    request_gateway(bus, GatewayActions.REGISTER_DRONE, {"drone_id": "D1"})
    assert request_gateway(
        bus,
        GatewayActions.ADD_NO_FLY_ZONE,
        {
            "zone_id": "Z1",
            "bounds": {"min_lat": 0, "max_lat": 10, "min_lon": 0, "max_lon": 10},
        },
    )["status"] == "zone_added"

    response = request_gateway(
        bus,
        GatewayActions.REGISTER_MISSION,
        {
            "mission_id": "M1",
            "drone_id": "D1",
            "route": [{"lat": 5, "lon": 5}],
        },
    )

    assert response["status"] == "rejected"
    assert response["reason"] == "route intersects no_fly_zone"


def test_carpet_mode_blocks_takeoff_and_commands_landing(running_system):
    bus, _, _, _ = running_system

    response = request_gateway(
        bus,
        GatewayActions.ACTIVATE_CARPET_MODE,
        {
            "area_id": "A1",
            "bounds": {"min_lat": 0, "max_lat": 10, "min_lon": 0, "max_lon": 10},
        },
    )
    assert response["status"] == "carpet_activated"
    assert response["command"] == "LAND_IN_ZONE"

    point_response = request_gateway(
        bus,
        GatewayActions.CHECK_NO_FLY_POINT,
        {"coords": {"lat": 5, "lon": 5}},
    )
    assert point_response["violates"] is True
    assert point_response["command"] == "LAND"

    request_gateway(bus, GatewayActions.REGISTER_DRONE, {"drone_id": "D1"})
    mission_response = request_gateway(
        bus,
        GatewayActions.REGISTER_MISSION,
        {
            "mission_id": "M1",
            "drone_id": "D1",
            "route": [{"lat": 5, "lon": 5}],
        },
    )
    assert mission_response["status"] == "rejected"


def test_history_contains_core_events(running_system):
    bus, _, _, _ = running_system

    request_gateway(bus, GatewayActions.REGISTER_DRONE, {"drone_id": "D1"})
    request_gateway(
        bus,
        GatewayActions.REGISTER_MISSION,
        {"mission_id": "M1", "drone_id": "D1", "route": []},
    )

    response = request_gateway(bus, GatewayActions.GET_HISTORY)
    events = [entry["event"] for entry in response["history"]]

    assert "drone_registered" in events
    assert "mission_registered" in events
