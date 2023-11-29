"""Hook configuration."""

from functools import lru_cache

from pydantic import AnyUrl, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Hook settings."""

    model_config = SettingsConfigDict(env_prefix="HOOK_")

    moodle_url: HttpUrl = "http://moodle"
    moodle_webservice_token: str = "32323232323232323232323232323232"

    kafka_topic: str = "statements"
    kafka_bootstrap_servers: str = "kafka:9092"

    spark_master_url: AnyUrl = "spark://spark-master:7077"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
