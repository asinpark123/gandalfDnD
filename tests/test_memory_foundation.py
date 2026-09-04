import hashlib
import uuid
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select, text, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from alembic import command
from app.db import get_engine, get_session_factory
from app.models import (
    CampaignEvent,
    CampaignMemoryIndex,
    MemoryDocument,
    MemoryEmbedding,
    MemoryEmbeddingProfile,
    MemoryIndexJob,
    MemoryRetrieval,
    MemoryRetrievalItem,
)


def _campaign(client: TestClient, name: str = "Memory Foundation") -> uuid.UUID:
    response = client.post(
        "/campaigns",
        json={"name": name, "starting_location": "Lantern Archive"},
    )
    assert response.status_code == 201, response.text
    return uuid.UUID(response.json()["id"])


def _source_event_id(campaign_id: uuid.UUID) -> uuid.UUID:
    with get_session_factory()() as session:
        event_id = session.scalar(
            select(CampaignEvent.id)
            .where(CampaignEvent.campaign_id == campaign_id)
            .order_by(CampaignEvent.sequence)
            .limit(1)
        )
    assert event_id is not None
    return event_id


def _profile(*, key: str = "deterministic-test-v1", dimensions: int = 3) -> MemoryEmbeddingProfile:
    return MemoryEmbeddingProfile(
        profile_key=key,
        provider_kind="deterministic",
        model_name="fixed-test-vectors",
        model_revision="1",
        artifact_sha256="a" * 64,
        license_id="test-only",
        dimensions=dimensions,
        normalization="l2",
        distance_metric="cosine",
        adapter_version="pgvector-python-0.5.0",
    )


def _document(
    campaign_id: uuid.UUID,
    event_id: uuid.UUID,
    content: str,
    *,
    chunk_index: int = 0,
) -> MemoryDocument:
    return MemoryDocument(
        campaign_id=campaign_id,
        source_kind="event",
        source_event_id=event_id,
        source_version=1,
        chunk_index=chunk_index,
        event_sequence_start=1,
        event_sequence_end=1,
        visibility="player",
        content=content,
        content_sha256=hashlib.sha256(content.encode()).hexdigest(),
        chunker_version="test-1",
        status="active",
        source_world_revision=0,
        source_time_minutes=0,
    )


def test_pgvector_extension_identity_and_memory_schema_are_explicit() -> None:
    expected_tables = {
        "campaign_memory_indexes",
        "memory_documents",
        "memory_embedding_profiles",
        "memory_embeddings",
        "memory_index_jobs",
        "memory_retrieval_items",
        "memory_retrievals",
        "memory_summaries",
        "memory_summary_sources",
        "memory_summary_uses",
    }
    with get_engine().connect() as connection:
        identity = connection.execute(
            text(
                "SELECT current_database(), current_user, "
                "current_setting('server_version_num')::integer"
            )
        ).one()
        vector_version = connection.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        ).scalar_one()
        tables = set(
            connection.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = 'public' AND tablename LIKE 'memory_%' "
                    "OR schemaname = 'public' AND tablename = 'campaign_memory_indexes'"
                )
            ).scalars()
        )
        raw_query_column = connection.execute(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = 'memory_retrievals' "
                "AND column_name IN ('query', 'query_text', 'prompt')"
            )
        ).scalar_one()

    assert identity[:2] == ("gandalfdnd_test", "gandalfdnd_test_user")
    assert identity[2] >= 180000
    assert vector_version == "0.8.6"
    assert tables == expected_tables
    assert raw_query_column == 0


