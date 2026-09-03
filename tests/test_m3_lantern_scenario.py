import uuid
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api import app
from app.db import get_engine, get_session_factory
from app.llm.factory import get_turn_interpreter, get_turn_narrator
from app.models import (
    CampaignEvent,
    DecisionPoint,
    Faction,
    FactionRelationship,
    Quest,
    Scene,
    SceneNPCPresence,
    WorldFact,
)
from app.schemas import (
    DecisionOpen,
    FactionAttitudeSet,
    FactionCreate,
    FactionMembershipSet,
    MoveLocation,
    NarrativeTimeAdvance,
    NPCArrive,
    NPCAttitudeSet,
    NPCDepart,
    NPCIntroduce,
    PromiseRecord,
    QuestCreate,
    TurnNarrationOutput,
    WorldFactReveal,
)
from app.services import record_world_fact
from app.turn_interpretation import NarrativeIntent
from tests.test_world_presence import _ready_world


class ScenarioInterpreter:
    provider_name = "m3-lantern-fixture"
    model_name = None
    interpretation_prompt_version = "m3-lantern-fixture-1"

    def __init__(self) -> None:
        self.calls = 0

    def interpret_action(self, context: dict[str, Any], player_action: str) -> NarrativeIntent:
        self.calls += 1
        return NarrativeIntent(type="narrative", summary=player_action)


class ScenarioNarrator:
    provider_name = "m3-lantern-fixture"
    model_name = None
    narration_prompt_version = "m3-lantern-fixture-1"

    def __init__(self, changes: list, captured: dict[str, Any] | None = None) -> None:
        self.changes = changes
        self.captured = captured

    def narrate_outcome(self, context: dict[str, Any], *args: Any) -> TurnNarrationOutput:
        if self.captured is not None:
            self.captured.update(context)
        return TurnNarrationOutput(
            narration="The party's declared choice becomes durable campaign history.",
            state_changes=self.changes,
        )


def _complete_turn(
    client: TestClient,
    campaign_id: str,
    actor_id: str,
    changes: list,
    *,
    action: str,
    target_npc_id: str | None = None,
    decision_id: str | None = None,
    option_key: str | None = None,
    captured: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "command_id": str(uuid.uuid4()),
        "action": action,
        "actor_character_id": actor_id,
        "target_npc_id": target_npc_id,
    }
    if decision_id is not None:
        payload["decision_id"] = decision_id
        payload["decision_option_key"] = option_key
    created = client.post(f"/campaigns/{campaign_id}/turn-executions", json=payload)
    assert created.status_code == 201, created.text
    turn_id = created.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text
    app.dependency_overrides[get_turn_narrator] = lambda: ScenarioNarrator(changes, captured)
    finalized = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert finalized.status_code == 200, finalized.text
    return finalized.json()


def _all_events(campaign_id: uuid.UUID) -> list[CampaignEvent]:
    with get_session_factory()() as session:
        return list(
            session.scalars(
                select(CampaignEvent)
                .where(CampaignEvent.campaign_id == campaign_id)
                .order_by(CampaignEvent.sequence)
            )
        )


