from kafka import KafkaProducer
import json
from app.core.config import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_telemetry(data: dict):
    producer.send(settings.KAFKA_TOPIC_TELEMETRY, value=data)
    producer.flush()

def send_event(data: dict):
    producer.send(settings.KAFKA_TOPIC_EVENTS, value=data)
    producer.flush()