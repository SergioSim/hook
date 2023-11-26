"""Swarmoodle configuration."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from annotated_types import Ge, Gt
from pydantic import (
    AliasChoices,
    Field,
    HttpUrl,
    RedisDsn,
    StringConstraints,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Swarmoodle settings."""

    model_config = SettingsConfigDict(env_prefix="SWARMOODLE_")

    hook_url: HttpUrl = "http://hook:8000/"

    logging: dict = {
        "version": 1,
        "formatters": {
            "swarmoodle": {
                "format": "%(asctime)-23s %(levelname)-8s %(name)-8s %(message)s"
            },
            "plain": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "stream": "ext://sys.stderr",
                "formatter": "swarmoodle",
            },
            "console_plain": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
            },
        },
        "loggers": {
            "swarmoodle": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "locust": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "locust.stats_logger": {
                "handlers": ["console_plain"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }

    moodle_course_id: Annotated[int, Gt(0)] = 2
    moodle_delete_users_after_run: bool = False
    moodle_url: HttpUrl = Field(
        "http://moodle", alias=AliasChoices("SWARMOODLE_MOODLE_URL", "LOCUST_HOST")
    )
    moodle_students: Annotated[int, Gt(0)] = Field(
        1, alias=AliasChoices("SWARMOODLE_MOODLE_STUDENTS", "LOCUST_USERS")
    )
    moodle_student_password: Annotated[
        str, StringConstraints(min_length=8)
    ] = "Passwd1!"
    moodle_student_role_id: Annotated[int, Gt(0)] = 5
    moodle_webservices_token: str = "32323232323232323232323232323232"

    oulad_code_module: Literal["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"] = "AAA"
    oulad_code_presentation: Literal["2013B", "2013J", "2014J", "2014B"] = "2013J"
    oulad_default_path: Path = Path("/app/data/OULAD")

    redis_dsn: RedisDsn = "redis://redis:6379"

    request_timeout: Annotated[int, Ge(0)] = 400
    request_milliseconds_duration: Annotated[int, Ge(0)] = 400
    simulate_fixed_day_duration: bool = False

    @computed_field
    @property
    def moodle_ws_url(self) -> HttpUrl:
        """Return the Moodle webservices endpoint URL."""
        self.moodle_url: HttpUrl
        return self.moodle_url.build(
            scheme=self.moodle_url.scheme,
            host=self.moodle_url.host,
            port=self.moodle_url.port,
            path="webservice/rest/server.php",
        )

    @model_validator(mode="after")
    def check_oulad_course_module_presentation(self) -> "Settings":
        """Check that a valid combination of OULAD module/presentation is used."""
        module_presentations = {
            "AAA": {"2013J", "2014J"},
            "BBB": {"2013B", "2013J", "2014B", "2014J"},
            "CCC": {"2014B", "2014J"},
            "DDD": {"2013B", "2013J", "2014B", "2014J"},
            "EEE": {"2013J", "2014B", "2014J"},
            "FFF": {"2013B", "2013J", "2014B", "2014J"},
            "GGG": {"2013J", "2014B", "2014J"},
        }
        allowed_presentations = module_presentations.get(self.oulad_code_module, set())
        if self.oulad_code_presentation not in allowed_presentations:
            raise ValueError(
                f"invalid oulad_code_module/oulad_code_presentation combination: "
                f"for code_module: {self.oulad_code_module} the code_presentation "
                f"should be one of: {sorted(allowed_presentations)}"
            )

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
