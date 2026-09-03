import json
import uuid
from pathlib import Path
from typing import Any

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from alembic import command
from app.api import app
from app.db import get_engine
from app.llm.factory import get_turn_narrator
from app.schemas import (
    DecisionOpen,
    DiscoveryRecord,
    NPCAttitudeSet,
    QuestCreate,
    QuestObjectiveTransition,
    QuestTransition,
    TurnNarrationOutput,
)
from tests.test_world_presence import _ready_world


class BranchNarrator:
    provider_name = "m3-branch-fixture"
    model_name = None
    narration_prompt_version = "m3-branch-fixture-1"

    def __init__(self, changes: list, captured: dict[str, Any] | None = None) -> None:
        self.changes = changes
        self.captured = captured

    def narrate_outcome(self, context: dict[str, Any], *args: Any) -> TurnNarrationOutput:
        if self.captured is not None:
            self.captured.update(context)
        return TurnNarrationOutput(
            narration="The chosen path becomes part of the campaign history.",
            state_changes=self.changes,
        )


def _run_turn(
    client: TestClient,
    campaign_id: str,
    actor_id: str,
    changes: list,
    *,
    command_id: str | None = None,
    decision_id: str | None = None,
    option_key: str | None = None,
    captured: dict[str, Any] | None = None,
) -> Any:
    payload: dict[str, Any] = {
        "command_id": command_id or str(uuid.uuid4()),
        "action": "Choose the next course of action.",
        "actor_character_id": actor_id,
    }
    if decision_id is not None:
        payload["decision_id"] = decision_id
        payload["decision_option_key"] = option_key
    created = client.post(f"/campaigns/{campaign_id}/turn-executions", json=payload)
    assert created.status_code == 201, created.text
    turn_id = created.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text
    app.dependency_overrides[get_turn_narrator] = lambda: BranchNarrator(changes, captured)
    return client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")


def _create_quest(client: TestClient, campaign_id: str, actor_id: str) -> dict[str, Any]:
    response = _run_turn(
        client,
        campaign_id,
        actor_id,
        [
            QuestCreate(
                type="quest_create",
                quest_key="broken_bridge",
                title="The Broken Bridge",
                summary="Choose how the party will cross the gorge.",
                objectives=[
                    {
                        "objective_key": "cross_gorge",
                        "title": "Cross the gorge",
                        "status": "active",
                    }
                ],
            )
        ],
    )
    assert response.status_code == 200, response.text
    return client.get(f"/campaigns/{campaign_id}/world").json()["quests"][0]


def _open_branch(
    client: TestClient, campaign_id: str, actor_id: str, objective_id: str
) -> dict[str, Any]:
    response = _run_turn(
        client,
        campaign_id,
        actor_id,
        [
            DecisionOpen(
                type="decision_open",
                decision_key="gorge_route",
                prompt="How will the party cross the gorge?",
                options=[
                    {
                        "option_key": "repair_bridge",
                        "label": "Repair the bridge",
                        "description": "Restore the old span and cross openly.",
                        "consequences": [
                            {
                                "type": "transition_objective",
                                "objective_id": objective_id,
                                "expected_revision": 0,
                                "status": "completed",
                            },
                            {
                                "type": "record_fact",
                                "fact_type": "discovery",
                                "value": "The party repaired and crossed the old bridge.",
                            },
                        ],
                    },
                    {
                        "option_key": "take_tunnel",
                        "label": "Take the tunnel",
                        "description": "Abandon the bridge and descend underground.",
                        "consequences": [
                            {
                                "type": "transition_objective",
                                "objective_id": objective_id,
                                "expected_revision": 0,
                                "status": "failed",
                            },
                            {
                                "type": "record_fact",
                                "fact_type": "discovery",
                                "value": "The party abandoned the bridge for the hidden tunnel.",
                            },
                        ],
                    },
                ],
            )
        ],
    )
    assert response.status_code == 200, response.text
    return client.get(f"/campaigns/{campaign_id}/world").json()["decisions"][0]


def test_quests_and_two_to_four_option_decisions_are_durable(client: TestClient) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    quest = _create_quest(client, campaign_id, characters[0])
    decision = _open_branch(client, campaign_id, characters[0], quest["objectives"][0]["id"])

    assert quest["status"] == "active"
    assert quest["objectives"][0]["status"] == "active"
    assert decision["status"] == "open"
    assert [option["option_key"] for option in decision["options"]] == [
        "repair_bridge",
        "take_tunnel",
    ]
    assert "consequences" not in json.dumps(decision)

    get_engine().dispose()
    restarted = client.get(f"/campaigns/{campaign_id}/world")
    assert restarted.status_code == 200
    assert restarted.json()["quests"][0]["id"] == quest["id"]
    assert restarted.json()["decisions"][0]["id"] == decision["id"]


