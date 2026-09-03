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
from app.db import get_engine, get_session_factory
from app.models import (
    NPC,
    Campaign,
    DecisionOption,
    DecisionPoint,
    Faction,
    FactionRelationship,
    Quest,
    QuestObjective,
    SceneNPCPresence,
    WorldFact,
)
from app.schemas import (
    CampaignState,
    FactionAttitudeSet,
    FactionCreate,
    FactionMembershipSet,
    NarrativeTimeAdvance,
)
from app.services import (
    _add_event,
    _provider_context,
    get_campaign_state,
    get_world_state,
    record_faction,
    record_faction_relationship,
    record_world_fact,
)
from tests.test_quests_decisions import _run_turn
from tests.test_world_presence import _ready_world


def _create_faction(client: TestClient, campaign_id: str, actor_id: str) -> dict[str, Any]:
    response = _run_turn(
        client,
        campaign_id,
        actor_id,
        [
            FactionCreate(
                type="faction_create",
                faction_key="lantern_watch",
                name="Lantern Watch",
                description="Wardens of the northern road.",
            )
        ],
    )
    assert response.status_code == 200, response.text
    return client.get(f"/campaigns/{campaign_id}/world").json()["factions"][0]


def _cancel_latest_turn(client: TestClient, campaign_id: str) -> None:
    turns = client.get(f"/campaigns/{campaign_id}/turn-executions").json()
    cancelled = client.post(f"/campaigns/{campaign_id}/turn-executions/{turns[-1]['id']}/cancel")
    assert cancelled.status_code == 200, cancelled.text


def test_factions_relationships_and_time_are_durable_but_mechanically_inert(
    client: TestClient,
) -> None:
    campaign_id, characters, npcs = _ready_world(client)
    before_state = client.get(f"/campaigns/{campaign_id}/state").json()
    faction = _create_faction(client, campaign_id, characters[0])
    changed = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            FactionAttitudeSet(
                type="faction_attitude_set",
                faction_id=faction["id"],
                attitude="friendly",
            ),
            FactionMembershipSet(
                type="faction_membership_set",
                faction_id=faction["id"],
                member_type="character",
                member_id=characters[0],
                membership="member",
            ),
            FactionMembershipSet(
                type="faction_membership_set",
                faction_id=faction["id"],
                member_type="npc",
                member_id=npcs[0],
                membership="associate",
            ),
            NarrativeTimeAdvance(
                type="narrative_time_advance",
                minutes=90,
                reason="The party attends the Watch briefing.",
            ),
        ],
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["turn"]["world_revision_after"] == 5

    world = client.get(f"/campaigns/{campaign_id}/world").json()
    assert world["narrative_time_minutes"] == 90
    relationships = world["factions"][0]["relationships"]
    assert {(relation["relation_type"], relation["value"]) for relation in relationships} == {
        ("attitude", "friendly"),
        ("membership", "member"),
        ("membership", "associate"),
    }
    after_state = client.get(f"/campaigns/{campaign_id}/state").json()
    assert [
        (character["hp"], character["resources"], character["state_revision"])
        for character in after_state["characters"]
    ] == [
        (character["hp"], character["resources"], character["state_revision"])
        for character in before_state["characters"]
    ]

    attitude = next(row for row in relationships if row["relation_type"] == "attitude")
    membership = next(row for row in relationships if row["character_id"] == characters[0])
    updated = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            FactionAttitudeSet(
                type="faction_attitude_set",
                faction_id=faction["id"],
                expected_revision=attitude["revision"],
                attitude="wary",
            ),
            FactionMembershipSet(
                type="faction_membership_set",
                faction_id=faction["id"],
                member_type="character",
                member_id=characters[0],
                expected_revision=membership["revision"],
                membership="former_member",
            ),
        ],
    )
    assert updated.status_code == 200, updated.text
    get_engine().dispose()
    restarted = client.get(f"/campaigns/{campaign_id}/world")
    assert restarted.status_code == 200
    restarted_relations = restarted.json()["factions"][0]["relationships"]
    assert {row["value"] for row in restarted_relations} == {
        "wary",
        "former_member",
        "associate",
    }
    assert all(row["revision"] == 1 for row in restarted_relations if row["value"] != "associate")


