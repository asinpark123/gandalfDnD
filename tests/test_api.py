from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db import get_engine
from app.llm.factory import get_dm_provider
from app.schemas import DMTurnOutput, HPDelta, InventoryChange, MoveLocation


class StateChangingProvider:
    provider_name = "test"
    model_name = "fixed"

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput:
        return DMTurnOutput(
            narration="You climb into the stable loft, but the rotten ladder gives way.",
            state_changes=[
                MoveLocation(type="move_location", location_name="Stable Loft"),
                HPDelta(type="hp_delta", amount=-2, reason="Fell from the ladder"),
                InventoryChange(
                    type="inventory_change",
                    item_name="Javelin",
                    quantity_delta=-1,
                    reason="Dropped and extinguished",
                ),
            ],
        )


def _create_campaign(client: TestClient) -> str:
    response = client.post(
        "/campaigns",
        json={"name": "The Lantern Test", "starting_location": "Roadside Inn"},
    )
    assert response.status_code == 201
    assert response.json()["ruleset_release_id"] == "srd-5.2.1"
    assert response.json()["ruleset_data_catalog_id"] == "srd-5.2.1-party-state-v1"
    assert response.json()["play_mode"] == "party_commander"
    assert response.json()["party_min_active"] == 2
    assert response.json()["party_max_active"] == 4
    return response.json()["id"]


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


def test_health_checks_database(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "environment": "test"}


