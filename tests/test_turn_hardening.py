import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api import app
from app.db import get_engine
from app.dice import DiceService, get_dice_service
from app.llm.base import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderRateLimitError,
    ProviderRefusalError,
    ProviderResponseError,
    ProviderResult,
    ProviderTimeoutError,
)
from app.llm.deterministic import DeterministicDMProvider
from app.llm.factory import get_turn_interpreter, get_turn_narrator
from app.schemas import RuleResolutionRead, TurnNarrationOutput
from app.turn_interpretation import TurnIntent


class FixedRandom:
    algorithm_version = "m2-hardening-fixed-1.0.0"

    def __init__(self, results: list[int]) -> None:
        self._results = iter(results)
        self.calls = 0

    def randint(self, start: int, end: int) -> int:
        self.calls += 1
        value = next(self._results)
        assert start <= value <= end
        return value


def _fixed_dice(results: list[int]) -> FixedRandom:
    random = FixedRandom(results)
    app.dependency_overrides[get_dice_service] = lambda: DiceService(random)
    return random


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


def _ready_campaign(client: TestClient, name: str = "M2 Hardening") -> tuple[str, list[str]]:
    campaign = client.post(
        "/campaigns",
        json={"name": name, "starting_location": "Crossroads"},
    )
    assert campaign.status_code == 201
    campaign_id = campaign.json()["id"]
    characters = []
    for index, character_name in enumerate(("Arin", "Bryn")):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": character_name})
        assert draft.status_code == 201
        character_id = draft.json()["id"]
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{character_id}/finalize",
            json=_finalize_payload(alternate=index == 1),
        )
        assert finalized.status_code == 200, finalized.text
        characters.append(character_id)
    return campaign_id, characters


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


def _turn_events(turn_id: str) -> list[str]:
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


class FailingInterpreter:
    provider_name = "failure-injection"
    model_name = "offline-fixture"
    interpretation_prompt_version = "failure-injection-1"

    def __init__(self, failure: Exception | None) -> None:
        self.failure = failure

    def interpret_action(self, context: dict[str, Any], player_action: str) -> Any:
        if self.failure is not None:
            raise self.failure
        return None


