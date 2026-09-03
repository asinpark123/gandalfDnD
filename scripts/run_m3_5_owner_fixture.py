"""Create two reviewable M3.5 branch campaigns in the development database."""

import argparse
import json
from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient

from app.api import app
from app.config import get_settings
from tests.test_m3_lantern_scenario import _run_branching_lantern


def _print_stage(label: str, stage: str, payload: dict[str, Any]) -> None:
    world = payload.get("world")
    print(f"\n[{label}] {stage.replace('_', ' ')}")
    if stage == "quest_offer":
        decision = payload["decision"]
        print(f"Decision opened: {decision['decision_key']}")
        return
    if stage == "route_choice":
        decision = payload["decision"]
        print(f"Decision opened: {decision['decision_key']}")
        return
    if world is None:
        return
    summary = {
        "campaign_id": payload["campaign_id"],
        "world_revision": world["world_revision"],
        "location": world["location"]["name"],
        "narrative_time_minutes": world["narrative_time_minutes"],
        "present_npcs": [
            {
                "id": npc["id"],
                "name": npc["name"],
                "description": npc["public_description"],
            }
            for npc in world["present_npcs"]
        ],
        "continuity_facts": [
            {
                "subject_npc_id": fact["subject_npc_id"],
                "type": fact["fact_type"],
                "value": fact["value"],
            }
            for fact in world["facts"]
            if fact["fact_type"] in {"promise", "npc_attitude", "discovery"}
        ],
        "quests": [
            {
                "title": quest["title"],
                "status": quest["status"],
                "objectives": [
                    {"title": objective["title"], "status": objective["status"]}
                    for objective in quest["objectives"]
                ],
            }
            for quest in world["quests"]
        ],
        "selected_decisions": [
            {
                "key": decision["decision_key"],
                "option": decision["selected_option_key"],
            }
            for decision in world["decisions"]
            if decision["selected_option_key"] is not None
        ],
    }
    if "absent_target_error" in payload:
        summary["absent_target_error"] = payload["absent_target_error"]
    if "selected_route" in payload:
        summary["selected_route"] = payload["selected_route"]
    print(json.dumps(summary, indent=2))


def _guided_selector(label: str, used_routes: list[str]) -> Callable[[dict[str, Any]], str]:
    def select(decision: dict[str, Any]) -> str:
        print(f"\n[{label}] {decision['prompt']}")
        for option in decision["options"]:
            print(f"  {option['option_key']}: {option['label']}")
        valid_options = {option["option_key"] for option in decision["options"]}
        while True:
            selected = input("Choose an option key: ").strip()
            if selected not in valid_options:
                print(f"Choose one of: {', '.join(sorted(valid_options))}")
                continue
            if decision["decision_key"] == "accept_lantern_patrol" and selected != "accept":
                print(
                    "This complete-path acceptance retest requires 'accept'; choose it to continue."
                )
                continue
            if decision["decision_key"] == "tower_route" and selected in used_routes:
                print("Choose the other route so both deterministic outcomes are covered.")
                continue
            if decision["decision_key"] == "tower_route":
                used_routes.append(selected)
            return selected

    return select


def _run_guided(client: TestClient) -> dict[str, Any]:
    routes: list[str] = []
    results: dict[str, Any] = {}
    for label in ("campaign_one", "campaign_two"):
        world, ids = _run_branching_lantern(
            client,
            None,
            select_decision=_guided_selector(label, routes),
            observe=lambda stage, payload, label=label: _print_stage(label, stage, payload),
        )
        results[label] = {**ids, "world": world}
    return {
        "fixture": "m3.5-guided-owner-retest-v2",
        "selected_routes": routes,
        **results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--guided",
        action="store_true",
        help="pause for the owner's quest and route choices and print review checkpoints",
    )
    args = parser.parse_args()
    database_name = get_settings().database_url.rsplit("/", 1)[-1].split("?", 1)[0]
    if not database_name.startswith("gandalfdnd_dev"):
        raise RuntimeError(
            "Refusing to create the M3.5 owner fixture outside a gandalfdnd_dev database"
        )
    with TestClient(app) as client:
        if args.guided:
            result = _run_guided(client)
        else:
            bridge_world, bridge_ids = _run_branching_lantern(client, "signal_bridge")
            tunnel_world, tunnel_ids = _run_branching_lantern(client, "flooded_tunnel")
            result = {
                "fixture": "m3.5-branching-lantern-v2",
                "signal_bridge": {**bridge_ids, "world": bridge_world},
                "flooded_tunnel": {**tunnel_ids, "world": tunnel_world},
            }
    print(
        json.dumps(
            {
                "database": database_name,
                "external_provider_calls": 0,
                **result,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
