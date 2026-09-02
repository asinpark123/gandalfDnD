from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GANDALF_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str
    llm_provider: Literal["deterministic", "openai"] = "deterministic"
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.4"
    turn_stage_timeout_seconds: int = Field(default=120, ge=1, le=3600)
    ruleset_registry_path: Path = Path("rulesets/registry.json")
    ruleset_cache_dir: Path = Path(".cache/rulesets")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