def test_time_bounds_stale_relations_and_partial_batches_write_nothing(
    client: TestClient,
) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    faction = _create_faction(client, campaign_id, characters[0])
    before = client.get(f"/campaigns/{campaign_id}/world").json()
    rejected = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            NarrativeTimeAdvance(type="narrative_time_advance", minutes=30, reason="A short wait."),
            FactionAttitudeSet(
                type="faction_attitude_set",
                faction_id=faction["id"],
                expected_revision=4,
                attitude="hostile",
            ),
        ],
    )
    assert rejected.status_code == 422
    assert client.get(f"/campaigns/{campaign_id}/world").json() == before
    _cancel_latest_turn(client, campaign_id)

    duplicate_time = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            NarrativeTimeAdvance(
                type="narrative_time_advance", minutes=10, reason="First interval."
            ),
            NarrativeTimeAdvance(
                type="narrative_time_advance", minutes=10, reason="Second interval."
            ),
        ],
    )
    assert duplicate_time.status_code == 422
    assert client.get(f"/campaigns/{campaign_id}/world").json() == before

    for minutes in (0, 10_081):
        with pytest.raises(ValidationError):
            NarrativeTimeAdvance(
                type="narrative_time_advance", minutes=minutes, reason="Invalid interval."
            )
    with pytest.raises(ValidationError):
        FactionAttitudeSet.model_validate(
            {
                "type": "faction_attitude_set",
                "faction_id": faction["id"],
                "attitude": "friendly",
                "reputation_score": 10,
            }
        )
    with pytest.raises(ValidationError):
        NarrativeTimeAdvance.model_validate(
            {
                "type": "narrative_time_advance",
                "minutes": 480,
                "reason": "An overnight pause.",
                "rest": True,
            }
        )


def test_faction_and_member_ids_are_campaign_isolated(client: TestClient) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    other_campaign_id, other_characters, _other_npcs = _ready_world(client)
    faction = _create_faction(client, campaign_id, characters[0])
    other_faction = _create_faction(client, other_campaign_id, other_characters[0])

    wrong_faction = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            FactionAttitudeSet(
                type="faction_attitude_set",
                faction_id=other_faction["id"],
                attitude="friendly",
            )
        ],
    )
    assert wrong_faction.status_code == 422
    _cancel_latest_turn(client, campaign_id)
    wrong_member = _run_turn(
        client,
        campaign_id,
        characters[0],
        [
            FactionMembershipSet(
                type="faction_membership_set",
                faction_id=faction["id"],
                member_type="character",
                member_id=other_characters[0],
                membership="member",
            )
        ],
    )
    assert wrong_member.status_code == 422
    assert (
        client.get(f"/campaigns/{campaign_id}/world").json()["factions"][0]["relationships"] == []
    )


