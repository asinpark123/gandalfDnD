import json
import math
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update

from app.config import get_settings
from app.db import get_engine, get_session_factory
from app.embeddings import DeterministicEmbeddingProvider
from app.memory import (
    IncompleteMemoryIndexError,
    SourceHashDriftError,
    activate_memory_index,
    drain_index_jobs,
    ensure_embedding_profile,
    project_completed_turns,
    recover_expired_leases,
    start_index_build,
)
from app.models import (
    Campaign,
    CampaignEvent,
    CampaignMemoryIndex,
    MemoryDocument,
    MemoryEmbedding,
    MemoryEmbeddingProfile,
    MemoryIndexJob,
    Turn,
)


def _campaign(client: TestClient, name: str = "M4.2 Indexing") -> uuid.UUID:
    response = client.post(
        "/campaigns", json={"name": name, "starting_location": "Lantern Archive"}
    )
    assert response.status_code == 201, response.text
    return uuid.UUID(response.json()["id"])


def _completed_turn(
    campaign_id: uuid.UUID,
    *,
    action: str = "Ask the archivist about the silver key.",
    narration: str = "The archivist recalls that the key rests beneath the sundial.",
    status: str = "completed",
    hidden_text: str | None = None,
) -> uuid.UUID:
    with get_session_factory()() as session:
        campaign = session.get(Campaign, campaign_id)
        assert campaign is not None
        turn_sequence = (
            session.scalar(select(func.max(Turn.sequence)).where(Turn.campaign_id == campaign_id))
            or 0
        ) + 1
        event_sequence = (
            session.scalar(
                select(func.max(CampaignEvent.sequence)).where(
                    CampaignEvent.campaign_id == campaign_id
                )
            )
            or 0
        )
        turn = Turn(
            command_id=uuid.uuid4(),
            campaign_id=campaign_id,
            sequence=turn_sequence,
            player_action=action,
            dm_narration=narration if status == "completed" else None,
            structured_output={"narration": narration, "state_changes": []}
            if status == "completed"
            else None,
            workflow_version="two-stage-turn-1.0.0",
            status=status,
            failure_stage="narration" if status == "failed" else None,
            error_code="test_failure" if status == "failed" else None,
            error_detail="Safe fixture failure" if status == "failed" else None,
            resumable=False,
            world_revision_before=campaign.world_revision,
            world_revision_after=campaign.world_revision if status == "completed" else None,
            completed_at=datetime.now(UTC) if status == "completed" else None,
        )
        session.add(turn)
        session.flush()
        session.add(
            CampaignEvent(
                campaign_id=campaign_id,
                ruleset_release_id=campaign.ruleset_release_id,
                ruleset_data_catalog_id=campaign.ruleset_data_catalog_id,
                turn_id=turn.id,
                sequence=event_sequence + 1,
                event_type="player_action",
                visibility="player",
                payload={"action": action},
            )
        )
        if hidden_text is not None:
            session.add(
                CampaignEvent(
                    campaign_id=campaign_id,
                    ruleset_release_id=campaign.ruleset_release_id,
                    ruleset_data_catalog_id=campaign.ruleset_data_catalog_id,
                    turn_id=turn.id,
                    sequence=event_sequence + 2,
                    event_type="secret_note",
                    visibility="dm_only",
                    payload={"secret": hidden_text},
                )
            )
        if status == "completed":
            session.add(
                CampaignEvent(
                    campaign_id=campaign_id,
                    ruleset_release_id=campaign.ruleset_release_id,
                    ruleset_data_catalog_id=campaign.ruleset_data_catalog_id,
                    turn_id=turn.id,
                    sequence=event_sequence + (3 if hidden_text else 2),
                    event_type="dm_response",
                    visibility="player",
                    payload={"narration": narration},
                )
            )
        session.commit()
        return turn.id


def _project_and_build(
    campaign_id: uuid.UUID, provider: DeterministicEmbeddingProvider
) -> tuple[uuid.UUID, uuid.UUID]:
    with get_session_factory()() as session:
        project_completed_turns(session, campaign_id=campaign_id)
        profile = ensure_embedding_profile(session, provider)
        campaign_index = start_index_build(session, campaign_id=campaign_id, profile_id=profile.id)
        session.commit()
        return profile.id, campaign_index.id


def test_deterministic_embedding_is_stable_normalized_and_query_compatible() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=32)
    first = provider.embed_documents(["Silver key beneath the sundial"])[0]
    repeated = provider.embed_query("Silver key beneath the sundial")
    different = provider.embed_query("Ferryman at the eastern quay")

    assert provider.profile_key == "deterministic-hash-v1-32d"
    assert first == repeated
    assert first != different
    assert len(first) == 32
    assert math.sqrt(sum(value * value for value in first)) == pytest.approx(1.0)


