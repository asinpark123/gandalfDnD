"""Player-safe, versioned hybrid retrieval with immutable audit evidence."""

from __future__ import annotations

import hashlib
import math
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import func, literal_column, select
from sqlalchemy.exc import DBAPIError

from app.db import get_session_factory
from app.embeddings import EmbeddingProvider, validate_embedding
from app.memory import activate_memory_index
from app.models import (
    CampaignEvent,
    CampaignMemoryIndex,
    MemoryDocument,
    MemoryEmbedding,
    MemoryEmbeddingProfile,
    MemoryRetrieval,
    MemoryRetrievalItem,
)

LEGACY_RANKING_POLICY = "hybrid-rrf-entity-recency-1.0.0"
RANKING_POLICY = "hybrid-rrf-entity-recency-1.1.0"
SUPPORTED_RANKING_POLICIES = frozenset({LEGACY_RANKING_POLICY, RANKING_POLICY})
MAX_MEMORY_ITEMS = 8
MAX_MEMORY_CONTEXT_CHARS = 6000
CANDIDATE_LIMIT = 50
RRF_SEMANTIC_WEIGHT = 0.65
RRF_LEXICAL_WEIGHT = 0.25
ENTITY_WEIGHT = 0.07
RECENCY_WEIGHT = 0.03
SUPPORT_MIN_RELATIVE_SCORE = 0.50
SUPPORT_MIN_QUERY_TERM_COVERAGE = 0.40
SUPPORT_MAX_CONTENT_SIMILARITY = 0.80
_TERM_PATTERN = re.compile(r"[a-z0-9]+")
_QUERY_STOPWORDS = frozenset(
    {
        "a",
        "about",
        "after",
        "all",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "before",
        "by",
        "can",
        "did",
        "do",
        "does",
        "for",
        "from",
        "had",
        "has",
        "have",
        "how",
        "i",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "our",
        "the",
        "their",
        "them",
        "there",
        "they",
        "this",
        "to",
        "was",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
    }
)


class MemoryRetrievalError(RuntimeError):
    """Base error for a retrieval path that must not affect canonical state."""


class MemoryRetrievalUnavailableError(MemoryRetrievalError):
    """Raised when no eligible, complete memory index can serve the request."""


class MemoryRetrievalReplayError(MemoryRetrievalError):
    """Raised when caller-supplied replay material does not match the audit."""


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    campaign_id: uuid.UUID
    query_text: str
    requested_count: int = MAX_MEMORY_ITEMS
    context_budget_chars: int = MAX_MEMORY_CONTEXT_CHARS
    max_event_sequence: int | None = None
    turn_id: uuid.UUID | None = None
    provider_call_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
    npc_id: uuid.UUID | None = None
    character_id: uuid.UUID | None = None
    quest_id: uuid.UUID | None = None
    decision_id: uuid.UUID | None = None
    faction_id: uuid.UUID | None = None
    evaluation_profile_id: uuid.UUID | None = None


@dataclass(frozen=True, slots=True)
class RetrievedMemory:
    document_id: uuid.UUID
    content: str
    selected_chars: int
    source_kind: str
    source_turn_id: uuid.UUID | None
    source_event_id: uuid.UUID | None
    event_sequence_start: int
    event_sequence_end: int
    semantic_score: float | None
    lexical_score: float | None
    recency_score: float
    entity_score: float
    combined_score: float


@dataclass(frozen=True, slots=True)
class MemoryRetrievalResult:
    retrieval_id: uuid.UUID
    campaign_id: uuid.UUID
    profile_id: uuid.UUID
    ranking_policy: str
    query_source_sha256: str
    items: tuple[RetrievedMemory, ...]
    latency_ms: int
    context_chars: int
    truncated: bool


@dataclass(frozen=True, slots=True)
class RetrievalReplayResult:
    retrieval_id: uuid.UUID
    matched: bool
    expected_document_ids: tuple[uuid.UUID, ...]
    replayed_document_ids: tuple[uuid.UUID, ...]


@dataclass(frozen=True, slots=True)
class GoldenMemoryQuery:
    query_text: str
    relevant_document_ids: frozenset[uuid.UUID]
    critical: bool = False