def _add_hidden_world_records(campaign_id: uuid.UUID) -> None:
    with get_session_factory()() as session:
        campaign = session.get(Campaign, campaign_id)
        assert campaign is not None
        scene = session.scalar(
            text("SELECT id FROM scenes WHERE campaign_id = :campaign_id AND status = 'active'"),
            {"campaign_id": campaign_id},
        )
        assert scene is not None
        event = _add_event(
            session,
            campaign_id,
            "hidden_world_fixture_created",
            {"secret": "M3.4 hidden fixture"},
            visibility="dm_only",
        )
        npc_id = uuid.uuid4()
        session.add(
            NPC(
                id=npc_id,
                campaign_id=campaign_id,
                name="Veiled Envoy",
                public_description="Hidden NPC description",
                status="active",
                visibility="dm_only",
                revision=0,
                introduced_by_event_id=event.id,
            )
        )
        session.add(
            SceneNPCPresence(
                campaign_id=campaign_id,
                scene_id=scene,
                npc_id=npc_id,
                status="present",
                revision=0,
                arrived_by_event_id=event.id,
            )
        )
        quest_id = uuid.uuid4()
        session.add(
            Quest(
                id=quest_id,
                campaign_id=campaign_id,
                quest_key="hidden_quest",
                title="Hidden Quest Title",
                summary="Hidden quest summary",
                status="active",
                visibility="dm_only",
                revision=0,
                created_by_event_id=event.id,
            )
        )
        session.add(
            QuestObjective(
                campaign_id=campaign_id,
                quest_id=quest_id,
                objective_key="hidden_objective",
                title="Hidden Objective Title",
                status="active",
                position=1,
                revision=0,
                created_by_event_id=event.id,
            )
        )
        decision_id = uuid.uuid4()
        session.add(
            DecisionPoint(
                id=decision_id,
                campaign_id=campaign_id,
                decision_key="hidden_decision",
                prompt="Hidden Decision Prompt",
                status="open",
                visibility="dm_only",
                revision=0,
                created_by_event_id=event.id,
            )
        )
        for position, key in enumerate(("secret_a", "secret_b"), start=1):
            session.add(
                DecisionOption(
                    campaign_id=campaign_id,
                    decision_id=decision_id,
                    option_key=key,
                    label=f"Hidden Option {position}",
                    position=position,
                    consequences=[],
                )
            )
        campaign.world_revision += 3
        session.commit()


def test_explicit_audience_projection_excludes_every_hidden_m3_entity(
    client: TestClient,
) -> None:
    campaign_id_text, characters, npcs = _ready_world(client)
    campaign_id = uuid.UUID(campaign_id_text)
    with get_session_factory()() as session:
        record_world_fact(
            session,
            campaign_id,
            fact_type="clue",
            value="Hidden Fact Value",
            visibility="dm_only",
        )
        faction = record_faction(
            session,
            campaign_id,
            faction_key="hidden_faction",
            name="Hidden Faction Name",
            description="Hidden faction description",
            visibility="dm_only",
        )
        record_faction_relationship(
            session,
            campaign_id,
            faction.id,
            relation_type="membership",
            value="member",
            npc_id=uuid.UUID(npcs[0]),
            visibility="dm_only",
        )
    _add_hidden_world_records(campaign_id)

    public_response = client.get(f"/campaigns/{campaign_id}/world")
    assert public_response.status_code == 200
    public_text = public_response.text
    events_text = client.get(f"/campaigns/{campaign_id}/events").text
    with get_session_factory()() as session:
        player_world = get_world_state(session, campaign_id, audience="player")
        dm_world = get_world_state(session, campaign_id, audience="dm")
        context = _provider_context(
            CampaignState.model_validate(get_campaign_state(session, campaign_id)), player_world
        )
    context_text = json.dumps(context)
    dm_text = dm_world.model_dump_json()
    secrets = {
        "Hidden Fact Value",
        "Hidden Faction Name",
        "Veiled Envoy",
        "Hidden Quest Title",
        "Hidden Objective Title",
        "Hidden Decision Prompt",
        "M3.4 hidden fixture",
    }
    for secret in secrets:
        assert secret not in public_text
        assert secret not in events_text
        assert secret not in context_text
    assert all(secret in dm_text for secret in secrets - {"M3.4 hidden fixture"})
    assert str(characters[0]) in context_text


