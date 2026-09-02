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
from app.dice import DiceService, get_dice_service


class FixedRandom:
    algorithm_version = "fixed-sequence-1.0.0"

    def __init__(self, results: list[int]) -> None:
        self._results = iter(results)

    def randint(self, start: int, end: int) -> int:
        value = next(self._results)
        assert start <= value <= end
        return value


def _fixed_dice(results: list[int]) -> None:
    app.dependency_overrides[get_dice_service] = lambda: DiceService(FixedRandom(results))


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


def _ready_party(client: TestClient) -> tuple[str, str, str]:
    campaign = client.post("/campaigns", json={"name": "Resolution Test"})
    assert campaign.status_code == 201, campaign.text
    campaign_id = campaign.json()["id"]
    character_ids: list[str] = []
    for index, name in enumerate(("Arin", "Bryn")):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201, draft.text
        character_id = draft.json()["id"]
        character_ids.append(character_id)
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{character_id}/finalize",
            json=_finalize_payload(alternate=index == 1),
        )
        assert finalized.status_code == 200, finalized.text
    return campaign_id, character_ids[0], character_ids[1]


def _resolution_command(
    actor_character_id: str,
    *,
    command_id: str | None = None,
    resolution_type: str = "ability_check",
    ability: str = "strength",
    skill: str | None = "athletics",
    difficulty_class: int = 15,
    advantage_reasons: list[str] | None = None,
    disadvantage_reasons: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "command_id": command_id or str(uuid.uuid4()),
        "actor_character_id": actor_character_id,
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": resolution_type,
        "ability": ability,
        "skill": skill,
        "difficulty_class": difficulty_class,
        "advantage_reasons": advantage_reasons or [],
        "disadvantage_reasons": disadvantage_reasons or [],
    }


def test_authoritative_save_persists_replays_and_is_idempotent(client: TestClient) -> None:
    campaign_id, first_character_id, _second_character_id = _ready_party(client)
    command = _resolution_command(
        first_character_id,
        resolution_type="saving_throw",
        ability="strength",
        skill=None,
        difficulty_class=13,
    )
    _fixed_dice([8])
    response = client.post(f"/campaigns/{campaign_id}/resolutions", json=command)
    assert response.status_code == 201, response.text
    resolution = response.json()
    assert resolution["actor_character_id"] == first_character_id
    assert resolution["modifier"] == 5
    assert [component["value"] for component in resolution["modifier_components"]] == [3, 2]
    assert resolution["dice_faces"] == [8]
    assert resolution["selected_die"] == 8
    assert resolution["total"] == 13
    assert resolution["outcome"] == "success"
    assert resolution["rng_version"] == "fixed-sequence-1.0.0"
    assert resolution["resolver_version"] == "check-save-resolution-1.0.0"
    assert resolution["ruleset_data_catalog_id"] == ("srd-5.2.1-check-save-resolution-v1")
    assert set(resolution["rule_definition_keys"]) >= {
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.saving_throw",
        "srd-5.2.1:rule.difficulty_class",
    }
    assert resolution["source_ids"] == ["srd-check-save-resolution"]
    assert all(
        component["provenance"]["definition_keys"]
        for component in resolution["modifier_components"]
    )
    assert all(
        component["provenance"]["acquisition_event_ids"]
        for component in resolution["modifier_components"]
    )

    _fixed_dice([1])
    duplicate = client.post(f"/campaigns/{campaign_id}/resolutions", json=command)
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == resolution["id"]
    assert duplicate.json()["dice_faces"] == [8]
    listed = client.get(f"/campaigns/{campaign_id}/resolutions")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [resolution["id"]]

    changed = {**command, "difficulty_class": 14}
    reused = client.post(f"/campaigns/{campaign_id}/resolutions", json=changed)
    assert reused.status_code == 409
    assert reused.json()["detail"] == (
        "command_id was already used for a different resolution command"
    )

    get_engine().dispose()
    replay = client.post(f"/campaigns/{campaign_id}/resolutions/{resolution['id']}/replay")
    assert replay.status_code == 200, replay.text
    assert replay.json()["equivalent"] is True
    assert replay.json()["replayed"]["total"] == 13

    events = client.get(f"/campaigns/{campaign_id}/events")
    assert events.status_code == 200
    rule_events = [event for event in events.json() if event["event_type"] == "rule_resolved"]
    assert len(rule_events) == 1
    assert rule_events[0]["actor_character_id"] == first_character_id
    assert rule_events[0]["payload"]["resolution_id"] == resolution["id"]


