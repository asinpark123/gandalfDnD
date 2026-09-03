import json
import os
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from openai import OpenAI
from sqlalchemy import func, select

from app.api import app
from app.db import get_engine, get_session_factory
from app.llm.base import ProviderResult
from app.llm.factory import get_turn_interpreter, get_turn_narrator
from app.llm.openclaw_provider import OpenClawTurnProvider
from app.models import ProviderCall
from app.schemas import DecisionOpen, TurnNarrationOutput
from app.turn_interpretation import TurnIntent
from tests.test_m3_lantern_scenario import (
    ScenarioInterpreter,
    _complete_turn,
    _run_branching_lantern,
)

pytestmark = pytest.mark.skipif(
    os.getenv("GANDALF_RUN_OPENCLAW_M3_LIVE") != "1",
    reason="live OpenClaw M3 evaluation is opt-in",
)

MAX_PROVIDER_ATTEMPTS = 50


class CappedRecordingOpenClawProvider(OpenClawTurnProvider):
    def __init__(self, *args: Any, attempts_used_before: int, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.attempts_used_before = attempts_used_before
        self.attempts = 0
        self.records: list[dict[str, Any]] = []

    def _claim_attempt(self) -> None:
        if self.attempts_used_before + self.attempts >= MAX_PROVIDER_ATTEMPTS:
            raise RuntimeError(f"OpenClaw M3 live cap of {MAX_PROVIDER_ATTEMPTS} reached")
        self.attempts += 1

    @staticmethod
    def _context_summary(context: dict[str, Any]) -> dict[str, Any]:
        world = context["world"]
        selected_target = world.get("selected_target")
        selected_choice = world.get("selected_choice")
        return {
            "world_revision": world["world_revision"],
            "narrative_time_minutes": world["narrative_time_minutes"],
            "location": context["location"]["name"],
            "present_npc_ids": [npc["id"] for npc in world["present_npcs"]],
            "selected_target_id": selected_target["id"] if selected_target else None,
            "selected_choice": selected_choice,
            "fact_values": [fact["value"] for fact in world["facts"]],
        }

    def interpret_action(
        self, context: dict[str, Any], player_action: str
    ) -> ProviderResult[TurnIntent]:
        self._claim_attempt()
        result = super().interpret_action(context, player_action)
        self.records.append(
            {
                "stage": "interpretation",
                "action": player_action,
                "context": self._context_summary(context),
                "output": result.output.model_dump(mode="json"),
            }
        )
        return result

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: Any,
    ) -> ProviderResult[TurnNarrationOutput]:
        self._claim_attempt()
        result = super().narrate_outcome(context, player_action, intent, resolution)
        self.records.append(
            {
                "stage": "narration",
                "action": player_action,
                "context": self._context_summary(context),
                "narration": result.output.narration,
                "state_changes": [
                    change.model_dump(mode="json") for change in result.output.state_changes
                ],
            }
        )
        return result


def _provider() -> CappedRecordingOpenClawProvider:
    token = os.environ.get("GANDALF_OPENCLAW_LIVE_TOKEN", "")
    if not token:
        pytest.fail("GANDALF_OPENCLAW_LIVE_TOKEN is required for an opted-in live run")
    base_url = os.getenv("GANDALF_OPENCLAW_LIVE_BASE_URL", "http://127.0.0.1:18790/v1")
    model = os.getenv("GANDALF_OPENCLAW_LIVE_MODEL") or None
    headers = {"x-openclaw-model": model} if model else None
    sdk = OpenAI(
        api_key=token,
        base_url=base_url.rstrip("/") + "/",
        timeout=180,
        max_retries=0,
        default_headers=headers,
    )
    return CappedRecordingOpenClawProvider(
        base_url=base_url,
        gateway_token=token,
        agent_id="gandalf",
        model=model,
        gm_style="classic_heroic_fantasy",
        timeout_seconds=180,
        client=sdk,
        attempts_used_before=int(os.getenv("GANDALF_OPENCLAW_M3_ATTEMPTS_USED", "0")),
    )


