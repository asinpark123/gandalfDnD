import json
import uuid
from pathlib import Path
from typing import Any

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from alembic import command
from app.api import app
from app.db import get_engine
from app.llm.factory import get_turn_interpreter, get_turn_narrator
from app.schemas import TurnNarrationOutput
from app.turn_interpretation import NarrativeIntent


def _finalize_payload(*, alternate: bool = False) -> dict[str, Any]:
    abilities = {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 8,
        "wisdom": 10,
        "charisma": 12,
    }
    if alternate:
        abilities = {
            "strength": 8,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 15,
        }
    return {
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "species_definition_key": "srd-5.2.1:species.human",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "class_definition_key": "srd-5.2.1:class.fighter",
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "size": "medium",
        "alignment": "NG",
        "languages": ["dwarvish", "elvish"],
        "base_ability_scores": abilities,
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


def _ready_world(client: TestClient) -> tuple[str, list[str], list[str]]:
    campaign = client.post(
        "/campaigns",
        json={
            "name": "M3 World Presence",
            "starting_location": "Lantern Hall",
            "starting_scene": {
                "title": "A Rainy Arrival",
                "summary": "Rain drums on the inn roof.",
                "npcs": [
                    {"name": "Mira", "public_description": "A watchful innkeeper."},
                    {"name": "Mira", "public_description": "A weary caravan guard."},
                ],
            },
        },
    )
    assert campaign.status_code == 201, campaign.text
    campaign_id = campaign.json()["id"]
    character_ids: list[str] = []
    for index, name in enumerate(("Arin", "Bryn")):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201
        character_id = draft.json()["id"]
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{character_id}/finalize",
            json=_finalize_payload(alternate=index == 1),
        )
        assert finalized.status_code == 200, finalized.text
        character_ids.append(character_id)
    world = client.get(f"/campaigns/{campaign_id}/world")
    assert world.status_code == 200
    return campaign_id, character_ids, [npc["id"] for npc in world.json()["present_npcs"]]


def _create_turn(
    client: TestClient,
    campaign_id: str,
    actor_id: str,
    *,
    target_npc_id: str | None,
    action: str = "Arin greets Mira.",
) -> Any:
    return client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": str(uuid.uuid4()),
            "action": action,
            "actor_character_id": actor_id,
            "target_npc_id": target_npc_id,
        },
    )


def test_starting_world_is_player_safe_durable_and_supports_duplicate_names(
    client: TestClient,
) -> None:
    campaign_id, _characters, npc_ids = _ready_world(client)
    world = client.get(f"/campaigns/{campaign_id}/world")
    assert world.status_code == 200
    body = world.json()
    assert body["world_revision"] == 0
    assert body["location"]["name"] == "Lantern Hall"
    assert body["scene"]["title"] == "A Rainy Arrival"
    assert [npc["name"] for npc in body["present_npcs"]] == ["Mira", "Mira"]
    assert len(set(npc_ids)) == 2
    assert all("visibility" not in npc for npc in body["present_npcs"])

    get_engine().dispose()
    restarted = client.get(f"/campaigns/{campaign_id}/world")
    assert restarted.status_code == 200
    assert [npc["id"] for npc in restarted.json()["present_npcs"]] == npc_ids


def test_target_is_validated_before_provider_and_included_in_context(
    client: TestClient,
) -> None:
    campaign_id, characters, npc_ids = _ready_world(client)
    captured: dict[str, Any] = {}

    class CapturingInterpreter:
        provider_name = "capture"
        model_name = None
        interpretation_prompt_version = "capture-1"

        def interpret_action(self, context: dict[str, Any], player_action: str) -> NarrativeIntent:
            captured.update(context)
            return NarrativeIntent(type="narrative", summary="A direct conversation begins.")

    app.dependency_overrides[get_turn_interpreter] = lambda: CapturingInterpreter()
    created = _create_turn(client, campaign_id, characters[0], target_npc_id=npc_ids[1])
    assert created.status_code == 201, created.text
    assert created.json()["target_npc_id"] == npc_ids[1]
    assert created.json()["world_revision_before"] == 0
    repeated = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": created.json()["command_id"],
            "action": "Arin greets Mira.",
            "actor_character_id": characters[0],
            "target_npc_id": npc_ids[1],
        },
    )
    assert repeated.status_code == 201
    assert repeated.json()["id"] == created.json()["id"]
    changed_target = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": created.json()["command_id"],
            "action": "Arin greets Mira.",
            "actor_character_id": characters[0],
            "target_npc_id": npc_ids[0],
        },
    )
    assert changed_target.status_code == 409
    interpreted = client.post(
        f"/campaigns/{campaign_id}/turn-executions/{created.json()['id']}/interpret"
    )
    assert interpreted.status_code == 200, interpreted.text
    assert captured["world"]["selected_target"]["id"] == npc_ids[1]
    assert [npc["id"] for npc in captured["world"]["present_npcs"]] == npc_ids
    assert len(json.dumps(captured)) < 20_000
    cancelled = client.post(
        f"/campaigns/{campaign_id}/turn-executions/{created.json()['id']}/cancel"
    )
    assert cancelled.status_code == 200

    other = client.post(
        "/campaigns",
        json={
            "name": "Other World",
            "starting_scene": {"title": "Elsewhere", "npcs": [{"name": "Outsider"}]},
        },
    )
    assert other.status_code == 201
    other_world = client.get(f"/campaigns/{other.json()['id']}/world").json()
    cross_campaign = _create_turn(
        client,
        campaign_id,
        characters[0],
        target_npc_id=other_world["present_npcs"][0]["id"],
    )
    assert cross_campaign.status_code == 404

    with get_engine().begin() as connection:
        connection.execute(
            text("UPDATE npcs SET visibility = 'dm_only' WHERE id = :npc_id"),
            {"npc_id": uuid.UUID(npc_ids[0])},
        )
        connection.execute(
            text(
                "UPDATE campaigns SET world_revision = world_revision + 1 WHERE id = :campaign_id"
            ),
            {"campaign_id": uuid.UUID(campaign_id)},
        )
    hidden = _create_turn(client, campaign_id, characters[0], target_npc_id=npc_ids[0])
    assert hidden.status_code == 409
    assert hidden.json()["detail"] == "Target NPC is not player-visible"
    with get_engine().begin() as connection:
        connection.execute(
            text("UPDATE npcs SET visibility = 'player', status = 'inactive' WHERE id = :npc_id"),
            {"npc_id": uuid.UUID(npc_ids[0])},
        )
    inactive = _create_turn(client, campaign_id, characters[0], target_npc_id=npc_ids[0])
    assert inactive.status_code == 409
    assert inactive.json()["detail"] == "Target NPC is not active"


