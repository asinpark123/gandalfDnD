"""Create concise deterministic M5.5 owner-review scenarios in the development database."""

from __future__ import annotations

import argparse
import json
import uuid
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import make_url, text

from app.api import app
from app.config import get_settings
from app.db import get_engine
from app.dice import DiceService, get_dice_service


class FixedRandom:
    algorithm_version = "fixed-m5.5-owner-sequence-1.0.0"

    def __init__(self, results: list[int]) -> None:
        self._results = iter(results)

    def randint(self, start: int, end: int) -> int:
        try:
            value = next(self._results)
        except StopIteration as exc:
            raise RuntimeError("Owner fixture requested an unexpected die roll") from exc
        if not start <= value <= end:
            raise RuntimeError(f"Fixed die face {value} is outside {start}..{end}")
        return value


def _fixed_dice(results: list[int]) -> None:
    app.dependency_overrides[get_dice_service] = lambda: DiceService(FixedRandom(results))


def _request(response: Any, expected: int = 200) -> dict[str, Any]:
    if response.status_code != expected:
        raise RuntimeError(f"Fixture request failed ({response.status_code}): {response.text}")
    return response.json()


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


def _ready_party(client: TestClient, name: str) -> tuple[str, str, list[str]]:
    campaign = _request(
        client.post(
            "/campaigns",
            json={
                "name": name,
                "starting_scene": {
                    "title": "M5.5 Review Arena",
                    "summary": "An isolated deterministic owner-review encounter.",
                },
            },
        ),
        201,
    )
    character_ids: list[str] = []
    for index, character_name in enumerate(("Arin", "Bryn")):
        draft = _request(
            client.post(f"/campaigns/{campaign['id']}/characters", json={"name": character_name}),
            201,
        )
        character_ids.append(draft["id"])
        _request(
            client.post(
                f"/campaigns/{campaign['id']}/characters/{draft['id']}/finalize",
                json=_finalize_payload(alternate=index == 1),
            )
        )
    world = _request(client.get(f"/campaigns/{campaign['id']}/world"))
    return campaign["id"], world["scene"]["id"], character_ids


def _create_encounter(
    client: TestClient,
    name: str,
    *,
    enemy_count: int = 1,
    enemy_x: int = 7,
    enemy_y: int = 2,
) -> tuple[str, dict[str, Any]]:
    campaign_id, scene_id, character_ids = _ready_party(client, name)
    encounter = _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters",
            json={
                "command_id": str(uuid.uuid4()),
                "expected_world_revision": 0,
                "scene_id": scene_id,
                "combat_catalog_id": "srd-5.2.1-combat-v2",
                "grid_width": 12,
                "grid_height": 8,
                "party": [
                    {"character_id": character_ids[0], "x": 1, "y": 2},
                    {"character_id": character_ids[1], "x": 1, "y": 3},
                ],
                "enemies": [
                    {
                        "monster_definition_id": "goblin_warrior",
                        "instance_name": f"Review Goblin {index + 1}",
                        "x": enemy_x + index,
                        "y": enemy_y,
                    }
                    for index in range(enemy_count)
                ],
            },
        ),
        201,
    )
    return campaign_id, encounter


def _start(
    client: TestClient, campaign_id: str, encounter: dict[str, Any], dice: list[int]
) -> dict[str, Any]:
    _fixed_dice(dice)
    return _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/start",
            json={"command_id": str(uuid.uuid4()), "expected_encounter_revision": 0},
        )
    )


def _difficulty_samples(client: TestClient) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for enemy_count in range(1, 5):
        _, encounter = _create_encounter(
            client, f"M5.5 Difficulty {enemy_count}", enemy_count=enemy_count, enemy_x=5
        )
        samples.append(
            {
                "goblin_warriors": enemy_count,
                "enemy_xp": encounter["enemy_xp"],
                "label": encounter["difficulty_label"],
                "party_budgets": {
                    "low": encounter["low_xp_budget"],
                    "moderate": encounter["moderate_xp_budget"],
                    "high": encounter["high_xp_budget"],
                },
            }
        )
    return samples