def _replay_player_world(events: list[CampaignEvent]) -> dict[str, Any]:
    replay: dict[str, Any] = {
        "world_revision": 0,
        "narrative_time_minutes": 0,
        "scene_id": None,
        "location_id": None,
        "present_npc_ids": set(),
        "npcs": {},
        "facts": {},
        "quests": {},
        "decisions": {},
        "factions": {},
    }
    for event in events:
        payload = event.payload
        if "world_revision" in payload:
            replay["world_revision"] = payload["world_revision"]
        if event.event_type == "scene_opened":
            replay["scene_id"] = payload["scene_id"]
            replay["location_id"] = payload["location_id"]
        elif event.event_type == "scene_closed" and replay["scene_id"] == payload["scene_id"]:
            replay["scene_id"] = None
        elif event.event_type == "npc_introduced":
            replay["npcs"][payload["npc_id"]] = payload["name"]
        elif event.event_type == "npc_arrived":
            replay["present_npc_ids"].add(payload["npc_id"])
        elif event.event_type == "npc_departed":
            replay["present_npc_ids"].discard(payload["npc_id"])
        elif event.event_type in {"world_fact_recorded", "world_fact_superseded"}:
            if payload.get("supersedes_fact_id"):
                replay["facts"].pop(payload["supersedes_fact_id"], None)
            replay["facts"][payload["fact_id"]] = {
                "fact_type": payload["fact_type"],
                "subject_npc_id": payload["subject_npc_id"],
                "value": payload["value"],
                "visibility": event.visibility,
            }
        elif event.event_type == "world_fact_revealed":
            replay["facts"][payload["fact_id"]] = {
                "fact_type": payload["fact_type"],
                "subject_npc_id": payload["subject_npc_id"],
                "value": payload["value"],
                "visibility": "player",
            }
        elif event.event_type == "quest_created":
            replay["quests"][payload["quest_id"]] = {
                "quest_key": payload["quest_key"],
                "status": "active",
                "objectives": {row["objective_id"]: row["status"] for row in payload["objectives"]},
            }
        elif event.event_type == "quest_status_changed":
            replay["quests"][payload["quest_id"]]["status"] = payload["status"]
        elif event.event_type == "quest_objective_status_changed":
            replay["quests"][payload["quest_id"]]["objectives"][payload["objective_id"]] = payload[
                "status"
            ]
        elif event.event_type == "decision_opened":
            replay["decisions"][payload["decision_id"]] = {
                "decision_key": payload["decision_key"],
                "status": "open",
                "selected_option_key": None,
            }
        elif event.event_type == "decision_selected":
            replay["decisions"][payload["decision_id"]].update(
                status="selected", selected_option_key=payload["option_key"]
            )
        elif event.event_type == "faction_created":
            replay["factions"][payload["faction_id"]] = {
                "faction_key": payload["faction_key"],
                "relationships": {},
            }
        elif event.event_type in {"faction_attitude_set", "faction_membership_set"}:
            replay["factions"][payload["faction_id"]]["relationships"][
                payload["relationship_id"]
            ] = {
                "relation_type": payload["relation_type"],
                "character_id": payload["character_id"],
                "npc_id": payload["npc_id"],
                "value": payload["value"],
            }
        elif event.event_type == "narrative_time_advanced":
            replay["narrative_time_minutes"] = payload["narrative_time_minutes"]
    return replay


def _assert_replay_matches_world(campaign_id: uuid.UUID, world: dict[str, Any]) -> None:
    events = _all_events(campaign_id)
    replay = _replay_player_world(events)
    revisions = [
        event.payload["world_revision"] for event in events if "world_revision" in event.payload
    ]
    assert revisions == sorted(revisions)
    assert set(revisions) == set(range(world["world_revision"] + 1))
    assert replay["world_revision"] == world["world_revision"]
    assert replay["narrative_time_minutes"] == world["narrative_time_minutes"]
    assert replay["scene_id"] == world["scene"]["id"]
    assert replay["location_id"] == world["location"]["id"]
    assert replay["present_npc_ids"] == {row["id"] for row in world["present_npcs"]}
    assert {replay["npcs"][npc_id] for npc_id in replay["present_npc_ids"]} == {
        row["name"] for row in world["present_npcs"]
    }

    visible_replayed_facts = {
        fact_id: row for fact_id, row in replay["facts"].items() if row["visibility"] == "player"
    }
    assert visible_replayed_facts == {
        row["id"]: {
            "fact_type": row["fact_type"],
            "subject_npc_id": row["subject_npc_id"],
            "value": row["value"],
            "visibility": "player",
        }
        for row in world["facts"]
    }
    assert replay["quests"] == {
        row["id"]: {
            "quest_key": row["quest_key"],
            "status": row["status"],
            "objectives": {objective["id"]: objective["status"] for objective in row["objectives"]},
        }
        for row in world["quests"]
    }
    assert replay["decisions"] == {
        row["id"]: {
            "decision_key": row["decision_key"],
            "status": row["status"],
            "selected_option_key": row["selected_option_key"],
        }
        for row in world["decisions"]
    }
    assert replay["factions"] == {
        row["id"]: {
            "faction_key": row["faction_key"],
            "relationships": {
                relation["id"]: {
                    "relation_type": relation["relation_type"],
                    "character_id": relation["character_id"],
                    "npc_id": relation["npc_id"],
                    "value": relation["value"],
                }
                for relation in row["relationships"]
            },
        }
        for row in world["factions"]
    }