def test_guided_character_creation_persists_state_turns_and_events(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    options = client.get("/rulesets/srd-5.2.1/character-creation/options")
    assert options.status_code == 200
    assert options.json()["selected_ruleset_data_catalog_id"] == "srd-5.2.1-party-state-v1"
    assert options.json()["character_creation"]["id"] == "srd-5.2.1-character-creation-v1"
    assert len(options.json()["character_creation"]["skills"]) == 18
    assert options.json()["party"]["maximum_active_characters"] == 4

    character = client.post(
        f"/campaigns/{campaign_id}/characters",
        json={"name": "Arin"},
    )
    assert character.status_code == 201
    assert character.json()["ruleset_release_id"] == "srd-5.2.1"
    assert character.json()["creation_status"] == "draft"
    assert character.json()["max_hp"] is None
    assert character.json()["party_position"] == 1
    first_character_id = character.json()["id"]

    second = client.post(
        f"/campaigns/{campaign_id}/characters",
        json={"name": "Bryn"},
    )
    assert second.status_code == 201
    assert second.json()["party_position"] == 2
    second_character_id = second.json()["id"]

    blocked_turn = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "I leave before finishing my character."},
    )
    assert blocked_turn.status_code == 409

    finalized = client.post(
        f"/campaigns/{campaign_id}/characters/{first_character_id}/finalize",
        json=_finalize_payload(),
    )
    assert finalized.status_code == 200, finalized.text
    finalized_character = finalized.json()
    assert finalized_character["creation_status"] == "finalized"
    assert finalized_character["revision"] == 1
    assert finalized_character["hp"] == finalized_character["max_hp"] == 12
    sheet = finalized_character["character_sheet"]
    assert sheet["abilities"]["strength"] == {
        "base": 15,
        "background_increase": 2,
        "final": 17,
        "modifier": 3,
    }
    assert sheet["abilities"]["constitution"]["final"] == 14
    assert sheet["skill_proficiencies"] == [
        "athletics",
        "insight",
        "intimidation",
        "perception",
        "survival",
    ]
    assert finalized_character["inventory"]["Javelin"] == 8
    assert finalized_character["inventory"]["GP"] == 18
    mechanics = finalized_character["mechanical_state"]
    assert mechanics["saving_throws"]["strength"]["value"] == 5
    assert mechanics["saving_throws"]["constitution"]["value"] == 4
    assert mechanics["initiative"]["value"] == 4
    assert mechanics["armor_class"]["value"] == 17
    assert mechanics["passive_perception"]["value"] == 12
    assert mechanics["resources"]["second_wind"]["current"] == 2
    assert mechanics["resources"]["heroic_inspiration"]["long_rest_recovery"] == "none"
    assert mechanics["saving_throws"]["strength"]["provenance"]["acquisition_event_ids"]
    assert all(item["provenance_definition_keys"] for item in mechanics["equipment"])
    assert all(item["source_ids"] for item in mechanics["equipment"])
    assert all(item["acquisition_event_ids"] for item in mechanics["equipment"])
    equipment_by_name = {item["name"]: item for item in mechanics["equipment"]}
    assert equipment_by_name["Dice Set"]["definition_key"] == ("srd-5.2.1:tool.gaming_set.dice")
    assert set(equipment_by_name["GP"]["provenance_definition_keys"]) == {
        "srd-5.2.1:equipment_package.soldier.a",
        "srd-5.2.1:equipment_package.fighter.a",
    }

    still_blocked = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "Arin tries to leave.", "actor_character_id": first_character_id},
    )
    assert still_blocked.status_code == 409

    second_finalized = client.post(
        f"/campaigns/{campaign_id}/characters/{second_character_id}/finalize",
        json=_finalize_payload(),
    )
    assert second_finalized.status_code == 200, second_finalized.text

    grants = client.get(f"/campaigns/{campaign_id}/characters/{first_character_id}/grants")
    assert grants.status_code == 200
    assert len(grants.json()) >= 30
    assert {grant["ruleset_data_catalog_id"] for grant in grants.json()} == {
        "srd-5.2.1-party-state-v1"
    }
    assert all(grant["value"]["source_ids"] for grant in grants.json())

    from app.api import app

    app.dependency_overrides[get_dm_provider] = lambda: StateChangingProvider()
    turn = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "I climb into the loft.", "actor_character_id": first_character_id},
    )
    assert turn.status_code == 201, turn.text
    assert turn.json()["sequence"] == 1
    assert turn.json()["actor_character_id"] == first_character_id
    assert turn.json()["dice_rolls"] == []

    get_engine().dispose()
    state = client.get(f"/campaigns/{campaign_id}/state")
    assert state.status_code == 200
    payload = state.json()
    assert payload["character"] is None
    assert payload["party_ready"] is True
    assert payload["characters"][0]["hp"] == 10
    assert payload["characters"][0]["inventory"]["Javelin"] == 7
    assert payload["characters"][1]["hp"] == 12
    assert payload["characters"][1]["inventory"]["Javelin"] == 8
    assert payload["location"]["name"] == "Stable Loft"
    assert payload["turn_count"] == 1

    events = client.get(f"/campaigns/{campaign_id}/events")
    assert events.status_code == 200
    assert [event["event_type"] for event in events.json()] == [
        "campaign_created",
        "scene_opened",
        "character_draft_created",
        "character_draft_created",
        "character_finalized",
        "character_finalized",
        "player_action",
        "scene_closed",
        "scene_opened",
        "dm_response",
        "state_changed",
    ]
    assert {event["ruleset_release_id"] for event in events.json()} == {"srd-5.2.1"}
    turn_events = [
        event
        for event in events.json()
        if event["event_type"] in {"player_action", "dm_response", "state_changed"}
    ]
    assert {event["actor_character_id"] for event in turn_events} == {first_character_id}