def _live_turn(
    client: TestClient,
    provider: CappedRecordingOpenClawProvider,
    *,
    campaign_id: str,
    actor_id: str,
    action: str,
    target_npc_id: str,
    decision_id: str | None = None,
    decision_option_key: str | None = None,
) -> dict[str, Any]:
    app.dependency_overrides[get_turn_interpreter] = lambda: provider
    app.dependency_overrides[get_turn_narrator] = lambda: provider
    payload: dict[str, Any] = {
        "command_id": str(uuid.uuid4()),
        "action": action,
        "actor_character_id": actor_id,
        "target_npc_id": target_npc_id,
    }
    if decision_id is not None:
        payload["decision_id"] = decision_id
        payload["decision_option_key"] = decision_option_key
    created = client.post(f"/campaigns/{campaign_id}/turn-executions", json=payload)
    assert created.status_code == 201, created.text
    turn_id = created.json()["id"]
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text
    finalized = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert finalized.status_code == 200, finalized.text
    return finalized.json()


def _open_followup_decision(
    client: TestClient,
    *,
    campaign_id: str,
    actor_id: str,
    guide_id: str,
) -> dict[str, Any]:
    app.dependency_overrides[get_turn_interpreter] = lambda: ScenarioInterpreter()
    _complete_turn(
        client,
        campaign_id,
        actor_id,
        [
            DecisionOpen(
                type="decision_open",
                decision_key="tower_followup",
                prompt="How will the party secure the Old Tower after the patrol search?",
                options=[
                    {
                        "option_key": "light_beacon",
                        "label": "Light the restored beacon",
                        "consequences": [
                            {
                                "type": "record_fact",
                                "fact_type": "discovery",
                                "value": (
                                    "The party lit the Old Tower beacon for the Lantern Watch."
                                ),
                            }
                        ],
                    },
                    {
                        "option_key": "seal_cellar",
                        "label": "Seal the flooded cellar",
                        "consequences": [
                            {
                                "type": "record_fact",
                                "fact_type": "discovery",
                                "value": "The party sealed the flooded Old Tower cellar.",
                            }
                        ],
                    },
                ],
            )
        ],
        action="Mira asks how the party will secure the Old Tower.",
        target_npc_id=guide_id,
    )
    world = client.get(f"/campaigns/{campaign_id}/world").json()
    return next(
        decision for decision in world["decisions"] if decision["decision_key"] == "tower_followup"
    )


def _assert_live_context(
    records: list[dict[str, Any]],
    *,
    action: str,
    guide_id: str,
    absent_npc_id: str,
    expected_fact: str,
) -> None:
    matching = [record for record in records if record["action"] == action]
    assert [record["stage"] for record in matching] == ["interpretation", "narration"]
    for record in matching:
        context = record["context"]
        assert context["location"] == "Old Tower"
        assert context["selected_target_id"] == guide_id
        assert guide_id in context["present_npc_ids"]
        assert absent_npc_id not in context["present_npc_ids"]
        assert expected_fact in context["fact_values"]


