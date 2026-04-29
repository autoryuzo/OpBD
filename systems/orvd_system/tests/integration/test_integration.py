"""
E2E тесты ORVD системы через реальный брокер.
Требует: make docker-up (Kafka/Mosquitto + ORVD gateway + ORVD component).
Если контейнеры не запущены — тесты пропускаются (skip).
"""

import pytest
import os
import time
import socket

from systems.orvd_system.src.gateway.topics import SystemTopics, GatewayActions
from systems.orvd_system.src.orvd_component.topics import ComponentTopics


# ==========================================================
# BROKER CHECK
# ==========================================================

def _broker_available(retries=10, delay=1):
    bt = os.environ.get("BROKER_TYPE", "kafka").lower()
    host = os.environ.get("BROKER_HOST", "localhost")
    port = int(os.environ.get("KAFKA_PORT", "9092" if bt == "kafka" else "1883"))

    for _ in range(retries):
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except Exception:
            time.sleep(delay)

    return False


@pytest.fixture(scope="function")
def system_bus():
    if not _broker_available():
        pytest.skip("Broker not available")

    from broker.bus_factory import create_system_bus

    bus = create_system_bus(client_id="test_client")
    bus.start()

    # ждём стабилизации системы
    time.sleep(5)

    yield bus

    bus.stop()


# ==========================================================
# HELPERS
# ==========================================================

def unique(prefix):
    return f"{prefix}_{int(time.time() * 1000)}"


# ==========================================================
# CORE FLOW TEST
# ==========================================================

def test_orvd_full_lifecycle(system_bus):
    drone_id = unique("DRONE")
    mission_id = unique("MISSION")

    # ---------------- REGISTER DRONE ----------------
    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REGISTER_DRONE,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {"drone_id": drone_id},
        },
        timeout=10.0,
    )

    assert resp["status"] == "registered"

    # ---------------- REGISTER MISSION ----------------
    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REGISTER_MISSION,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {
                "mission_id": mission_id,
                "drone_id": drone_id,
                "route": [],
            },
        },
        timeout=10.0,
    )

    assert resp["status"] == "mission_registered"

    # ---------------- AUTHORIZE ----------------
    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.AUTHORIZE_MISSION,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {"mission_id": mission_id},
        },
        timeout=10.0,
    )

    assert resp["status"] == "authorized"

    # ---------------- TAKEOFF ----------------
    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REQUEST_TAKEOFF,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {
                "drone_id": drone_id,
                "mission_id": mission_id,
            },
        },
        timeout=10.0,
    )

    assert resp["status"] == "takeoff_authorized"


# ==========================================================
# NEGATIVE CASES
# ==========================================================

def test_register_drone_without_id(system_bus):
    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REGISTER_DRONE,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {},
        },
        timeout=10.0,
    )

    assert resp["status"] == "error"


def test_register_mission_without_drone(system_bus):
    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REGISTER_MISSION,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {
                "mission_id": unique("MISSION"),
                "drone_id": "UNKNOWN",
                "route": [],
            },
        },
        timeout=10.0,
    )

    assert resp["status"] == "error"


def test_takeoff_without_authorization(system_bus):
    drone_id = unique("DRONE")
    mission_id = unique("MISSION")

    system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REGISTER_DRONE,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {"drone_id": drone_id},
        },
        timeout=10.0,
    )

    system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REGISTER_MISSION,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {
                "mission_id": mission_id,
                "drone_id": drone_id,
                "route": [],
            },
        },
        timeout=10.0,
    )

    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.REQUEST_TAKEOFF,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {
                "drone_id": drone_id,
                "mission_id": mission_id,
            },
        },
        timeout=10.0,
    )

    assert resp["status"] == "takeoff_denied"


# ==========================================================
# HISTORY CHECK
# ==========================================================

def test_history_contains_events(system_bus):
    resp = system_bus.request(
        ComponentTopics.ORVD_COMPONENT,
        {
            "action": GatewayActions.GET_HISTORY,
            "sender": SystemTopics.ORVD_SYSTEM,
            "payload": {},
        },
        timeout=10.0,
    )

    assert "history" in resp

    events = [e["event"] for e in resp["history"]]

    # базовые события системы
    assert "drone_registered" in events
    assert "mission_registered" in events