@dataclass(frozen=True, slots=True)
class MemoryQualityResult:
    passed: bool
    query_count: int
    critical_query_count: int
    corpus_count: int
    critical_recall_at_8: float
    overall_recall_at_8: float
    mean_reciprocal_rank: float
    latency_p95_ms: int
    retrieval_ids: tuple[uuid.UUID, ...] = field(default_factory=tuple)

    def as_gate(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "ranking_policy": RANKING_POLICY,
            "query_count": self.query_count,
            "critical_query_count": self.critical_query_count,
            "corpus_count": self.corpus_count,
            "critical_recall_at_8": self.critical_recall_at_8,
            "overall_recall_at_8": self.overall_recall_at_8,
            "mean_reciprocal_rank": self.mean_reciprocal_rank,
            "latency_p95_ms": self.latency_p95_ms,
            "thresholds": {
                "minimum_queries": 20,
                "minimum_critical_queries": 5,
                "minimum_corpus_count": 500,
                "critical_recall_at_8": 1.0,
                "overall_recall_at_8": 0.9,
                "mean_reciprocal_rank": 0.65,
                "latency_p95_ms": 250,
            },
        }


@dataclass(slots=True)
class _Candidate:
    document: MemoryDocument
    semantic_score: float | None = None
    lexical_score: float | None = None
    semantic_rank: int | None = None
    lexical_rank: int | None = None
    recency_score: float = 0.0
    entity_score: float = 0.0
    combined_score: float = 0.0


def _canonical_query(value: str) -> str:
    canonical = " ".join(value.split())
    if not 1 <= len(canonical) <= 6000:
        raise ValueError("memory query must contain between 1 and 6000 characters")
    return canonical


def _query_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _provider_matches_profile(provider: EmbeddingProvider, profile: MemoryEmbeddingProfile) -> bool:
    return (
        profile.profile_key == provider.profile_key
        and profile.provider_kind == provider.provider_kind
        and profile.model_name == provider.model_name
        and profile.model_revision == provider.model_revision
        and profile.artifact_sha256 == provider.artifact_sha256
        and profile.license_id == provider.license_id
        and profile.dimensions == provider.dimensions
        and profile.normalization == provider.normalization
        and profile.adapter_version == provider.adapter_version
    )


def _validate_request(request: MemoryQuery) -> str:
    query = _canonical_query(request.query_text)
    if not 1 <= request.requested_count <= MAX_MEMORY_ITEMS:
        raise ValueError(f"requested_count must be between 1 and {MAX_MEMORY_ITEMS}")
    if not 1 <= request.context_budget_chars <= MAX_MEMORY_CONTEXT_CHARS:
        raise ValueError(f"context_budget_chars must be between 1 and {MAX_MEMORY_CONTEXT_CHARS}")
    if request.max_event_sequence is not None and request.max_event_sequence < 1:
        raise ValueError("max_event_sequence must be positive when supplied")
    return query


def _resolve_profile(request: MemoryQuery) -> tuple[uuid.UUID, uuid.UUID, int]:
    with get_session_factory()() as session:
        statement = select(CampaignMemoryIndex).where(
            CampaignMemoryIndex.campaign_id == request.campaign_id
        )
        if request.evaluation_profile_id is None:
            statement = statement.where(CampaignMemoryIndex.status == "active")
        else:
            statement = statement.where(
                CampaignMemoryIndex.profile_id == request.evaluation_profile_id,
                CampaignMemoryIndex.status.in_(("ready", "active")),
            )
        campaign_index = session.scalar(statement)
        if campaign_index is None:
            purpose = "active" if request.evaluation_profile_id is None else "ready evaluation"
            raise MemoryRetrievalUnavailableError(f"no {purpose} memory index is available")
        profile = session.get(MemoryEmbeddingProfile, campaign_index.profile_id)
        if profile is None:
            raise MemoryRetrievalUnavailableError("memory embedding profile is missing")
        maximum = request.max_event_sequence
        if maximum is None:
            maximum = session.scalar(
                select(func.max(CampaignEvent.sequence)).where(
                    CampaignEvent.campaign_id == request.campaign_id
                )
            )
        maximum = maximum or 1
        checkpoint = campaign_index.indexed_through_event_sequence
        if checkpoint is not None:
            maximum = min(maximum, checkpoint)
        elif campaign_index.source_count:
            raise MemoryRetrievalUnavailableError("memory index checkpoint is inconsistent")
        return campaign_index.id, profile.id, maximum


