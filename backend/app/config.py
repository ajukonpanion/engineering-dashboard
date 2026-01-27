# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Host/port for the local hub UI
    host: str = "0.0.0.0"
    port: int = 8000

    # Hub identity (unique per hub)
    hub_id: str = "HUB-PI-001"

    # Ring buffer sizes (per device per stream)
    max_samples: int = 1200  # e.g., 20 minutes at 1Hz

    # Optional: require a shared secret for device POSTs (recommended later)
    ingest_token: str = ""   # if empty, no auth on ingest endpoints

    # Optional: enable sqlite logging later
    enable_sqlite: bool = False
    sqlite_path: str = "./hub_telemetry.sqlite"

    # Auth / access control
    session_secret: str = "CHANGE_ME_IN_PROD"   # set via env in real deployments
    users_file: str = "./users.json"            # allow-list stored on hub

    model_config = SettingsConfigDict(env_prefix="KONPANION_", env_file=".env")

settings = Settings()
