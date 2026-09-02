import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import app
from app.db import get_engine
from app.dice import DiceService, get_dice_service
from app.llm.deterministic import DeterministicDMProvider
from app.llm.factory import get_dm_provider, get_turn_interpreter
from app.schemas import DiceRequest, DMTurnOutput
from app.services import interpret_turn_execution
from app.turn_interpretation import (
    D20ResolutionRequest,
    D20TestIntent,
    NarrativeIntent,
    validate_turn_intent,
)


class FixedRandom:
    algorithm_version = "m2-fixed-sequence-1.0.0"

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


def _ready_campaign(client: TestClient) -> tuple[str, list[str]]:
    campaign = client.post("/campaigns", json={"name": "M2 Interpretation"})
    assert campaign.status_code == 201
    campaign_id = campaign.json()["id"]
    character_ids = []
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
    return campaign_id, character_ids


def _execution(client: TestClient, campaign_id: str, actor_id: str, action: str) -> str:
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


def test_interpretation_contract_forbids_modifier_and_dice_results() -> None:
    base = {
        "type": "d20_test",
        "summary": "Attempt a difficult climb",
        "resolution": {
            "resolution_type": "ability_check",
            "ability": "strength",
            "skill": "athletics",
            "difficulty_class": 12,
            "purpose": "Climb the wall",
        },
    }
    with pytest.raises(ValidationError):
        validate_turn_intent({**base, "resolution": {**base["resolution"], "modifier": 99}})
    with pytest.raises(ValidationError):
        validate_turn_intent({**base, "resolution": {**base["resolution"], "dice_faces": [20]}})


def test_check_uses_actor_state_and_retry_never_rerolls(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin climbs the wet stone wall.")
    first_random = _fixed_dice([7])
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text
    body = interpreted.json()
    assert body["turn"]["status"] == "resolved"
    assert body["intent"]["type"] == "d20_test"
    assert "modifier" not in body["intent"]["resolution"]
    assert "dice_faces" not in body["intent"]["resolution"]
    assert body["resolution"]["modifier"] == 5
    assert body["resolution"]["dice_faces"] == [7]
    assert body["resolution"]["total"] == 12
    assert body["resolution"]["outcome"] == "success"
    assert first_random.calls == 1

    retry_random = _fixed_dice([1])
    retry = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert retry.status_code == 200
    assert retry.json()["resolution"]["id"] == body["resolution"]["id"]
    assert retry.json()["resolution"]["dice_faces"] == [7]
    assert retry_random.calls == 0

    with get_engine().begin() as connection:
        connection.execute(
            text(
                "UPDATE turns SET status = 'resolving', resolution_id = NULL, "
                "stage_started_at = now() WHERE id = :turn_id"
            ),
            {"turn_id": uuid.UUID(turn_id)},
        )
    interrupted_retry_random = _fixed_dice([2])
    interrupted_retry = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interrupted_retry.status_code == 200
    assert interrupted_retry.json()["resolution"]["id"] == body["resolution"]["id"]
    assert interrupted_retry.json()["resolution"]["dice_faces"] == [7]
    assert interrupted_retry_random.calls == 0

    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls")
    assert calls.status_code == 200
    assert len(calls.json()) == 1
    assert calls.json()[0]["prompt_version"] == "deterministic-intent-1.0.0"
    assert calls.json()[0]["status"] == "succeeded"

    with get_engine().connect() as connection:
        linked = connection.execute(
            text(
                "SELECT d.turn_id, e.turn_id FROM rule_resolutions r "
                "JOIN dice_rolls d ON d.id = r.dice_roll_id "
                "JOIN campaign_events e ON e.payload->>'resolution_id' = CAST(r.id AS text) "
                "WHERE r.id = :resolution_id"
            ),
            {"resolution_id": uuid.UUID(body["resolution"]["id"])},
        ).one()
    assert linked == (uuid.UUID(turn_id), uuid.UUID(turn_id))


def test_contrasting_actor_and_save_use_canonical_modifiers(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    first_turn = _execution(client, campaign_id, characters[0], "Arin climbs the wall.")
    _fixed_dice([7])
    first = client.post(f"/campaigns/{campaign_id}/turn-executions/{first_turn}/interpret")
    assert first.status_code == 200
    assert first.json()["resolution"]["modifier"] == 5
    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{first_turn}/cancel").status_code
        == 200
    )

    second_turn = _execution(client, campaign_id, characters[1], "Bryn climbs the wall.")
    _fixed_dice([9])
    second = client.post(f"/campaigns/{campaign_id}/turn-executions/{second_turn}/interpret")
    assert second.status_code == 200, second.text
    assert second.json()["resolution"]["modifier"] == 2
    assert second.json()["resolution"]["total"] == 11
    assert second.json()["resolution"]["outcome"] == "failure"
    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{second_turn}/cancel").status_code
        == 200
    )

    save_turn = _execution(
        client,
        campaign_id,
        characters[0],
        "Arin tries to resist the poison.",
    )
    _fixed_dice([9])
    save = client.post(f"/campaigns/{campaign_id}/turn-executions/{save_turn}/interpret")
    assert save.status_code == 200, save.text
    resolution = save.json()["resolution"]
    assert resolution["resolution_type"] == "saving_throw"
    assert resolution["ability"] == "constitution"
    assert resolution["skill"] is None
    assert resolution["modifier"] == 4
    assert resolution["total"] == 13
    assert resolution["outcome"] == "success"