def _scope_filters(
    *, campaign_id: uuid.UUID, profile_id: uuid.UUID, max_event_sequence: int
) -> tuple[Any, ...]:
    return (
        MemoryDocument.campaign_id == campaign_id,
        MemoryDocument.visibility == "player",
        MemoryDocument.status == "active",
        MemoryDocument.event_sequence_end <= max_event_sequence,
        MemoryEmbedding.profile_id == profile_id,
        MemoryEmbedding.document_sha256 == MemoryDocument.content_sha256,
    )


def _entity_score(document: MemoryDocument, request: MemoryQuery) -> float:
    pairs = (
        (request.location_id, document.location_id),
        (request.npc_id, document.npc_id),
        (request.character_id, document.character_id),
        (request.quest_id, document.quest_id),
        (request.decision_id, document.decision_id),
        (request.faction_id, document.faction_id),
    )
    supplied = [(expected, actual) for expected, actual in pairs if expected is not None]
    if not supplied:
        return 0.0
    return sum(expected == actual for expected, actual in supplied) / len(supplied)


def _filters_payload(
    request: MemoryQuery, *, campaign_index_id: uuid.UUID, max_event_sequence: int
) -> dict[str, Any]:
    entities = {
        key: str(value)
        for key, value in {
            "location_id": request.location_id,
            "npc_id": request.npc_id,
            "character_id": request.character_id,
            "quest_id": request.quest_id,
            "decision_id": request.decision_id,
            "faction_id": request.faction_id,
        }.items()
        if value is not None
    }
    return {
        "audience": "player",
        "document_status": "active",
        "campaign_index_id": str(campaign_index_id),
        "max_event_sequence": max_event_sequence,
        "candidate_limit": CANDIDATE_LIMIT,
        "source_range_deduplication": "overlap",
        "support_selection": {
            "policy": "relative-score-query-evidence-diversity-1.0.0",
            "minimum_relative_score": SUPPORT_MIN_RELATIVE_SCORE,
            "minimum_query_term_coverage": SUPPORT_MIN_QUERY_TERM_COVERAGE,
            "maximum_content_similarity": SUPPORT_MAX_CONTENT_SIMILARITY,
        },
        "entities": entities,
    }


def _rank_candidates(
    request: MemoryQuery,
    *,
    profile_id: uuid.UUID,
    query_vector: list[float],
    query_text: str,
    max_event_sequence: int,
) -> list[_Candidate]:
    scope = _scope_filters(
        campaign_id=request.campaign_id,
        profile_id=profile_id,
        max_event_sequence=max_event_sequence,
    )
    distance = MemoryEmbedding.embedding.cosine_distance(query_vector)
    semantic = 1.0 - distance
    english = literal_column("'english'::regconfig")
    text_vector = func.to_tsvector(english, MemoryDocument.content)
    text_query = func.plainto_tsquery(english, query_text)
    lexical = func.ts_rank_cd(text_vector, text_query)

    with get_session_factory()() as session:
        semantic_rows = session.execute(
            select(MemoryDocument, semantic.label("score"))
            .join(MemoryEmbedding, MemoryEmbedding.document_id == MemoryDocument.id)
            .where(*scope)
            .order_by(distance, MemoryDocument.event_sequence_end.desc(), MemoryDocument.id)
            .limit(CANDIDATE_LIMIT)
        ).all()
        lexical_rows = session.execute(
            select(MemoryDocument, lexical.label("score"))
            .join(MemoryEmbedding, MemoryEmbedding.document_id == MemoryDocument.id)
            .where(*scope, text_vector.op("@@")(text_query))
            .order_by(lexical.desc(), MemoryDocument.event_sequence_end.desc(), MemoryDocument.id)
            .limit(CANDIDATE_LIMIT)
        ).all()

    candidates: dict[uuid.UUID, _Candidate] = {}
    for rank, (document, score) in enumerate(semantic_rows, start=1):
        candidates[document.id] = _Candidate(
            document=document,
            semantic_score=float(score),
            semantic_rank=rank,
        )
    for rank, (document, score) in enumerate(lexical_rows, start=1):
        candidate = candidates.setdefault(document.id, _Candidate(document=document))
        candidate.lexical_score = float(score)
        candidate.lexical_rank = rank

    for candidate in candidates.values():
        candidate.recency_score = min(
            1.0, candidate.document.event_sequence_end / max(1, max_event_sequence)
        )
        candidate.entity_score = _entity_score(candidate.document, request)
        semantic_rrf = 1.0 / candidate.semantic_rank if candidate.semantic_rank is not None else 0.0
        lexical_rrf = 1.0 / candidate.lexical_rank if candidate.lexical_rank is not None else 0.0
        candidate.combined_score = (
            RRF_SEMANTIC_WEIGHT * semantic_rrf
            + RRF_LEXICAL_WEIGHT * lexical_rrf
            + ENTITY_WEIGHT * candidate.entity_score
            + RECENCY_WEIGHT * candidate.recency_score
        )
    return sorted(
        candidates.values(),
        key=lambda candidate: (
            -candidate.combined_score,
            -candidate.document.event_sequence_end,
            str(candidate.document.id),
        ),
    )


