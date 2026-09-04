import json
import uuid
from typing import Any, cast

from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError

from app.api import app
from app.db import get_session_factory
from app.embeddings import DeterministicEmbeddingProvider
from app.llm.base import ProviderResult
from app.llm.factory import get_turn_interpreter, get_turn_narrator
from app.memory import (
    activate_memory_index,
    drain_index_jobs,
    ensure_embedding_profile,
    start_index_build,
)
from app.memory_context import (
    MemorySummaryOutput,
    MemorySummaryRequest,
    TurnMemoryContextService,
    get_turn_memory_context_service,
)
from app.models import (
    MemoryRetrieval,
    MemorySummary,
    MemorySummarySource,
    MemorySummaryUse,
    ProviderCall,
)
from app.schemas import TurnNarrationOutput
from app.turn_interpretation import NarrativeIntent, TurnIntent


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
    campaign = client.post(
        "/campaigns", json={"name": "M4.4 Memory Context", "starting_location": "Lantern Archive"}
    )
    assert campaign.status_code == 201, campaign.text
    campaign_id = campaign.json()["id"]
    characters: list[str] = []
    for index, name in enumerate(("Arin", "Bryn")):
        draft = client.post(f"/campaigns/{campaign_id}/characters", json={"name": name})
        assert draft.status_code == 201, draft.text
        character_id = draft.json()["id"]
        finalized = client.post(
            f"/campaigns/{campaign_id}/characters/{character_id}/finalize",
            json=_finalize_payload(alternate=index == 1),
        )
        assert finalized.status_code == 200, finalized.text
        characters.append(character_id)
    return campaign_id, characters


def _create_turn(client: TestClient, campaign_id: str, actor_id: str, action: str) -> str:
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