def test_contextual_skill_and_advantage_cancellation_use_canonical_state(
    client: TestClient,
) -> None:
    campaign_id, first_character_id, second_character_id = _ready_party(client)

    _fixed_dice([18, 3])
    stealth = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(
            first_character_id,
            ability="dexterity",
            skill="stealth",
            difficulty_class=10,
        ),
    )
    assert stealth.status_code == 201, stealth.text
    assert stealth.json()["advantage_state"] == "disadvantage"
    assert stealth.json()["dice_notation"] == "2d20"
    assert stealth.json()["selected_die"] == 3
    assert stealth.json()["modifier"] == 2
    assert stealth.json()["total"] == 5
    assert stealth.json()["disadvantage_sources"] == [
        {
            "definition_key": "srd-5.2.1:equipment.chain_mail",
            "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
            "source_ids": ["srd-equipment-state"],
            "automatic": True,
        }
    ]

    _fixed_dice([11])
    cancelled = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(
            first_character_id,
            ability="dexterity",
            skill="stealth",
            difficulty_class=13,
            advantage_reasons=["An ally used the Help action"],
        ),
    )
    assert cancelled.status_code == 201, cancelled.text
    assert cancelled.json()["advantage_state"] == "normal"
    assert cancelled.json()["dice_faces"] == [11]
    assert cancelled.json()["total"] == 13
    assert set(cancelled.json()["rule_definition_keys"]) >= {
        "srd-5.2.1:rule.advantage",
        "srd-5.2.1:rule.disadvantage",
    }

    _fixed_dice([9])
    contextual_stealth = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(
            first_character_id,
            ability="strength",
            skill="stealth",
            difficulty_class=12,
        ),
    )
    assert contextual_stealth.status_code == 201, contextual_stealth.text
    assert contextual_stealth.json()["advantage_state"] == "normal"
    assert contextual_stealth.json()["disadvantage_sources"] == []

    _fixed_dice([7])
    contextual = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(
            first_character_id,
            ability="charisma",
            skill="athletics",
            difficulty_class=10,
        ),
    )
    assert contextual.status_code == 201, contextual.text
    assert contextual.json()["modifier"] == 3
    assert [component["value"] for component in contextual.json()["modifier_components"]] == [
        1,
        2,
    ]

    _fixed_dice([10])
    isolated = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(
            second_character_id,
            resolution_type="saving_throw",
            ability="strength",
            skill=None,
            difficulty_class=12,
        ),
    )
    assert isolated.status_code == 201, isolated.text
    assert isolated.json()["actor_character_id"] == second_character_id
    assert isolated.json()["modifier"] == 2
    assert isolated.json()["total"] == 12


def test_resolution_rejects_modifier_bad_context_and_cross_release(
    client: TestClient,
) -> None:
    campaign_id, first_character_id, _second_character_id = _ready_party(client)

    supplied_modifier = _resolution_command(first_character_id)
    supplied_modifier["modifier"] = 99
    rejected = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=supplied_modifier,
    )
    assert rejected.status_code == 422
    assert any(error["loc"][-1] == "modifier" for error in rejected.json()["detail"])

    saving_throw_skill = _resolution_command(
        first_character_id,
        resolution_type="saving_throw",
        ability="strength",
        skill="athletics",
    )
    assert (
        client.post(
            f"/campaigns/{campaign_id}/resolutions",
            json=saving_throw_skill,
        ).status_code
        == 422
    )

    _fixed_dice([10])
    unknown_skill = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(first_character_id, skill="made_up_skill"),
    )
    assert unknown_skill.status_code == 422
    assert unknown_skill.json()["detail"] == "Unknown skill for this ruleset: made_up_skill"

    wrong_release = _resolution_command(first_character_id)
    wrong_release["ruleset_release_id"] = "mock-6.0.0"
    cross_release = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=wrong_release,
    )
    assert cross_release.status_code == 409
    assert cross_release.json()["detail"] == (
        "Resolution ruleset release does not match the campaign pin"
    )


def test_checks_and_saves_do_not_treat_natural_one_or_twenty_as_automatic(
    client: TestClient,
) -> None:
    campaign_id, first_character_id, _second_character_id = _ready_party(client)

    _fixed_dice([1])
    natural_one = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(
            first_character_id,
            resolution_type="saving_throw",
            ability="strength",
            skill=None,
            difficulty_class=6,
        ),
    )
    assert natural_one.status_code == 201, natural_one.text
    assert natural_one.json()["total"] == 6
    assert natural_one.json()["outcome"] == "success"

    _fixed_dice([20])
    natural_twenty = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(
            first_character_id,
            ability="intelligence",
            skill=None,
            difficulty_class=20,
        ),
    )
    assert natural_twenty.status_code == 201, natural_twenty.text
    assert natural_twenty.json()["modifier"] == -1
    assert natural_twenty.json()["total"] == 19
    assert natural_twenty.json()["outcome"] == "failure"


def test_rule_resolution_records_are_database_immutable(client: TestClient) -> None:
    campaign_id, first_character_id, _second_character_id = _ready_party(client)
    _fixed_dice([12])
    response = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(first_character_id),
    )
    assert response.status_code == 201, response.text

    with (
        pytest.raises(DBAPIError, match="rule_resolutions is immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text("UPDATE rule_resolutions SET total = 999 WHERE id = :id"),
            {"id": response.json()["id"]},
        )


def test_migration_refuses_to_discard_recorded_resolutions(client: TestClient) -> None:
    campaign_id, first_character_id, _second_character_id = _ready_party(client)
    _fixed_dice([12])
    response = client.post(
        f"/campaigns/{campaign_id}/resolutions",
        json=_resolution_command(first_character_id),
    )
    assert response.status_code == 201, response.text

    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after rule resolutions"):
        command.downgrade(config, "0004_party_commander_state")
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
            "0008_world_presence"
        )