def test_provider_projection_is_bounded_under_large_visible_world(client: TestClient) -> None:
    campaign_id_text, _characters, _npcs = _ready_world(client)
    campaign_id = uuid.UUID(campaign_id_text)
    with get_session_factory()() as session:
        campaign = session.get(Campaign, campaign_id)
        assert campaign is not None
        event = _add_event(
            session,
            campaign_id,
            "synthetic_context_fixture_created",
            {"counts": {"facts": 101, "quests": 25, "decisions": 25, "factions": 25}},
        )
        for index in range(101):
            session.add(
                WorldFact(
                    campaign_id=campaign_id,
                    fact_type="discovery",
                    value=f"Visible synthetic fact {index:03d}",
                    status="current",
                    visibility="player",
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
        relationship_faction_id = uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
        for index in range(25):
            quest_id = uuid.uuid4()
            session.add(
                Quest(
                    id=quest_id,
                    campaign_id=campaign_id,
                    quest_key=f"stress_quest_{index:02d}",
                    title=f"Stress Quest {index:02d}",
                    status="active",
                    visibility="player",
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
            session.add(
                QuestObjective(
                    campaign_id=campaign_id,
                    quest_id=quest_id,
                    objective_key="current",
                    title=f"Stress Objective {index:02d}",
                    status="active",
                    position=1,
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
            decision_id = uuid.uuid4()
            session.add(
                DecisionPoint(
                    id=decision_id,
                    campaign_id=campaign_id,
                    decision_key=f"stress_decision_{index:02d}",
                    prompt=f"Stress Decision {index:02d}",
                    status="open",
                    visibility="player",
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
            for position, key in enumerate(("left", "right"), start=1):
                session.add(
                    DecisionOption(
                        campaign_id=campaign_id,
                        decision_id=decision_id,
                        option_key=key,
                        label=f"{key.title()} {index:02d}",
                        position=position,
                        consequences=[],
                    )
                )
            session.add(
                Faction(
                    id=relationship_faction_id if index == 24 else uuid.uuid4(),
                    campaign_id=campaign_id,
                    faction_key=f"stress_faction_{index:02d}",
                    name=f"Stress Faction {index:02d}",
                    status="active",
                    visibility="player",
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
        stress_member_ids = []
        for index in range(60):
            npc_id = uuid.uuid4()
            stress_member_ids.append(npc_id)
            session.add(
                NPC(
                    id=npc_id,
                    campaign_id=campaign_id,
                    name=f"Stress Member {index:02d}",
                    status="active",
                    visibility="player",
                    revision=0,
                    introduced_by_event_id=event.id,
                )
            )
        session.flush()
        for npc_id in stress_member_ids:
            session.add(
                FactionRelationship(
                    campaign_id=campaign_id,
                    faction_id=relationship_faction_id,
                    relation_type="membership",
                    npc_id=npc_id,
                    value="associate",
                    visibility="player",
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
        campaign.world_revision += 296
        session.commit()

    with get_session_factory()() as session:
        world = get_world_state(session, campaign_id)
        state = get_campaign_state(session, campaign_id)
        context = _provider_context(state, world)
    assert (len(world.facts), len(world.quests), len(world.decisions), len(world.factions)) == (
        101,
        25,
        25,
        25,
    )
    projected = context["world"]
    assert (
        len(projected["facts"]),
        len(projected["quests"]),
        len(projected["decisions"]),
        len(projected["factions"]),
    ) == (50, 20, 20, 20)
    assert (
        projected["facts_truncated"],
        projected["quests_truncated"],
        projected["decisions_truncated"],
        projected["factions_truncated"],
    ) == (51, 5, 5, 5)
    assert sum(len(faction["relationships"]) for faction in projected["factions"]) == 50
    assert max(faction["relationships_truncated"] for faction in projected["factions"]) == 10
    assert len(json.dumps(context)) < 100_000


def test_migration_refuses_to_discard_faction_or_elapsed_time(client: TestClient) -> None:
    campaign_id, characters, _npcs = _ready_world(client)
    _create_faction(client, campaign_id, characters[0])
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after M3.4 faction or narrative time"):
        command.downgrade(config, "0010_quests_decisions")
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
            "0011_factions_time"
        )