def _ranges_overlap(left: MemoryDocument, right: MemoryDocument) -> bool:
    return not (
        left.event_sequence_end < right.event_sequence_start
        or right.event_sequence_end < left.event_sequence_start
    )


def _significant_terms(value: str) -> frozenset[str]:
    return frozenset(
        token
        for token in _TERM_PATTERN.findall(value.casefold())
        if len(token) > 2 and token not in _QUERY_STOPWORDS
    )


def _query_term_coverage(candidate: _Candidate, query_terms: frozenset[str]) -> float:
    if not query_terms:
        return 0.0
    document_terms = _significant_terms(candidate.document.content)
    return len(query_terms.intersection(document_terms)) / len(query_terms)


def _content_similarity(left: _Candidate, right: _Candidate) -> float:
    left_terms = _significant_terms(left.document.content)
    right_terms = _significant_terms(right.document.content)
    union = left_terms.union(right_terms)
    if not union:
        return 1.0
    return len(left_terms.intersection(right_terms)) / len(union)


def _support_is_useful(
    candidate: _Candidate,
    *,
    primary: _Candidate,
    query_terms: frozenset[str],
    selected: list[tuple[_Candidate, str]],
) -> bool:
    if candidate.combined_score < primary.combined_score * SUPPORT_MIN_RELATIVE_SCORE:
        return False
    if _query_term_coverage(candidate, query_terms) < SUPPORT_MIN_QUERY_TERM_COVERAGE:
        return False
    return all(
        _content_similarity(candidate, prior) < SUPPORT_MAX_CONTENT_SIMILARITY
        for prior, _ in selected
    )


def _select_bounded(
    ranked: list[_Candidate],
    *,
    query_text: str,
    requested_count: int,
    context_budget_chars: int,
    ranking_policy: str = RANKING_POLICY,
) -> tuple[list[tuple[_Candidate, str]], bool]:
    selected: list[tuple[_Candidate, str]] = []
    used = 0
    skipped = False
    query_terms = _significant_terms(query_text)
    primary = ranked[0] if ranked else None
    for candidate in ranked:
        if any(_ranges_overlap(candidate.document, prior.document) for prior, _ in selected):
            skipped = True
            continue
        if (
            ranking_policy != LEGACY_RANKING_POLICY
            and primary is not None
            and candidate is not primary
            and not _support_is_useful(
                candidate,
                primary=primary,
                query_terms=query_terms,
                selected=selected,
            )
        ):
            skipped = True
            continue
        if len(selected) >= requested_count or used >= context_budget_chars:
            skipped = True
            break
        remaining = context_budget_chars - used
        content = candidate.document.content[:remaining]
        if not content:
            skipped = True
            break
        if len(content) < len(candidate.document.content):
            skipped = True
        selected.append((candidate, content))
        used += len(content)
    if len(selected) < len(ranked):
        skipped = True
    return selected, skipped


