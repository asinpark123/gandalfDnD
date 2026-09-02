import os
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api import app
from app.db import get_engine
from app.llm.base import ProviderTimeoutError
from app.llm.factory import get_turn_interpreter, get_turn_narrator
from app.llm.openclaw_provider import OpenClawTurnProvider

pytestmark = pytest.mark.skipif(
    os.getenv("GANDALF_RUN_OPENCLAW_LIVE") != "1",
    reason="live OpenClaw evaluation is opt-in",
)


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


def _ready_campaign(client: TestClient) -> tuple[str, list[str]]:
    campaign = client.post(
        "/campaigns",
        json={"name": "Ten-run live OpenClaw Lantern", "starting_location": "Crossroads"},
    )
    assert campaign.status_code == 201, campaign.text
    campaign_id = campaign.json()["id"]
    character_ids = []
    for index, name in enumerate(("Arin", "Bryn")):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201, draft.text
        character_id = draft.json()["id"]
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{character_id}/finalize",
            json=_finalize_payload(alternate=index == 1),
        )
        assert finalized.status_code == 200, finalized.text
        character_ids.append(character_id)
    return campaign_id, character_ids


def _create_turn(client: TestClient, campaign_id: str, actor_id: str, action: str) -> str:
    response = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": str(uuid.uuid4()),
            "action": action,
            "actor_character_id": actor_id,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _event_types(turn_id: str) -> list[str]:
    with get_engine().connect() as connection:
        return list(
            connection.execute(
                text(
                    "SELECT event_type FROM campaign_events "
                    "WHERE turn_id = :turn_id AND visibility = 'player' ORDER BY sequence"
                ),
                {"turn_id": uuid.UUID(turn_id)},
            ).scalars()
        )


class _InjectedTimeoutNarrator:
    provider_name = "live-resume-fixture"
    model_name = "no-external-call"
    narration_prompt_version = "live-resume-fixture-1.0.0"

    def narrate_outcome(self, *args: Any) -> None:
        raise ProviderTimeoutError


