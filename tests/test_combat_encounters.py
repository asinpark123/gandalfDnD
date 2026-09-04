import uuid
from pathlib import Path
from typing import Any

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from alembic import command
from app.api import app
from app.db import get_engine
from app.dice import DiceService, get_dice_service


class FixedRandom:
    algorithm_version = "fixed-combat-sequence-1.0.0"

    def __init__(self, results: list[int]) -> None:
        self._results = iter(results)

    def randint(self, start: int, end: int) -> int:
        value = next(self._results)
        assert start <= value <= end
        return value


def _fixed_dice(results: list[int]) -> None:
    app.dependency_overrides[get_dice_service] = lambda: DiceService(FixedRandom(results))


def _finalize_payload(
    *,
    alternate: bool = False,
    fighting_style: str = "defense",
) -> dict[str, Any]:
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
        "fighting_style_definition_key": (f"srd-5.2.1:feat.fighting_style.{fighting_style}"),
        "weapon_mastery_definition_keys": [
            "srd-5.2.1:weapon.javelin",
            "srd-5.2.1:weapon.flail",
            "srd-5.2.1:weapon.greatsword",
        ],
        "equipment_route_id": "soldier-a+fighter-a",
    }


def _ready_party(
    client: TestClient,
    *,
    first_fighting_style: str = "defense",
) -> tuple[str, str, list[str]]:
    campaign = client.post(
        "/campaigns",
        json={
            "name": "M5 Encounter Test",
            "starting_scene": {"title": "Ambush", "summary": "A guarded road."},
        },
    )
    assert campaign.status_code == 201, campaign.text
    campaign_id = campaign.json()["id"]
    character_ids: list[str] = []
    for index, name in enumerate(("Arin", "Bryn")):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201, draft.text
        character_id = draft.json()["id"]
        character_ids.append(character_id)
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{character_id}/finalize",
            json=_finalize_payload(
                alternate=index == 1,
                fighting_style=first_fighting_style if index == 0 else "defense",
            ),
        )
        assert finalized.status_code == 200, finalized.text
    world = client.get(f"/campaigns/{campaign_id}/world")
    assert world.status_code == 200, world.text
    return campaign_id, world.json()["scene"]["id"], character_ids


def _encounter_command(scene_id: str, character_ids: list[str], **changes: Any) -> dict[str, Any]:
    command: dict[str, Any] = {
        "command_id": str(uuid.uuid4()),
        "expected_world_revision": 0,
        "scene_id": scene_id,
        "combat_catalog_id": "srd-5.2.1-combat-v1",
        "grid_width": 10,
        "grid_height": 8,
        "party": [
            {"character_id": character_ids[0], "x": 1, "y": 2},
            {"character_id": character_ids[1], "x": 1, "y": 3},
        ],
        "enemies": [
            {
                "monster_definition_id": "goblin_warrior",
                "instance_name": "Road Goblin",
                "x": 7,
                "y": 2,
            }
        ],
    }
    command.update(changes)
    return command


def test_encounter_creation_initiative_restart_and_replay(client: TestClient) -> None:
    campaign_id, scene_id, character_ids = _ready_party(client)
    create_command = _encounter_command(scene_id, character_ids)
    created = client.post(f"/campaigns/{campaign_id}/combat-encounters", json=create_command)
    assert created.status_code == 201, created.text
    encounter = created.json()
    assert encounter["status"] == "setup"
    assert encounter["revision"] == 0
    assert [
        (row["instance_name"], row["hp"], row["armor_class"]) for row in encounter["combatants"]
    ] == [
        ("Arin", 12, 17),
        ("Bryn", 12, 17),
        ("Road Goblin", 10, 15),
    ]
    assert [row["initiative_modifier"] for row in encounter["combatants"]] == [4, 4, 2]
    assert encounter["combat_catalog_sha256"] == (
        "423b80e84593738d4cadc5537278d208a51fbebacbb074a2d79531f0ee023204"
    )

    duplicate = client.post(f"/campaigns/{campaign_id}/combat-encounters", json=create_command)
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == encounter["id"]

    _fixed_dice([18, 12, 5])
    start_command = {"command_id": str(uuid.uuid4()), "expected_encounter_revision": 0}
    started = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/start",
        json=start_command,
    )
    assert started.status_code == 200, started.text
    active = started.json()
    assert active["status"] == "active"
    assert active["revision"] == 1
    assert active["round_number"] == 1
    assert [row["initiative_total"] for row in active["combatants"]] == [22, 16, 7]
    assert [row["initiative_order"] for row in active["combatants"]] == [0, 1, 2]

    _fixed_dice([])
    duplicate_start = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/start",
        json=start_command,
    )
    assert duplicate_start.status_code == 200
    assert duplicate_start.json()["events"] == active["events"]

    get_engine().dispose()
    after_restart = client.get(f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}")
    assert after_restart.status_code == 200
    assert after_restart.json() == active
    replay = client.post(f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/replay")
    assert replay.status_code == 200, replay.text
    assert replay.json()["equivalent"] is True
    assert replay.json()["replayed_initiative_order"] == [row["id"] for row in active["combatants"]]
    with get_engine().connect() as connection:
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM dice_rolls WHERE combat_encounter_id = CAST(:id AS uuid)"
                ),
                {"id": encounter["id"]},
            ).scalar_one()
            == 3
        )


