"""Settings read from environment variables (and the .env file in the project root)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = the folder that contains backend/ and .env
ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    # No real defaults for the database: the address must come from .env
    database_url: str = ""
    test_database_url: str = ""
    base_url: str = "http://localhost:8000"
    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    """Create the settings once and reuse them."""
    return Settings()