def test_ten_consecutive_live_openclaw_lantern_scenarios(client: TestClient) -> None:
    token = os.environ.get("GANDALF_OPENCLAW_LIVE_TOKEN", "")
    if not token:
        pytest.fail("GANDALF_OPENCLAW_LIVE_TOKEN is required for an opted-in live run")
    provider = OpenClawTurnProvider(
        base_url=os.getenv("GANDALF_OPENCLAW_LIVE_BASE_URL", "http://127.0.0.1:18790/v1"),
        gateway_token=token,
        agent_id="gandalf",
        model=os.getenv("GANDALF_OPENCLAW_LIVE_MODEL") or None,
        gm_style="classic_heroic_fantasy",
        timeout_seconds=180,
    )
    app.dependency_overrides[get_turn_interpreter] = lambda: provider
    app.dependency_overrides[get_turn_narrator] = lambda: provider
    campaign_id, characters = _ready_campaign(client)
    scenarios = [
        (characters[0], "Arin greets the innkeeper."),
        (characters[0], "Arin travels to the Old Tower."),
        (characters[0], "Arin uses a Javelin to mark the trail."),
        (characters[0], "Arin climbs the wall."),
        (characters[1], "Bryn climbs the wall."),
        (characters[1], "Bryn greets the innkeeper."),
        (characters[0], "Arin tries to resist the poison."),
        (characters[0], "Arin tries to sneak past the sentry."),
        (characters[1], "Bryn leaves a Javelin to mark the trail."),
        (characters[0], "Arin greets the innkeeper again."),
    ]

    turn_ids: list[str] = []
    resolution_snapshots: dict[str, tuple[str, list[int]]] = {}
    for index, (actor_id, action) in enumerate(scenarios, start=1):
        turn_id = _create_turn(client, campaign_id, actor_id, action)
        turn_ids.append(turn_id)
        interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
        assert interpreted.status_code == 200, (
            f"scenario {index} interpretation: {interpreted.text}"
        )
        interpretation = interpreted.json()
        assert interpretation["turn"]["actor_character_id"] == actor_id
        resolution = interpretation["resolution"]
        if resolution is not None:
            resolution_snapshots[turn_id] = (resolution["id"], resolution["dice_faces"])

        if index == 7:
            get_engine().dispose()
        if index == 8:
            app.dependency_overrides[get_turn_narrator] = lambda: _InjectedTimeoutNarrator()
            failed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
            assert failed.status_code == 502, f"scenario {index} injected failure: {failed.text}"
            assert failed.json()["detail"]["error_code"] == "provider_timeout"
            get_engine().dispose()
            resumed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
            assert resumed.status_code == 200, f"scenario {index} resume: {resumed.text}"
            app.dependency_overrides[get_turn_narrator] = lambda: provider

        finalized = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
        assert finalized.status_code == 200, f"scenario {index} narration: {finalized.text}"
        result = finalized.json()
        assert result["turn"]["status"] == "completed"
        assert result["turn"]["actor_character_id"] == actor_id
        output = result["turn"]["structured_output"]
        if result["resolution"] is None:
            assert output["resolution_id"] is None
            assert output["acknowledged_outcome"] is None
        else:
            assert output["resolution_id"] == result["resolution"]["id"]
            assert output["acknowledged_outcome"] == result["resolution"]["outcome"]
            if turn_id in resolution_snapshots:
                assert (result["resolution"]["id"], result["resolution"]["dice_faces"]) == (
                    resolution_snapshots[turn_id]
                )

        expected_events = ["player_action"]
        if result["resolution"] is not None:
            expected_events.append("rule_resolved")
        expected_events.append("dm_response")
        if output["state_changes"]:
            expected_events.append("state_changed")
        assert _event_types(turn_id) == expected_events

        calls = client.get(
            f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls"
        ).json()
        successful_live_calls = [
            call
            for call in calls
            if call["provider"] == "openclaw" and call["status"] == "succeeded"
        ]
        assert [call["stage"] for call in successful_live_calls] == [
            "interpretation",
            "narration",
        ]
        assert all(call["model"] == provider.model_name for call in successful_live_calls)
        assert all(call["latency_ms"] >= 0 for call in successful_live_calls)
        assert all((call["input_tokens"] or 0) > 0 for call in successful_live_calls)
        assert all((call["output_tokens"] or 0) > 0 for call in successful_live_calls)

    state = client.get(f"/campaigns/{campaign_id}/state").json()
    assert state["turn_count"] == 10
    assert len(state["characters"]) == 2
    assert {character["id"] for character in state["characters"]} == set(characters)
    assert all(0 <= character["hp"] <= character["max_hp"] for character in state["characters"])
    assert all(
        quantity >= 0
        for character in state["characters"]
        for quantity in character["inventory"].values()
    )
    assert len(turn_ids) == len(set(turn_ids)) == 10

    with get_engine().connect() as connection:
        (
            completed,
            live_successes,
            injected_failures,
            input_tokens,
            output_tokens,
            average_latency_ms,
            maximum_latency_ms,
        ) = connection.execute(
            text(
                "SELECT "
                "(SELECT count(*) FROM turns WHERE campaign_id = :campaign_id "
                "AND status = 'completed'), "
                "(SELECT count(*) FROM provider_calls WHERE campaign_id = :campaign_id "
                "AND provider = 'openclaw' AND status = 'succeeded'), "
                "(SELECT count(*) FROM provider_calls WHERE campaign_id = :campaign_id "
                "AND provider = 'live-resume-fixture' AND status = 'failed'), "
                "(SELECT sum(input_tokens) FROM provider_calls WHERE campaign_id = :campaign_id "
                "AND provider = 'openclaw' AND status = 'succeeded'), "
                "(SELECT sum(output_tokens) FROM provider_calls WHERE campaign_id = :campaign_id "
                "AND provider = 'openclaw' AND status = 'succeeded'), "
                "(SELECT round(avg(latency_ms)) FROM provider_calls "
                "WHERE campaign_id = :campaign_id "
                "AND provider = 'openclaw' AND status = 'succeeded'), "
                "(SELECT max(latency_ms) FROM provider_calls WHERE campaign_id = :campaign_id "
                "AND provider = 'openclaw' AND status = 'succeeded')"
            ),
            {"campaign_id": uuid.UUID(campaign_id)},
        ).one()
    assert (completed, live_successes, injected_failures) == (10, 20, 1)
    print(
        "OpenClaw live metrics: "
        f"turns={completed}, calls={live_successes}, injected_failures={injected_failures}, "
        f"input_tokens={input_tokens}, output_tokens={output_tokens}, "
        f"average_latency_ms={average_latency_ms}, maximum_latency_ms={maximum_latency_ms}"
    )
