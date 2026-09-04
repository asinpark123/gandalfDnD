import hashlib
import json
import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session_factory
from app.embeddings import (
    DeterministicEmbeddingProvider,
    EmbeddingProvider,
    LocalFastEmbedProvider,
)
from app.models import (
    Campaign,
    CampaignEvent,
    CampaignMemoryIndex,
    Location,
    MemoryDocument,
    MemoryEmbedding,
    MemoryEmbeddingProfile,
    MemoryRetrieval,
    MemoryRetrievalItem,
)
from app.retrieval import (
    LEGACY_RANKING_POLICY,
    GoldenMemoryQuery,
    MemoryQuery,
    MemoryRetrievalError,
    MemoryRetrievalReplayError,
    MemoryRetrievalUnavailableError,
    _Candidate,
    _select_bounded,
    evaluate_and_activate_memory_index,
    replay_memory_retrieval,
    retrieve_memories,
)


def _campaign(client: TestClient, name: str) -> uuid.UUID:
    response = client.post(
        "/campaigns", json={"name": name, "starting_location": "Lantern Archive"}
    )
    assert response.status_code == 201, response.text
    return uuid.UUID(response.json()["id"])


def _profile(provider: EmbeddingProvider) -> MemoryEmbeddingProfile:
    return MemoryEmbeddingProfile(
        profile_key=provider.profile_key,
        provider_kind=provider.provider_kind,
        model_name=provider.model_name,
        model_revision=provider.model_revision,
        artifact_sha256=provider.artifact_sha256,
        license_id=provider.license_id,
        dimensions=provider.dimensions,
        normalization=provider.normalization,
        distance_metric="cosine",
        adapter_version=provider.adapter_version,
    )


def _add_event(
    session: Session, campaign: Campaign, *, sequence: int, visibility: str = "player"
) -> CampaignEvent:
    event = CampaignEvent(
        campaign_id=campaign.id,
        ruleset_release_id=campaign.ruleset_release_id,
        ruleset_data_catalog_id=campaign.ruleset_data_catalog_id,
        sequence=sequence,
        event_type="memory_fixture",
        visibility=visibility,
        payload={"sequence": sequence},
    )
    session.add(event)
    session.flush()
    return event


def _add_document(
    session: Session,
    *,
    campaign_id: uuid.UUID,
    event: CampaignEvent,
    content: str,
    sequence_start: int | None = None,
    sequence_end: int | None = None,
    status: str = "active",
    superseded_by_document_id: uuid.UUID | None = None,
    location_id: uuid.UUID | None = None,
    document_id: uuid.UUID | None = None,
) -> MemoryDocument:
    document = MemoryDocument(
        id=document_id or uuid.uuid4(),
        campaign_id=campaign_id,
        source_kind="event",
        source_event_id=event.id,
        source_version=1,
        chunk_index=0,
        event_sequence_start=sequence_start or event.sequence,
        event_sequence_end=sequence_end or event.sequence,
        visibility="player",
        content=content,
        content_sha256=hashlib.sha256(content.encode()).hexdigest(),
        chunker_version="retrieval-test-1.0.0",
        status=status,
        source_world_revision=0,
        source_time_minutes=event.sequence,
        location_id=location_id,
        superseded_by_document_id=superseded_by_document_id,
    )
    session.add(document)
    session.flush()
    return document


def _add_embedding(
    session: Session,
    *,
    document: MemoryDocument,
    profile: MemoryEmbeddingProfile,
    provider: EmbeddingProvider,
) -> None:
    session.add(
        MemoryEmbedding(
            document_id=document.id,
            profile_id=profile.id,
            document_sha256=document.content_sha256,
            embedding=provider.embed_documents([document.content])[0],
        )
    )


def _selection_candidate(content: str, *, sequence: int, score: float) -> _Candidate:
    document = MemoryDocument(
        id=uuid.uuid5(uuid.NAMESPACE_URL, f"selection:{sequence}:{content}"),
        campaign_id=uuid.uuid4(),
        source_kind="event",
        source_event_id=uuid.uuid4(),
        source_version=1,
        chunk_index=0,
        event_sequence_start=sequence,
        event_sequence_end=sequence,
        visibility="player",
        content=content,
        content_sha256=hashlib.sha256(content.encode()).hexdigest(),
        chunker_version="selection-test-1.0.0",
        status="active",
    )
    return _Candidate(document=document, combined_score=score)


