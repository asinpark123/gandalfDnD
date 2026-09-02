import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from alembic import command


def _load_test_environment() -> None:
    path = Path(__file__).parents[1] / ".env.test"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key] = value


_load_test_environment()

from app.api import app  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.db import get_engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def migrated_test_database() -> Generator[None, None, None]:
    database_url = get_settings().database_url
    if not database_url.rsplit("/", 1)[-1].startswith("gandalfdnd_test"):
        raise RuntimeError("Refusing to run integration tests outside gandalfdnd_test")
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    yield


@pytest.fixture(autouse=True)
def clean_database(migrated_test_database: None) -> Generator[None, None, None]:
    with get_engine().begin() as connection:
        connection.execute(
            text(
                "TRUNCATE scene_npc_presences, npcs, scenes, "
                "provider_calls, rule_resolutions, character_grants, "
                "campaign_events, dice_rolls, "
                "turns, characters, "
                "locations, campaigns, ruleset_data_catalogs, ruleset_releases "
                "RESTART IDENTITY CASCADE"
            )
        )
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