def _assert_all_projection_links_are_causal(campaign_id: uuid.UUID) -> None:
    with get_session_factory()() as session:
        event_ids = set(
            session.scalars(
                select(CampaignEvent.id).where(CampaignEvent.campaign_id == campaign_id)
            )
        )
        scenes = list(session.scalars(select(Scene).where(Scene.campaign_id == campaign_id)))
        presences = list(
            session.scalars(
                select(SceneNPCPresence).where(SceneNPCPresence.campaign_id == campaign_id)
            )
        )
        facts = list(session.scalars(select(WorldFact).where(WorldFact.campaign_id == campaign_id)))
        quests = list(session.scalars(select(Quest).where(Quest.campaign_id == campaign_id)))
        decisions = list(
            session.scalars(select(DecisionPoint).where(DecisionPoint.campaign_id == campaign_id))
        )
        factions = list(session.scalars(select(Faction).where(Faction.campaign_id == campaign_id)))
        relationships = list(
            session.scalars(
                select(FactionRelationship).where(FactionRelationship.campaign_id == campaign_id)
            )
        )
        assert all(scene.opened_by_event_id in event_ids for scene in scenes)
        assert all(
            scene.status == "active" or scene.closed_by_event_id in event_ids for scene in scenes
        )
        assert all(presence.arrived_by_event_id in event_ids for presence in presences)
        assert all(
            presence.status == "present" or presence.departed_by_event_id in event_ids
            for presence in presences
        )
        assert all(fact.created_by_event_id in event_ids for fact in facts)
        assert all(quest.created_by_event_id in event_ids for quest in quests)
        assert all(decision.created_by_event_id in event_ids for decision in decisions)
        assert all(decision.selected_by_event_id in event_ids for decision in decisions)
        assert all(faction.created_by_event_id in event_ids for faction in factions)
        assert all(relation.created_by_event_id in event_ids for relation in relationships)