def test_narration_alone_cannot_change_mechanical_state(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    character_ids: list[str] = []
    for name in ("Arin", "Bryn"):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201
        character_ids.append(draft.json()["id"])
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{draft.json()['id']}/finalize",
            json=_finalize_payload(),
        )
        assert finalized.status_code == 200

    before = client.get(f"/campaigns/{campaign_id}/state")
    assert before.status_code == 200
    response = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={
            "action": "Describe an ominous magical transformation without applying one.",
            "actor_character_id": character_ids[0],
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["dice_rolls"] == []
    assert response.json()["state"]["characters"] == before.json()["characters"]
    assert response.json()["state"]["location"] == before.json()["location"]

    events = client.get(f"/campaigns/{campaign_id}/events")
    assert events.status_code == 200
    event_types = [event["event_type"] for event in events.json()]
    assert event_types[-2:] == ["player_action", "dm_response"]
    assert "state_changed" not in event_types
    assert "dice_rolled" not in event_types


def test_guided_creation_rejects_duplicate_and_legacy_character_input(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    legacy = client.post(
        f"/campaigns/{campaign_id}/character",
        json={"name": "Legacy", "max_hp": 10},
    )
    assert legacy.status_code == 422

    created = []
    for name in ("Arin", "Bryn", "Cora", "Dain"):
        response = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert response.status_code == 201
        created.append(response.json())
    assert (
        client.post(f"/campaigns/{campaign_id}/characters", json={"name": "Eryn"}).status_code
        == 409
    )

    invalid = _finalize_payload()
    invalid["base_ability_scores"]["charisma"] = 10
    response = client.post(
        f"/campaigns/{campaign_id}/characters/{created[0]['id']}/finalize",
        json=invalid,
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"] == "base ability scores must use each standard-array value once"
    )

    state = client.get(f"/campaigns/{campaign_id}/state")
    assert state.status_code == 200
    assert state.json()["characters"][0]["creation_status"] == "draft"


def test_finalized_creation_facts_and_provenance_are_immutable(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    assert (
        client.post(f"/campaigns/{campaign_id}/character", json={"name": "Arin"}).status_code == 201
    )
    finalized = client.post(
        f"/campaigns/{campaign_id}/character/finalize",
        json=_finalize_payload(),
    )
    assert finalized.status_code == 200
    assert (
        client.post(
            f"/campaigns/{campaign_id}/character/finalize",
            json=_finalize_payload(),
        ).status_code
        == 409
    )

    with (
        pytest.raises(DBAPIError, match="finalized character creation facts are immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text("UPDATE characters SET name = 'Mutated' WHERE campaign_id = :campaign_id"),
            {"campaign_id": campaign_id},
        )

    with (
        pytest.raises(DBAPIError, match="character_grants is immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text("UPDATE character_grants SET active = false WHERE campaign_id = :campaign_id"),
            {"campaign_id": campaign_id},
        )


def test_campaign_rejects_unknown_dynamic_and_legacy_ruleset_inputs(
    client: TestClient,
) -> None:
    unknown = client.post("/campaigns", json={"name": "Unknown", "ruleset_release_id": "srd-9.9.9"})
    assert unknown.status_code == 422
    assert unknown.json()["detail"] == "Unknown ruleset release: srd-9.9.9"

    latest = client.post("/campaigns", json={"name": "Dynamic", "ruleset_release_id": "latest"})
    assert latest.status_code == 422
    assert latest.json()["detail"] == "Dynamic ruleset alias 'latest' is not supported"

    legacy = client.post("/campaigns", json={"name": "Legacy", "ruleset": "SRD 5.2.1"})
    assert legacy.status_code == 422


def test_party_loadout_and_actor_guards(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    character_ids = []
    for name in ("Arin", "Bryn"):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201
        character_ids.append(draft.json()["id"])
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{draft.json()['id']}/finalize",
            json=_finalize_payload(),
        )
        assert finalized.status_code == 200

    missing_actor = client.post(
        f"/campaigns/{campaign_id}/turns", json={"action": "Someone scouts ahead."}
    )
    assert missing_actor.status_code == 409
    assert missing_actor.json()["detail"] == "Party Commander turns require actor_character_id"

    invalid_loadout = client.put(
        f"/campaigns/{campaign_id}/characters/{character_ids[0]}/loadout",
        json={
            "worn_armor_item_id": "chain_mail",
            "held_item_ids": ["greatsword", "flail"],
        },
    )
    assert invalid_loadout.status_code == 422
    assert invalid_loadout.json()["detail"] == "held items require more than two hands"

    changed = client.put(
        f"/campaigns/{campaign_id}/characters/{character_ids[0]}/loadout",
        json={"worn_armor_item_id": None, "held_item_ids": ["greatsword"]},
    )
    assert changed.status_code == 200
    assert changed.json()["state_revision"] == 2
    assert changed.json()["mechanical_state"]["armor_class"]["value"] == 12
    assert changed.json()["mechanical_state"]["equipment"]

    other_campaign_id = _create_campaign(client)
    outsider = client.post(f"/campaigns/{other_campaign_id}/characters", json={"name": "Outsider"})
    assert outsider.status_code == 201
    wrong_campaign_actor = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "An outsider acts.", "actor_character_id": outsider.json()["id"]},
    )
    assert wrong_campaign_actor.status_code == 404