def test_unconstrained_vectors_support_profile_filtered_exact_cosine_search(
    client: TestClient,
) -> None:
    campaign_id = _campaign(client)
    event_id = _source_event_id(campaign_id)
    with get_session_factory()() as session:
        profile = _profile()
        first = _document(campaign_id, event_id, "The silver key rests beneath the sundial.")
        second = _document(
            campaign_id,
            event_id,
            "The ferryman waits at the eastern quay.",
            chunk_index=1,
        )
        session.add_all([profile, first, second])
        session.flush()
        session.add_all(
            [
                MemoryEmbedding(
                    document_id=first.id,
                    profile_id=profile.id,
                    document_sha256=first.content_sha256,
                    embedding=[1.0, 0.0, 0.0],
                ),
                MemoryEmbedding(
                    document_id=second.id,
                    profile_id=profile.id,
                    document_sha256=second.content_sha256,
                    embedding=[0.0, 1.0, 0.0],
                ),
            ]
        )
        session.commit()

        distance = MemoryEmbedding.embedding.cosine_distance([1.0, 0.0, 0.0])
        results = session.execute(
            select(MemoryDocument.content, distance.label("distance"))
            .join(MemoryEmbedding, MemoryEmbedding.document_id == MemoryDocument.id)
            .where(MemoryEmbedding.profile_id == profile.id)
            .order_by(distance)
        ).all()

    assert [row.content for row in results] == [first.content, second.content]
    assert results[0].distance == pytest.approx(0.0)
    assert results[1].distance == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("document_hash", "embedding", "message"),
    [
        ("b" * 64, [1.0, 0.0, 0.0], "document hash mismatch"),
        (None, [1.0, 0.0], "dimension mismatch"),
        (None, [float("nan"), 0.0, 1.0], "NaN not allowed"),
    ],
)
def test_embedding_hash_dimension_and_finite_value_invariants(
    client: TestClient,
    document_hash: str | None,
    embedding: list[float],
    message: str,
) -> None:
    campaign_id = _campaign(client)
    event_id = _source_event_id(campaign_id)
    with get_session_factory()() as session:
        profile = _profile()
        document = _document(campaign_id, event_id, "A bounded memory fixture.")
        session.add_all([profile, document])
        session.flush()
        session.add(
            MemoryEmbedding(
                document_id=document.id,
                profile_id=profile.id,
                document_sha256=document_hash or document.content_sha256,
                embedding=embedding,
            )
        )
        with pytest.raises(DBAPIError, match=message):
            session.commit()