def test_initiative_tie_requires_explicit_exact_order(client: TestClient) -> None:
    campaign_id, scene_id, character_ids = _ready_party(client)
    created = client.post(
        f"/campaigns/{campaign_id}/combat-encounters",
        json=_encounter_command(scene_id, character_ids),
    ).json()
    _fixed_dice([10, 10, 1])
    started = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{created['id']}/start",
        json={"command_id": str(uuid.uuid4()), "expected_encounter_revision": 0},
    )
    assert started.status_code == 200, started.text
    pending = started.json()
    assert pending["status"] == "tie_pending"
    tie = pending["initiative_ties"][0]
    assert tie["initiative_total"] == 14
    assert set(tie["participant_ids"]) == {
        row["id"] for row in pending["combatants"] if row["side"] == "party"
    }
    assert all(row["initiative_order"] is None for row in pending["combatants"])

    invalid = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{created['id']}/initiative-ties/{tie['id']}",
        json={
            "command_id": str(uuid.uuid4()),
            "expected_encounter_revision": 1,
            "ordered_combatant_ids": [tie["participant_ids"][0], pending["combatants"][2]["id"]],
        },
    )
    assert invalid.status_code == 409
    unchanged = client.get(f"/campaigns/{campaign_id}/combat-encounters/{created['id']}").json()
    assert unchanged["revision"] == 1
    assert unchanged["initiative_ties"][0]["status"] == "pending"

    command = {
        "command_id": str(uuid.uuid4()),
        "expected_encounter_revision": 1,
        "ordered_combatant_ids": list(reversed(tie["participant_ids"])),
    }
    resolved = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{created['id']}/initiative-ties/{tie['id']}",
        json=command,
    )
    assert resolved.status_code == 200, resolved.text
    active = resolved.json()
    assert active["status"] == "active"
    assert active["revision"] == 2
    assert [row["id"] for row in active["combatants"]] == [
        *command["ordered_combatant_ids"],
        next(row["id"] for row in active["combatants"] if row["side"] == "enemy"),
    ]
    replay = client.post(f"/campaigns/{campaign_id}/combat-encounters/{created['id']}/replay")
    assert replay.status_code == 200
    assert replay.json()["equivalent"] is True


