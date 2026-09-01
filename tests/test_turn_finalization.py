import uuid
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import app
from app.db import get_engine
from app.dice import DiceService, get_dice_service
from app.llm.factory import get_turn_narrator
from app.schemas import TurnNarrationOutput
from app.services import finalize_turn_execution
from app.turn_interpretation import TurnIntent


class FixedRandom:
    algorithm_version = "m2-finalization-fixed-1.0.0"

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


def _ready_campaign(client: TestClient) -> tuple[str, list[str]]:
    campaign = client.post("/campaigns", json={"name": "M2 Finalization"})
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
    turn_id = response.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text
    return turn_id


def _character(state: dict[str, Any], character_id: str) -> dict[str, Any]:
    return next(character for character in state["characters"] if character["id"] == character_id)


def _turn_event_types(turn_id: str) -> list[str]:
    with get_engine().connect() as connection:
        return list(
            connection.execute(
                text(
                    "SELECT event_type FROM campaign_events "
                    "WHERE turn_id = :turn_id ORDER BY sequence"
                ),
                {"turn_id": uuid.UUID(turn_id)},
            ).scalars()
        )


def test_dialogue_finalizes_once_with_audited_narration(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin greets the innkeeper.")

    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["turn"]["status"] == "completed"
    assert body["turn"]["completed_at"] is not None
    assert body["turn"]["narration_prompt_version"] == "deterministic-narration-1.0.0"
    assert "innkeeper" in body["turn"]["narration"].casefold()
    assert body["resolution"] is None
    assert _turn_event_types(turn_id) == ["player_action", "dm_response"]

    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls")
    assert [(call["stage"], call["attempt"]) for call in calls.json()] == [
        ("interpretation", 1),
        ("narration", 1),
    ]

    class MustNotRunNarrator:
        provider_name = "must-not-run"
        model_name = None
        narration_prompt_version = "must-not-run-1"

        def narrate_outcome(self, *args: Any) -> TurnNarrationOutput:
            raise AssertionError("a completed turn must be idempotent")

    app.dependency_overrides[get_turn_narrator] = lambda: MustNotRunNarrator()
    repeated = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert repeated.status_code == 200
    assert repeated.json()["turn"]["structured_output"] == body["turn"]["structured_output"]
    assert _turn_event_types(turn_id) == ["player_action", "dm_response"]


def test_movement_and_inventory_proposals_update_only_typed_state(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    movement = _execution(client, campaign_id, characters[0], "Arin travels to the Old Tower.")
    moved = client.post(f"/campaigns/{campaign_id}/turn-executions/{movement}/finalize")
    assert moved.status_code == 200, moved.text
    assert moved.json()["state"]["location"]["name"] == "Old Tower"
    assert _turn_event_types(movement) == ["player_action", "dm_response", "state_changed"]

    inventory = _execution(
        client,
        campaign_id,
        characters[0],
        "Arin uses a Javelin to mark the trail.",
    )
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    before_actor = _character(before, characters[0])
    used = client.post(f"/campaigns/{campaign_id}/turn-executions/{inventory}/finalize")
    assert used.status_code == 200, used.text
    after_actor = _character(used.json()["state"], characters[0])
    other = _character(used.json()["state"], characters[1])
    assert after_actor["inventory"]["Javelin"] == before_actor["inventory"]["Javelin"] - 1
    assert after_actor["state_revision"] == before_actor["state_revision"] + 1
    assert other["inventory"]["Javelin"] == 8


def test_check_outcome_controls_success_movement_and_failure_damage(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    _fixed_dice([7])
    success_turn = _execution(client, campaign_id, characters[0], "Arin climbs the wall.")
    succeeded = client.post(f"/campaigns/{campaign_id}/turn-executions/{success_turn}/finalize")
    assert succeeded.status_code == 200, succeeded.text
    success = succeeded.json()
    assert success["resolution"]["outcome"] == "success"
    assert "succeeds" in success["turn"]["narration"].casefold()
    assert success["turn"]["structured_output"]["resolution_id"] == success["resolution"]["id"]
    assert success["turn"]["structured_output"]["acknowledged_outcome"] == "success"
    assert success["state"]["location"]["name"] == "Wall Top"
    assert _turn_event_types(success_turn) == [
        "player_action",
        "rule_resolved",
        "dm_response",
        "state_changed",
    ]

    _fixed_dice([9])
    failure_turn = _execution(client, campaign_id, characters[1], "Bryn climbs the wall.")
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    failed = client.post(f"/campaigns/{campaign_id}/turn-executions/{failure_turn}/finalize")
    assert failed.status_code == 200, failed.text
    failure = failed.json()
    assert failure["resolution"]["outcome"] == "failure"
    assert "fails" in failure["turn"]["narration"].casefold()
    assert _character(failure["state"], characters[1])["hp"] == (
        _character(before, characters[1])["hp"] - 2
    )
    assert failure["state"]["location"]["name"] == "Wall Top"


class InvalidAtomicNarrator:
    provider_name = "invalid-atomic-test"
    model_name = None
    narration_prompt_version = "invalid-atomic-1"

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: Any,
    ) -> TurnNarrationOutput:
        return TurnNarrationOutput(
            narration="A valid change is followed by an invalid one.",
            state_changes=[
                {"type": "hp_delta", "amount": -1, "reason": "First proposal"},
                {
                    "type": "inventory_change",
                    "item_name": "Javelin",
                    "quantity_delta": -99,
                    "reason": "Invalid second proposal",
                },
            ],
        )


def test_invalid_proposal_is_audited_without_partial_state_or_final_events(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin considers the supplies.")
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    app.dependency_overrides[get_turn_narrator] = lambda: InvalidAtomicNarrator()

    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 422
    after = client.get(f"/campaigns/{campaign_id}/state").json()
    assert _character(after, characters[0]) == _character(before, characters[0])
    assert after["location"] == before["location"]
    assert _turn_event_types(turn_id) == ["player_action"]
    turn = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert turn["status"] == "failed"
    assert turn["error_code"] == "invalid_state_proposal"
    assert turn["resumable"] is True
    assert turn["resume_status"] == "intent_ready"
    calls = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls").json()
    assert calls[-1]["stage"] == "narration"
    assert calls[-1]["status"] == "succeeded"
    assert calls[-1]["structured_output"] is not None


class NarrativeClaimOnlyProvider:
    provider_name = "claim-only-test"
    model_name = None
    narration_prompt_version = "claim-only-1"

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: Any,
    ) -> TurnNarrationOutput:
        return TurnNarrationOutput(narration="The prose claims that Arin's HP falls to 1.")


def test_narration_text_alone_cannot_create_a_mechanical_effect(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin tells a dramatic story.")
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    app.dependency_overrides[get_turn_narrator] = lambda: NarrativeClaimOnlyProvider()

    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 200, response.text
    after = response.json()["state"]
    assert _character(after, characters[0])["hp"] == _character(before, characters[0])["hp"]
    assert _turn_event_types(turn_id) == ["player_action", "dm_response"]


class InvalidStructuredNarrator:
    provider_name = "invalid-structured-test"
    model_name = None
    narration_prompt_version = "invalid-structured-1"

    def narrate_outcome(self, *args: Any) -> dict[str, Any]:
        return {"narration": "Invalid extra mechanics.", "dice_faces": [20]}


def test_untyped_provider_output_fails_safely_and_can_be_resumed(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin speaks.")
    app.dependency_overrides[get_turn_narrator] = lambda: InvalidStructuredNarrator()

    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 502
    turn = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert turn["status"] == "failed"
    assert turn["error_code"] == "invalid_structured_output"
    assert turn["resume_status"] == "intent_ready"
    assert _turn_event_types(turn_id) == ["player_action"]


class OutcomeMismatchNarrator:
    provider_name = "outcome-mismatch-test"
    model_name = None
    narration_prompt_version = "outcome-mismatch-1"

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: Any,
    ) -> TurnNarrationOutput:
        return TurnNarrationOutput(
            narration="The narration contradicts the authoritative result.",
            resolution_id=resolution.id,
            acknowledged_outcome="failure",
        )


def test_narration_must_acknowledge_the_exact_authoritative_outcome(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    _fixed_dice([7])
    turn_id = _execution(client, campaign_id, characters[0], "Arin climbs the wall.")
    app.dependency_overrides[get_turn_narrator] = lambda: OutcomeMismatchNarrator()

    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 502
    assert response.json()["detail"] == "Narration did not acknowledge the stored outcome"
    turn = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert turn["status"] == "failed"
    assert turn["error_code"] == "invalid_outcome_acknowledgement"
    assert turn["resume_status"] == "resolved"
    assert _turn_event_types(turn_id) == ["player_action", "rule_resolved"]


class StateChangingNarrator:
    provider_name = "stale-narration-test"
    model_name = None
    narration_prompt_version = "stale-narration-1"

    def __init__(self, character_id: str) -> None:
        self.character_id = uuid.UUID(character_id)

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: Any,
    ) -> TurnNarrationOutput:
        with get_engine().begin() as connection:
            connection.execute(
                text(
                    "UPDATE characters SET state_revision = state_revision + 1 "
                    "WHERE id = :character_id"
                ),
                {"character_id": self.character_id},
            )
        return TurnNarrationOutput(
            narration="This proposal was generated against stale state.",
            state_changes=[{"type": "hp_delta", "amount": -1, "reason": "Must not be applied"}],
        )


def test_state_change_during_narration_rejects_all_proposals(client: TestClient) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin pauses.")
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    app.dependency_overrides[get_turn_narrator] = lambda: StateChangingNarrator(characters[0])

    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 409
    after = client.get(f"/campaigns/{campaign_id}/state").json()
    assert _character(after, characters[0])["hp"] == _character(before, characters[0])["hp"]
    assert _character(after, characters[0])["state_revision"] == (
        _character(before, characters[0])["state_revision"] + 1
    )
    assert _turn_event_types(turn_id) == ["player_action"]
    turn = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert turn["status"] == "failed"
    assert turn["error_code"] == "stale_campaign_state"


class TransactionInspectingNarrator:
    provider_name = "transaction-narration-test"
    model_name = None
    narration_prompt_version = "transaction-narration-1"

    def __init__(self, session: Session) -> None:
        self.session = session
        self.transaction_was_open: bool | None = None

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: Any,
    ) -> TurnNarrationOutput:
        self.transaction_was_open = self.session.in_transaction()
        return TurnNarrationOutput(narration="Narration ran outside a database transaction.")


def test_narration_provider_runs_without_an_open_database_transaction(
    client: TestClient,
) -> None:
    campaign_id, characters = _ready_campaign(client)
    turn_id = _execution(client, campaign_id, characters[0], "Arin greets the innkeeper.")
    with Session(get_engine()) as session:
        provider = TransactionInspectingNarrator(session)
        result = finalize_turn_execution(
            session,
            uuid.UUID(campaign_id),
            uuid.UUID(turn_id),
            provider,
        )
    assert provider.transaction_was_open is False
    assert result.turn.status == "completed"