def _store_success(
    request: MemoryQuery,
    *,
    profile_id: uuid.UUID,
    query_sha256: str,
    filters: dict[str, Any],
    selected: list[tuple[_Candidate, str]],
    latency_ms: int,
    truncated: bool,
) -> MemoryRetrievalResult:
    with get_session_factory()() as session:
        audit = MemoryRetrieval(
            campaign_id=request.campaign_id,
            turn_id=request.turn_id,
            provider_call_id=request.provider_call_id,
            profile_id=profile_id,
            ranking_policy=RANKING_POLICY,
            query_source_sha256=query_sha256,
            filters=filters,
            requested_count=request.requested_count,
            returned_count=len(selected),
            latency_ms=latency_ms,
            context_budget_chars=request.context_budget_chars,
            truncated=truncated,
            status="succeeded",
        )
        session.add(audit)
        session.flush()
        results: list[RetrievedMemory] = []
        for rank, (candidate, content) in enumerate(selected, start=1):
            document = candidate.document
            session.add(
                MemoryRetrievalItem(
                    retrieval_id=audit.id,
                    document_id=document.id,
                    rank=rank,
                    semantic_score=candidate.semantic_score,
                    lexical_score=candidate.lexical_score,
                    recency_score=candidate.recency_score,
                    entity_score=candidate.entity_score,
                    combined_score=candidate.combined_score,
                    selected_chars=len(content),
                )
            )
            results.append(
                RetrievedMemory(
                    document_id=document.id,
                    content=content,
                    selected_chars=len(content),
                    source_kind=document.source_kind,
                    source_turn_id=document.source_turn_id,
                    source_event_id=document.source_event_id,
                    event_sequence_start=document.event_sequence_start,
                    event_sequence_end=document.event_sequence_end,
                    semantic_score=candidate.semantic_score,
                    lexical_score=candidate.lexical_score,
                    recency_score=candidate.recency_score,
                    entity_score=candidate.entity_score,
                    combined_score=candidate.combined_score,
                )
            )
        session.commit()
        return MemoryRetrievalResult(
            retrieval_id=audit.id,
            campaign_id=request.campaign_id,
            profile_id=profile_id,
            ranking_policy=RANKING_POLICY,
            query_source_sha256=query_sha256,
            items=tuple(results),
            latency_ms=latency_ms,
            context_chars=sum(item.selected_chars for item in results),
            truncated=truncated,
        )


def _store_failure(
    request: MemoryQuery,
    *,
    profile_id: uuid.UUID,
    query_sha256: str,
    filters: dict[str, Any],
    latency_ms: int,
    error_code: str,
) -> None:
    with get_session_factory()() as session:
        session.add(
            MemoryRetrieval(
                campaign_id=request.campaign_id,
                turn_id=request.turn_id,
                provider_call_id=request.provider_call_id,
                profile_id=profile_id,
                ranking_policy=RANKING_POLICY,
                query_source_sha256=query_sha256,
                filters=filters,
                requested_count=request.requested_count,
                returned_count=0,
                latency_ms=latency_ms,
                context_budget_chars=request.context_budget_chars,
                truncated=False,
                status="failed",
                error_code=error_code,
            )
        )
        session.commit()


def retrieve_memories(
    request: MemoryQuery, *, provider: EmbeddingProvider
) -> MemoryRetrievalResult:
    """Retrieve bounded memories without exposing them to a gameplay provider."""

    query_text = _validate_request(request)
    query_sha256 = _query_sha256(query_text)
    campaign_index_id, profile_id, maximum = _resolve_profile(request)
    filters = _filters_payload(
        request, campaign_index_id=campaign_index_id, max_event_sequence=maximum
    )
    started = time.perf_counter()
    try:
        with get_session_factory()() as session:
            profile = session.get(MemoryEmbeddingProfile, profile_id)
            if profile is None or not _provider_matches_profile(provider, profile):
                raise MemoryRetrievalUnavailableError(
                    "retrieval provider does not match the selected memory profile"
                )
            dimensions = profile.dimensions
        query_vector = validate_embedding(provider.embed_query(query_text), dimensions=dimensions)
        ranked = _rank_candidates(
            request,
            profile_id=profile_id,
            query_vector=query_vector,
            query_text=query_text,
            max_event_sequence=maximum,
        )
        selected, truncated = _select_bounded(
            ranked,
            query_text=query_text,
            requested_count=request.requested_count,
            context_budget_chars=request.context_budget_chars,
        )
    except Exception as exc:
        latency_ms = max(0, math.ceil((time.perf_counter() - started) * 1000))
        error_code = (
            "retrieval_timeout"
            if isinstance(exc, DBAPIError) and "statement timeout" in str(exc).casefold()
            else "retrieval_failed"
        )
        _store_failure(
            request,
            profile_id=profile_id,
            query_sha256=query_sha256,
            filters=filters,
            latency_ms=latency_ms,
            error_code=error_code,
        )
        raise MemoryRetrievalError("memory retrieval failed safely") from exc
    latency_ms = max(0, math.ceil((time.perf_counter() - started) * 1000))
    return _store_success(
        request,
        profile_id=profile_id,
        query_sha256=query_sha256,
        filters=filters,
        selected=selected,
        latency_ms=latency_ms,
        truncated=truncated,
    )