def test_stale_or_invalid_setup_rolls_nothing_and_persists_no_partial_state(
    client: TestClient,
) -> None:
    campaign_id, scene_id, character_ids = _ready_party(client)
    stale = client.post(
        f"/campaigns/{campaign_id}/combat-encounters",
        json=_encounter_command(scene_id, character_ids, expected_world_revision=99),
    )
    assert stale.status_code == 409
    unsupported = client.post(
        f"/campaigns/{campaign_id}/combat-encounters",
        json=_encounter_command(
            scene_id,
            character_ids,
            enemies=[
                {
                    "monster_definition_id": "ancient_red_dragon",
                    "instance_name": "Too Soon",
                    "x": 7,
                    "y": 2,
                }
            ],
        ),
    )
    assert unsupported.status_code == 409
    with get_engine().connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM combat_encounters")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM combatants")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM dice_rolls")).scalar_one() == 0

    created = client.post(
        f"/campaigns/{campaign_id}/combat-encounters",
        json=_encounter_command(scene_id, character_ids),
    ).json()
    _fixed_dice([20, 19, 18])
    stale_start = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{created['id']}/start",
        json={"command_id": str(uuid.uuid4()), "expected_encounter_revision": 7},
    )
    assert stale_start.status_code == 409
    with get_engine().connect() as connection:
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM dice_rolls WHERE combat_encounter_id = CAST(:id AS uuid)"
                ),
                {"id": created["id"]},
            ).scalar_one()
            == 0
        )
    unchanged = client.get(f"/campaigns/{campaign_id}/combat-encounters/{created['id']}").json()
    assert unchanged["status"] == "setup"
    assert unchanged["revision"] == 0

    second = client.post(
        f"/campaigns/{campaign_id}/combat-encounters",
        json=_encounter_command(scene_id, character_ids, expected_world_revision=1),
    )
    assert second.status_code == 409
    assert "already has open combat encounter" in second.json()["detail"]


def test_combat_audit_is_immutable_and_migration_refuses_material_data(
    client: TestClient,
) -> None:
    campaign_id, scene_id, character_ids = _ready_party(client)
    encounter = client.post(
        f"/campaigns/{campaign_id}/combat-encounters",
        json=_encounter_command(scene_id, character_ids),
    ).json()
    with (
        pytest.raises(DBAPIError, match="combat_commands is immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text(
                "UPDATE combat_commands SET result = '{}'::jsonb "
                "WHERE encounter_id = CAST(:id AS uuid)"
            ),
            {"id": encounter["id"]},
        )
    with (
        pytest.raises(DBAPIError, match="combat_events is immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text(
                "UPDATE combat_events SET event_type = 'changed' "
                "WHERE encounter_id = CAST(:id AS uuid)"
            ),
            {"id": encounter["id"]},
        )

    with get_engine().connect() as connection:
        expected_revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after combat (turn|encounter) data"):
        command.downgrade(config, "0015_memory_summaries")
    with get_engine().connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == expected_revision
        )


def _started_encounter(
    client: TestClient,
    *,
    enemy_x: int = 7,
    enemy_y: int = 2,
    first_fighting_style: str = "defense",
) -> tuple[str, dict[str, Any]]:
    campaign_id, scene_id, character_ids = _ready_party(
        client,
        first_fighting_style=first_fighting_style,
    )
    create = _encounter_command(
        scene_id,
        character_ids,
        enemies=[
            {
                "monster_definition_id": "goblin_warrior",
                "instance_name": "Road Goblin",
                "x": enemy_x,
                "y": enemy_y,
            }
        ],
    )
    encounter = client.post(f"/campaigns/{campaign_id}/combat-encounters", json=create).json()
    _fixed_dice([18, 12, 1])
    started = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/start",
        json={"command_id": str(uuid.uuid4()), "expected_encounter_revision": 0},
    )
    assert started.status_code == 200, started.text
    return campaign_id, started.json()