def test_capped_live_openclaw_reads_and_narrates_persistent_m3_branches(
    client: TestClient,
) -> None:
    provider = _provider()
    branch_specs = [
        (
            "signal_bridge",
            "light_beacon",
            "The party rescued the patrol across the signal bridge.",
            "The party lit the Old Tower beacon for the Lantern Watch.",
        ),
        (
            "flooded_tunnel",
            "seal_cellar",
            "The flooded tunnel collapsed before the patrol was found.",
            "The party sealed the flooded Old Tower cellar.",
        ),
    ]
    evaluated: list[dict[str, Any]] = []

    for route, followup_option, route_fact, followup_fact in branch_specs:
        world, ids = _run_branching_lantern(client, route)
        campaign_id = ids["campaign_id"]
        actor_id = ids["character_ids"][0]
        guide_id = ids["guide_npc_id"]
        absent_npc_id = ids["absent_npc_id"]
        assert route_fact in {fact["value"] for fact in world["facts"]}

        recap_action = (
            f"Arin asks Mira to recap the consequences of choosing {route} and the patrol search."
        )
        recap = _live_turn(
            client,
            provider,
            campaign_id=campaign_id,
            actor_id=actor_id,
            action=recap_action,
            target_npc_id=guide_id,
        )
        assert recap["turn"]["status"] == "completed"

        attempts_before_absent = provider.attempts
        absent = client.post(
            f"/campaigns/{campaign_id}/turn-executions",
            json={
                "command_id": str(uuid.uuid4()),
                "action": "Ask the absent caravan guard for help.",
                "actor_character_id": actor_id,
                "target_npc_id": absent_npc_id,
            },
        )
        assert absent.status_code == 409
        assert absent.json()["code"] == "world_target_not_present"
        assert provider.attempts == attempts_before_absent

        decision = _open_followup_decision(
            client,
            campaign_id=campaign_id,
            actor_id=actor_id,
            guide_id=guide_id,
        )
        decision_action = f"The party chooses {followup_option} to secure the Old Tower."
        selected = _live_turn(
            client,
            provider,
            campaign_id=campaign_id,
            actor_id=actor_id,
            action=decision_action,
            target_npc_id=guide_id,
            decision_id=decision["id"],
            decision_option_key=followup_option,
        )
        assert selected["turn"]["status"] == "completed"
        after_choice = client.get(f"/campaigns/{campaign_id}/world").json()
        assert [fact["value"] for fact in after_choice["facts"]].count(followup_fact) == 1
        selected_followup = next(
            item for item in after_choice["decisions"] if item["decision_key"] == "tower_followup"
        )
        assert selected_followup["selected_option_key"] == followup_option

        get_engine().dispose()
        followup_action = f"Arin asks Mira what {followup_option} means for the Old Tower now."
        followup = _live_turn(
            client,
            provider,
            campaign_id=campaign_id,
            actor_id=actor_id,
            action=followup_action,
            target_npc_id=guide_id,
        )
        assert followup["turn"]["status"] == "completed"
        final_world = client.get(f"/campaigns/{campaign_id}/world").json()
        assert final_world["location"]["name"] == "Old Tower"
        assert final_world["present_npcs"][0]["id"] == guide_id
        assert route_fact in {fact["value"] for fact in final_world["facts"]}
        assert [fact["value"] for fact in final_world["facts"]].count(followup_fact) == 1

        _assert_live_context(
            provider.records,
            action=recap_action,
            guide_id=guide_id,
            absent_npc_id=absent_npc_id,
            expected_fact=route_fact,
        )
        _assert_live_context(
            provider.records,
            action=followup_action,
            guide_id=guide_id,
            absent_npc_id=absent_npc_id,
            expected_fact=followup_fact,
        )
        matching_choice = [
            record for record in provider.records if record["action"] == decision_action
        ]
        assert [record["stage"] for record in matching_choice] == [
            "interpretation",
            "narration",
        ]
        assert all(
            record["context"]["selected_choice"]["option_key"] == followup_option
            for record in matching_choice
        )
        evaluated.append(
            {
                "campaign_id": campaign_id,
                "route": route,
                "followup_option": followup_option,
                "guide_npc_id": guide_id,
                "absent_target_status": absent.status_code,
                "world_revision": final_world["world_revision"],
            }
        )

    campaign_ids = [uuid.UUID(item["campaign_id"]) for item in evaluated]
    with get_session_factory()() as session:
        live_calls = list(
            session.scalars(
                select(ProviderCall)
                .where(
                    ProviderCall.campaign_id.in_(campaign_ids),
                    ProviderCall.provider == "openclaw",
                )
                .order_by(ProviderCall.created_at, ProviderCall.id)
            )
        )
        totals = session.execute(
            select(
                func.sum(ProviderCall.input_tokens),
                func.sum(ProviderCall.output_tokens),
                func.round(func.avg(ProviderCall.latency_ms)),
                func.max(ProviderCall.latency_ms),
            ).where(
                ProviderCall.campaign_id.in_(campaign_ids),
                ProviderCall.provider == "openclaw",
            )
        ).one()

    assert provider.attempts == len(live_calls) == 12
    assert provider.attempts_used_before + provider.attempts <= MAX_PROVIDER_ATTEMPTS
    assert all(call.status == "succeeded" for call in live_calls)
    assert [call.stage for call in live_calls].count("interpretation") == 6
    assert [call.stage for call in live_calls].count("narration") == 6
    assert all((call.input_tokens or 0) > 0 for call in live_calls)
    assert all((call.output_tokens or 0) > 0 for call in live_calls)

    print(
        "OpenClaw M3 live evidence: "
        + json.dumps(
            {
                "cap": MAX_PROVIDER_ATTEMPTS,
                "attempts_used_before_run": provider.attempts_used_before,
                "provider_attempts": provider.attempts,
                "total_attempts_used": provider.attempts_used_before + provider.attempts,
                "successful_calls": len(live_calls),
                "input_tokens": totals[0],
                "output_tokens": totals[1],
                "average_latency_ms": totals[2],
                "maximum_latency_ms": totals[3],
                "branches": evaluated,
                "narrations": [
                    {
                        "action": record["action"],
                        "narration": record["narration"],
                        "state_changes": record["state_changes"],
                    }
                    for record in provider.records
                    if record["stage"] == "narration"
                ],
            },
            default=str,
        )
    )