@pytest.mark.parametrize(
    ("failure", "error_code", "message"),
    [
        (ProviderTimeoutError(), "provider_timeout", "Interpretation provider timed out"),
        (
            ProviderConnectionError(),
            "provider_connection_error",
            "Interpretation provider could not be reached",
        ),
        (
            ProviderAuthenticationError(),
            "provider_authentication_error",
            "Interpretation provider authentication failed",
        ),
        (
            ProviderRateLimitError(),
            "provider_rate_limit",
            "Interpretation provider quota is unavailable",
        ),
        (
            ProviderResponseError(),
            "provider_response_error",
            "Interpretation provider returned an error",
        ),
        (
            ProviderRefusalError(),
            "provider_refusal",
            "Interpretation provider refused the request",
        ),
        (None, "provider_empty_output", "Interpretation provider returned no structured output"),
    ],
)
def test_interpretation_failures_are_normalized_audited_and_recoverable(
    client: TestClient,
    failure: Exception | None,
    error_code: str,
    message: str,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _create_turn(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    app.dependency_overrides[get_turn_interpreter] = lambda: FailingInterpreter(failure)

    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert response.status_code == 502
    assert response.json()["detail"] == {
        "turn_id": turn_id,
        "stage": "interpretation",
        "error_code": error_code,
        "message": message,
        "resumable": True,
    }
    assert client.get(f"/campaigns/{campaign_id}/state").json() == before
    assert _turn_events(turn_id) == ["player_action"]
    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls").json()
    assert len(calls) == 1
    assert calls[0]["status"] == "failed"
    assert calls[0]["error_code"] == error_code

    resumed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "received"
    app.dependency_overrides[get_turn_interpreter] = lambda: DeterministicDMProvider()
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200
    assert interpreted.json()["turn"]["status"] == "intent_ready"


class TimeoutNarrator:
    provider_name = "timeout-fixture"
    model_name = "offline-fixture"
    narration_prompt_version = "timeout-narration-1"

    def narrate_outcome(self, *args: Any) -> TurnNarrationOutput:
        raise ProviderTimeoutError


def test_post_resolution_timeout_resume_reuses_exact_dice_after_restart(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    random = _fixed_dice([7])
    turn_id = _create_turn(client, campaign_id, characters[0], "Arin climbs the wall.")
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200
    original_resolution = interpreted.json()["resolution"]
    assert random.calls == 1
    app.dependency_overrides[get_turn_narrator] = lambda: TimeoutNarrator()

    failed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert failed.status_code == 502
    assert failed.json()["detail"]["error_code"] == "provider_timeout"
    assert failed.json()["detail"]["turn_id"] == turn_id
    assert _turn_events(turn_id) == ["player_action", "rule_resolved"]

    get_engine().dispose()
    resumed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "resolved"
    no_reroll = _fixed_dice([1])
    retry_resolution = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert retry_resolution.status_code == 200
    assert retry_resolution.json()["resolution"]["id"] == original_resolution["id"]
    assert retry_resolution.json()["resolution"]["dice_faces"] == [7]
    assert no_reroll.calls == 0
    app.dependency_overrides[get_turn_narrator] = lambda: DeterministicDMProvider()
    completed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert completed.status_code == 200
    assert completed.json()["turn"]["status"] == "completed"
    assert _turn_events(turn_id) == [
        "player_action",
        "rule_resolved",
        "dm_response",
        "state_changed",
    ]
    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls").json()
    narration_calls = [call for call in calls if call["stage"] == "narration"]
    assert [call["attempt"] for call in narration_calls] == [1, 2]
    assert [call["status"] for call in narration_calls] == ["failed", "succeeded"]


class MeteredProvider(DeterministicDMProvider):
    provider_name = "metered-fixture"
    model_name = "offline-metered"
    interpretation_prompt_version = "metered-intent-1"
    narration_prompt_version = "metered-narration-1"

    def interpret_action(
        self, context: dict[str, Any], player_action: str
    ) -> ProviderResult[TurnIntent]:
        output = super().interpret_action(context, player_action)
        return ProviderResult(output=output, input_tokens=17, output_tokens=5)

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: RuleResolutionRead | None,
    ) -> ProviderResult[TurnNarrationOutput]:
        output = super().narrate_outcome(context, player_action, intent, resolution)
        return ProviderResult(output=output, input_tokens=23, output_tokens=11)


def test_provider_reported_usage_and_measured_latency_are_persisted(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    provider = MeteredProvider()
    app.dependency_overrides[get_turn_interpreter] = lambda: provider
    app.dependency_overrides[get_turn_narrator] = lambda: provider
    turn_id = _create_turn(client, campaign_id, characters[0], "Arin greets the innkeeper.")

    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret").status_code
        == 200
    )
    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize").status_code
        == 200
    )
    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls").json()
    assert [(call["input_tokens"], call["output_tokens"]) for call in calls] == [
        (17, 5),
        (23, 11),
    ]
    assert all(call["latency_ms"] >= 0 for call in calls)
    assert all(call["provider"] == "metered-fixture" for call in calls)
    assert all(call["model"] == "offline-metered" for call in calls)


def _set_interrupted_stage(turn_id: str, status: str, *, clear_resolution: bool = False) -> None:
    resolution_sql = ", resolution_id = NULL" if clear_resolution else ""
    with get_engine().begin() as connection:
        connection.execute(
            text(
                f"UPDATE turns SET status = :status, "  # noqa: S608 - fixed test-only fragment
                "stage_started_at = :started_at"
                f"{resolution_sql} WHERE id = :turn_id"
            ),
            {
                "status": status,
                "started_at": datetime.now(UTC) - timedelta(minutes=10),
                "turn_id": uuid.UUID(turn_id),
            },
        )


def test_interrupted_interpretation_requires_expired_lease_then_recovers(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _create_turn(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    with get_engine().begin() as connection:
        connection.execute(
            text(
                "UPDATE turns SET status = 'interpreting', stage_started_at = now() "
                "WHERE id = :turn_id"
            ),
            {"turn_id": uuid.UUID(turn_id)},
        )
    active = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
    assert active.status_code == 409
    assert "still in progress" in active.json()["detail"]

    _set_interrupted_stage(turn_id, "interpreting")
    get_engine().dispose()
    recovered = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
    assert recovered.status_code == 200
    assert recovered.json()["status"] == "received"
    assert recovered.json()["stage_started_at"] is None
    with get_engine().connect() as connection:
        recovery = connection.execute(
            text(
                "SELECT payload FROM campaign_events WHERE turn_id = :turn_id "
                "AND event_type = 'turn_stage_recovered'"
            ),
            {"turn_id": uuid.UUID(turn_id)},
        ).scalar_one()
    assert recovery["interrupted_stage"] == "interpreting"
    assert recovery["restored_checkpoint"] == "received"


def test_interrupted_resolution_relinks_existing_result_without_reroll(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    random = _fixed_dice([7])
    turn_id = _create_turn(client, campaign_id, characters[0], "Arin climbs the wall.")
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    resolution = interpreted.json()["resolution"]
    assert random.calls == 1

    _set_interrupted_stage(turn_id, "resolving", clear_resolution=True)
    get_engine().dispose()
    recovered = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
    assert recovered.status_code == 200
    assert recovered.json()["status"] == "resolved"
    assert recovered.json()["resolution_id"] == resolution["id"]
    no_reroll = _fixed_dice([1])
    retried = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert retried.status_code == 200
    assert retried.json()["resolution"]["dice_faces"] == [7]
    assert no_reroll.calls == 0


def test_interrupted_narration_recovers_checkpoint_and_finalizes_once(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _create_turn(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.json()["turn"]["status"] == "intent_ready"
    _set_interrupted_stage(turn_id, "narrating")
    get_engine().dispose()

    recovered = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume")
    assert recovered.status_code == 200
    assert recovered.json()["status"] == "intent_ready"
    completed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert completed.status_code == 200
    assert completed.json()["turn"]["status"] == "completed"
    assert _turn_events(turn_id) == ["player_action", "dm_response"]


class CountingNarrator(DeterministicDMProvider):
    calls = 0

    def narrate_outcome(self, *args: Any) -> TurnNarrationOutput:
        self.calls += 1
        return super().narrate_outcome(*args)


def test_fresh_narration_lease_blocks_a_competing_provider_call(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _create_turn(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret").status_code
        == 200
    )
    with get_engine().begin() as connection:
        connection.execute(
            text(
                "UPDATE turns SET status = 'narrating', stage_started_at = now() "
                "WHERE id = :turn_id"
            ),
            {"turn_id": uuid.UUID(turn_id)},
        )
    provider = CountingNarrator()
    app.dependency_overrides[get_turn_narrator] = lambda: provider
    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 409
    assert response.json()["detail"] == "Turn narration is already in progress"
    assert provider.calls == 0
    assert _turn_events(turn_id) == ["player_action"]


def test_ten_consecutive_deterministic_lantern_scenarios(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client, "Ten-run deterministic Lantern")
    scenarios = [
        (characters[0], "Arin greets the innkeeper.", None),
        (characters[0], "Arin travels to the Old Tower.", None),
        (characters[0], "Arin uses a Javelin to mark the trail.", None),
        (characters[0], "Arin climbs the wall.", [7]),
        (characters[1], "Bryn climbs the wall.", [9]),
        (characters[1], "Bryn greets the innkeeper.", None),
        (characters[0], "Arin tries to resist the poison.", [9]),
        (characters[0], "Arin tries to sneak past the sentry.", [15, 4]),
        (characters[1], "Bryn leaves a Javelin to mark the trail.", None),
        (characters[0], "Arin greets the innkeeper again.", None),
    ]
    turn_ids = []
    for index, (actor_id, action, dice) in enumerate(scenarios, start=1):
        if dice is not None:
            _fixed_dice(dice)
        turn_id = _create_turn(client, campaign_id, actor_id, action)
        turn_ids.append(turn_id)
        interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
        assert interpreted.status_code == 200, f"scenario {index}: {interpreted.text}"
        if index == 7:
            get_engine().dispose()
        finalized = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
        assert finalized.status_code == 200, f"scenario {index}: {finalized.text}"
        assert finalized.json()["turn"]["status"] == "completed"
        expected = ["player_action", "dm_response"]
        if interpreted.json()["resolution"] is not None:
            expected.insert(1, "rule_resolved")
        if finalized.json()["turn"]["structured_output"]["state_changes"]:
            expected.append("state_changed")
        assert _turn_events(turn_id) == expected

    state = client.get(f"/campaigns/{campaign_id}/state").json()
    arin = next(character for character in state["characters"] if character["id"] == characters[0])
    bryn = next(character for character in state["characters"] if character["id"] == characters[1])
    assert state["turn_count"] == 10
    assert state["location"]["name"] == "Wall Top"
    assert arin["inventory"]["Javelin"] == 7
    assert bryn["inventory"]["Javelin"] == 7
    assert bryn["hp"] == 10
    assert all(character["hp"] >= 0 for character in state["characters"])
    with get_engine().connect() as connection:
        counts = connection.execute(
            text(
                "SELECT "
                "(SELECT count(*) FROM turns WHERE campaign_id = :campaign_id "
                "AND status = 'completed'), "
                "(SELECT count(*) FROM provider_calls WHERE campaign_id = :campaign_id), "
                "(SELECT count(*) FROM provider_calls WHERE campaign_id = :campaign_id "
                "AND status = 'failed')"
            ),
            {"campaign_id": uuid.UUID(campaign_id)},
        ).one()
    assert counts == (10, 20, 0)
    assert len(turn_ids) == len(set(turn_ids)) == 10