def test_support_selection_treats_count_as_ceiling_and_keeps_only_useful_context() -> None:
    primary = _selection_candidate(
        "Mira promised to carry the brass astrolabe to the Old Tower after three moon bells.",
        sequence=1,
        score=0.80,
    )
    useful = _selection_candidate(
        "The Old Tower custodian opens the moonward stair after the third moon bell for safe "
        "astrolabe delivery.",
        sequence=2,
        score=0.50,
    )
    generic = _selection_candidate(
        "Chronicle 279: patrol 13 advanced quest Recover the Astrolabe after branch Mira.",
        sequence=3,
        score=0.60,
    )
    duplicate = _selection_candidate(
        "Mira promised to carry the brass astrolabe to the Old Tower after three moon bells!",
        sequence=4,
        score=0.70,
    )
    ranked = [primary, duplicate, generic, useful]
    query = "What did Mira promise about the brass astrolabe and Old Tower?"

    selected, truncated = _select_bounded(
        ranked,
        query_text=query,
        requested_count=4,
        context_budget_chars=6000,
    )

    assert [candidate for candidate, _ in selected] == [primary, useful]
    assert truncated is True

    legacy, _ = _select_bounded(
        ranked,
        query_text=query,
        requested_count=4,
        context_budget_chars=6000,
        ranking_policy=LEGACY_RANKING_POLICY,
    )
    assert [candidate for candidate, _ in legacy] == ranked


