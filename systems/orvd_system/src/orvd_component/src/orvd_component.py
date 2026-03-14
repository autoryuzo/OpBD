"""
OrvdComponent - шаблон для создания новых компонентов.

Копируй эту папку и адаптируй под свои нужды.
"""
from typing import Dict, Any

from sdk.base_component import BaseComponent
from broker.system_bus import SystemBus


class OrvdComponent(BaseComponent):

    def __init__(
        self,
        component_id: str,
        name: str,
        bus: SystemBus,
        topic: str = "components.orvd_component",
    ):
        self.name = name

        # состояние системы
        self._drones = {}
        self._missions = {}
        self._authorized = set()
        self._active_flights = {}
        self._telemetry = {}
        self._history = []

        super().__init__(
            component_id=component_id,
            component_type="orvd_component",
            topic=topic,
            bus=bus,
        )

        print(f"OrvdComponent '{name}' initialized")

    def _register_handlers(self):

        self.register_handler("register_drone", self._handle_register_drone)
        self.register_handler("register_mission", self._handle_register_mission)
        self.register_handler("authorize_mission", self._handle_authorize_mission)
        self.register_handler("request_takeoff", self._handle_request_takeoff)
        self.register_handler("revoke_takeoff", self._handle_revoke_takeoff)
        self.register_handler("send_telemetry", self._handle_send_telemetry)
        self.register_handler("get_history", self._handle_get_history)

    # Регистрация дрона
    def _handle_register_drone(self, message: Dict[str, Any]) -> Dict[str, Any]:

        payload = message.get("payload", {})
        drone_id = payload.get("drone_id")

        if not drone_id:
            return {"status": "error", "message": "drone_id required"}

        self._drones[drone_id] = payload

        self._history.append({
            "event": "drone_registered",
            "drone_id": drone_id
        })

        return {
            "status": "registered",
            "drone_id": drone_id,
            "from": self.component_id
        }

    # Регистрация миссии
    def _handle_register_mission(self, message: Dict[str, Any]) -> Dict[str, Any]:

        payload = message.get("payload", {})
        mission_id = payload.get("mission_id")
        drone_id = payload.get("drone_id")

        if not mission_id or not drone_id:
            return {"status": "error", "message": "mission_id and drone_id required"}

        if drone_id not in self._drones:
            return {"status": "error", "message": "drone not registered"}

        self._missions[mission_id] = payload

        self._history.append({
            "event": "mission_registered",
            "mission_id": mission_id,
            "drone_id": drone_id
        })

        return {
            "status": "mission_registered",
            "mission_id": mission_id,
            "from": self.component_id
        }

    # Авторизация миссии
    def _handle_authorize_mission(self, message: Dict[str, Any]) -> Dict[str, Any]:

        payload = message.get("payload", {})
        mission_id = payload.get("mission_id")

        if mission_id not in self._missions:
            return {"status": "error", "message": "mission not found"}

        self._authorized.add(mission_id)

        self._history.append({
            "event": "mission_authorized",
            "mission_id": mission_id
        })

        return {
            "status": "authorized",
            "mission_id": mission_id,
            "from": self.component_id
        }
    
    # Авторизация вылета
    def _handle_authorize_mission(self, message: Dict[str, Any]) -> Dict[str, Any]:

        payload = message.get("payload", {})
        mission_id = payload.get("mission_id")

        if mission_id not in self._missions:
            return {"status": "error", "message": "mission not found"}

        self._authorized.add(mission_id)

        self._history.append({
            "event": "mission_authorized",
            "mission_id": mission_id
        })

        return {
            "status": "authorized",
            "mission_id": mission_id,
            "from": self.component_id
        }
    
    # Отзыв разрешения / посадка
    def _handle_revoke_takeoff(self, message: Dict[str, Any]) -> Dict[str, Any]:

        payload = message.get("payload", {})
        drone_id = payload.get("drone_id")

        if drone_id not in self._active_flights:
            return {"status": "error", "message": "drone not in flight"}

        mission_id = self._active_flights.pop(drone_id)

        self._history.append({
            "event": "flight_revoked",
            "drone_id": drone_id,
            "mission_id": mission_id
        })

        return {
            "status": "landing_required",
            "drone_id": drone_id,
            "from": self.component_id
        }

    # Телеметрия
    def _handle_send_telemetry(self, message: Dict[str, Any]) -> Dict[str, Any]:

        payload = message.get("payload", {})
        drone_id = payload.get("drone_id")

        if not drone_id:
            return {"status": "error", "message": "drone_id required"}

        self._telemetry[drone_id] = payload

        return {
            "status": "telemetry_received",
            "from": self.component_id
        }
    
    # История событий
    def _handle_get_history(self, message: Dict[str, Any]) -> Dict[str, Any]:

        return {
            "history": self._history,
            "from": self.component_id
        }