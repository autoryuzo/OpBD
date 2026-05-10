"""Entry point for noflyzones_component."""
import os
import signal
import sys
import time

from broker.bus_factory import create_system_bus
try:
    from systems.orvd_system.src.noflyzones_component.src.noflyzones_component import (
        NoFlyZonesComponent,
    )
    from systems.orvd_system.src.noflyzones_component.topics import ComponentTopics
except ModuleNotFoundError:
    from src.noflyzones_component.src.noflyzones_component import NoFlyZonesComponent
    from src.noflyzones_component.topics import ComponentTopics


def main():
    component_id = os.environ.get("COMPONENT_ID", "noflyzones_component")
    name = os.environ.get("COMPONENT_NAME", component_id.replace("_", " ").title())

    bus = create_system_bus(client_id=component_id)
    component = NoFlyZonesComponent(
        component_id=component_id,
        name=name,
        bus=bus,
        topic=ComponentTopics.NOFLYZONES_COMPONENT,
    )
    component.start()

    print(f"[{component_id}] Running. Press Ctrl+C to stop.")

    def signal_handler(sig, frame):
        print(f"\n[{component_id}] Received signal {sig}, shutting down...")
        component.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while component._running:
            signal.pause()
    except AttributeError:
        while component._running:
            time.sleep(1)


if __name__ == "__main__":
    main()