class CapturingInterpreter:
    provider_name = "capturing_interpreter"
    model_name = None
    interpretation_prompt_version = "capture-intent-1.0.0"

    def __init__(self) -> None:
        self.contexts: list[dict[str, Any]] = []

    def interpret_action(
        self, context: dict[str, Any], player_action: str
    ) -> ProviderResult[TurnIntent]:
        self.contexts.append(context)
        return ProviderResult(
            output=NarrativeIntent(type="narrative", summary="Continue the conversation."),
            input_tokens=max(1, len(json.dumps(context)) // 4),
            output_tokens=8,
        )


class CapturingNarrator:
    provider_name = "capturing_narrator"
    model_name = None
    narration_prompt_version = "capture-narration-1.0.0"

    def __init__(self) -> None:
        self.contexts: list[dict[str, Any]] = []

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: Any,
    ) -> ProviderResult[TurnNarrationOutput]:
        self.contexts.append(context)
        return ProviderResult(
            output=TurnNarrationOutput(
                narration="The archivist confirms the silver key remains beneath the sundial.",
                resolution_id=None,
                acknowledged_outcome=None,
                state_changes=[],
            ),
            input_tokens=max(1, len(json.dumps(context)) // 4),
            output_tokens=16,
        )


class CountingSummaryProvider:
    provider_name = "test_summary"
    model_name = "offline-test"

    def __init__(self, prompt_version: str = "summary-test-1.0.0") -> None:
        self.prompt_version = prompt_version
        self.calls = 0

    def summarize(self, request: MemorySummaryRequest) -> ProviderResult[MemorySummaryOutput]:
        self.calls += 1
        return ProviderResult(
            output=MemorySummaryOutput(
                summary="Earlier, the archivist said the silver key was beneath the sundial.",
                source_document_ids=[source.document_id for source in request.sources],
            ),
            input_tokens=41,
            output_tokens=17,
        )


class InvalidSummaryProvider:
    provider_name = "invalid_test_summary"
    model_name = None
    prompt_version = "invalid-summary-test-1.0.0"

    def summarize(self, request: MemorySummaryRequest) -> MemorySummaryOutput:
        return cast(
            MemorySummaryOutput,
            {"summary": "Unsupported and uncited output.", "source_document_ids": []},
        )


def _complete_turn(client: TestClient, campaign_id: str, actor_id: str, action: str) -> str:
    turn_id = _create_turn(client, campaign_id, actor_id, action)
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text
    finalized = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize")
    assert finalized.status_code == 200, finalized.text
    return turn_id


def _activate_index(campaign_id: str) -> DeterministicEmbeddingProvider:
    provider = DeterministicEmbeddingProvider(dimensions=48)
    with get_session_factory()() as session:
        profile = ensure_embedding_profile(session, provider)
        start_index_build(
            session,
            campaign_id=uuid.UUID(campaign_id),
            profile_id=profile.id,
        )
        session.commit()
        profile_id = profile.id
    drained = drain_index_jobs(provider=provider, worker_id="m4-4-test", limit=20)
    assert drained.failed == 0
    assert drained.completed >= 1
    with get_session_factory()() as session:
        activate_memory_index(
            session,
            campaign_id=uuid.UUID(campaign_id),
            profile_id=profile_id,
            quality_gate={"passed": True, "fixture": "m4.4"},
        )
        session.commit()
    return provider


def _memory_service(
    embedding: DeterministicEmbeddingProvider,
    summary: CountingSummaryProvider | InvalidSummaryProvider,
) -> TurnMemoryContextService:
    return TurnMemoryContextService(
        embedding_provider_factory=lambda: embedding,
        summary_provider=summary,
    )


class RecordingMemoryContextService:
    def __init__(self, wrapped: TurnMemoryContextService) -> None:
        self.wrapped = wrapped
        self.results: list[dict[str, Any] | None] = []
        self.exceptions: list[Exception] = []

    def build(self, **kwargs: Any) -> dict[str, Any] | None:
        try:
            result = self.wrapped.build(**kwargs)
        except Exception as exc:
            self.exceptions.append(exc)
            raise
        self.results.append(result)
        return result


def test_early_memory_reaches_both_stages_with_citations_and_bounded_overhead(
    client: TestClient,
) -> None:
    interpreter = CapturingInterpreter()
    narrator = CapturingNarrator()
    app.dependency_overrides[get_turn_interpreter] = lambda: interpreter
    app.dependency_overrides[get_turn_narrator] = lambda: narrator
    campaign_id, characters = _ready_campaign(client)
    early_turn_id = _complete_turn(
        client,
        campaign_id,
        characters[0],
        "Ask the archivist where the silver key is hidden.",
    )
    assert "historical_memory" not in interpreter.contexts[-1]
    assert "historical_memory" not in narrator.contexts[-1]

    embedding = _activate_index(campaign_id)
    summary_provider = CountingSummaryProvider()
    memory_service = RecordingMemoryContextService(_memory_service(embedding, summary_provider))
    dependency_calls: list[bool] = []

    def memory_override() -> RecordingMemoryContextService:
        dependency_calls.append(True)
        return memory_service

    app.dependency_overrides[get_turn_memory_context_service] = memory_override
    interpreter.contexts.clear()
    narrator.contexts.clear()

    later_turn_id = _complete_turn(
        client,
        campaign_id,
        characters[0],
        "Ask whether the silver key is still beneath the sundial.",
    )

    assert len(dependency_calls) == 2
    assert not memory_service.exceptions
    assert len(memory_service.results) == 2
    assert all(result is not None for result in memory_service.results)

    for context in (interpreter.contexts[-1], narrator.contexts[-1]):
        memory = context["historical_memory"]
        assert memory["trust"] == "untrusted_historical_prose"
        assert memory["source_item_count"] == len(memory["citations"]) >= 1
        assert any(citation["source_turn_id"] == early_turn_id for citation in memory["citations"])
        assert memory["source_selected_chars"] <= 6000
        assert len(memory["summary"]) <= 3000
        exact_context = {k: v for k, v in context.items() if k != "historical_memory"}
        exact_chars = len(json.dumps(exact_context))
        total_chars = len(json.dumps(context))
        assert 0 < total_chars - exact_chars < 6000

    assert summary_provider.calls == 1
    with get_session_factory()() as session:
        summaries = list(session.scalars(select(MemorySummary).order_by(MemorySummary.created_at)))
        uses = list(session.scalars(select(MemorySummaryUse).order_by(MemorySummaryUse.created_at)))
        sources = list(session.scalars(select(MemorySummarySource)))
        retrievals = list(session.scalars(select(MemoryRetrieval)))
        provider_calls = list(
            session.scalars(
                select(ProviderCall).where(ProviderCall.turn_id == uuid.UUID(later_turn_id))
            )
        )
        assert len(summaries) == 1
        assert summaries[0].status == "succeeded"
        assert (summaries[0].input_tokens, summaries[0].output_tokens) == (41, 17)
        assert len(sources) == summaries[0].source_count
        assert {use.stage for use in uses} == {"interpretation", "narration"}
        assert {use.summary_id for use in uses} == {summaries[0].id}
        assert len(retrievals) == len(uses) == 2
        assert all(retrieval.turn_id == uuid.UUID(later_turn_id) for retrieval in retrievals)
        expected_input_tokens = {
            "interpretation": len(json.dumps(interpreter.contexts[-1])) // 4,
            "narration": len(json.dumps(narrator.contexts[-1])) // 4,
        }
        assert {call.stage: call.input_tokens for call in provider_calls} == expected_input_tokens

    replacement_provider = CountingSummaryProvider("summary-test-2.0.0")
    replacement_service = _memory_service(embedding, replacement_provider)
    pending_turn_id = _create_turn(
        client,
        campaign_id,
        characters[0],
        "Ask whether the silver key is still beneath the sundial.",
    )
    replacement = replacement_service.build(
        campaign_id=uuid.UUID(campaign_id),
        turn_id=uuid.UUID(pending_turn_id),
        stage="interpretation",
        player_action="Ask whether the silver key is still beneath the sundial.",
    )
    assert replacement is not None
    with get_session_factory()() as session:
        new_summary = session.get(MemorySummary, uuid.UUID(replacement["summary_id"]))
        assert new_summary is not None
        assert new_summary.replaces_summary_id == summaries[0].id


def test_malformed_summary_falls_back_to_exact_state_without_failing_gameplay(
    client: TestClient,
) -> None:
    interpreter = CapturingInterpreter()
    narrator = CapturingNarrator()
    app.dependency_overrides[get_turn_interpreter] = lambda: interpreter
    app.dependency_overrides[get_turn_narrator] = lambda: narrator
    campaign_id, characters = _ready_campaign(client)
    _complete_turn(
        client,
        campaign_id,
        characters[0],
        "Ask the archivist about the silver key.",
    )
    embedding = _activate_index(campaign_id)
    invalid_service = _memory_service(embedding, InvalidSummaryProvider())
    app.dependency_overrides[get_turn_memory_context_service] = lambda: invalid_service
    interpreter.contexts.clear()
    narrator.contexts.clear()

    turn_id = _complete_turn(
        client,
        campaign_id,
        characters[0],
        "Return to the archivist and ask about the silver key.",
    )

    assert "historical_memory" not in interpreter.contexts[-1]
    assert "historical_memory" not in narrator.contexts[-1]
    response = client.get(f"/campaigns/{campaign_id}/turn-executions/{turn_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    with get_session_factory()() as session:
        failures = list(
            session.scalars(
                select(MemorySummary).where(
                    MemorySummary.provider == "invalid_test_summary",
                    MemorySummary.status == "failed",
                )
            )
        )
        assert len(failures) == 2
        assert {failure.error_code for failure in failures} == {"invalid_summary_output"}

    mismatched_service = _memory_service(
        DeterministicEmbeddingProvider(dimensions=47), CountingSummaryProvider()
    )
    app.dependency_overrides[get_turn_memory_context_service] = lambda: mismatched_service
    interpreter.contexts.clear()
    narrator.contexts.clear()
    retrieval_failure_turn_id = _complete_turn(
        client,
        campaign_id,
        characters[0],
        "Ask one final time about the silver key.",
    )
    assert "historical_memory" not in interpreter.contexts[-1]
    assert "historical_memory" not in narrator.contexts[-1]
    response = client.get(f"/campaigns/{campaign_id}/turn-executions/{retrieval_failure_turn_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    with get_session_factory()() as session:
        retrieval_failures = list(
            session.scalars(
                select(MemoryRetrieval).where(
                    MemoryRetrieval.turn_id == uuid.UUID(retrieval_failure_turn_id),
                    MemoryRetrieval.status == "failed",
                )
            )
        )
        assert len(retrieval_failures) == 2
        assert {failure.error_code for failure in retrieval_failures} == {"retrieval_failed"}


def test_successful_summary_records_are_database_immutable(client: TestClient) -> None:
    interpreter = CapturingInterpreter()
    narrator = CapturingNarrator()
    app.dependency_overrides[get_turn_interpreter] = lambda: interpreter
    app.dependency_overrides[get_turn_narrator] = lambda: narrator
    campaign_id, characters = _ready_campaign(client)
    _complete_turn(client, campaign_id, characters[0], "Ask about the silver key.")
    embedding = _activate_index(campaign_id)
    app.dependency_overrides[get_turn_memory_context_service] = lambda: _memory_service(
        embedding, CountingSummaryProvider()
    )
    turn_id = _create_turn(client, campaign_id, characters[0], "Recall the silver key.")
    interpreted = client.post(f"/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret")
    assert interpreted.status_code == 200, interpreted.text

    with get_session_factory()() as session:
        summary_id = session.scalar(select(MemorySummary.id))
        assert summary_id is not None
        try:
            session.execute(
                update(MemorySummary)
                .where(MemorySummary.id == summary_id)
                .values(content="Rewritten history")
            )
            session.commit()
        except DBAPIError as exc:
            session.rollback()
            assert "memory_summaries is immutable" in str(exc.orig)
        else:
            raise AssertionError("database accepted a memory summary mutation")