def test_hybrid_retrieval_filters_before_rank_bounds_context_and_replays(
    client: TestClient,
) -> None:
    campaign_id = _campaign(client, "M4.3 Hybrid")
    other_campaign_id = _campaign(client, "M4.3 Cross Campaign")
    provider = DeterministicEmbeddingProvider(dimensions=256)
    wrong_provider = DeterministicEmbeddingProvider(dimensions=48)
    with get_session_factory()() as session:
        campaign = session.get(Campaign, campaign_id)
        other_campaign = session.get(Campaign, other_campaign_id)
        assert campaign is not None and other_campaign is not None
        location_id = session.scalar(select(Location.id).where(Location.campaign_id == campaign_id))
        assert location_id is not None
        profile = _profile(provider)
        wrong_profile = _profile(wrong_provider)
        session.add_all([profile, wrong_profile])
        session.flush()

        base_sequence = (
            session.scalar(
                select(func.max(CampaignEvent.sequence)).where(
                    CampaignEvent.campaign_id == campaign_id
                )
            )
            or 0
        )
        relevant_event = _add_event(session, campaign, sequence=base_sequence + 1)
        relevant = _add_document(
            session,
            campaign_id=campaign_id,
            event=relevant_event,
            content="The archivist hid the silver key beneath the sundial.",
            location_id=location_id,
        )
        _add_embedding(session, document=relevant, profile=profile, provider=provider)

        overlap_event = _add_event(session, campaign, sequence=base_sequence + 2)
        overlap = _add_document(
            session,
            campaign_id=campaign_id,
            event=overlap_event,
            content="The silver key remains beneath the old archive sundial.",
            sequence_start=base_sequence + 1,
        )
        _add_embedding(session, document=overlap, profile=profile, provider=provider)

        ordinary_event = _add_event(session, campaign, sequence=base_sequence + 3)
        ordinary = _add_document(
            session,
            campaign_id=campaign_id,
            event=ordinary_event,
            content="The ferryman waits beside the eastern quay at dawn.",
        )
        _add_embedding(session, document=ordinary, profile=profile, provider=provider)

        successor_event = _add_event(session, campaign, sequence=base_sequence + 4)
        successor = _add_document(
            session,
            campaign_id=campaign_id,
            event=successor_event,
            content="The archive bell is now silent.",
        )
        _add_embedding(session, document=successor, profile=profile, provider=provider)
        old_event = _add_event(session, campaign, sequence=base_sequence + 5)
        superseded = _add_document(
            session,
            campaign_id=campaign_id,
            event=old_event,
            content="The archivist hid the silver key inside the ringing archive bell.",
            status="superseded",
            superseded_by_document_id=successor.id,
        )
        _add_embedding(session, document=superseded, profile=profile, provider=provider)

        future_event = _add_event(session, campaign, sequence=base_sequence + 6)
        future = _add_document(
            session,
            campaign_id=campaign_id,
            event=future_event,
            content="Future revelation: the archivist moved the silver key beneath the sundial.",
            location_id=location_id,
        )
        _add_embedding(session, document=future, profile=profile, provider=provider)

        wrong_event = _add_event(session, campaign, sequence=base_sequence + 7)
        wrong_profile_document = _add_document(
            session,
            campaign_id=campaign_id,
            event=wrong_event,
            content="Wrong profile says the archivist hid the silver key beneath the sundial.",
        )
        _add_embedding(
            session,
            document=wrong_profile_document,
            profile=wrong_profile,
            provider=wrong_provider,
        )

        cross_base_sequence = (
            session.scalar(
                select(func.max(CampaignEvent.sequence)).where(
                    CampaignEvent.campaign_id == other_campaign_id
                )
            )
            or 0
        )
        cross_event = _add_event(session, other_campaign, sequence=cross_base_sequence + 1)
        cross = _add_document(
            session,
            campaign_id=other_campaign_id,
            event=cross_event,
            content="The archivist hid the silver key beneath the sundial.",
        )
        _add_embedding(session, document=cross, profile=profile, provider=provider)
        session.add_all(
            [
                CampaignMemoryIndex(
                    campaign_id=campaign_id,
                    profile_id=profile.id,
                    status="active",
                    indexed_through_event_sequence=base_sequence + 6,
                    source_count=5,
                    quality_gate={"passed": True, "fixture": True},
                    activated_at=datetime.now(UTC),
                ),
                CampaignMemoryIndex(
                    campaign_id=other_campaign_id,
                    profile_id=profile.id,
                    status="active",
                    indexed_through_event_sequence=cross_base_sequence + 1,
                    source_count=1,
                    quality_gate={"passed": True, "fixture": True},
                    activated_at=datetime.now(UTC),
                ),
            ]
        )
        session.commit()

    query = "archivist silver key"
    result = retrieve_memories(
        MemoryQuery(
            campaign_id=campaign_id,
            query_text=query,
            requested_count=4,
            context_budget_chars=90,
            max_event_sequence=base_sequence + 5,
            location_id=location_id,
        ),
        provider=provider,
    )

    returned = {item.document_id for item in result.items}
    assert relevant.id in returned
    assert not returned.intersection(
        {overlap.id, superseded.id, future.id, wrong_profile_document.id, cross.id}
    )
    assert len(result.items) <= 4
    assert result.context_chars <= 90
    assert result.truncated is True
    assert all(item.source_event_id is not None for item in result.items)
    relevant_item = next(item for item in result.items if item.document_id == relevant.id)
    assert relevant_item.semantic_score is not None
    assert relevant_item.lexical_score is not None
    assert relevant_item.entity_score == 1.0
    assert relevant_item.recency_score == pytest.approx(
        relevant.event_sequence_end / (base_sequence + 5)
    )

    with get_session_factory()() as session:
        audit = session.get(MemoryRetrieval, result.retrieval_id)
        assert audit is not None
        assert audit.ranking_policy == "hybrid-rrf-entity-recency-1.1.0"
        assert audit.filters["max_event_sequence"] == base_sequence + 5
        assert audit.filters["audience"] == "player"
        assert audit.filters["support_selection"] == {
            "policy": "relative-score-query-evidence-diversity-1.0.0",
            "minimum_relative_score": 0.5,
            "minimum_query_term_coverage": 0.4,
            "maximum_content_similarity": 0.8,
        }
        assert query not in json.dumps(audit.filters)
        items = list(
            session.scalars(
                select(MemoryRetrievalItem)
                .where(MemoryRetrievalItem.retrieval_id == result.retrieval_id)
                .order_by(MemoryRetrievalItem.rank)
            )
        )
        assert len(items) == len(result.items)
        assert sum(item.selected_chars for item in items) == result.context_chars

    replay = replay_memory_retrieval(result.retrieval_id, query_text=query, provider=provider)
    assert replay.matched is True
    assert replay.expected_document_ids == replay.replayed_document_ids
    with pytest.raises(MemoryRetrievalReplayError, match="query text does not match"):
        replay_memory_retrieval(
            result.retrieval_id, query_text="different query", provider=provider
        )
    with pytest.raises(MemoryRetrievalReplayError, match="provider does not match"):
        replay_memory_retrieval(result.retrieval_id, query_text=query, provider=wrong_provider)

    # Existing immutable 1.0.0 audits remain replayable after support selection becomes 1.1.0.
    single = retrieve_memories(
        MemoryQuery(
            campaign_id=campaign_id,
            query_text=query,
            requested_count=1,
            max_event_sequence=base_sequence + 5,
            location_id=location_id,
        ),
        provider=provider,
    )
    with get_session_factory()() as session:
        source_audit = session.get(MemoryRetrieval, single.retrieval_id)
        source_item = session.scalar(
            select(MemoryRetrievalItem).where(
                MemoryRetrievalItem.retrieval_id == single.retrieval_id
            )
        )
        assert source_audit is not None and source_item is not None
        legacy_audit = MemoryRetrieval(
            campaign_id=source_audit.campaign_id,
            profile_id=source_audit.profile_id,
            ranking_policy=LEGACY_RANKING_POLICY,
            query_source_sha256=source_audit.query_source_sha256,
            filters=source_audit.filters,
            requested_count=source_audit.requested_count,
            returned_count=source_audit.returned_count,
            latency_ms=source_audit.latency_ms,
            context_budget_chars=source_audit.context_budget_chars,
            truncated=source_audit.truncated,
            status="succeeded",
        )
        session.add(legacy_audit)
        session.flush()
        session.add(
            MemoryRetrievalItem(
                retrieval_id=legacy_audit.id,
                document_id=source_item.document_id,
                rank=source_item.rank,
                semantic_score=source_item.semantic_score,
                lexical_score=source_item.lexical_score,
                recency_score=source_item.recency_score,
                entity_score=source_item.entity_score,
                combined_score=source_item.combined_score,
                selected_chars=source_item.selected_chars,
            )
        )
        session.commit()
        legacy_retrieval_id = legacy_audit.id

    legacy_replay = replay_memory_retrieval(
        legacy_retrieval_id, query_text=query, provider=provider
    )
    assert legacy_replay.matched is True