def _second_wind_and_restart(client: TestClient) -> dict[str, Any]:
    campaign_id, created = _create_encounter(client, "M5.5 Second Wind")
    encounter = _start(client, campaign_id, created, [18, 12, 5])
    actor = encounter["combatants"][0]
    with get_engine().begin() as connection:
        connection.execute(
            text("UPDATE characters SET hp = 5 WHERE id = CAST(:id AS uuid)"),
            {"id": actor["character_id"]},
        )
        connection.execute(
            text("UPDATE combatants SET hp = 5 WHERE id = CAST(:id AS uuid)"),
            {"id": actor["id"]},
        )
    _fixed_dice([6])
    result = _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/health-actions",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": actor["id"],
                "target_combatant_id": actor["id"],
                "expected_encounter_revision": 1,
                "expected_actor_revision": 0,
                "expected_target_revision": 0,
                "action": "second_wind",
            },
        )
    )
    get_engine().dispose()
    restored = _request(client.get(f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}"))
    return {
        "campaign_id": campaign_id,
        "encounter_id": encounter["id"],
        "starting_hp": 5,
        "die": 6,
        "fighter_level": 1,
        "ending_hp": result["encounter"]["combatants"][0]["hp"],
        "uses_remaining": result["encounter"]["combatants"][0]["second_wind_remaining"],
        "bonus_action_remaining": result["encounter"]["current_turn"]["bonus_action_available"],
        "restart_state_matches": restored == result["encounter"],
    }


def _natural_twenty_death_save(client: TestClient) -> dict[str, Any]:
    campaign_id, created = _create_encounter(client, "M5.5 Death Save")
    encounter = _start(client, campaign_id, created, [18, 12, 5])
    actor = encounter["combatants"][0]
    with get_engine().begin() as connection:
        connection.execute(
            text("UPDATE characters SET hp = 0 WHERE id = CAST(:id AS uuid)"),
            {"id": actor["character_id"]},
        )
        connection.execute(
            text(
                "UPDATE combatants SET hp = 0, state = 'unconscious' WHERE id = CAST(:id AS uuid)"
            ),
            {"id": actor["id"]},
        )
    _fixed_dice([20])
    result = _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/health-actions",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": actor["id"],
                "target_combatant_id": actor["id"],
                "expected_encounter_revision": 1,
                "expected_actor_revision": 0,
                "expected_target_revision": 0,
                "action": "death_save",
            },
        )
    )
    return {
        "campaign_id": campaign_id,
        "die": 20,
        "outcome": result["resolution"]["result"]["outcome"],
        "hp": result["encounter"]["combatants"][0]["hp"],
        "state": result["encounter"]["combatants"][0]["state"],
    }


def _knockout_victory(client: TestClient) -> dict[str, Any]:
    campaign_id, created = _create_encounter(client, "M5.5 Knockout", enemy_x=2, enemy_y=2)
    encounter = _start(client, campaign_id, created, [18, 12, 5])
    actor = encounter["combatants"][0]
    target = encounter["combatants"][2]
    _fixed_dice([15, 4, 4])
    result = _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/attacks",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": actor["id"],
                "target_combatant_id": target["id"],
                "expected_encounter_revision": 1,
                "expected_actor_revision": 0,
                "expected_target_revision": 0,
                "attack_definition_id": "greatsword",
                "attack_mode": "melee",
                "knock_out": True,
            },
        )
    )
    target_after = result["encounter"]["combatants"][2]
    return {
        "campaign_id": campaign_id,
        "attack_damage_before_knockout": result["resolution"]["attack_result"]["damage_total"],
        "target_hp": target_after["hp"],
        "target_state": target_after["state"],
        "encounter_outcome": result["encounter"]["outcome"],
        "summary": result["encounter"]["outcome_summary"],
    }