def test_narrative_intent_stops_before_m2_3_without_rolling(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    random = _fixed_dice([20])
    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert response.status_code == 200, response.text
    assert response.json()["turn"]["status"] == "intent_ready"
    assert response.json()["intent"]["type"] == "narrative"
    assert response.json()["resolution"] is None
    assert random.calls == 0


class InvalidInterpretationProvider:
    provider_name = "invalid-test"
    model_name = "invalid-output"
    interpretation_prompt_version = "invalid-intent-1"

    def interpret_action(self, context: dict[str, Any], player_action: str) -> dict[str, Any]:
        return {
            "type": "d20_test",
            "summary": "Invalid provider output",
            "resolution": {
                "resolution_type": "ability_check",
                "ability": "strength",
                "skill": "athletics",
                "difficulty_class": 12,
                "purpose": "Invalid fixture",
                "modifier": 99,
            },
        }


def test_invalid_provider_output_is_audited_and_resumable_without_roll(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin climbs the wall.")
    app.dependency_overrides[get_turn_interpreter] = lambda: InvalidInterpretationProvider()
    random = _fixed_dice([10])
    failed = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert failed.status_code == 502
    assert random.calls == 0
    stored = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert stored["status"] == "failed"
    assert stored["error_code"] == "invalid_structured_output"
    assert stored["resumable"] is True
    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls").json()
    assert len(calls) == 1
    assert calls[0]["status"] == "failed"
    assert calls[0]["structured_output"] is None

    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/resume").status_code == 200
    )
    app.dependency_overrides[get_turn_interpreter] = lambda: DeterministicDMProvider()
    recovered = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert recovered.status_code == 200, recovered.text
    assert recovered.json()["turn"]["status"] == "resolved"
    assert random.calls == 1
    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls").json()
    assert [call["attempt"] for call in calls] == [1, 2]
    assert [call["status"] for call in calls] == ["failed", "succeeded"]


class UnknownSkillProvider:
    provider_name = "unknown-skill-test"
    model_name = None
    interpretation_prompt_version = "unknown-skill-1"

    def interpret_action(self, context: dict[str, Any], player_action: str) -> D20TestIntent:
        return D20TestIntent(
            type="d20_test",
            summary="Request an unknown skill.",
            resolution=D20ResolutionRequest(
                resolution_type="ability_check",
                ability="strength",
                skill="made_up_skill",
                difficulty_class=12,
                purpose="Prove validation occurs before rolling",
            ),
        )


def test_invalid_resolution_request_fails_before_rolling(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Use an unknown skill.")
    app.dependency_overrides[get_turn_interpreter] = lambda: UnknownSkillProvider()
    random = _fixed_dice([20])
    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert response.status_code == 422
    assert response.json()["detail"] == "Unknown skill for this ruleset: made_up_skill"
    assert random.calls == 0
    stored = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert stored["status"] == "failed"
    assert stored["failure_stage"] == "resolution"
    assert stored["resumable"] is False
    with get_engine().connect() as connection:
        assert (
            connection.execute(
                text("SELECT count(*) FROM rule_resolutions WHERE campaign_id = :campaign_id"),
                {"campaign_id": uuid.UUID(campaign_id)},
            ).scalar_one()
            == 0
        )


class LegacyDiceProvider:
    provider_name = "legacy-dice-test"
    model_name = None

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput:
        return DMTurnOutput(
            narration="This response must not be committed.",
            dice_requests=[
                DiceRequest(
                    notation="1d20",
                    modifier=99,
                    purpose="Attempt to bypass authoritative resolution",
                )
            ],
        )


def test_legacy_provider_dice_path_is_rejected_without_mutation(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    app.dependency_overrides[get_dm_provider] = lambda: LegacyDiceProvider()
    response = client.post(
        f"/campaigns/{campaign_id}/turns",
        json={
            "action": "Use the unsafe legacy roll.",
            "actor_character_id": characters[0],
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Legacy provider dice requests are disabled; use the authoritative turn-execution path"
    )
    after = client.get(f"/campaigns/{campaign_id}/state").json()
    assert after == before
    with get_engine().connect() as connection:
        counts = connection.execute(
            text(
                "SELECT (SELECT count(*) FROM turns WHERE campaign_id = :campaign_id), "
                "(SELECT count(*) FROM dice_rolls WHERE campaign_id = :campaign_id)"
            ),
            {"campaign_id": uuid.UUID(campaign_id)},
        ).one()
    assert counts == (0, 0)


class StateChangingInterpreter:
    provider_name = "stale-state-test"
    model_name = None
    interpretation_prompt_version = "stale-state-1"

    def __init__(self, character_id: str) -> None:
        self.character_id = uuid.UUID(character_id)

    def interpret_action(self, context: dict[str, Any], player_action: str) -> NarrativeIntent:
        with get_engine().begin() as connection:
            connection.execute(
                text(
                    "UPDATE characters SET state_revision = state_revision + 1 "
                    "WHERE id = :character_id"
                ),
                {"character_id": self.character_id},
            )
        return NarrativeIntent(
            type="narrative",
            summary="The provider completed against a state that is now stale.",
        )


def test_state_change_during_interpretation_is_rejected(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    app.dependency_overrides[get_turn_interpreter] = lambda: StateChangingInterpreter(characters[0])
    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert response.status_code == 409
    assert response.json()["detail"] == "Acting character state changed during interpretation"
    stored = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert stored["status"] == "failed"
    assert stored["error_code"] == "stale_character_state"
    assert stored["resumable"] is False
    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls").json()
    assert len(calls) == 1
    assert calls[0]["status"] == "succeeded"


class TransactionInspectingProvider:
    provider_name = "transaction-test"
    model_name = None
    interpretation_prompt_version = "transaction-test-1"

    def __init__(self, session: Session) -> None:
        self.session = session
        self.transaction_was_open: bool | None = None

    def interpret_action(self, context: dict[str, Any], player_action: str) -> NarrativeIntent:
        self.transaction_was_open = self.session.in_transaction()
        return NarrativeIntent(
            type="narrative",
            summary="No database transaction was open during the provider operation.",
        )


def test_provider_operation_runs_without_open_database_transaction(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    with Session(get_engine()) as session:
        provider = TransactionInspectingProvider(session)
        result = interpret_turn_execution(
            session,
            uuid.UUID(campaign_id),
            uuid.UUID(turn_id),
            provider,
        )
    assert provider.transaction_was_open is False
    assert result.turn.status == "intent_ready"