def test_explicit_choices_diverge_deterministically_and_are_explainable(
    client: TestClient,
) -> None:
    results: list[dict[str, Any]] = []
    for option_key in ("repair_bridge", "take_tunnel"):
        campaign_id, characters, _npcs = _ready_world(client)
        quest = _create_quest(client, campaign_id, characters[0])
        decision = _open_branch(client, campaign_id, characters[0], quest["objectives"][0]["id"])
        captured: dict[str, Any] = {}
        selected = _run_turn(
            client,
            campaign_id,
            characters[0],
            [],
            decision_id=decision["id"],
            option_key=option_key,
            captured=captured,
        )
        assert selected.status_code == 200, selected.text
        world = client.get(f"/campaigns/{campaign_id}/world").json()
        events = client.get(f"/campaigns/{campaign_id}/events").json()
        assert captured["world"]["selected_choice"]["option_key"] == option_key
        assert captured["world"]["selected_choice"]["consequences"]
        branch_events = [
            event["event_type"]
            for event in events
            if event["event_type"]
            in {
                "decision_selected",
                "quest_objective_status_changed",
                "world_fact_recorded",
                "dm_response",
            }
        ][-4:]
        assert branch_events == [
            "decision_selected",
            "quest_objective_status_changed",
            "world_fact_recorded",
            "dm_response",
        ]
        results.append(world)

    assert results[0]["quests"][0]["objectives"][0]["status"] == "completed"
    assert results[1]["quests"][0]["objectives"][0]["status"] == "failed"
    assert results[0]["facts"][0]["value"] != results[1]["facts"][0]["value"]
    assert results[0]["decisions"][0]["selected_option_key"] == "repair_bridge"
    assert results[1]["decisions"][0]["selected_option_key"] == "take_tunnel"


def test_choice_idempotency_conflict_and_double_selection_rejection(client: TestClient) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    quest = _create_quest(client, campaign_id, characters[0])
    decision = _open_branch(client, campaign_id, characters[0], quest["objectives"][0]["id"])
    command_id = str(uuid.uuid4())
    payload = {
        "command_id": command_id,
        "action": "Choose the next course of action.",
        "actor_character_id": characters[0],
        "decision_id": decision["id"],
        "decision_option_key": "repair_bridge",
    }
    created = client.post(f"/campaigns/{campaign_id}/turn-executions", json=payload)
    assert created.status_code == 201
    repeated = client.post(f"/campaigns/{campaign_id}/turn-executions", json=payload)
    assert repeated.status_code == 201
    assert repeated.json()["id"] == created.json()["id"]
    changed = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={**payload, "decision_option_key": "take_tunnel"},
    )
    assert changed.status_code == 409
    assert "different turn input" in changed.json()["detail"]
    assert (
        client.post(
            f"/campaigns/{campaign_id}/turn-executions/{created.json()['id']}/interpret"
        ).status_code
        == 200
    )
    app.dependency_overrides[get_turn_narrator] = lambda: BranchNarrator([])
    finalized = client.post(
        f"/campaigns/{campaign_id}/turn-executions/{created.json()['id']}/finalize"
    )
    assert finalized.status_code == 200

    second = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={**payload, "command_id": str(uuid.uuid4())},
    )
    assert second.status_code == 409
    assert second.json()["detail"] == "Decision has already been selected"


def test_illegal_or_partial_quest_batch_rolls_back_every_change(client: TestClient) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    quest = _create_quest(client, campaign_id, characters[0])
    objective = quest["objectives"][0]
    before = client.get(f"/campaigns/{campaign_id}/world").json()
    response = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            DiscoveryRecord(type="discovery_record", discovery="This must roll back."),
            QuestObjectiveTransition(
                type="quest_objective_transition",
                objective_id=objective["id"],
                expected_revision=9,
                status="completed",
            ),
        ],
    )
    assert response.status_code == 422
    after = client.get(f"/campaigns/{campaign_id}/world").json()
    assert after == before