def test_turn_budget_split_movement_full_round_dodge_expiry_and_restart(
    client: TestClient,
) -> None:
    campaign_id, encounter = _started_encounter(client)
    encounter_id = encounter["id"]
    first, second, enemy = encounter["combatants"]
    assert encounter["current_turn"]["combatant_id"] == first["id"]
    assert encounter["current_turn"]["movement_allowance_feet"] == 30
    assert encounter["current_turn"]["action_available"] is True

    moved = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": first["id"],
            "expected_encounter_revision": 1,
            "expected_combatant_revision": 0,
            "path": [{"x": 2, "y": 2}, {"x": 3, "y": 2}],
        },
    )
    assert moved.status_code == 200, moved.text
    state = moved.json()
    assert state["combatants"][0]["position_x"] == 3
    assert state["current_turn"]["movement_spent_feet"] == 10

    dash_command = {
        "command_id": str(uuid.uuid4()),
        "actor_combatant_id": first["id"],
        "expected_encounter_revision": 2,
        "expected_combatant_revision": 1,
        "action": "dash",
    }
    dashed = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/actions",
        json=dash_command,
    )
    assert dashed.status_code == 200, dashed.text
    state = dashed.json()
    assert state["current_turn"]["movement_allowance_feet"] == 60
    assert state["current_turn"]["action_available"] is False
    duplicate = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/actions",
        json=dash_command,
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["revision"] == 3

    split = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": first["id"],
            "expected_encounter_revision": 3,
            "expected_combatant_revision": 2,
            "path": [{"x": 4, "y": 2}],
        },
    )
    assert split.status_code == 200, split.text
    state = split.json()
    assert state["current_turn"]["movement_spent_feet"] == 15
    assert state["combatants"][0]["position_x"] == 4

    wrong_actor = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/actions",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": second["id"],
            "expected_encounter_revision": 4,
            "expected_combatant_revision": 0,
            "action": "dodge",
        },
    )
    assert wrong_actor.status_code == 409
    assert wrong_actor.json()["detail"] == "Combatant is not the active turn actor"

    revisions = [(4, first["id"], 3), (5, second["id"], 0), (6, enemy["id"], 0)]
    for expected_encounter, actor_id, expected_actor in revisions:
        ended = client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/end-turn",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": actor_id,
                "expected_encounter_revision": expected_encounter,
                "expected_combatant_revision": expected_actor,
            },
        )
        assert ended.status_code == 200, ended.text
        state = ended.json()
    assert state["round_number"] == 2
    assert state["current_turn"]["combatant_id"] == first["id"]
    assert state["current_turn"]["movement_spent_feet"] == 0
    assert state["current_turn"]["action_available"] is True

    dodged = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/actions",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": first["id"],
            "expected_encounter_revision": 7,
            "expected_combatant_revision": 3,
            "action": "dodge",
        },
    )
    assert dodged.status_code == 200, dodged.text
    state = dodged.json()
    assert state["effects"][0]["effect_id"] == "dodge"
    assert state["effects"][0]["status"] == "active"

    revisions = [(8, first["id"], 4), (9, second["id"], 0), (10, enemy["id"], 0)]
    for expected_encounter, actor_id, expected_actor in revisions:
        ended = client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/end-turn",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": actor_id,
                "expected_encounter_revision": expected_encounter,
                "expected_combatant_revision": expected_actor,
            },
        )
        assert ended.status_code == 200, ended.text
        state = ended.json()
    assert state["round_number"] == 3
    assert state["effects"][0]["status"] == "expired"
    assert state["effects"][0]["ended_round"] == 3
    get_engine().dispose()
    restored = client.get(f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}")
    assert restored.status_code == 200
    assert restored.json() == state


def test_reaction_window_requires_explicit_pass_before_movement(client: TestClient) -> None:
    campaign_id, encounter = _started_encounter(client, enemy_x=2, enemy_y=2)
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    enemy = next(row for row in encounter["combatants"] if row["side"] == "enemy")
    path = [{"x": 0, "y": 2}]
    opened = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 1,
            "expected_combatant_revision": 0,
            "path": path,
        },
    )
    assert opened.status_code == 200, opened.text
    pending = opened.json()
    assert pending["combatants"][0]["position_x"] == 1
    assert pending["current_turn"]["movement_spent_feet"] == 0
    assert pending["reaction_windows"][0]["status"] == "pending"
    window = pending["reaction_windows"][0]
    assert window["reactor_combatant_id"] == enemy["id"]

    passed = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}"
        f"/reaction-windows/{window['id']}",
        json={
            "command_id": str(uuid.uuid4()),
            "reactor_combatant_id": enemy["id"],
            "expected_encounter_revision": 2,
            "expected_combatant_revision": 0,
            "response": "pass",
        },
    )
    assert passed.status_code == 200, passed.text
    assert passed.json()["reaction_windows"][0]["status"] == "passed"
    assert passed.json()["combatants"][2]["reaction_available"] is True

    moved = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 3,
            "expected_combatant_revision": 0,
            "path": path,
        },
    )
    assert moved.status_code == 200, moved.text
    state = moved.json()
    assert state["combatants"][0]["position_x"] == 0
    assert state["current_turn"]["movement_spent_feet"] == 5


