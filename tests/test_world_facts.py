import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from alembic import command
from app.api import app
from app.db import get_engine, get_session_factory
from app.llm.factory import get_turn_interpreter, get_turn_narrator
from app.models import WorldFact
from app.schemas import (
    CampaignState,
    ClueRecord,
    DiscoveryRecord,
    NPCAttitudeSet,
    PromiseRecord,
    RelationshipNoteAdd,
    TurnNarrationOutput,
    WorldFactRead,
    WorldFactReveal,
    WorldFactSupersede,
    WorldStateRead,
)
from app.services import _provider_context, record_world_fact
from app.turn_interpretation import NarrativeIntent
from tests.test_world_presence import _create_turn, _ready_world


class FixedNarrator:
    provider_name = "m3-fact-fixture"
    model_name = None
    narration_prompt_version = "m3-fact-fixture-1"

    def __init__(self, changes: list, captured: dict[str, Any] | None = None) -> None:
        self.changes = changes
        self.captured = captured

    def narrate_outcome(self, context: dict[str, Any], *args: Any) -> TurnNarrationOutput:
        if self.captured is not None:
            self.captured.update(context)
        return TurnNarrationOutput(
            narration="The conversation leaves a durable narrative consequence.",
            state_changes=self.changes,
        )


def _finalize_with(
    client: TestClient,
    campaign_id: str,
    actor_id: str,
    npc_id: str,
    changes: list,
    *,
    captured: dict[str, Any] | None = None,
) -> Any:
    created = _create_turn(client, campaign_id, actor_id, target_npc_id=npc_id)
    assert created.status_code == 201, created.text
    turn_id = created.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text
    app.dependency_overrides[get_turn_narrator] = lambda: FixedNarrator(changes, captured)
    return client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")


def test_typed_facts_persist_without_changing_character_mechanics(client: TestClient) -> None:
    campaign_id, characters, npcs = _ready_world(client)
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    response = _finalize_with(
        client,
        campaign_id,
        characters[0],
        npcs[0],
        [
            NPCAttitudeSet(type="npc_attitude_set", npc_id=npcs[0], attitude="friendly"),
            RelationshipNoteAdd(
                type="relationship_note_add", npc_id=npcs[0], note="Mira trusts Arin's word."
            ),
            PromiseRecord(
                type="promise_record", npc_id=npcs[0], promise="Mira will keep a room available."
            ),
            DiscoveryRecord(
                type="discovery_record", discovery="The northern road floods after heavy rain."
            ),
            ClueRecord(
                type="clue_record",
                subject_npc_id=npcs[0],
                clue="Mira recognizes the sigil on the sealed letter.",
            ),
        ],
    )
    assert response.status_code == 200, response.text
    assert response.json()["turn"]["world_revision_before"] == 0
    assert response.json()["turn"]["world_revision_after"] == 5

    world = client.get(f"/campaigns/{campaign_id}/world").json()
    assert world["world_revision"] == 5
    assert {fact["fact_type"] for fact in world["facts"]} == {
        "npc_attitude",
        "relationship_note",
        "promise",
        "discovery",
        "clue",
    }
    assert all("visibility" not in fact for fact in world["facts"])
    after = client.get(f"/campaigns/{campaign_id}/state").json()
    assert [(row["hp"], row["inventory"]) for row in after["characters"]] == [
        (row["hp"], row["inventory"]) for row in before["characters"]
    ]

    get_engine().dispose()
    restarted = client.get(f"/campaigns/{campaign_id}/world")
    assert restarted.status_code == 200
    assert restarted.json()["facts"] == world["facts"]