def replay_memory_retrieval(
    retrieval_id: uuid.UUID,
    *,
    query_text: str,
    provider: EmbeddingProvider,
) -> RetrievalReplayResult:
    """Replay an audit using caller-held query text; raw prompts are never persisted."""

    canonical = _canonical_query(query_text)
    with get_session_factory()() as session:
        audit = session.get(MemoryRetrieval, retrieval_id)
        if audit is None or audit.status != "succeeded":
            raise MemoryRetrievalReplayError("successful retrieval audit not found")
        if audit.ranking_policy not in SUPPORTED_RANKING_POLICIES:
            raise MemoryRetrievalReplayError("ranking policy is not supported for replay")
        if audit.query_source_sha256 != _query_sha256(canonical):
            raise MemoryRetrievalReplayError("query text does not match the audit hash")
        filters = audit.filters
        entities = filters.get("entities", {})
        expected_items = session.scalars(
            select(MemoryRetrievalItem)
            .where(MemoryRetrievalItem.retrieval_id == retrieval_id)
            .order_by(MemoryRetrievalItem.rank)
        ).all()
        expected = tuple(item.document_id for item in expected_items)
        request = MemoryQuery(
            campaign_id=audit.campaign_id,
            query_text=canonical,
            requested_count=audit.requested_count,
            context_budget_chars=audit.context_budget_chars,
            max_event_sequence=int(filters["max_event_sequence"]),
            location_id=_optional_uuid(entities.get("location_id")),
            npc_id=_optional_uuid(entities.get("npc_id")),
            character_id=_optional_uuid(entities.get("character_id")),
            quest_id=_optional_uuid(entities.get("quest_id")),
            decision_id=_optional_uuid(entities.get("decision_id")),
            faction_id=_optional_uuid(entities.get("faction_id")),
            evaluation_profile_id=audit.profile_id,
        )
        profile_id = audit.profile_id
        profile = session.get(MemoryEmbeddingProfile, profile_id)
        if profile is None or not _provider_matches_profile(provider, profile):
            raise MemoryRetrievalReplayError("provider does not match the audited profile")

    vector = validate_embedding(provider.embed_query(canonical), dimensions=provider.dimensions)
    ranked = _rank_candidates(
        request,
        profile_id=profile_id,
        query_vector=vector,
        query_text=canonical,
        max_event_sequence=request.max_event_sequence or 1,
    )
    selected, _ = _select_bounded(
        ranked,
        query_text=canonical,
        requested_count=request.requested_count,
        context_budget_chars=request.context_budget_chars,
        ranking_policy=audit.ranking_policy,
    )
    replayed = tuple(candidate.document.id for candidate, _ in selected)
    score_match = len(expected_items) == len(selected) and all(
        expected_item.document_id == candidate.document.id
        and expected_item.selected_chars == len(content)
        and _optional_score_matches(expected_item.semantic_score, candidate.semantic_score)
        and _optional_score_matches(expected_item.lexical_score, candidate.lexical_score)
        and math.isclose(expected_item.recency_score, candidate.recency_score, abs_tol=1e-12)
        and math.isclose(expected_item.entity_score, candidate.entity_score, abs_tol=1e-12)
        and math.isclose(expected_item.combined_score, candidate.combined_score, abs_tol=1e-12)
        for expected_item, (candidate, content) in zip(expected_items, selected, strict=True)
    )
    return RetrievalReplayResult(
        retrieval_id, expected == replayed and score_match, expected, replayed
    )