def test_disengage_prevents_window_and_invalid_path_is_atomic(client: TestClient) -> None:
    campaign_id, encounter = _started_encounter(client, enemy_x=2, enemy_y=2)
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    occupied = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 1,
            "expected_combatant_revision": 0,
            "path": [{"x": 2, "y": 2}],
        },
    )
    assert occupied.status_code == 409
    assert occupied.json()["detail"] == "Movement path enters an occupied cell"
    unchanged = client.get(f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}").json()
    assert unchanged["revision"] == 1
    assert unchanged["combatants"][0]["revision"] == 0

    disengaged = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/actions",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 1,
            "expected_combatant_revision": 0,
            "action": "disengage",
        },
    )
    assert disengaged.status_code == 200, disengaged.text
    assert disengaged.json()["current_turn"]["disengaged"] is True
    moved = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 2,
            "expected_combatant_revision": 1,
            "path": [{"x": 0, "y": 2}],
        },
    )
    assert moved.status_code == 200, moved.text
    assert moved.json()["combatants"][0]["position_x"] == 0
    assert moved.json()["reaction_windows"] == []


def test_opportunity_attack_selection_consumes_reaction_and_blocks_movement(
    client: TestClient,
) -> None:
    campaign_id, encounter = _started_encounter(client, enemy_x=2, enemy_y=2)
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    enemy = next(row for row in encounter["combatants"] if row["side"] == "enemy")
    path = [{"x": 0, "y": 2}]
    pending = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 1,
            "expected_combatant_revision": 0,
            "path": path,
        },
    ).json()
    window = pending["reaction_windows"][0]
    selected = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}"
        f"/reaction-windows/{window['id']}",
        json={
            "command_id": str(uuid.uuid4()),
            "reactor_combatant_id": enemy["id"],
            "expected_encounter_revision": 2,
            "expected_combatant_revision": 0,
            "response": "opportunity_attack",
        },
    )
    assert selected.status_code == 200, selected.text
    state = selected.json()
    assert state["reaction_windows"][0]["status"] == "opportunity_attack_pending"
    assert (
        next(row for row in state["combatants"] if row["id"] == enemy["id"])["reaction_available"]
        is False
    )
    blocked = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 3,
            "expected_combatant_revision": 0,
            "path": path,
        },
    )
    assert blocked.status_code == 409
    assert "must resolve before" in blocked.json()["detail"]
    restored = client.get(f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}").json()
    assert restored["combatants"][0]["position_x"] == 1
    assert restored["current_turn"]["movement_spent_feet"] == 0


