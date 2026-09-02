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
    llm_provider: Literal["deterministic", "openai", "openclaw"] = "deterministic"
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.4"
    openclaw_base_url: str = "http://127.0.0.1:18789/v1"
    openclaw_gateway_token: SecretStr | None = None
    openclaw_agent_id: str = Field(default="gandalf", pattern=r"^[a-z0-9][a-z0-9_-]{1,63}$")
    openclaw_model: str | None = None
    openclaw_gm_style: Literal[
        "classic_heroic_fantasy",
        "lighthearted_adventure",
        "mystery_and_intrigue",
        "grounded_low_fantasy",
        "epic_high_fantasy",
        "dark_fantasy",
    ] = "classic_heroic_fantasy"
    turn_stage_timeout_seconds: int = Field(default=120, ge=1, le=3600)
    ruleset_registry_path: Path = Path("rulesets/registry.json")
    ruleset_cache_dir: Path = Path(".cache/rulesets")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