def test_movement_closes_scene_removes_presence_and_advances_world_revision(
    client: TestClient,
) -> None:
    campaign_id, characters, npc_ids = _ready_world(client)
    created = _create_turn(
        client,
        campaign_id,
        characters[0],
        target_npc_id=npc_ids[0],
        action="Arin travels to the Old Tower.",
    )
    assert created.status_code == 201
    turn_id = created.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200
    finalized = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert finalized.status_code == 200, finalized.text
    assert finalized.json()["turn"]["world_revision_after"] == 1

    world = client.get(f"/campaigns/{campaign_id}/world").json()
    assert world["world_revision"] == 1
    assert world["location"]["name"] == "Old Tower"
    assert world["scene"]["sequence"] == 2
    assert world["present_npcs"] == []

    absent = _create_turn(client, campaign_id, characters[0], target_npc_id=npc_ids[0])
    assert absent.status_code == 409
    assert absent.json()["detail"] == "Target NPC is not present in the current scene"


def test_world_change_during_interpretation_fails_without_using_stale_output(
    client: TestClient,
) -> None:
    campaign_id, characters, npc_ids = _ready_world(client)

    class MutatingInterpreter:
        provider_name = "world-mutator"
        model_name = None
        interpretation_prompt_version = "world-mutator-1"

        def interpret_action(self, context: dict[str, Any], player_action: str) -> NarrativeIntent:
            with get_engine().begin() as connection:
                connection.execute(
                    text(
                        "UPDATE campaigns SET world_revision = world_revision + 1 "
                        "WHERE id = :campaign_id"
                    ),
                    {"campaign_id": uuid.UUID(campaign_id)},
                )
            return NarrativeIntent(type="narrative", summary="This output must be rejected.")

    app.dependency_overrides[get_turn_interpreter] = lambda: MutatingInterpreter()
    created = _create_turn(client, campaign_id, characters[0], target_npc_id=npc_ids[0])
    assert created.status_code == 201
    turn_id = created.json()["id"]
    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert response.status_code == 409
    stored = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert stored["status"] == "failed"
    assert stored["error_code"] == "stale_world_state"
    assert stored["resumable"] is False


def test_world_change_during_narration_fails_without_applying_output(
    client: TestClient,
) -> None:
    campaign_id, characters, npc_ids = _ready_world(client)
    created = _create_turn(client, campaign_id, characters[0], target_npc_id=npc_ids[0])
    assert created.status_code == 201
    turn_id = created.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200

    class MutatingNarrator:
        provider_name = "world-mutator"
        model_name = None
        narration_prompt_version = "world-mutator-1"

        def narrate_outcome(self, *args: Any) -> TurnNarrationOutput:
            with get_engine().begin() as connection:
                connection.execute(
                    text(
                        "UPDATE campaigns SET world_revision = world_revision + 1 "
                        "WHERE id = :campaign_id"
                    ),
                    {"campaign_id": uuid.UUID(campaign_id)},
                )
            return TurnNarrationOutput(narration="This stale narration must not be applied.")

    app.dependency_overrides[get_turn_narrator] = lambda: MutatingNarrator()
    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 409
    stored = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert stored["status"] == "failed"
    assert stored["error_code"] == "stale_world_state"
    assert stored["structured_output"] is None


def test_migration_backfills_default_scene_and_blocks_world_data_loss(
    client: TestClient,
) -> None:
    default = client.post("/campaigns", json={"name": "Migration Backfill"})
    assert default.status_code == 201
    campaign_id = default.json()["id"]
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.downgrade(config, "0007_turn_stage_recovery")
    command.upgrade(config, "head")
    get_engine().dispose()
    world = client.get(f"/campaigns/{campaign_id}/world")
    assert world.status_code == 200
    assert world.json()["scene"]["title"] == "Roadside Inn"
    assert world.json()["present_npcs"] == []

    with get_engine().begin() as connection:
        npc_id = uuid.uuid4()
        connection.execute(
            text(
                "INSERT INTO npcs "
                "(id, campaign_id, name, status, visibility, revision) "
                "VALUES (:id, :campaign_id, 'Guard', 'active', 'player', 0)"
            ),
            {"id": npc_id, "campaign_id": uuid.UUID(campaign_id)},
        )
    get_engine().dispose()
    with pytest.raises(DBAPIError, match="Cannot downgrade after M3 world data"):
        command.downgrade(config, "0007_turn_stage_recovery")
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
            "0010_quests_decisions"
        )