def test_ranged_attack_persists_damage_mastery_replay_and_idempotency(
    client: TestClient,
) -> None:
    campaign_id, encounter = _started_encounter(client)
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    target = encounter["combatants"][2]
    command_id = str(uuid.uuid4())
    payload = {
        "command_id": command_id,
        "actor_combatant_id": actor["id"],
        "target_combatant_id": target["id"],
        "expected_encounter_revision": 1,
        "expected_actor_revision": 0,
        "expected_target_revision": 0,
        "attack_definition_id": "javelin",
        "attack_mode": "ranged",
        "use_mastery": True,
    }
    _fixed_dice([15, 4])
    attacked = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json=payload,
    )
    assert attacked.status_code == 200, attacked.text
    execution = attacked.json()
    resolution = execution["resolution"]
    state = execution["encounter"]
    assert resolution["attack_result"]["hit"] is True
    assert resolution["attack_result"]["critical"] is False
    assert resolution["attack_result"]["damage_total"] == 7
    assert resolution["attack_result"]["mastery_id"] == "slow"
    assert resolution["attack_result"]["mastery_applied"] is True
    assert resolution["damage_result"]["hit_points_after"] == 3
    assert state["revision"] == 2
    assert state["current_turn"]["action_available"] is False
    assert state["current_turn"]["free_interaction_available"] is False
    assert state["combatants"][0]["revision"] == 1
    assert state["combatants"][2]["hp"] == 3
    assert state["combatants"][2]["revision"] == 1
    assert state["effects"][0]["effect_id"] == "slow"
    assert state["effects"][0]["status"] == "active"
    assert state["events"][-1]["event_type"] == "combat_attack_resolved"

    _fixed_dice([])
    duplicate = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json=payload,
    )
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json() == execution
    replay = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}"
        f"/attacks/{resolution['id']}/replay"
    )
    assert replay.status_code == 200, replay.text
    assert replay.json()["equivalent"] is True

    with get_engine().connect() as connection:
        rolls = connection.execute(
            text(
                "SELECT roll.notation, roll.rolls, roll.modifier, roll.total "
                "FROM dice_rolls roll JOIN combat_commands command "
                "ON command.id = roll.combat_command_id "
                "WHERE command.command_id = CAST(:id AS uuid) ORDER BY roll.roll_index"
            ),
            {"id": command_id},
        ).all()
        assert rolls == [("1d20", [15], 5, 20), ("1d6", [4], 3, 7)]
        inventory = connection.execute(
            text("SELECT inventory FROM characters WHERE id = CAST(:id AS uuid)"),
            {"id": actor["character_id"]},
        ).scalar_one()
        assert inventory["Javelin"] == 7
    for expected_encounter, actor_id, actor_revision in (
        (2, actor["id"], 1),
        (3, state["combatants"][1]["id"], 0),
    ):
        ended = client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/end-turn",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": actor_id,
                "expected_encounter_revision": expected_encounter,
                "expected_combatant_revision": actor_revision,
            },
        )
        assert ended.status_code == 200, ended.text
    slowed_turn = ended.json()["current_turn"]
    assert slowed_turn["combatant_id"] == target["id"]
    assert slowed_turn["movement_allowance_feet"] == 20
    with (
        pytest.raises(DBAPIError, match="canonical character HP must match active combatant HP"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text("UPDATE characters SET hp = hp - 1 WHERE id = CAST(:id AS uuid)"),
            {"id": actor["character_id"]},
        )
    with (
        pytest.raises(DBAPIError, match="active combatant HP must match canonical character HP"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text("UPDATE combatants SET hp = hp - 1 WHERE id = CAST(:id AS uuid)"),
            {"id": actor["id"]},
        )
    with (
        pytest.raises(DBAPIError, match="combat_attack_resolutions is immutable"),
        get_engine().begin() as connection,
    ):
        connection.execute(
            text(
                "UPDATE combat_attack_resolutions SET attack_result = '{}'::jsonb "
                "WHERE id = CAST(:id AS uuid)"
            ),
            {"id": resolution["id"]},
        )

    with get_engine().connect() as connection:
        expected_revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after combat attacks"):
        command.downgrade(config, "0017_combat_turns_movement")
    with get_engine().connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == expected_revision
        )


def test_long_range_disadvantage_and_graze_are_deterministic(client: TestClient) -> None:
    campaign_id, encounter = _started_encounter(client, enemy_x=9)
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    target = encounter["combatants"][2]
    _fixed_dice([])
    same_side = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "target_combatant_id": encounter["combatants"][1]["id"],
            "expected_encounter_revision": 1,
            "expected_actor_revision": 0,
            "expected_target_revision": 0,
            "attack_definition_id": "greatsword",
            "attack_mode": "melee",
        },
    )
    assert same_side.status_code == 409
    assert same_side.json()["detail"] == "Combat attacks require an opposing-side target"
    out_of_reach = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "target_combatant_id": target["id"],
            "expected_encounter_revision": 1,
            "expected_actor_revision": 0,
            "expected_target_revision": 0,
            "attack_definition_id": "greatsword",
            "attack_mode": "melee",
        },
    )
    assert out_of_reach.status_code == 409
    assert out_of_reach.json()["detail"] == "Melee target is outside weapon reach"
    unchanged = client.get(f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}").json()
    assert unchanged["revision"] == 1
    assert unchanged["current_turn"]["action_available"] is True
    with get_engine().connect() as connection:
        assert (
            connection.execute(
                text(
                    "SELECT count(*) FROM dice_rolls "
                    "WHERE combat_encounter_id = CAST(:id AS uuid) "
                    "AND purpose LIKE 'combat attack:%'"
                ),
                {"id": encounter_id},
            ).scalar_one()
            == 0
        )
    _fixed_dice([18, 4])
    long_range = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "target_combatant_id": target["id"],
            "expected_encounter_revision": 1,
            "expected_actor_revision": 0,
            "expected_target_revision": 0,
            "attack_definition_id": "javelin",
            "attack_mode": "ranged",
        },
    )
    assert long_range.status_code == 200, long_range.text
    result = long_range.json()["resolution"]
    assert result["attack_result"]["d20"]["advantage_state"] == "disadvantage"
    assert result["attack_result"]["d20"]["dice_faces"] == [18, 4]
    assert result["attack_result"]["d20"]["selected_die"] == 4
    assert result["attack_result"]["hit"] is False
    assert result["attack_result"]["damage_total"] == 0
    assert result["damage_result"]["hit_points_after"] == 10

    campaign_id, encounter = _started_encounter(client)
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    target = encounter["combatants"][2]
    moved = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "expected_encounter_revision": 1,
            "expected_combatant_revision": 0,
            "path": [{"x": x, "y": 2} for x in range(2, 7)],
        },
    )
    assert moved.status_code == 200, moved.text
    _fixed_dice([1])
    grazed = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "target_combatant_id": target["id"],
            "expected_encounter_revision": 2,
            "expected_actor_revision": 1,
            "expected_target_revision": 0,
            "attack_definition_id": "greatsword",
            "attack_mode": "melee",
        },
    )
    assert grazed.status_code == 200, grazed.text
    result = grazed.json()["resolution"]
    assert result["attack_result"]["hit"] is False
    assert result["attack_result"]["miss_reason"] == "natural_one"
    assert result["attack_result"]["mastery_id"] == "graze"
    assert result["attack_result"]["mastery_applied"] is True
    assert result["attack_result"]["weapon_damage"] is None
    assert result["attack_result"]["damage_total"] == 3
    assert result["damage_result"]["hit_points_after"] == 7