def _optional_uuid(value: Any) -> uuid.UUID | None:
    return uuid.UUID(str(value)) if value is not None else None


def _optional_score_matches(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is right
    return math.isclose(left, right, abs_tol=1e-12)


def _nearest_rank_p95(values: list[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)]


def evaluate_and_activate_memory_index(
    *,
    campaign_id: uuid.UUID,
    profile_id: uuid.UUID,
    provider: EmbeddingProvider,
    golden_queries: tuple[GoldenMemoryQuery, ...],
    max_event_sequence: int | None = None,
) -> MemoryQualityResult:
    """Run the fixed M4 quality gate and atomically activate only a passing index."""

    retrieved_ids: list[uuid.UUID] = []
    recall_values: list[float] = []
    reciprocal_ranks: list[float] = []
    critical_hits: list[bool] = []
    latencies: list[int] = []
    for golden in golden_queries:
        if not golden.relevant_document_ids:
            raise ValueError("every golden query must identify at least one relevant document")
        result = retrieve_memories(
            MemoryQuery(
                campaign_id=campaign_id,
                query_text=golden.query_text,
                requested_count=MAX_MEMORY_ITEMS,
                context_budget_chars=MAX_MEMORY_CONTEXT_CHARS,
                max_event_sequence=max_event_sequence,
                evaluation_profile_id=profile_id,
            ),
            provider=provider,
        )
        ranked_ids = [item.document_id for item in result.items]
        matched = golden.relevant_document_ids.intersection(ranked_ids)
        recall_values.append(len(matched) / len(golden.relevant_document_ids))
        first_rank = next(
            (rank for rank, item_id in enumerate(ranked_ids, start=1) if item_id in matched), None
        )
        reciprocal_ranks.append(0.0 if first_rank is None else 1.0 / first_rank)
        if golden.critical:
            critical_hits.append(bool(matched))
        retrieved_ids.append(result.retrieval_id)
        latencies.append(result.latency_ms)

    with get_session_factory()() as session:
        campaign_index = session.scalar(
            select(CampaignMemoryIndex).where(
                CampaignMemoryIndex.campaign_id == campaign_id,
                CampaignMemoryIndex.profile_id == profile_id,
            )
        )
        if campaign_index is None:
            raise MemoryRetrievalUnavailableError("evaluation memory index is missing")
        corpus_count = (
            session.scalar(
                select(func.count(MemoryEmbedding.id))
                .join(MemoryDocument, MemoryDocument.id == MemoryEmbedding.document_id)
                .where(
                    MemoryDocument.campaign_id == campaign_id,
                    MemoryDocument.visibility == "player",
                    MemoryDocument.status == "active",
                    MemoryEmbedding.profile_id == profile_id,
                    MemoryEmbedding.document_sha256 == MemoryDocument.content_sha256,
                )
            )
            or 0
        )

    query_count = len(golden_queries)
    critical_count = len(critical_hits)
    critical_recall = sum(critical_hits) / critical_count if critical_count else 0.0
    overall_recall = sum(recall_values) / query_count if query_count else 0.0
    mrr = sum(reciprocal_ranks) / query_count if query_count else 0.0
    latency_p95 = _nearest_rank_p95(latencies)
    passed = (
        query_count >= 20
        and critical_count >= 5
        and corpus_count >= 500
        and critical_recall == 1.0
        and overall_recall >= 0.9
        and mrr >= 0.65
        and latency_p95 <= 250
    )
    result = MemoryQualityResult(
        passed=passed,
        query_count=query_count,
        critical_query_count=critical_count,
        corpus_count=corpus_count,
        critical_recall_at_8=critical_recall,
        overall_recall_at_8=overall_recall,
        mean_reciprocal_rank=mrr,
        latency_p95_ms=latency_p95,
        retrieval_ids=tuple(retrieved_ids),
    )
    if passed:
        with get_session_factory()() as session:
            activate_memory_index(
                session,
                campaign_id=campaign_id,
                profile_id=profile_id,
                quality_gate=result.as_gate(),
            )
            session.commit()
    return result