def _party_defeat(client: TestClient) -> dict[str, Any]:
    campaign_id, created = _create_encounter(client, "M5.5 Defeat", enemy_x=2, enemy_y=2)
    encounter = _start(client, campaign_id, created, [1, 2, 18])
    enemy = next(row for row in encounter["combatants"] if row["side"] == "enemy")
    party = [row for row in encounter["combatants"] if row["side"] == "party"]
    with get_engine().begin() as connection:
        connection.execute(
            text("UPDATE characters SET hp = 0 WHERE id = CAST(:id AS uuid)"),
            {"id": party[0]["character_id"]},
        )
        connection.execute(
            text("UPDATE combatants SET hp = 0, state = 'stable' WHERE id = CAST(:id AS uuid)"),
            {"id": party[0]["id"]},
        )
        connection.execute(
            text("UPDATE characters SET hp = 5 WHERE id = CAST(:id AS uuid)"),
            {"id": party[1]["character_id"]},
        )
        connection.execute(
            text("UPDATE combatants SET hp = 5 WHERE id = CAST(:id AS uuid)"),
            {"id": party[1]["id"]},
        )
    _fixed_dice([15, 6])
    result = _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/attacks",
            json={
                "command_id": str(uuid.uuid4()),
                "actor_combatant_id": enemy["id"],
                "target_combatant_id": party[1]["id"],
                "expected_encounter_revision": 1,
                "expected_actor_revision": 0,
                "expected_target_revision": 0,
                "attack_definition_id": "scimitar",
                "attack_mode": "melee",
            },
        )
    )
    retry = client.post(
        f"/campaigns/{campaign_id}/combat-encounters",
        json={
            "command_id": str(uuid.uuid4()),
            "expected_world_revision": result["encounter"]["events"][-1]["payload"][
                "world_revision"
            ],
            "scene_id": result["encounter"]["scene_id"],
            "combat_catalog_id": "srd-5.2.1-combat-v2",
            "grid_width": 12,
            "grid_height": 8,
            "party": [
                {"character_id": party[0]["character_id"], "x": 1, "y": 2},
                {"character_id": party[1]["character_id"], "x": 1, "y": 3},
            ],
            "enemies": [
                {
                    "monster_definition_id": "goblin_warrior",
                    "instance_name": "Improper Recovery Goblin",
                    "x": 7,
                    "y": 2,
                }
            ],
        },
    )
    return {
        "campaign_id": campaign_id,
        "encounter_outcome": result["encounter"]["outcome"],
        "party": [
            {"name": row["instance_name"], "hp": row["hp"], "state": row["state"]}
            for row in result["encounter"]["combatants"]
            if row["side"] == "party"
        ],
        "summary": result["encounter"]["outcome_summary"],
        "new_combat_rejected": retry.status_code == 409,
        "recovery_error": retry.json().get("detail"),
    }


def _javelin_recovery(client: TestClient) -> dict[str, Any]:
    campaign_id, created = _create_encounter(client, "M5.5 Javelin Recovery")
    encounter = _start(client, campaign_id, created, [18, 12, 5])
    actor = encounter["combatants"][0]
    target = encounter["combatants"][2]
    _fixed_dice([15, 1])
    attacked = _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/attacks",
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
    )
    completed = _request(
        client.post(
            f"/campaigns/{campaign_id}/combat-encounters/{encounter['id']}/outcome",
            json={
                "command_id": str(uuid.uuid4()),
                "expected_encounter_revision": attacked["encounter"]["revision"],
                "outcome": "agreement",
            },
        )
    )
    return {
        "campaign_id": campaign_id,
        "outcome": completed["encounter"]["outcome"],
        "recovered_items": completed["resolution"]["summary"]["recovered_items"],
        "completion_event_count": sum(
            event["event_type"] == "combat_encounter_completed"
            for event in completed["encounter"]["events"]
        ),
    }


def build_report() -> dict[str, Any]:
    with TestClient(app) as client:
        return {
            "fixture": "m5.5-owner-health-outcomes-v1",
            "database": make_url(get_settings().database_url).database,
            "difficulty_samples": _difficulty_samples(client),
            "second_wind_and_restart": _second_wind_and_restart(client),
            "natural_twenty_death_save": _natural_twenty_death_save(client),
            "explicit_knockout_victory": _knockout_victory(client),
            "party_defeat": _party_defeat(client),
            "javelin_recovery": _javelin_recovery(client),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-create",
        action="store_true",
        help="Confirm creation of isolated development campaigns.",
    )
    args = parser.parse_args()
    database_name = make_url(get_settings().database_url).database or ""
    if not database_name.startswith("gandalfdnd_dev"):
        raise SystemExit("Refusing to run outside a gandalfdnd_dev database")
    if not args.confirm_create:
        raise SystemExit("Pass --confirm-create after reading the owner checklist")
    try:
        report = build_report()
    finally:
        app.dependency_overrides.clear()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