def test_adjacent_hostile_imposes_ranged_attack_disadvantage(client: TestClient) -> None:
    campaign_id, encounter = _started_encounter(client, enemy_x=2, enemy_y=2)
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    target = encounter["combatants"][2]
    _fixed_dice([18, 4])
    attacked = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "target_combatant_id": target["id"],
            "expected_encounter_revision": 1,
            "expected_actor_revision": 0,
            "expected_target_revision": 0,
            "attack_definition_id": "javelin",
            "attack_mode": "ranged",
        },
    )
    assert attacked.status_code == 200, attacked.text
    result = attacked.json()["resolution"]["attack_result"]
    assert result["d20"]["advantage_state"] == "disadvantage"
    assert result["d20"]["disadvantage_sources"] == ["hostile_within_5_feet"]
    assert result["d20"]["selected_die"] == 4
    assert result["hit"] is False


def test_critical_great_weapon_fighting_and_restart_are_exact(client: TestClient) -> None:
    campaign_id, encounter = _started_encounter(
        client,
        enemy_x=2,
        enemy_y=2,
        first_fighting_style="great_weapon_fighting",
    )
    encounter_id = encounter["id"]
    actor = encounter["combatants"][0]
    target = encounter["combatants"][2]
    _fixed_dice([20, 1, 2, 5, 6])
    attacked = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": actor["id"],
            "target_combatant_id": target["id"],
            "expected_encounter_revision": 1,
            "expected_actor_revision": 0,
            "expected_target_revision": 0,
            "attack_definition_id": "greatsword",
            "attack_mode": "melee",
        },
    )
    assert attacked.status_code == 200, attacked.text
    state = attacked.json()["encounter"]
    result = attacked.json()["resolution"]["attack_result"]
    assert result["hit"] is True
    assert result["critical"] is True
    assert result["weapon_damage"]["notation"] == "4d6"
    assert result["weapon_damage"]["original_faces"] == [1, 2, 5, 6]
    assert result["weapon_damage"]["adjusted_faces"] == [3, 3, 5, 6]
    assert result["weapon_damage"]["adjustment"] == "great_weapon_fighting"
    assert result["damage_modifier"] == 3
    assert result["damage_total"] == 20
    assert state["combatants"][2]["hp"] == 0
    assert state["combatants"][2]["state"] == "dead"
    get_engine().dispose()
    restored = client.get(f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}")
    assert restored.status_code == 200, restored.text
    assert restored.json() == state