def test_attitude_and_fact_supersession_preserve_history(client: TestClient) -> None:
    campaign_id, characters, npcs = _ready_world(client)
    with get_session_factory()() as session:
        attitude = record_world_fact(
            session,
            uuid.UUID(campaign_id),
            fact_type="npc_attitude",
            value="neutral",
            subject_npc_id=uuid.UUID(npcs[0]),
        )
        promise = record_world_fact(
            session,
            uuid.UUID(campaign_id),
            fact_type="promise",
            value="Mira will ask the caravan master.",
            subject_npc_id=uuid.UUID(npcs[0]),
        )

    response = _finalize_with(
        client,
        campaign_id,
        characters[0],
        npcs[0],
        [
            NPCAttitudeSet(type="npc_attitude_set", npc_id=npcs[0], attitude="wary"),
            WorldFactSupersede(
                type="world_fact_supersede",
                fact_id=promise.id,
                expected_revision=0,
                value="Mira has asked the caravan master and awaits an answer.",
            ),
        ],
    )
    assert response.status_code == 200, response.text
    assert response.json()["turn"]["world_revision_after"] == 4
    visible = client.get(f"/campaigns/{campaign_id}/world").json()["facts"]
    assert {fact["value"] for fact in visible} == {
        "wary",
        "Mira has asked the caravan master and awaits an answer.",
    }

    with get_session_factory()() as session:
        history = list(
            session.scalars(
                select(WorldFact)
                .where(WorldFact.campaign_id == uuid.UUID(campaign_id))
                .order_by(WorldFact.fact_type, WorldFact.revision)
            )
        )
    old_attitude = next(fact for fact in history if fact.id == attitude.id)
    new_attitude = next(
        fact for fact in history if fact.fact_type == "npc_attitude" and fact.status == "current"
    )
    old_promise = next(fact for fact in history if fact.id == promise.id)
    new_promise = next(
        fact for fact in history if fact.fact_type == "promise" and fact.status == "current"
    )
    assert (old_attitude.status, new_attitude.revision, new_attitude.supersedes_fact_id) == (
        "superseded",
        1,
        old_attitude.id,
    )
    assert (old_promise.status, new_promise.revision, new_promise.supersedes_fact_id) == (
        "superseded",
        1,
        old_promise.id,
    )
    assert old_attitude.superseded_by_event_id is not None
    assert old_promise.superseded_by_event_id is not None


def test_hidden_fact_is_excluded_until_explicit_reveal(client: TestClient) -> None:
    campaign_id, characters, npcs = _ready_world(client)
    secret = "The silver key is hidden beneath the third stair."
    with get_session_factory()() as session:
        hidden = record_world_fact(
            session,
            uuid.UUID(campaign_id),
            fact_type="clue",
            value=secret,
            visibility="dm_only",
        )

    assert secret not in client.get(f"/campaigns/{campaign_id}/world").text
    assert secret not in client.get(f"/campaigns/{campaign_id}/events").text
    captured_interpretation: dict[str, Any] = {}

    class CapturingInterpreter:
        provider_name = "fact-context-capture"
        model_name = None
        interpretation_prompt_version = "fact-context-capture-1"

        def interpret_action(self, context: dict[str, Any], *args: Any) -> NarrativeIntent:
            captured_interpretation.update(context)
            return NarrativeIntent(type="narrative", summary="Look for a clue.")

    app.dependency_overrides[get_turn_interpreter] = lambda: CapturingInterpreter()
    created = _create_turn(client, campaign_id, characters[0], target_npc_id=npcs[0])
    turn_id = created.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200
    assert secret not in json.dumps(captured_interpretation)
    assert str(hidden.id) not in json.dumps(captured_interpretation)
    cancelled = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/cancel")
    assert cancelled.status_code == 200
    app.dependency_overrides.pop(get_turn_interpreter)

    captured_narration: dict[str, Any] = {}
    revealed = _finalize_with(
        client,
        campaign_id,
        characters[0],
        npcs[0],
        [WorldFactReveal(type="world_fact_reveal", fact_id=hidden.id, expected_revision=0)],
        captured=captured_narration,
    )
    assert revealed.status_code == 200, revealed.text
    assert secret not in json.dumps(captured_narration)
    world = client.get(f"/campaigns/{campaign_id}/world").json()
    revealed_fact = next(fact for fact in world["facts"] if fact["id"] == str(hidden.id))
    assert revealed_fact["value"] == secret
    assert revealed_fact["revision"] == 1
    reveal_events = [
        event
        for event in client.get(f"/campaigns/{campaign_id}/events").json()
        if event["event_type"] == "world_fact_revealed"
    ]
    assert reveal_events[0]["payload"]["value"] == secret


