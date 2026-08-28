from typing import Any

from fastapi.testclient import TestClient

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
                    item_name="Torch",
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

    from app.api import app

    app.dependency_overrides[get_dm_provider] = lambda: StateChangingProvider()
    turn = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={"action": "I climb into the loft."},
    )
    assert turn.status_code == 201, turn.text
    assert turn.json()["sequence"] == 1

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
        "dm_response",
        "state_changed",
    ]


def test_phase_zero_allows_only_one_character(client: TestClient) -> None:
    campaign_id = _create_campaign(client)
    body = {"name": "Arin", "max_hp": 10}
    assert client.post(f"/campaigns/{campaign_id}/character", json=body).status_code == 201
    assert client.post(f"/campaigns/{campaign_id}/character", json=body).status_code == 409
