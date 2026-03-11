from kafka import KafkaConsumer
import json
from app.kafka.topics import DRONE_TAKEOFF_REQUEST, DRONE_TELEMETRY

consumer = KafkaConsumer(
    DRONE_TAKEOFF_REQUEST,
    DRONE_TELEMETRY,
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="ordv"
)