def test_sap_applies_to_exactly_the_targets_next_attack(client: TestClient) -> None:
    campaign_id, encounter = _started_encounter(client, enemy_x=2, enemy_y=2)
    encounter_id = encounter["id"]
    first, second, enemy = encounter["combatants"]
    _fixed_dice([10, 4])
    flail = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": first["id"],
            "target_combatant_id": enemy["id"],
            "expected_encounter_revision": 1,
            "expected_actor_revision": 0,
            "expected_target_revision": 0,
            "attack_definition_id": "flail",
            "attack_mode": "melee",
        },
    )
    assert flail.status_code == 200, flail.text
    state = flail.json()["encounter"]
    assert flail.json()["resolution"]["attack_result"]["d20"]["total"] == 15
    assert flail.json()["resolution"]["attack_result"]["hit"] is True
    assert state["effects"][0]["effect_id"] == "sap"
    assert state["effects"][0]["status"] == "active"

    for expected_encounter, actor_id, actor_revision in (
        (2, first["id"], 1),
        (3, second["id"], 0),
    ):
        ended = client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/end-turn",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": actor_id,
                "expected_encounter_revision": expected_encounter,
                "expected_combatant_revision": actor_revision,
            },
        )
        assert ended.status_code == 200, ended.text
    _fixed_dice([18, 4])
    goblin_attack = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": enemy["id"],
            "target_combatant_id": second["id"],
            "expected_encounter_revision": 4,
            "expected_actor_revision": 1,
            "expected_target_revision": 0,
            "attack_definition_id": "scimitar",
            "attack_mode": "melee",
        },
    )
    assert goblin_attack.status_code == 200, goblin_attack.text
    result = goblin_attack.json()["resolution"]["attack_result"]
    state = goblin_attack.json()["encounter"]
    assert result["d20"]["advantage_state"] == "disadvantage"
    assert result["d20"]["disadvantage_sources"] == ["sap"]
    assert result["d20"]["selected_die"] == 4
    assert result["hit"] is False
    assert (
        next(effect for effect in state["effects"] if effect["effect_id"] == "sap")["status"]
        == "expired"
    )


def test_opportunity_attack_resolves_then_original_movement_can_continue(
    client: TestClient,
) -> None:
    campaign_id, encounter = _started_encounter(client, enemy_x=2, enemy_y=2)
    encounter_id = encounter["id"]
    mover = encounter["combatants"][0]
    reactor = encounter["combatants"][2]
    path = [{"x": 0, "y": 2}]
    pending = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": mover["id"],
            "expected_encounter_revision": 1,
            "expected_combatant_revision": 0,
            "path": path,
        },
    ).json()
    window = pending["reaction_windows"][0]
    selected = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}"
        f"/reaction-windows/{window['id']}",
        json={
            "command_id": str(uuid.uuid4()),
            "reactor_combatant_id": reactor["id"],
            "expected_encounter_revision": 2,
            "expected_combatant_revision": 0,
            "response": "opportunity_attack",
        },
    )
    assert selected.status_code == 200, selected.text
    _fixed_dice([15, 5])
    attacked = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": reactor["id"],
            "target_combatant_id": mover["id"],
            "expected_encounter_revision": 3,
            "expected_actor_revision": 1,
            "expected_target_revision": 0,
            "attack_definition_id": "scimitar",
            "attack_mode": "melee",
            "reaction_window_id": window["id"],
        },
    )
    assert attacked.status_code == 200, attacked.text
    state = attacked.json()["encounter"]
    assert attacked.json()["resolution"]["attack_result"]["damage_total"] == 7
    assert state["reaction_windows"][0]["status"] == "opportunity_attack_resolved"
    assert state["combatants"][0]["hp"] == 5
    assert state["current_turn"]["action_available"] is True

    continued = client.post(
        f"/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        json={
            "command_id": str(uuid.uuid4()),
            "actor_combatant_id": mover["id"],
            "expected_encounter_revision": 4,
            "expected_combatant_revision": 1,
            "path": path,
        },
    )
    assert continued.status_code == 200, continued.text
    assert continued.json()["combatants"][0]["position_x"] == 0
    assert continued.json()["current_turn"]["movement_spent_feet"] == 5
