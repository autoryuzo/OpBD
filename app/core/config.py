import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "Telemetry & Event System"

    # Postgres
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "telemetry"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Kafka
    KAFKA_BROKER: str = "kafka:9092"
    KAFKA_TOPIC_TELEMETRY: str = "telemetry"
    KAFKA_TOPIC_EVENTS: str = "events"

    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "supersecret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

settings = Settings()