def test_invalid_world_batch_rolls_back_all_facts_and_mechanics(client: TestClient) -> None:
    campaign_id, characters, npcs = _ready_world(client)
    other_campaign, _other_characters, other_npcs = _ready_world(client)
    assert other_campaign != campaign_id
    before = client.get(f"/campaigns/{campaign_id}/state").json()
    response = _finalize_with(
        client,
        campaign_id,
        characters[0],
        npcs[0],
        [
            RelationshipNoteAdd(
                type="relationship_note_add", npc_id=npcs[0], note="This must roll back."
            ),
            PromiseRecord(
                type="promise_record",
                npc_id=other_npcs[0],
                promise="A cross-campaign promise must be rejected.",
            ),
        ],
    )
    assert response.status_code == 422
    assert client.get(f"/campaigns/{campaign_id}/world").json()["facts"] == []
    after = client.get(f"/campaigns/{campaign_id}/state").json()
    assert after["characters"] == before["characters"]
    turn_id = response.request.url.path.split("/")[-2]
    stored = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}").json()
    assert stored["status"] == "failed"
    assert stored["error_code"] == "invalid_state_proposal"


def test_unknown_or_mechanical_fact_shape_is_rejected_by_provider_contract(
    client: TestClient,
) -> None:
    campaign_id, characters, npcs = _ready_world(client)

    class InvalidNarrator:
        provider_name = "invalid-fact-fixture"
        model_name = None
        narration_prompt_version = "invalid-fact-fixture-1"

        def narrate_outcome(self, *args: Any) -> dict[str, Any]:
            return {
                "narration": "An invalid mechanical reward is proposed.",
                "resolution_id": None,
                "acknowledged_outcome": None,
                "state_changes": [
                    {
                        "type": "promise_record",
                        "npc_id": npcs[0],
                        "promise": "Mira promises assistance.",
                        "modifier": 2,
                    }
                ],
            }

    created = _create_turn(client, campaign_id, characters[0], target_npc_id=npcs[0])
    turn_id = created.json()["id"]
    assert client.post(
        f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret"
    ).status_code == 200
    app.dependency_overrides[get_turn_narrator] = lambda: InvalidNarrator()
    response = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert response.status_code == 502
    assert response.json()["detail"]["error_code"] == "invalid_structured_output"
    assert client.get(f"/campaigns/{campaign_id}/world").json()["facts"] == []


def test_provider_context_caps_large_fact_history(client: TestClient) -> None:
    campaign_id, _characters, _npcs = _ready_world(client)
    state = CampaignState.model_validate(client.get(f"/campaigns/{campaign_id}/state").json())
    world = WorldStateRead.model_validate(client.get(f"/campaigns/{campaign_id}/world").json())
    now = datetime.now(UTC)
    facts = [
        WorldFactRead(
            id=uuid.uuid4(),
            subject_npc_id=None,
            fact_type="discovery",
            value=f"Discovery {index}",
            status="current",
            revision=0,
            created_at=now,
        )
        for index in range(101)
    ]
    context = _provider_context(state, world.model_copy(update={"facts": facts}))
    assert len(context["world"]["facts"]) == 50
    assert context["world"]["facts_truncated"] == 51
    assert context["world"]["facts"][0]["value"] == "Discovery 51"
    assert len(json.dumps(context)) < 30_000


def test_migration_refuses_to_discard_world_facts(client: TestClient) -> None:
    campaign_id, _characters, _npcs = _ready_world(client)
    with get_session_factory()() as session:
        record_world_fact(
            session,
            uuid.UUID(campaign_id),
            fact_type="discovery",
            value="A durable migration fact.",
        )
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after M3.2 world facts"):
        command.downgrade(config, "0008_world_presence")
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
            "0009_world_facts"
        )
