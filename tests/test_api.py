from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db import get_engine
from app.llm.factory import get_dm_provider
from app.schemas import DiceRequest, DMTurnOutput, HPDelta, InventoryChange, MoveLocation


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
            dice_requests=[
                DiceRequest(
                    notation="1d20",
                    modifier=2,
                    purpose="Check whether Arin lands safely",
                )
            ],
        )


def _create_campaign(client: TestClient) -> str:
    response = client.post(
        "/campaigns",
        json={"name": "The Lantern Test", "starting_location": "Roadside Inn"},
    )
    assert response.status_code == 201
    assert response.json()["ruleset_release_id"] == "srd-5.2.1"
    assert response.json()["ruleset_data_catalog_id"] == "srd-5.2.1-character-creation-v1"
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
    assert options.json()["id"] == "srd-5.2.1-character-creation-v1"
    assert len(options.json()["skills"]) == 18
    assert all(option["beginner_description"] for option in options.json()["skills"])

    character = client.post(
        f"/campaigns/{campaign_id}/character",
        json={"name": "Arin"},
    )
    assert character.status_code == 201
    assert character.json()["ruleset_release_id"] == "srd-5.2.1"
    assert character.json()["creation_status"] == "draft"
    assert character.json()["max_hp"] is None

    blocked_turn = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "I leave before finishing my character."},
    )
    assert blocked_turn.status_code == 409

    finalized = client.post(
        f"/campaigns/{campaign_id}/character/finalize",
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

    grants = client.get(f"/campaigns/{campaign_id}/character/grants")
    assert grants.status_code == 200
    assert len(grants.json()) >= 30
    assert {grant["ruleset_data_catalog_id"] for grant in grants.json()} == {
        "srd-5.2.1-character-creation-v1"
    }
    assert all(grant["value"]["source_ids"] for grant in grants.json())

    from app.api import app

    app.dependency_overrides[get_dm_provider] = lambda: StateChangingProvider()
    turn = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "I climb into the loft."},
    )
    assert turn.status_code == 201, turn.text
    assert turn.json()["sequence"] == 1
    assert turn.json()["dice_rolls"][0]["notation"] == "1d20"
    assert turn.json()["dice_rolls"][0]["ruleset_release_id"] == "srd-5.2.1"
    assert 3 <= turn.json()["dice_rolls"][0]["total"] <= 22

    get_engine().dispose()
    state = client.get(f"/campaigns/{campaign_id}/state")
    assert state.status_code == 200
    payload = state.json()
    assert payload["character"]["hp"] == 10
    assert payload["character"]["inventory"]["Javelin"] == 7
    assert payload["location"]["name"] == "Stable Loft"
    assert payload["turn_count"] == 1

    events = client.get(f"/campaigns/{campaign_id}/events")
    assert events.status_code == 200
    assert [event["event_type"] for event in events.json()] == [
        "campaign_created",
        "character_draft_created",
        "character_finalized",
        "player_action",
        "dice_rolled",
        "dm_response",
        "state_changed",
    ]
    assert {event["ruleset_release_id"] for event in events.json()} == {"srd-5.2.1"}


def test_guided_creation_rejects_duplicate_and_legacy_character_input(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    legacy = client.post(
        f"/campaigns/{campaign_id}/character",
        json={"name": "Legacy", "max_hp": 10},
    )
    assert legacy.status_code == 422

    body = {"name": "Arin"}
    assert client.post(f"/campaigns/{campaign_id}/character", json=body).status_code == 201
    assert client.post(f"/campaigns/{campaign_id}/character", json=body).status_code == 409

    invalid = _finalize_payload()
    invalid["base_ability_scores"]["charisma"] = 10
    response = client.post(
        f"/campaigns/{campaign_id}/character/finalize",
        json=invalid,
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"] == "base ability scores must use each standard-array value once"
    )

    state = client.get(f"/campaigns/{campaign_id}/state")
    assert state.status_code == 200
    assert state.json()["character"]["creation_status"] == "draft"


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