def test_quest_and_objective_transitions_enforce_revisions_and_terminal_states(
    client: TestClient,
) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    quest = _create_quest(client, campaign_id, characters[0])
    objective = quest["objectives"][0]
    completed = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            QuestObjectiveTransition(
                type="quest_objective_transition",
                objective_id=objective["id"],
                expected_revision=0,
                status="completed",
            )
        ],
    )
    assert completed.status_code == 200
    finished = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            QuestTransition(
                type="quest_transition",
                quest_id=quest["id"],
                expected_revision=0,
                status="completed",
            )
        ],
    )
    assert finished.status_code == 200
    world = client.get(f"/campaigns/{campaign_id}/world").json()
    assert world["quests"][0]["status"] == "completed"
    assert world["quests"][0]["revision"] == 1

    rejected = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            QuestTransition(
                type="quest_transition",
                quest_id=quest["id"],
                expected_revision=1,
                status="failed",
            )
        ],
    )
    assert rejected.status_code == 422
    assert "Only an active quest" in rejected.json()["detail"]


def test_decision_contract_rejects_implicit_rewards_and_bad_option_counts() -> None:
    base = {
        "type": "decision_open",
        "decision_key": "reward_test",
        "prompt": "Choose.",
    }
    with pytest.raises(ValidationError):
        DecisionOpen.model_validate(
            {
                **base,
                "options": [{"option_key": "only", "label": "Only option", "consequences": []}],
            }
        )
    with pytest.raises(ValidationError):
        DecisionOpen.model_validate(
            {
                **base,
                "options": [
                    {
                        "option_key": "a",
                        "label": "A",
                        "consequences": [{"type": "hp_delta", "amount": 5}],
                    },
                    {"option_key": "b", "label": "B", "consequences": []},
                ],
            }
        )


def test_branch_consequence_cannot_overlap_narrator_attitude_proposal(
    client: TestClient,
) -> None:
    campaign_id, characters, npcs = _ready_world(client)
    opened = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            DecisionOpen(
                type="decision_open",
                decision_key="mira_reply",
                prompt="How should the party answer Mira?",
                options=[
                    {
                        "option_key": "reassure",
                        "label": "Reassure her",
                        "consequences": [
                            {
                                "type": "record_fact",
                                "fact_type": "npc_attitude",
                                "subject_npc_id": npcs[0],
                                "value": "friendly",
                            }
                        ],
                    },
                    {"option_key": "leave", "label": "Leave", "consequences": []},
                ],
            )
        ],
    )
    assert opened.status_code == 200
    decision = client.get(f"/campaigns/{campaign_id}/world").json()["decisions"][0]
    rejected = _run_turn(
        client,
        campaign_id,
        characters[0],
        [NPCAttitudeSet(type="npc_attitude_set", npc_id=npcs[0], attitude="wary")],
        decision_id=decision["id"],
        option_key="reassure",
    )
    assert rejected.status_code == 422
    world = client.get(f"/campaigns/{campaign_id}/world").json()
    assert world["decisions"][0]["status"] == "open"
    assert world["facts"] == []


def test_branch_consequence_cannot_duplicate_narrator_fact_proposal(
    client: TestClient,
) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    discovery = "The party lit the Old Tower beacon for the Lantern Watch."
    opened = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            DecisionOpen(
                type="decision_open",
                decision_key="tower_beacon",
                prompt="Should the party light the beacon?",
                options=[
                    {
                        "option_key": "light",
                        "label": "Light the beacon",
                        "consequences": [
                            {
                                "type": "record_fact",
                                "fact_type": "discovery",
                                "value": discovery,
                            }
                        ],
                    },
                    {"option_key": "leave_dark", "label": "Leave it dark", "consequences": []},
                ],
            )
        ],
    )
    assert opened.status_code == 200
    decision = client.get(f"/campaigns/{campaign_id}/world").json()["decisions"][0]

    rejected = _run_turn(
        client,
        campaign_id,
        characters[0],
        [DiscoveryRecord(type="discovery_record", discovery=discovery)],
        decision_id=decision["id"],
        option_key="light",
    )

    assert rejected.status_code == 422
    assert "cannot duplicate a narrator fact proposal" in rejected.json()["detail"]
    world = client.get(f"/campaigns/{campaign_id}/world").json()
    assert world["decisions"][0]["status"] == "open"
    assert world["facts"] == []


def test_migration_refuses_to_discard_quest_or_decision_data(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "app.services._project_completed_turn_best_effort", lambda _session, _turn: None
    )
    campaign_id, characters, _npcs = _ready_world(client)
    _create_quest(client, campaign_id, characters[0])
    with get_engine().connect() as connection:
        expected_revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after M3.3 quest or decision data"):
        command.downgrade(config, "0009_world_facts")
    with get_engine().connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == expected_revision
        )
