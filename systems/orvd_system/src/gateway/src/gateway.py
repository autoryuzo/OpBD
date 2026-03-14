"""
DummyGateway — координатор dummy_system.

Принимает запросы на топик systems.dummy_system и проксирует
к внутренним компонентам по таблице ACTION_ROUTING.
Отправитель знает только систему и action, не компоненты.
"""
from typing import Optional

from sdk.base_gateway import BaseGateway
from broker.system_bus import SystemBus

from systems.orvd_system.src.gateway.topics import (
    SystemTopics,
    ComponentTopics,
    GatewayActions,
)


class OrvdGateway(BaseGateway):

    ACTION_ROUTING = {
        GatewayActions.REGISTER_MISSION: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.AUTHORIZE_MISSION: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.REQUEST_TAKEOFF: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.FORCE_LAND: ComponentTopics.ORVD_COMPONENT,
        GatewayActions.GET_REQUESTS: ComponentTopics.ORVD_COMPONENT,
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
            topic=SystemTopics.ORVD_SYSTEM,
            bus=bus,
            health_port=health_port,
        )
