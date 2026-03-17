"""
OrvdGateway - внешний API ORVD.

Совместим с Agrodron API:
Топик: v1.ORVD.ORVD001.main
Action: request_departure
"""

from typing import Optional, Dict, Any

from sdk.base_gateway import BaseGateway
from broker.system_bus import SystemBus

from systems.orvd_system.src.gateway.topics import (
    SystemTopics,
    ComponentTopics,
    GatewayActions,
)


class OrvdGateway(BaseGateway):

    ACTION_ROUTING = {
        # внутренние действия
        GatewayActions.REGISTER_DRONE: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.REGISTER_MISSION: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.AUTHORIZE_MISSION: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.REQUEST_TAKEOFF: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.REVOKE_TAKEOFF: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.SEND_TELEMETRY: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.UPDATE_NO_FLY_ZONE: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.GET_HISTORY: ComponentTopics.ORVD_COMPONENT,
    }

    PROXY_TIMEOUT = 10.0

    def __init__(
        self,
        system_id: str,
        bus: SystemBus,
        health_port: Optional[int] = None,
    ):
        super().__init__(
            system_id=system_id,
            system_type="orvd_system",
            topic=SystemTopics.ORVD_EXTERNAL,  # слушаем внешний топик
            bus=bus,
            health_port=health_port,
        )

    # --------------------------------------------------------
    # ВНЕШНИЙ КОНТРАКТ AGRODRON
    # --------------------------------------------------------

    def _handle_request_departure(
        self,
        payload: Dict[str, Any],
        sender: str,
    ) -> Dict[str, Any]:
        """
        Обрабатывает request_departure от дрона.
        Преобразует во внутренний request_takeoff.
        """

        mission_id = payload.get("mission_id")

        if not mission_id:
            return {"approved": False, "reason": "invalid_payload"}

        # проксируем во внутренний компонент
        internal_response = self.proxy_request(
            topic=ComponentTopics.ORVD_COMPONENT,
            action=GatewayActions.REQUEST_TAKEOFF,
            payload={"mission_id": mission_id},
            timeout=self.PROXY_TIMEOUT,
        )

        # Преобразуем формат ответа
        if not internal_response:
            return {"approved": False, "reason": "orvd_unavailable"}

        status = internal_response.get("status")

        if status == "takeoff_authorized":
            return {"approved": True}

        if status == "takeoff_denied":
            return {
                "approved": False,
                "reason": internal_response.get("reason", "airspace_restricted"),
            }

        return {"approved": False, "reason": "unknown_error"}

    # --------------------------------------------------------

    def register_handlers(self):
        super().register_handlers()

        # регистрируем внешний action
        self.register_handler(
            GatewayActions.REQUEST_DEPARTURE,
            self._handle_request_departure,
        )