import uuid
from pathlib import Path
from typing import Any

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from alembic import command
from app.db import get_engine
from app.models import ProviderCall
from app.services import mark_turn_execution_failed


def _finalize_payload() -> dict[str, Any]:
    return {
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "species_definition_key": "srd-5.2.1:species.human",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "class_definition_key": "srd-5.2.1:class.fighter",
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "size": "medium",
        "alignment": "NG",
        "languages": ["dwarvish", "elvish"],
        "base_ability_scores": {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 8,
            "wisdom": 10,
            "charisma": 12,
        },
        "background_ability_increases": {"strength": 2, "constitution": 1},
        "fighter_skills": ["perception", "survival"],
        "human_skill": "insight",
        "origin_feat_definition_key": "srd-5.2.1:feat.origin.alert",
        "skilled_feat_skills": [],
        "gaming_set": "dice",
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
            "srd-5.2.1:weapon.javelin",
            "srd-5.2.1:weapon.flail",
            "srd-5.2.1:weapon.greatsword",
        ],
        "equipment_route_id": "soldier-a+fighter-a",
    }


def _ready_campaign(client: TestClient) -> tuple[str, list[str]]:
    campaign = client.post(
        "/campaigns", json={"name": "M2 Lifecycle", "starting_location": "Crossroads"}
    )
    assert campaign.status_code == 201
    campaign_id = campaign.json()["id"]
    character_ids = []
    for name in ("Arin", "Bryn"):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201
        character_id = draft.json()["id"]
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{character_id}/finalize",
            json=_finalize_payload(),
        )
        assert finalized.status_code == 200, finalized.text
        character_ids.append(character_id)
    return campaign_id, character_ids


def _create_execution(
    client: TestClient,
    campaign_id: str,
    actor_id: str,
    *,
    command_id: str | None = None,
    action: str = "Arin checks the sealed door for traps.",
) -> tuple[str, str]:
    command_id = command_id or str(uuid.uuid4())
    response = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={"command_id": command_id, "action": action, "actor_character_id": actor_id},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"], command_id


def test_turn_execution_is_idempotent_persisted_and_auditable(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    command_id = str(uuid.uuid4())
    turn_id, _ = _create_execution(client, campaign_id, characters[0], command_id=command_id)

    retry = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": command_id,
            "action": "Arin checks the sealed door for traps.",
            "actor_character_id": characters[0],
        },
    )
    assert retry.status_code == 201
    assert retry.json()["id"] == turn_id
    assert retry.json()["status"] == "received"
    assert retry.json()["workflow_version"] == "two-stage-turn-1.0.0"
    assert retry.json()["state_revision_before"] == 1
    assert retry.json()["narration"] is None

    conflict = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": command_id,
            "action": "Arin breaks the door instead.",
            "actor_character_id": characters[0],
        },
    )
    assert conflict.status_code == 409
    assert "different turn input" in conflict.json()["detail"]

    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls")
    assert calls.status_code == 200
    assert calls.json() == []

    get_engine().dispose()
    fetched = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}")
    assert fetched.status_code == 200
    assert fetched.json()["command_id"] == command_id
    listed = client.get(f"/campaigns/{campaign_id}/turn-executions")
    assert listed.status_code == 200
    assert [turn["id"] for turn in listed.json()] == [turn_id]


def test_active_turn_blocks_other_paths_until_cancelled(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id, _ = _create_execution(client, campaign_id, characters[0])

    second = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": str(uuid.uuid4()),
            "action": "Bryn listens at the door.",
            "actor_character_id": characters[1],
        },
    )
    assert second.status_code == 409
    legacy = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "Try the old path.", "actor_character_id": characters[1]},
    )
    assert legacy.status_code == 409

    cancelled = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert cancelled.json()["completed_at"] is not None
    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/cancel").status_code == 409
    )

    next_turn, _ = _create_execution(client, campaign_id, characters[1])
    assert next_turn != turn_id
    events = client.get(f"/campaigns/{campaign_id}/events").json()
    assert [event["event_type"] for event in events[-3:]] == [
        "player_action",
        "turn_cancelled",
        "player_action",
    ]


def test_resumable_failure_restores_saved_checkpoint(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id, _ = _create_execution(client, campaign_id, characters[0])
    with Session(get_engine()) as session:
        failed = mark_turn_execution_failed(
            session,
            uuid.UUID(campaign_id),
            uuid.UUID(turn_id),
            failure_stage="interpretation",
            error_code="provider_timeout",
            error_detail="The deterministic test provider timed out",
            resume_status="received",
        )
    assert failed.status == "failed"
    assert failed.resumable is True

    resumed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
    assert resumed.status_code == 200
    body = resumed.json()
    assert body["status"] == "received"
    assert body["resumable"] is False
    assert body["resume_status"] is None
    assert body["error_code"] is None
    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume").status_code == 409
    )


def test_provider_call_records_are_immutable(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id, _ = _create_execution(client, campaign_id, characters[0])
    call_id = uuid.uuid4()
    with Session(get_engine()) as session:
        session.add(
            ProviderCall(
                id=call_id,
                campaign_id=uuid.UUID(campaign_id),
                turn_id=uuid.UUID(turn_id),
                stage="interpretation",
                attempt=1,
                provider="deterministic",
                model=None,
                prompt_version="intent-v1",
                status="succeeded",
                latency_ms=2,
                structured_output={"intent": "inspect"},
            )
        )
        session.commit()

    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls")
    assert calls.status_code == 200
    assert calls.json()[0]["structured_output"] == {"intent": "inspect"}

    with (
        get_engine().begin() as connection,
        pytest.raises(DBAPIError, match="provider_calls is immutable"),
    ):
        connection.execute(
            text("UPDATE provider_calls SET latency_ms = 3 WHERE id = :id"),
            {"id": call_id},
        )
    with (
        get_engine().begin() as connection,
        pytest.raises(DBAPIError, match="provider_calls is immutable"),
    ):
        connection.execute(text("DELETE FROM provider_calls WHERE id = :id"), {"id": call_id})


def test_m2_turn_blocks_destructive_migration_downgrade(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    _create_execution(client, campaign_id, characters[0])
    with get_engine().connect() as connection:
        expected_revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after two-stage turns"):
        command.downgrade(config, "0005_check_save_resolution")
    with get_engine().connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == expected_revision
        )