def test_memory_scope_immutability_jobs_and_retrieval_audits_are_enforced(
    client: TestClient,
) -> None:
    campaign_id = _campaign(client, "First Memory Campaign")
    other_campaign_id = _campaign(client, "Second Memory Campaign")
    event_id = _source_event_id(campaign_id)
    other_event_id = _source_event_id(other_campaign_id)

    with get_session_factory()() as session:
        session.add(
            _document(
                campaign_id,
                other_event_id,
                "This cross-campaign source must be rejected.",
            )
        )
        with pytest.raises(DBAPIError, match="event must belong to its campaign"):
            session.commit()

    with get_session_factory()() as session:
        profile = _profile()
        document = _document(campaign_id, event_id, "The old bell rang three times.")
        other_document = _document(
            other_campaign_id,
            other_event_id,
            "The other campaign remains isolated.",
        )
        session.add_all([profile, document, other_document])
        session.flush()
        session.add(
            MemoryEmbedding(
                document_id=document.id,
                profile_id=profile.id,
                document_sha256=document.content_sha256,
                embedding=[0.5, 0.5, 0.0],
            )
        )
        campaign_index = CampaignMemoryIndex(
            campaign_id=campaign_id,
            profile_id=profile.id,
            status="building",
            source_count=0,
        )
        job = MemoryIndexJob(
            campaign_id=campaign_id,
            document_id=document.id,
            profile_id=profile.id,
            status="pending",
            attempt_count=0,
        )
        session.add_all([campaign_index, job])
        retrieval = MemoryRetrieval(
            campaign_id=campaign_id,
            profile_id=profile.id,
            ranking_policy="exact-hybrid-test-1",
            query_source_sha256="c" * 64,
            filters={"audience": "player"},
            requested_count=1,
            returned_count=1,
            latency_ms=1,
            context_budget_chars=6000,
            truncated=False,
            status="succeeded",
        )
        session.add(retrieval)
        session.flush()
        session.add(
            MemoryRetrievalItem(
                retrieval_id=retrieval.id,
                document_id=document.id,
                rank=1,
                semantic_score=0.9,
                lexical_score=None,
                recency_score=0.0,
                entity_score=0.0,
                combined_score=0.9,
                selected_chars=len(document.content),
            )
        )
        session.commit()
        profile_id = profile.id
        document_id = document.id
        other_document_id = other_document.id
        retrieval_id = retrieval.id
        campaign_index_id = campaign_index.id
        job_id = job.id

    with (
        get_session_factory()() as session,
        pytest.raises(DBAPIError, match="memory_embedding_profiles is immutable"),
    ):
        session.execute(
            update(MemoryEmbeddingProfile)
            .where(MemoryEmbeddingProfile.id == profile_id)
            .values(model_revision="2")
        )

    with (
        get_session_factory()() as session,
        pytest.raises(DBAPIError, match="source and content are immutable"),
    ):
        session.execute(
            update(MemoryDocument)
            .where(MemoryDocument.id == document_id)
            .values(content="Retconned content")
        )

    with get_session_factory()() as session:
        session.add(
            MemoryIndexJob(
                campaign_id=other_campaign_id,
                document_id=document_id,
                profile_id=profile_id,
                status="pending",
                attempt_count=0,
            )
        )
        with pytest.raises(DBAPIError, match="document must belong to its campaign"):
            session.commit()

    with get_session_factory()() as session:
        session.add(
            MemoryRetrievalItem(
                retrieval_id=retrieval_id,
                document_id=other_document_id,
                rank=2,
                semantic_score=0.5,
                lexical_score=None,
                recency_score=0.0,
                entity_score=0.0,
                combined_score=0.5,
                selected_chars=10,
            )
        )
        with pytest.raises(DBAPIError, match="player-visible in its campaign"):
            session.commit()

    with (
        get_session_factory()() as session,
        pytest.raises(DBAPIError, match="campaign memory index identity is immutable"),
    ):
        session.execute(
            update(CampaignMemoryIndex)
            .where(CampaignMemoryIndex.id == campaign_index_id)
            .values(campaign_id=other_campaign_id)
        )

    with (
        get_session_factory()() as session,
        pytest.raises(DBAPIError, match="memory index job identity is immutable"),
    ):
        session.execute(
            update(MemoryIndexJob)
            .where(MemoryIndexJob.id == job_id)
            .values(campaign_id=other_campaign_id)
        )


def test_only_one_active_profile_is_allowed_per_campaign(client: TestClient) -> None:
    campaign_id = _campaign(client)
    with get_session_factory()() as session:
        first = _profile(key="first-profile")
        second = _profile(key="second-profile")
        session.add_all([first, second])
        session.flush()
        session.add_all(
            [
                CampaignMemoryIndex(
                    campaign_id=campaign_id,
                    profile_id=first.id,
                    status="active",
                    source_count=0,
                    quality_gate={"passed": True},
                    activated_at=text("now()"),
                ),
                CampaignMemoryIndex(
                    campaign_id=campaign_id,
                    profile_id=second.id,
                    status="active",
                    source_count=0,
                    quality_gate={"passed": True},
                    activated_at=text("now()"),
                ),
            ]
        )
        with pytest.raises(IntegrityError, match="uq_campaign_memory_indexes_one_active"):
            session.commit()


def test_empty_downgrade_is_reversible_and_keeps_the_extension() -> None:
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.downgrade(config, "0011_factions_time")
    with get_engine().connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == "0011_factions_time"
        )
        assert (
            connection.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            ).scalar_one()
            == "0.8.6"
        )
        assert (
            connection.execute(text("SELECT to_regclass('memory_documents')")).scalar_one() is None
        )
    get_engine().dispose()
    command.upgrade(config, "head")


def test_downgrade_refuses_to_discard_memory_data() -> None:
    with get_engine().connect() as connection:
        pre_attempt_head = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
    with get_session_factory()() as session:
        session.add(_profile())
        session.commit()
    get_engine().dispose()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(DBAPIError, match="Cannot downgrade after M4.1 memory data"):
        command.downgrade(config, "0011_factions_time")
    with get_engine().connect() as connection:
        assert (
            connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            == pre_attempt_head
        )