def _run_branching_lantern(
    client: TestClient, option_key: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    campaign_id, characters, starting_npcs = _ready_world(client)
    campaign_uuid = uuid.UUID(campaign_id)
    interpreter = ScenarioInterpreter()
    app.dependency_overrides[get_turn_interpreter] = lambda: interpreter
    state_before = client.get(f"/campaigns/{campaign_id}/state").json()
    secret = "The Lantern Watch bell bears a concealed tunnel map."
    with get_session_factory()() as session:
        hidden_clue = record_world_fact(
            session,
            campaign_uuid,
            fact_type="clue",
            value=secret,
            visibility="dm_only",
        )
    assert secret not in client.get(f"/campaigns/{campaign_id}/world").text
    assert secret not in client.get(f"/campaigns/{campaign_id}/events").text

    captured_interaction: dict[str, Any] = {}
    _complete_turn(
        client,
        campaign_id,
        characters[0],
        [
            NPCAttitudeSet(type="npc_attitude_set", npc_id=starting_npcs[0], attitude="friendly"),
            PromiseRecord(
                type="promise_record",
                npc_id=starting_npcs[0],
                promise="Mira will guide the party to the Old Tower.",
            ),
        ],
        action="Arin asks Mira about the missing lantern patrol.",
        target_npc_id=starting_npcs[0],
        captured=captured_interaction,
    )
    assert captured_interaction["world"]["selected_target"]["id"] == starting_npcs[0]

    _complete_turn(
        client,
        campaign_id,
        characters[1],
        [
            QuestCreate(
                type="quest_create",
                quest_key="missing_lantern_patrol",
                title="The Missing Lantern Patrol",
                summary="Find the patrol beyond the Old Tower.",
                objectives=[
                    {
                        "objective_key": "find_patrol",
                        "title": "Find the missing patrol",
                        "status": "pending",
                    }
                ],
            ),
            FactionCreate(
                type="faction_create",
                faction_key="lantern_watch",
                name="Lantern Watch",
                description="Wardens of the northern road.",
            ),
        ],
        action="Bryn listens to the Watch's request.",
        target_npc_id=starting_npcs[1],
    )
    world = client.get(f"/campaigns/{campaign_id}/world").json()
    quest = world["quests"][0]
    faction = world["factions"][0]
    objective = quest["objectives"][0]

    _complete_turn(
        client,
        campaign_id,
        characters[0],
        [
            DecisionOpen(
                type="decision_open",
                decision_key="accept_lantern_patrol",
                prompt="Will the party search for the missing Lantern Watch patrol?",
                options=[
                    {
                        "option_key": "accept",
                        "label": "Accept the search",
                        "consequences": [
                            {
                                "type": "transition_objective",
                                "objective_id": objective["id"],
                                "expected_revision": 0,
                                "status": "active",
                            }
                        ],
                    },
                    {
                        "option_key": "decline",
                        "label": "Decline the search",
                        "consequences": [
                            {
                                "type": "transition_quest",
                                "quest_id": quest["id"],
                                "expected_revision": 0,
                                "status": "abandoned",
                            }
                        ],
                    },
                ],
            )
        ],
        action="The party considers the Watch's request.",
    )
    offer = client.get(f"/campaigns/{campaign_id}/world").json()["decisions"][0]
    _complete_turn(
        client,
        campaign_id,
        characters[0],
        [],
        action="The party accepts the Lantern Watch mission.",
        decision_id=offer["id"],
        option_key="accept",
    )

    _complete_turn(
        client,
        campaign_id,
        characters[1],
        [
            MoveLocation(
                type="move_location",
                location_name="Old Tower",
                description="A ruined watchtower above the flooded road.",
            )
        ],
        action="Bryn leads the party to the Old Tower.",
    )
    after_move = client.get(f"/campaigns/{campaign_id}/world").json()
    assert after_move["present_npcs"] == []
    calls_before_absent_target = interpreter.calls
    events_before_absent_target = len(client.get(f"/campaigns/{campaign_id}/events").json())
    absent = client.post(
        f"/campaigns/{campaign_id}/turn-executions",
        json={
            "command_id": str(uuid.uuid4()),
            "action": "Ask Mira what she sees.",
            "actor_character_id": characters[0],
            "target_npc_id": starting_npcs[0],
        },
    )
    assert absent.status_code == 409
    assert absent.json()["detail"] == "Target NPC is not present in the current scene"
    assert interpreter.calls == calls_before_absent_target
    assert len(client.get(f"/campaigns/{campaign_id}/events").json()) == events_before_absent_target

    _complete_turn(
        client,
        campaign_id,
        characters[0],
        [
            NPCIntroduce(
                type="npc_introduce",
                name="Seren",
                public_description="A Lantern Watch scout sheltering in the tower.",
            )
        ],
        action="Arin finds a stranded Watch scout.",
    )
    introduced = client.get(f"/campaigns/{campaign_id}/world").json()["present_npcs"][0]
    _complete_turn(
        client,
        campaign_id,
        characters[1],
        [NPCDepart(type="npc_depart", npc_id=introduced["id"])],
        action="Seren leaves to warn the road patrol.",
        target_npc_id=introduced["id"],
    )
    _complete_turn(
        client,
        campaign_id,
        characters[0],
        [NPCArrive(type="npc_arrive", npc_id=starting_npcs[1])],
        action="The caravan guard Mira catches up at the Old Tower.",
    )
    assert [
        row["id"] for row in client.get(f"/campaigns/{campaign_id}/world").json()["present_npcs"]
    ] == [starting_npcs[1]]

    _complete_turn(
        client,
        campaign_id,
        characters[0],
        [WorldFactReveal(type="world_fact_reveal", fact_id=hidden_clue.id, expected_revision=0)],
        action="Arin deciphers the concealed map on the bell.",
        target_npc_id=starting_npcs[1],
    )
    assert secret in client.get(f"/campaigns/{campaign_id}/world").text
    assert secret in client.get(f"/campaigns/{campaign_id}/events").text

    _complete_turn(
        client,
        campaign_id,
        characters[1],
        [
            FactionAttitudeSet(
                type="faction_attitude_set", faction_id=faction["id"], attitude="friendly"
            ),
            FactionMembershipSet(
                type="faction_membership_set",
                faction_id=faction["id"],
                member_type="character",
                member_id=characters[0],
                membership="associate",
            ),
            NarrativeTimeAdvance(
                type="narrative_time_advance",
                minutes=90,
                reason="The party follows the map through the flooded tower cellars.",
            ),
        ],
        action="The Watch recognizes the party's help as the search continues.",
        target_npc_id=starting_npcs[1],
    )

    _complete_turn(
        client,
        campaign_id,
        characters[0],
        [
            DecisionOpen(
                type="decision_open",
                decision_key="tower_route",
                prompt="Which route will the party use to reach the patrol?",
                options=[
                    {
                        "option_key": "signal_bridge",
                        "label": "Cross the signal bridge",
                        "consequences": [
                            {
                                "type": "transition_objective",
                                "objective_id": objective["id"],
                                "expected_revision": 1,
                                "status": "completed",
                            },
                            {
                                "type": "record_fact",
                                "fact_type": "discovery",
                                "value": "The party rescued the patrol across the signal bridge.",
                            },
                        ],
                    },
                    {
                        "option_key": "flooded_tunnel",
                        "label": "Enter the flooded tunnel",
                        "consequences": [
                            {
                                "type": "transition_objective",
                                "objective_id": objective["id"],
                                "expected_revision": 1,
                                "status": "failed",
                            },
                            {
                                "type": "record_fact",
                                "fact_type": "discovery",
                                "value": (
                                    "The flooded tunnel collapsed before the patrol was found."
                                ),
                            },
                        ],
                    },
                ],
            )
        ],
        action="The party reaches two possible routes beneath the tower.",
    )
    branch = client.get(f"/campaigns/{campaign_id}/world").json()["decisions"][1]
    captured_choice: dict[str, Any] = {}
    finalized = _complete_turn(
        client,
        campaign_id,
        characters[0],
        [],
        action=f"The party chooses {option_key}.",
        decision_id=branch["id"],
        option_key=option_key,
        captured=captured_choice,
    )
    assert captured_choice["world"]["selected_choice"]["option_key"] == option_key
    assert finalized["turn"]["world_revision_after"] == 20

    world_before_restart = client.get(f"/campaigns/{campaign_id}/world").json()
    state_after = client.get(f"/campaigns/{campaign_id}/state").json()
    assert [
        (row["hp"], row["resources"], row["state_revision"]) for row in state_after["characters"]
    ] == [
        (row["hp"], row["resources"], row["state_revision"]) for row in state_before["characters"]
    ]
    assert world_before_restart["narrative_time_minutes"] == 90
    assert world_before_restart["world_revision"] == 20
    assert world_before_restart["location"]["name"] == "Old Tower"

    get_engine().dispose()
    world_after_restart = client.get(f"/campaigns/{campaign_id}/world").json()
    assert world_after_restart == world_before_restart
    _assert_replay_matches_world(campaign_uuid, world_after_restart)
    _assert_all_projection_links_are_causal(campaign_uuid)
    return world_after_restart, {
        "campaign_id": campaign_id,
        "character_ids": characters,
        "starting_npc_ids": starting_npcs,
    }


def test_complete_lantern_world_scenario_branches_restarts_and_replays(
    client: TestClient,
) -> None:
    bridge_world, bridge_ids = _run_branching_lantern(client, "signal_bridge")
    tunnel_world, tunnel_ids = _run_branching_lantern(client, "flooded_tunnel")

    assert bridge_ids["campaign_id"] != tunnel_ids["campaign_id"]
    assert bridge_world["world_revision"] == tunnel_world["world_revision"] == 20
    assert bridge_world["narrative_time_minutes"] == tunnel_world["narrative_time_minutes"] == 90
    assert bridge_world["location"]["name"] == tunnel_world["location"]["name"] == "Old Tower"
    assert bridge_world["quests"][0]["objectives"][0]["status"] == "completed"
    assert tunnel_world["quests"][0]["objectives"][0]["status"] == "failed"
    assert bridge_world["decisions"][1]["selected_option_key"] == "signal_bridge"
    assert tunnel_world["decisions"][1]["selected_option_key"] == "flooded_tunnel"
    bridge_discovery = next(
        fact["value"] for fact in bridge_world["facts"] if fact["fact_type"] == "discovery"
    )
    tunnel_discovery = next(
        fact["value"] for fact in tunnel_world["facts"] if fact["fact_type"] == "discovery"
    )
    assert bridge_discovery == "The party rescued the patrol across the signal bridge."
    assert tunnel_discovery == "The flooded tunnel collapsed before the patrol was found."


def test_presence_mutations_are_atomic_and_cannot_overlap_movement(client: TestClient) -> None:
    campaign_id, characters, starting_npcs = _ready_world(client)
    interpreter = ScenarioInterpreter()
    app.dependency_overrides[get_turn_interpreter] = lambda: interpreter
    before = client.get(f"/campaigns/{campaign_id}/world").json()

    payload = {
        "command_id": str(uuid.uuid4()),
        "action": "Try to move while changing the same scene's cast.",
        "actor_character_id": characters[0],
    }
    created = client.post(f"/campaigns/{campaign_id}/turn-executions", json=payload)
    assert created.status_code == 201
    turn_id = created.json()["id"]
    assert (
        client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret").status_code
        == 200
    )
    app.dependency_overrides[get_turn_narrator] = lambda: ScenarioNarrator(
        [
            NPCDepart(type="npc_depart", npc_id=starting_npcs[0]),
            MoveLocation(type="move_location", location_name="Old Tower"),
        ]
    )
    rejected = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert rejected.status_code == 422
    assert "separate turns" in rejected.json()["detail"]
    assert client.get(f"/campaigns/{campaign_id}/world").json() == before