@pytest.mark.local_embedding
def test_pinned_local_embedding_runs_offline_on_cpu() -> None:
    model_dir = get_settings().embedding_model_dir
    if not model_dir.is_dir():
        pytest.skip("pinned local embedding artifact was not explicitly downloaded")
    code = """
import json
import math
from app.config import get_settings
from app.embeddings import LocalFastEmbedProvider
provider = LocalFastEmbedProvider(get_settings().embedding_model_dir)
document = provider.embed_documents(['The archivist hid the silver key beneath the sundial.'])[0]
query = provider.embed_query('Where was the silver key hidden?')
print(json.dumps({
    'profile': provider.profile_key,
    'revision': provider.model_revision,
    'document_dimensions': len(document),
    'query_dimensions': len(query),
    'document_norm': math.sqrt(sum(value * value for value in document)),
}))
"""
    environment = {**os.environ, "HF_HUB_OFFLINE": "1"}
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    payload = json.loads(result.stdout)
    assert payload["profile"] == "local-bge-small-en-v1.5-q-v1"
    assert payload["revision"].endswith("c32e6154d1bb7a0e47c5e745fd895e7700f44385")
    assert payload["document_dimensions"] == payload["query_dimensions"] == 384
    assert payload["document_norm"] == pytest.approx(1.0, abs=1e-5)


def test_completed_turn_projection_is_player_safe_bounded_and_idempotent(
    client: TestClient,
) -> None:
    campaign_id = _campaign(client)
    secret = "THE HIDDEN DRAGON IS THE ARCHIVIST"
    turn_id = _completed_turn(campaign_id, hidden_text=secret)
    _completed_turn(campaign_id, status="failed")

    with get_session_factory()() as session:
        first = project_completed_turns(session, campaign_id=campaign_id)
        second = project_completed_turns(session, campaign_id=campaign_id, turn_id=turn_id, limit=1)
        session.commit()
        documents = list(
            session.scalars(select(MemoryDocument).where(MemoryDocument.campaign_id == campaign_id))
        )

    assert first.created_documents == 1
    assert second == type(second)(created_documents=0, existing_documents=1, created_jobs=0)
    assert len(documents) == 1
    document = documents[0]
    assert document.source_turn_id == turn_id
    assert document.visibility == "player"
    assert "silver key" in document.content.casefold()
    assert secret not in document.content
    assert len(document.content) <= 6000
    assert document.event_sequence_end - document.event_sequence_start == 2
    assert document.location_id is not None


def test_profile_build_drains_exactly_once_and_survives_engine_restart(
    client: TestClient,
) -> None:
    campaign_id = _campaign(client)
    _completed_turn(campaign_id)
    provider = DeterministicEmbeddingProvider(dimensions=24)
    profile_id, _index_id = _project_and_build(campaign_id, provider)

    first = drain_index_jobs(provider=provider, worker_id="m4-test-worker", limit=10)
    get_engine().dispose()
    second = drain_index_jobs(provider=provider, worker_id="m4-test-worker", limit=10)

    assert (first.claimed, first.completed, first.failed) == (1, 1, 0)
    assert second.claimed == 0
    with get_session_factory()() as session:
        assert session.scalar(select(func.count(MemoryEmbedding.id))) == 1
        job = session.scalar(select(MemoryIndexJob))
        campaign_index = session.scalar(select(CampaignMemoryIndex))
        assert job is not None and job.status == "complete" and job.attempt_count == 1
        assert campaign_index is not None and campaign_index.status == "ready"
        assert campaign_index.profile_id == profile_id
        assert campaign_index.source_count == 1


@dataclass(frozen=True)
class _FailingProvider:
    wrapped: DeterministicEmbeddingProvider

    @property
    def profile_key(self) -> str:
        return self.wrapped.profile_key

    @property
    def provider_kind(self) -> str:
        return self.wrapped.provider_kind

    @property
    def model_name(self) -> str:
        return self.wrapped.model_name

    @property
    def model_revision(self) -> str:
        return self.wrapped.model_revision

    @property
    def artifact_sha256(self) -> str:
        return self.wrapped.artifact_sha256

    @property
    def license_id(self) -> str:
        return self.wrapped.license_id

    @property
    def dimensions(self) -> int:
        return self.wrapped.dimensions

    @property
    def normalization(self) -> str:
        return self.wrapped.normalization

    @property
    def adapter_version(self) -> str:
        return self.wrapped.adapter_version

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("simulated offline encoder fault")

    def embed_query(self, text: str) -> list[float]:
        raise RuntimeError("simulated offline encoder fault")


