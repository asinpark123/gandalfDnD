from typing import Any

from fastapi.testclient import TestClient

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
                    item_name="Torch",
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
    return response.json()["id"]


def test_health_checks_database(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "environment": "test"}


def test_phase_zero_persists_state_turns_and_events(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    character = client.post(
        f"/campaigns/{campaign_id}/character",
        json={"name": "Arin", "max_hp": 10, "inventory": {"Torch": 1}},
    )
    assert character.status_code == 201
    assert character.json()["ruleset_release_id"] == "srd-5.2.1"

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
    assert payload["character"]["hp"] == 8
    assert payload["character"]["inventory"] == {}
    assert payload["location"]["name"] == "Stable Loft"
    assert payload["turn_count"] == 1

    events = client.get(f"/campaigns/{campaign_id}/events")
    assert events.status_code == 200
    assert [event["event_type"] for event in events.json()] == [
        "campaign_created",
        "character_created",
        "player_action",
        "dice_rolled",
        "dm_response",
        "state_changed",
    ]
    assert {event["ruleset_release_id"] for event in events.json()} == {"srd-5.2.1"}


def test_phase_zero_allows_only_one_character(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    body = {"name": "Arin", "max_hp": 10}
    assert client.post(f"/campaigns/{campaign_id}/character", json=body).status_code == 201
    assert client.post(f"/campaigns/{campaign_id}/character", json=body).status_code == 409


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