def test_retrieval_failure_is_safely_audited_without_raw_query(client: TestClient) -> None:
    campaign_id = _campaign(client, "M4.3 Failure Audit")
    provider = DeterministicEmbeddingProvider(dimensions=64)
    mismatched = DeterministicEmbeddingProvider(dimensions=32)
    with get_session_factory()() as session:
        profile = _profile(provider)
        session.add(profile)
        session.flush()
        session.add(
            CampaignMemoryIndex(
                campaign_id=campaign_id,
                profile_id=profile.id,
                status="active",
                source_count=0,
                quality_gate={"passed": True, "fixture": True},
                activated_at=datetime.now(UTC),
            )
        )
        session.commit()

    query = "A raw query that must never be stored"
    with pytest.raises(MemoryRetrievalError, match="failed safely"):
        retrieve_memories(MemoryQuery(campaign_id, query), provider=mismatched)

    with get_session_factory()() as session:
        audit = session.scalar(select(MemoryRetrieval))
        assert audit is not None
        assert audit.status == "failed"
        assert audit.error_code == "retrieval_failed"
        assert audit.returned_count == 0
        assert query not in json.dumps(audit.filters)


@pytest.mark.parametrize(
    "provider",
    [
        pytest.param(DeterministicEmbeddingProvider(dimensions=384), id="deterministic"),
        pytest.param(None, id="local-bge", marks=pytest.mark.local_embedding),
    ],
)
def test_500_event_golden_gate_activates_only_after_quality_thresholds(
    client: TestClient, provider: EmbeddingProvider | None
) -> None:
    campaign_id = _campaign(client, "M4.3 500 Event Gate")
    other_campaign_id = _campaign(client, "M4.3 Adversarial Neighbour")
    if provider is None:
        model_dir = get_settings().embedding_model_dir
        if not model_dir.is_dir():
            pytest.skip("pinned local embedding artifact was not explicitly downloaded")
        provider = LocalFastEmbedProvider(model_dir)
    golden_records: list[tuple[str, uuid.UUID, bool]] = []
    with get_session_factory()() as session:
        campaign = session.get(Campaign, campaign_id)
        other_campaign = session.get(Campaign, other_campaign_id)
        assert campaign is not None and other_campaign is not None
        start_sequence = (
            session.scalar(
                select(func.max(CampaignEvent.sequence)).where(
                    CampaignEvent.campaign_id == campaign_id
                )
            )
            or 0
        )
        profile = _profile(provider)
        session.add(profile)
        session.flush()
        documents: list[MemoryDocument] = []
        for offset in range(500):
            sequence = start_sequence + offset + 1
            event = _add_event(session, campaign, sequence=sequence)
            if offset < 20:
                token = f"runestone{offset:02d}"
                content = (
                    f"Clue {token}: keeper{offset:02d} placed relic{offset:02d} "
                    f"inside vault{offset:02d}."
                )
                query = (
                    f"Where did keeper{offset:02d} conceal relic{offset:02d}? "
                    f"Recall {token} and vault{offset:02d}."
                )
            else:
                content = (
                    f"Routine chronicle {offset:03d}: the market patrol crossed district "
                    f"{offset % 17:02d} before sunset."
                )
            document = _add_document(
                session,
                campaign_id=campaign_id,
                event=event,
                content=content,
                document_id=uuid.uuid5(
                    uuid.NAMESPACE_URL, f"gandalfdnd:m4.3:golden-corpus:{offset}"
                ),
            )
            documents.append(document)
            if offset < 20:
                golden_records.append((query, document.id, offset < 5))

        vectors = provider.embed_documents([document.content for document in documents])
        session.add_all(
            [
                MemoryEmbedding(
                    document_id=document.id,
                    profile_id=profile.id,
                    document_sha256=document.content_sha256,
                    embedding=vector,
                )
                for document, vector in zip(documents, vectors, strict=True)
            ]
        )
        # This exact-looking record belongs to another campaign and must never enter a result.
        other_sequence = (
            session.scalar(
                select(func.max(CampaignEvent.sequence)).where(
                    CampaignEvent.campaign_id == other_campaign_id
                )
            )
            or 0
        ) + 1
        other_event = _add_event(session, other_campaign, sequence=other_sequence)
        other_document = _add_document(
            session,
            campaign_id=other_campaign_id,
            event=other_event,
            content=golden_records[0][0],
        )
        _add_embedding(session, document=other_document, profile=profile, provider=provider)
        session.add(
            CampaignMemoryIndex(
                campaign_id=campaign_id,
                profile_id=profile.id,
                status="ready",
                indexed_through_event_sequence=start_sequence + 500,
                source_count=500,
            )
        )
        session.commit()
        profile_id = profile.id

    golden = tuple(
        GoldenMemoryQuery(
            query_text=content,
            relevant_document_ids=frozenset({document_id}),
            critical=critical,
        )
        for content, document_id, critical in golden_records
    )
    with pytest.raises(
        MemoryRetrievalUnavailableError, match="no active memory index is available"
    ):
        retrieve_memories(
            MemoryQuery(campaign_id=campaign_id, query_text=golden[0].query_text),
            provider=provider,
        )
    insufficient = evaluate_and_activate_memory_index(
        campaign_id=campaign_id,
        profile_id=profile_id,
        provider=provider,
        golden_queries=golden[:19],
        max_event_sequence=start_sequence + 500,
    )
    assert insufficient.passed is False
    with get_session_factory()() as session:
        assert (
            session.scalar(
                select(CampaignMemoryIndex.status).where(
                    CampaignMemoryIndex.campaign_id == campaign_id
                )
            )
            == "ready"
        )

    quality = evaluate_and_activate_memory_index(
        campaign_id=campaign_id,
        profile_id=profile_id,
        provider=provider,
        golden_queries=golden,
        max_event_sequence=start_sequence + 500,
    )

    assert quality.passed is True
    assert quality.query_count == 20
    assert quality.critical_query_count == 5
    assert quality.corpus_count == 500
    assert quality.critical_recall_at_8 == 1.0
    assert quality.overall_recall_at_8 >= 0.9
    assert quality.mean_reciprocal_rank >= 0.65
    assert quality.latency_p95_ms <= 250
    with get_session_factory()() as session:
        campaign_index = session.scalar(
            select(CampaignMemoryIndex).where(CampaignMemoryIndex.campaign_id == campaign_id)
        )
        assert campaign_index is not None
        assert campaign_index.status == "active"
        assert campaign_index.quality_gate["passed"] is True
        assert session.scalar(select(func.count(MemoryRetrieval.id))) == 39
        lexical_index = session.execute(
            text(
                "SELECT indexdef FROM pg_indexes "
                "WHERE schemaname = 'public' "
                "AND indexname = 'ix_memory_documents_content_english'"
            )
        ).scalar_one()
        assert "USING gin" in lexical_index
    if isinstance(provider, LocalFastEmbedProvider):
        provider.close()