def test_embedding_failure_is_retryable_and_does_not_change_completed_turn(
    client: TestClient,
) -> None:
    campaign_id = _campaign(client)
    turn_id = _completed_turn(campaign_id)
    provider = DeterministicEmbeddingProvider(dimensions=20)
    _project_and_build(campaign_id, provider)

    failed = drain_index_jobs(
        provider=_FailingProvider(provider), worker_id="failing-worker", limit=1
    )
    assert failed.failed == 1
    with get_session_factory()() as session:
        turn = session.get(Turn, turn_id)
        job = session.scalar(select(MemoryIndexJob))
        assert turn is not None and turn.status == "completed"
        assert job is not None and job.status == "failed"
        assert job.error_code == "embedding_failed"
        assert "simulated" not in (job.error_detail or "")
        session.execute(
            update(MemoryIndexJob)
            .where(MemoryIndexJob.id == job.id)
            .values(next_attempt_at=datetime.now(UTC) - timedelta(seconds=1))
        )
        session.commit()

    retried = drain_index_jobs(provider=provider, worker_id="recovery-worker", limit=1)
    assert retried.completed == 1
    with get_session_factory()() as session:
        job = session.scalar(select(MemoryIndexJob))
        assert job is not None and job.status == "complete" and job.attempt_count == 2


def test_expired_lease_is_recovered_without_duplicate_embedding(client: TestClient) -> None:
    campaign_id = _campaign(client)
    _completed_turn(campaign_id)
    provider = DeterministicEmbeddingProvider(dimensions=16)
    _project_and_build(campaign_id, provider)
    with get_session_factory()() as session:
        job = session.scalar(select(MemoryIndexJob))
        assert job is not None
        job.status = "claimed"
        job.attempt_count = 1
        job.lease_owner = "dead-worker"
        job.lease_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()
    get_engine().dispose()
    with get_session_factory()() as session:
        assert recover_expired_leases(session) == 1
        session.commit()
    recovered = drain_index_jobs(provider=provider, worker_id="replacement-worker", limit=2)
    assert recovered.completed == 1
    with get_session_factory()() as session:
        assert session.scalar(select(func.count(MemoryEmbedding.id))) == 1


def test_side_by_side_profile_activation_is_complete_and_atomic(client: TestClient) -> None:
    campaign_id = _campaign(client)
    _completed_turn(campaign_id)
    first_provider = DeterministicEmbeddingProvider(
        dimensions=12, profile_key="deterministic-primary-v1"
    )
    first_profile_id, _ = _project_and_build(campaign_id, first_provider)
    assert (
        drain_index_jobs(provider=first_provider, worker_id="primary-worker", limit=10).completed
        == 1
    )
    with get_session_factory()() as session:
        activate_memory_index(
            session,
            campaign_id=campaign_id,
            profile_id=first_profile_id,
            quality_gate={"passed": True, "evidence": "deterministic-lifecycle-gate"},
        )
        session.commit()

    second_provider = DeterministicEmbeddingProvider(
        dimensions=18, profile_key="deterministic-replacement-v1"
    )
    with get_session_factory()() as session:
        second_profile = ensure_embedding_profile(session, second_provider)
        start_index_build(session, campaign_id=campaign_id, profile_id=second_profile.id)
        second_profile_id = second_profile.id
        session.commit()
    with get_session_factory()() as session, pytest.raises(IncompleteMemoryIndexError):
        activate_memory_index(
            session,
            campaign_id=campaign_id,
            profile_id=second_profile_id,
            quality_gate={"passed": True},
        )

    with get_session_factory()() as session:
        active = session.scalar(
            select(CampaignMemoryIndex).where(CampaignMemoryIndex.status == "active")
        )
        assert active is not None and active.profile_id == first_profile_id
    assert (
        drain_index_jobs(
            provider=second_provider, worker_id="replacement-worker", limit=10
        ).completed
        == 1
    )
    with get_session_factory()() as session:
        activate_memory_index(
            session,
            campaign_id=campaign_id,
            profile_id=second_profile_id,
            quality_gate={"passed": True, "evidence": "replacement-lifecycle-gate"},
        )
        session.commit()
        indexes = list(
            session.scalars(select(CampaignMemoryIndex).order_by(CampaignMemoryIndex.created_at))
        )
        profiles = list(session.scalars(select(MemoryEmbeddingProfile)))
        assert [index.status for index in indexes] == ["retired", "active"]
        assert {profile.dimensions for profile in profiles} == {12, 18}
        assert session.scalar(select(func.count(MemoryEmbedding.id))) == 2


def test_source_hash_drift_fails_closed(client: TestClient) -> None:
    campaign_id = _campaign(client)
    turn_id = _completed_turn(campaign_id)
    with get_session_factory()() as session:
        project_completed_turns(session, campaign_id=campaign_id)
        session.commit()
    with get_session_factory()() as session:
        session.execute(
            update(Turn)
            .where(Turn.id == turn_id)
            .values(dm_narration="A retroactive and invalid narration change.")
        )
        session.commit()
    with get_session_factory()() as session, pytest.raises(SourceHashDriftError):
        project_completed_turns(session, campaign_id=campaign_id, turn_id=turn_id, limit=1)
