import hashlib
import io
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from alembic import command
from app.db import get_engine
from app.models import Campaign, RulesetDataCatalog, RulesetRelease
from app.rulesets import (
    ArtifactIntegrityError,
    LoadedRulesetRelease,
    NormalizedDataIndex,
    RulesetManifest,
    RulesetRegistry,
    RulesetRegistryError,
    fetch_ruleset_artifact,
)

REPOSITORY_ROOT = Path(__file__).parents[1]


def _alembic_config() -> Config:
    return Config(str(REPOSITORY_ROOT / "alembic.ini"))


def test_checked_in_registry_and_generated_schemas_are_valid() -> None:
    registry = RulesetRegistry.load(REPOSITORY_ROOT / "rulesets/registry.json")

    assert registry.default_release_id == "srd-5.2.1"
    assert registry.release_ids == ("srd-5.2.1",)
    release = registry.get("srd-5.2.1")
    assert release.manifest.artifact.sha256 == (
        "8974902d109d6e63672d7c490bde9ccf052410503d9cfa768237154fbc5e3d87"
    )
    assert release.manifest.artifact.size_bytes == 6031375
    assert release.data_index.definition_files == []
    assert release.data_index.support_status == "foundation_only"
    assert release.default_data_catalog_id == "srd-5.2.1-party-state-v1"
    character_catalog = registry.get_data_catalog("srd-5.2.1")
    assert character_catalog.kind == "character_state"
    assert character_catalog.sha256 == (
        "aba4fcdbffb037eece88c862c76be988ffc60808b46361cc9a9dda0730fe763b"
    )
    resolution_catalog = registry.get_data_catalog(
        "srd-5.2.1", "srd-5.2.1-check-save-resolution-v1"
    )
    assert resolution_catalog.kind == "rules_resolution"
    assert resolution_catalog.sha256 == (
        "09d2b0a963a5fba5c28a0a018b8114bcad25dd65717efcf5e1b791cc4f751448"
    )
    combat_catalog = registry.get_data_catalog("srd-5.2.1", "srd-5.2.1-combat-v1")
    assert combat_catalog.kind == "combat"
    assert combat_catalog.sha256 == (
        "423b80e84593738d4cadc5537278d208a51fbebacbb074a2d79531f0ee023204"
    )
    composed = registry.get_combat_catalogs(
        "srd-5.2.1",
        "srd-5.2.1-party-state-v1",
        "srd-5.2.1-combat-v1",
    )
    assert composed.character_creation.id == "srd-5.2.1-character-creation-v1"
    assert composed.character_state.id == "srd-5.2.1-party-state-v1"
    assert composed.combat.id == "srd-5.2.1-combat-v1"

    result = subprocess.run(
        [sys.executable, "-m", "scripts.export_ruleset_schemas", "--check"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _small_release(data: bytes = b"immutable rules") -> LoadedRulesetRelease:
    sha256 = hashlib.sha256(data).hexdigest()
    manifest = RulesetManifest.model_validate(
        {
            "schema_version": "1.0.0",
            "id": "test-1.0.0",
            "title": "Test Rules",
            "version": "1.0.0",
            "publication_date": "2026-08-30",
            "source_page": "https://example.com/rules",
            "license": {
                "id": "CC-BY-4.0",
                "name": "Creative Commons Attribution 4.0 International",
                "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
                "attribution_file": "ATTRIBUTION.md",
            },
            "artifact": {
                "filename": "rules.pdf",
                "media_type": "application/pdf",
                "sha256": sha256,
                "size_bytes": len(data),
                "sources": [{"name": "official", "url": "https://example.com/rules.pdf"}],
            },
            "normalized_data": {
                "schema_version": "1.0.0",
                "index_path": "data/index.json",
                "support_status": "foundation_only",
            },
        }
    )
    return LoadedRulesetRelease(
        manifest=manifest,
        manifest_path=Path("manifest.json"),
        manifest_sha256="0" * 64,
        data_index=NormalizedDataIndex(
            schema_version="1.0.0",
            data_catalog_id="test-1.0.0-foundation-v1",
            ruleset_release_id="test-1.0.0",
            support_status="foundation_only",
            definition_files=[],
        ),
        default_data_catalog_id="test-1.0.0-foundation-v1",
        data_catalogs={},
    )


def test_fetch_artifact_is_atomic_and_checksum_verified(tmp_path: Path) -> None:
    data = b"immutable rules"
    release = _small_release(data)
    fetched = fetch_ruleset_artifact(
        release,
        tmp_path,
        opener=lambda _url: io.BytesIO(data),
    )
    assert fetched.read_bytes() == data

    cached = fetch_ruleset_artifact(
        release,
        tmp_path,
        opener=lambda _url: pytest.fail("valid cache should not download again"),
    )
    assert cached == fetched


def test_fetch_rejects_bad_download_and_corrupt_cache(tmp_path: Path) -> None:
    release = _small_release()
    with pytest.raises(ArtifactIntegrityError, match="did not match"):
        fetch_ruleset_artifact(
            release,
            tmp_path,
            opener=lambda _url: io.BytesIO(b"wrong"),
        )
    target = tmp_path / "test-1.0.0/rules.pdf"
    assert not target.exists()

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"corrupt")
    with pytest.raises(ArtifactIntegrityError, match="Cached artifact"):
        fetch_ruleset_artifact(release, tmp_path)
    assert target.read_bytes() == b"corrupt"


def _registry_with_mock_release(tmp_path: Path) -> RulesetRegistry:
    rulesets = tmp_path / "rulesets"
    shutil.copytree(REPOSITORY_ROOT / "rulesets", rulesets)
    manifest_path = rulesets / "srd-5.2.1/manifest.json"
    mock_dir = rulesets / "mock-6.0.0"
    (mock_dir / "data").mkdir(parents=True)
    manifest = json.loads(manifest_path.read_text())
    manifest["id"] = "mock-6.0.0"
    manifest["title"] = "Mock Ruleset 6.0.0"
    manifest["version"] = "6.0.0"
    manifest["normalized_data"]["index_path"] = "data/index.json"
    (mock_dir / "manifest.json").write_text(json.dumps(manifest))
    mock_index = json.dumps(
        {
            "schema_version": "1.0.0",
            "data_catalog_id": "mock-6.0.0-foundation-v1",
            "ruleset_release_id": "mock-6.0.0",
            "support_status": "foundation_only",
            "definition_files": [],
        }
    )
    (mock_dir / "data/index.json").write_text(mock_index)
    registry_path = rulesets / "registry.json"
    registry = json.loads(registry_path.read_text())
    registry["releases"].append(
        {
            "id": "mock-6.0.0",
            "manifest": "mock-6.0.0/manifest.json",
            "default_data_catalog_id": "mock-6.0.0-foundation-v1",
            "data_catalogs": [
                {
                    "id": "mock-6.0.0-foundation-v1",
                    "kind": "foundation",
                    "path": "data/index.json",
                    "sha256": hashlib.sha256(mock_index.encode()).hexdigest(),
                }
            ],
        }
    )
    registry_path.write_text(json.dumps(registry))
    return RulesetRegistry.load(registry_path)


def test_new_release_coexists_without_changing_existing_campaign(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = _registry_with_mock_release(tmp_path)
    monkeypatch.setattr("app.services.get_ruleset_registry", lambda: registry)

    first = client.post("/campaigns", json={"name": "Existing"})
    assert first.status_code == 201, first.text
    second = client.post(
        "/campaigns",
        json={"name": "Future", "ruleset_release_id": "mock-6.0.0"},
    )
    assert second.status_code == 201, second.text

    with get_engine().connect() as connection:
        releases = set(connection.execute(select(RulesetRelease.id)).scalars())
        existing_pin = connection.execute(
            select(Campaign.ruleset_release_id).where(Campaign.id == first.json()["id"])
        ).scalar_one()
    assert releases == {"srd-5.2.1", "mock-6.0.0"}
    assert existing_pin == "srd-5.2.1"


def test_database_ruleset_release_is_immutable(client: TestClient) -> None:
    assert client.post("/campaigns", json={"name": "Immutable"}).status_code == 201
    with (
        pytest.raises(DBAPIError, match="ruleset_releases is immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text("UPDATE ruleset_releases SET title = 'Mutated' WHERE id = 'srd-5.2.1'")
        )


def test_database_data_catalog_and_campaign_pins_are_immutable(client: TestClient) -> None:
    campaign = client.post("/campaigns", json={"name": "Pinned"})
    assert campaign.status_code == 201
    with (
        pytest.raises(DBAPIError, match="ruleset_data_catalogs is immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text(
                "UPDATE ruleset_data_catalogs SET support_status = 'complete' "
                "WHERE id = 'srd-5.2.1-character-creation-v1'"
            )
        )
    with (
        pytest.raises(DBAPIError, match="campaign ruleset and play-mode pins are immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text(
                "UPDATE campaigns SET ruleset_data_catalog_id = 'srd-5.2.1-foundation-v1' "
                "WHERE id = :id"
            ),
            {"id": campaign.json()["id"]},
        )


def test_registry_rejects_path_traversal(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "1.1.0",
                "default_release_id": "test-1.0.0",
                "releases": [
                    {
                        "id": "test-1.0.0",
                        "manifest": "../manifest.json",
                        "default_data_catalog_id": "test-1.0.0-foundation-v1",
                        "data_catalogs": [
                            {
                                "id": "test-1.0.0-foundation-v1",
                                "kind": "foundation",
                                "path": "data/index.json",
                                "sha256": "0" * 64,
                            }
                        ],
                    }
                ],
            }
        )
    )
    with pytest.raises(RulesetRegistryError, match="Invalid ruleset registry"):
        RulesetRegistry.load(registry_path)


def test_migration_backfills_legacy_mechanical_records() -> None:
    get_engine().dispose()
    command.downgrade(_alembic_config(), "0001_phase_0")
    campaign_id = uuid.uuid4()
    character_id = uuid.uuid4()
    event_id = uuid.uuid4()
    roll_id = uuid.uuid4()
    try:
        with get_engine().begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO campaigns (id, name, ruleset, status)
                    VALUES (:id, 'Legacy', 'SRD 5.2.1', 'active')
                    """
                ),
                {"id": campaign_id},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO characters (id, campaign_id, name, max_hp, hp, inventory)
                    VALUES (:id, :campaign_id, 'Arin', 10, 10, '{}'::jsonb)
                    """
                ),
                {"id": character_id, "campaign_id": campaign_id},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO campaign_events (
                        id, campaign_id, sequence, event_type, visibility, payload
                    ) VALUES (
                        :id, :campaign_id, 1, 'legacy', 'player', '{}'::jsonb
                    )
                    """
                ),
                {"id": event_id, "campaign_id": campaign_id},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO dice_rolls (
                        id, campaign_id, notation, rolls, modifier, total, purpose, hidden
                    ) VALUES (
                        :id, :campaign_id, '1d20', '[12]'::jsonb, 0, 12, 'legacy', false
                    )
                    """
                ),
                {"id": roll_id, "campaign_id": campaign_id},
            )

        command.upgrade(_alembic_config(), "head")
        with get_engine().connect() as connection:
            assert connection.execute(
                text(
                    "SELECT ruleset_release_id, legacy_ruleset_label FROM campaigns WHERE id = :id"
                ),
                {"id": campaign_id},
            ).one() == ("srd-5.2.1", "SRD 5.2.1")
            assert (
                connection.execute(
                    text("SELECT ruleset_data_catalog_id FROM campaigns WHERE id = :id"),
                    {"id": campaign_id},
                ).scalar_one()
                == "srd-5.2.1-foundation-v1"
            )
            for table, record_id in (
                ("characters", character_id),
                ("campaign_events", event_id),
                ("dice_rolls", roll_id),
            ):
                assert connection.execute(
                    text(
                        f"SELECT ruleset_release_id, ruleset_data_catalog_id "
                        f"FROM {table} WHERE id = :id"
                    ),
                    {"id": record_id},
                ).one() == ("srd-5.2.1", "srd-5.2.1-foundation-v1")
            assert connection.execute(
                select(RulesetDataCatalog.id).order_by(RulesetDataCatalog.id)
            ).scalars().all() == [
                "srd-5.2.1-character-creation-v1",
                "srd-5.2.1-check-save-resolution-v1",
                "srd-5.2.1-combat-v1",
                "srd-5.2.1-foundation-v1",
                "srd-5.2.1-party-state-v1",
            ]
    finally:
        command.upgrade(_alembic_config(), "head")


def test_migration_refuses_unmapped_legacy_ruleset_without_data_loss() -> None:
    get_engine().dispose()
    command.downgrade(_alembic_config(), "0001_phase_0")
    campaign_id = uuid.uuid4()
    try:
        with get_engine().begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO campaigns (id, name, ruleset, status)
                    VALUES (:id, 'Unknown Legacy', 'unmapped-homebrew', 'active')
                    """
                ),
                {"id": campaign_id},
            )

        with pytest.raises(DBAPIError, match="unmapped legacy campaign ruleset"):
            command.upgrade(_alembic_config(), "head")

        with get_engine().begin() as connection:
            assert (
                connection.execute(
                    text("SELECT ruleset FROM campaigns WHERE id = :id"),
                    {"id": campaign_id},
                ).scalar_one()
                == "unmapped-homebrew"
            )
            assert connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one() == ("0001_phase_0")
            connection.execute(text("DELETE FROM campaigns WHERE id = :id"), {"id": campaign_id})
    finally:
        command.upgrade(_alembic_config(), "head")
