"""Player-safe source projection and durable M4 memory indexing."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db import get_session_factory
from app.embeddings import (
    EmbeddingModelUnavailableError,
    EmbeddingProvider,
    InvalidEmbeddingError,
    validate_embedding,
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

CHUNKER_VERSION = "completed-source-1.0.0"
MAX_DOCUMENT_CHARS = 6000
DEFAULT_LEASE_SECONDS = 120
MAX_JOB_ATTEMPTS = 5


class MemoryIndexError(RuntimeError):
    pass


class SourceHashDriftError(MemoryIndexError):
    pass


class MemoryLeaseConflictError(MemoryIndexError):
    pass


class IncompleteMemoryIndexError(MemoryIndexError):
    pass


@dataclass(frozen=True, slots=True)
class ProjectionResult:
    created_documents: int = 0
    existing_documents: int = 0
    created_jobs: int = 0


@dataclass(frozen=True, slots=True)
class DrainResult:
    claimed: int = 0
    completed: int = 0
    failed: int = 0


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bounded_turn_content(turn: Turn) -> str:
    action = " ".join(turn.player_action.split())
    narration = " ".join((turn.dm_narration or "").split())
    content = f"Player action:\n{action}\n\nGM narration:\n{narration}"
    if len(content) <= MAX_DOCUMENT_CHARS:
        return content
    marker = "\n\n[Memory source truncated deterministically]"
    return content[: MAX_DOCUMENT_CHARS - len(marker)].rstrip() + marker


def _uuid_from_payload(events: list[CampaignEvent], key: str) -> uuid.UUID | None:
    for event in reversed(events):
        raw = event.payload.get(key)
        if raw is None:
            continue
        try:
            return uuid.UUID(str(raw))
        except (TypeError, ValueError):
            continue
    return None


def _location_at_sequence(
    session: Session, campaign_id: uuid.UUID, sequence: int
) -> uuid.UUID | None:
    event = session.scalar(
        select(CampaignEvent)
        .where(
            CampaignEvent.campaign_id == campaign_id,
            CampaignEvent.visibility == "player",
            CampaignEvent.event_type == "scene_opened",
            CampaignEvent.sequence <= sequence,
        )
        .order_by(CampaignEvent.sequence.desc())
        .limit(1)
    )
    if event is None:
        return None
    try:
        return uuid.UUID(str(event.payload["location_id"]))
    except (KeyError, TypeError, ValueError):
        return None


def _time_at_sequence(session: Session, campaign_id: uuid.UUID, sequence: int) -> int:
    event = session.scalar(
        select(CampaignEvent)
        .where(
            CampaignEvent.campaign_id == campaign_id,
            CampaignEvent.visibility == "player",
            CampaignEvent.event_type == "narrative_time_advanced",
            CampaignEvent.sequence <= sequence,
        )
        .order_by(CampaignEvent.sequence.desc())
        .limit(1)
    )
    if event is None:
        return 0
    value = event.payload.get("narrative_time_minutes", 0)
    return value if isinstance(value, int) and value >= 0 else 0


def ensure_embedding_profile(
    session: Session, provider: EmbeddingProvider
) -> MemoryEmbeddingProfile:
    expected = {
        "provider_kind": provider.provider_kind,
        "model_name": provider.model_name,
        "model_revision": provider.model_revision,
        "artifact_sha256": provider.artifact_sha256,
        "license_id": provider.license_id,
        "dimensions": provider.dimensions,
        "normalization": provider.normalization,
        "distance_metric": "cosine",
        "adapter_version": provider.adapter_version,
    }
    profile = session.scalar(
        select(MemoryEmbeddingProfile).where(
            MemoryEmbeddingProfile.profile_key == provider.profile_key
        )
    )
    if profile is None:
        profile = MemoryEmbeddingProfile(profile_key=provider.profile_key, **expected)
        session.add(profile)
        session.flush()
        return profile
    actual = {key: getattr(profile, key) for key in expected}
    if actual != expected:
        raise MemoryIndexError(
            f"embedding profile {provider.profile_key!r} does not match its immutable metadata"
        )
    return profile


def _enqueue_job(
    session: Session,
    *,
    campaign_id: uuid.UUID,
    document_id: uuid.UUID,
    profile_id: uuid.UUID,
) -> bool:
    result = session.execute(
        insert(MemoryIndexJob)
        .values(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            document_id=document_id,
            profile_id=profile_id,
            status="pending",
            attempt_count=0,
        )
        .on_conflict_do_nothing(index_elements=["document_id", "profile_id"])
    )
    return bool(result.rowcount)


def _enqueue_document_for_existing_indexes(session: Session, document: MemoryDocument) -> int:
    indexes = list(
        session.scalars(
            select(CampaignMemoryIndex).where(
                CampaignMemoryIndex.campaign_id == document.campaign_id,
                CampaignMemoryIndex.status.in_(("building", "ready", "active")),
            )
        )
    )
    created = 0
    for campaign_index in indexes:
        if campaign_index.status == "ready":
            campaign_index.status = "building"
            campaign_index.quality_gate = None
        created += _enqueue_job(
            session,
            campaign_id=document.campaign_id,
            document_id=document.id,
            profile_id=campaign_index.profile_id,
        )
    return created


def project_completed_turns(
    session: Session,
    *,
    campaign_id: uuid.UUID | None = None,
    turn_id: uuid.UUID | None = None,
    limit: int = 100,
) -> ProjectionResult:
    if not 1 <= limit <= 1000:
        raise ValueError("projection limit must be between 1 and 1000")
    statement = (
        select(Turn)
        .where(
            Turn.status == "completed",
            Turn.dm_narration.is_not(None),
            Turn.completed_at.is_not(None),
        )
        .order_by(Turn.completed_at, Turn.id)
        .limit(limit)
    )
    if campaign_id is not None:
        statement = statement.where(Turn.campaign_id == campaign_id)
    if turn_id is not None:
        statement = statement.where(Turn.id == turn_id)
    else:
        already_projected = (
            select(MemoryDocument.id)
            .where(
                MemoryDocument.campaign_id == Turn.campaign_id,
                MemoryDocument.source_turn_id == Turn.id,
                MemoryDocument.source_version == 1,
                MemoryDocument.chunk_index == 0,
            )
            .exists()
        )
        statement = statement.where(~already_projected)

    created_documents = existing_documents = created_jobs = 0
    for turn in session.scalars(statement):
        events = list(
            session.scalars(
                select(CampaignEvent)
                .where(
                    CampaignEvent.campaign_id == turn.campaign_id,
                    CampaignEvent.turn_id == turn.id,
                    CampaignEvent.visibility == "player",
                )
                .order_by(CampaignEvent.sequence)
            )
        )
        if not events:
            continue
        content = _bounded_turn_content(turn)
        content_sha256 = _sha256(content)
        existing = session.scalar(
            select(MemoryDocument).where(
                MemoryDocument.campaign_id == turn.campaign_id,
                MemoryDocument.source_turn_id == turn.id,
                MemoryDocument.source_version == 1,
                MemoryDocument.chunk_index == 0,
            )
        )
        if existing is not None:
            if existing.content_sha256 != content_sha256:
                raise SourceHashDriftError(
                    f"completed turn {turn.id} no longer matches its immutable memory source"
                )
            existing_documents += 1
            continue

        end_sequence = events[-1].sequence
        document = MemoryDocument(
            campaign_id=turn.campaign_id,
            source_kind="turn",
            source_turn_id=turn.id,
            source_version=1,
            chunk_index=0,
            event_sequence_start=events[0].sequence,
            event_sequence_end=end_sequence,
            visibility="player",
            content=content,
            content_sha256=content_sha256,
            chunker_version=CHUNKER_VERSION,
            status="active",
            source_world_revision=turn.world_revision_after,
            source_time_minutes=_time_at_sequence(session, turn.campaign_id, end_sequence),
            location_id=_location_at_sequence(session, turn.campaign_id, end_sequence),
            npc_id=turn.target_npc_id or _uuid_from_payload(events, "npc_id"),
            character_id=turn.actor_character_id,
            quest_id=_uuid_from_payload(events, "quest_id"),
            decision_id=turn.decision_id or _uuid_from_payload(events, "decision_id"),
            faction_id=_uuid_from_payload(events, "faction_id"),
        )
        session.add(document)
        session.flush()
        created_jobs += _enqueue_document_for_existing_indexes(session, document)
        created_documents += 1
    return ProjectionResult(created_documents, existing_documents, created_jobs)


def start_index_build(
    session: Session, *, campaign_id: uuid.UUID, profile_id: uuid.UUID
) -> CampaignMemoryIndex:
    if session.get(Campaign, campaign_id) is None:
        raise MemoryIndexError("campaign not found")
    if session.get(MemoryEmbeddingProfile, profile_id) is None:
        raise MemoryIndexError("embedding profile not found")
    campaign_index = session.scalar(
        select(CampaignMemoryIndex).where(
            CampaignMemoryIndex.campaign_id == campaign_id,
            CampaignMemoryIndex.profile_id == profile_id,
        )
    )
    if campaign_index is None:
        campaign_index = CampaignMemoryIndex(
            campaign_id=campaign_id,
            profile_id=profile_id,
            status="building",
            source_count=0,
        )
        session.add(campaign_index)
        session.flush()
    elif campaign_index.status in {"failed", "retired", "ready"}:
        campaign_index.status = "building"
        campaign_index.activated_at = None
        campaign_index.last_error_code = None
        campaign_index.last_error_detail = None
        campaign_index.quality_gate = None

    documents = session.scalars(
        select(MemoryDocument).where(
            MemoryDocument.campaign_id == campaign_id,
            MemoryDocument.visibility == "player",
            MemoryDocument.status == "active",
        )
    )
    for document in documents:
        _enqueue_job(
            session,
            campaign_id=campaign_id,
            document_id=document.id,
            profile_id=profile_id,
        )
    _refresh_index_progress(session, campaign_id=campaign_id, profile_id=profile_id)
    return campaign_index


def recover_expired_leases(session: Session, *, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    jobs = list(
        session.scalars(
            select(MemoryIndexJob)
            .where(
                MemoryIndexJob.status == "claimed",
                MemoryIndexJob.lease_expires_at <= now,
            )
            .with_for_update(skip_locked=True)
        )
    )
    for job in jobs:
        job.status = "pending"
        job.lease_owner = None
        job.lease_expires_at = None
        job.next_attempt_at = now
        job.error_code = None
        job.error_detail = None
        job.updated_at = now
    return len(jobs)


def claim_index_job(
    session: Session,
    *,
    profile_id: uuid.UUID,
    worker_id: str,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    now: datetime | None = None,
) -> MemoryIndexJob | None:
    if not worker_id or len(worker_id) > 120:
        raise ValueError("worker_id must contain between 1 and 120 characters")
    if not 5 <= lease_seconds <= 3600:
        raise ValueError("lease_seconds must be between 5 and 3600")
    now = now or datetime.now(UTC)
    recover_expired_leases(session, now=now)
    job = session.scalar(
        select(MemoryIndexJob)
        .where(
            MemoryIndexJob.profile_id == profile_id,
            or_(
                and_(
                    MemoryIndexJob.status == "pending",
                    or_(
                        MemoryIndexJob.next_attempt_at.is_(None),
                        MemoryIndexJob.next_attempt_at <= now,
                    ),
                ),
                and_(
                    MemoryIndexJob.status == "failed",
                    MemoryIndexJob.attempt_count < MAX_JOB_ATTEMPTS,
                    MemoryIndexJob.next_attempt_at <= now,
                ),
            ),
        )
        .order_by(MemoryIndexJob.created_at, MemoryIndexJob.id)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    if job is None:
        return None
    job.status = "claimed"
    job.attempt_count += 1
    job.lease_owner = worker_id
    job.lease_expires_at = now + timedelta(seconds=lease_seconds)
    job.next_attempt_at = None
    job.error_code = None
    job.error_detail = None
    job.updated_at = now
    session.flush()
    return job


def _safe_failure(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, SourceHashDriftError):
        return "source_hash_drift", "Memory source changed during embedding"
    if isinstance(exc, InvalidEmbeddingError) or "dimension" in str(exc).casefold():
        return "invalid_embedding", "Embedding provider returned an invalid vector"
    if isinstance(exc, (EmbeddingModelUnavailableError, FileNotFoundError)):
        return "embedding_model_unavailable", "Local embedding model is unavailable"
    return "embedding_failed", "Embedding provider failed"


def _refresh_index_progress(
    session: Session, *, campaign_id: uuid.UUID, profile_id: uuid.UUID
) -> None:
    campaign_index = session.scalar(
        select(CampaignMemoryIndex)
        .where(
            CampaignMemoryIndex.campaign_id == campaign_id,
            CampaignMemoryIndex.profile_id == profile_id,
        )
        .with_for_update()
    )
    if campaign_index is None:
        return
    eligible = (
        session.scalar(
            select(func.count(MemoryDocument.id)).where(
                MemoryDocument.campaign_id == campaign_id,
                MemoryDocument.visibility == "player",
                MemoryDocument.status == "active",
            )
        )
        or 0
    )
    embedded = (
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
    checkpoint = session.scalar(
        select(func.max(MemoryDocument.event_sequence_end))
        .join(MemoryEmbedding, MemoryEmbedding.document_id == MemoryDocument.id)
        .where(
            MemoryDocument.campaign_id == campaign_id,
            MemoryDocument.visibility == "player",
            MemoryDocument.status == "active",
            MemoryEmbedding.profile_id == profile_id,
            MemoryEmbedding.document_sha256 == MemoryDocument.content_sha256,
        )
    )
    campaign_index.source_count = embedded
    campaign_index.indexed_through_event_sequence = checkpoint
    campaign_index.updated_at = datetime.now(UTC)
    if campaign_index.status == "building" and embedded == eligible:
        campaign_index.status = "ready"


def process_claimed_job(
    *,
    job_id: uuid.UUID,
    worker_id: str,
    provider: EmbeddingProvider,
) -> bool:
    factory = get_session_factory()
    with factory() as session:
        job = session.get(MemoryIndexJob, job_id)
        if (
            job is None
            or job.status != "claimed"
            or job.lease_owner != worker_id
            or job.lease_expires_at is None
            or job.lease_expires_at <= datetime.now(UTC)
        ):
            raise MemoryLeaseConflictError("memory index job lease is no longer owned by worker")
        document = session.get(MemoryDocument, job.document_id)
        profile = session.get(MemoryEmbeddingProfile, job.profile_id)
        if document is None or profile is None:
            raise MemoryIndexError("memory index job source is missing")
        content = document.content
        document_hash = document.content_sha256
        campaign_id = job.campaign_id
        profile_id = job.profile_id
        expected_key = profile.profile_key

    try:
        if expected_key != provider.profile_key:
            raise MemoryIndexError("worker provider does not match the claimed profile")
        vectors = provider.embed_documents([content])
        if len(vectors) != 1:
            raise MemoryIndexError("embedding provider returned the wrong batch size")
        vector = validate_embedding(vectors[0], dimensions=provider.dimensions)
        with factory() as session:
            job = session.scalar(
                select(MemoryIndexJob).where(MemoryIndexJob.id == job_id).with_for_update()
            )
            if (
                job is None
                or job.status != "claimed"
                or job.lease_owner != worker_id
                or job.lease_expires_at is None
                or job.lease_expires_at <= datetime.now(UTC)
            ):
                raise MemoryLeaseConflictError("memory index job lease expired during embedding")
            document = session.get(MemoryDocument, job.document_id)
            if document is None or document.content_sha256 != document_hash:
                raise SourceHashDriftError("memory source hash changed during embedding")
            session.execute(
                insert(MemoryEmbedding)
                .values(
                    id=uuid.uuid4(),
                    document_id=document.id,
                    profile_id=profile_id,
                    document_sha256=document_hash,
                    embedding=vector,
                )
                .on_conflict_do_nothing(index_elements=["document_id", "profile_id"])
            )
            job.status = "complete"
            job.lease_owner = None
            job.lease_expires_at = None
            job.next_attempt_at = None
            job.error_code = None
            job.error_detail = None
            job.updated_at = datetime.now(UTC)
            _refresh_index_progress(session, campaign_id=campaign_id, profile_id=profile_id)
            session.commit()
        return True
    except MemoryLeaseConflictError:
        raise
    except Exception as exc:
        error_code, error_detail = _safe_failure(exc)
        with factory() as session:
            job = session.scalar(
                select(MemoryIndexJob).where(MemoryIndexJob.id == job_id).with_for_update()
            )
            if job is not None and job.status == "claimed" and job.lease_owner == worker_id:
                job.status = "failed"
                job.lease_owner = None
                job.lease_expires_at = None
                job.next_attempt_at = datetime.now(UTC) + timedelta(
                    seconds=min(300, 2 ** min(job.attempt_count, 8))
                )
                job.error_code = error_code
                job.error_detail = error_detail
                job.updated_at = datetime.now(UTC)
                session.commit()
        return False


def drain_index_jobs(
    *,
    provider: EmbeddingProvider,
    worker_id: str,
    limit: int = 25,
) -> DrainResult:
    if not 1 <= limit <= 1000:
        raise ValueError("drain limit must be between 1 and 1000")
    factory = get_session_factory()
    claimed = completed = failed = 0
    for _ in range(limit):
        with factory() as session:
            profile = ensure_embedding_profile(session, provider)
            job = claim_index_job(session, profile_id=profile.id, worker_id=worker_id)
            session.commit()
            job_id = job.id if job is not None else None
        if job_id is None:
            break
        claimed += 1
        if process_claimed_job(job_id=job_id, worker_id=worker_id, provider=provider):
            completed += 1
        else:
            failed += 1
    return DrainResult(claimed, completed, failed)


def activate_memory_index(
    session: Session,
    *,
    campaign_id: uuid.UUID,
    profile_id: uuid.UUID,
    quality_gate: dict[str, Any],
) -> CampaignMemoryIndex:
    if quality_gate.get("passed") is not True:
        raise IncompleteMemoryIndexError("quality gate must explicitly pass before activation")
    target = session.scalar(
        select(CampaignMemoryIndex)
        .where(
            CampaignMemoryIndex.campaign_id == campaign_id,
            CampaignMemoryIndex.profile_id == profile_id,
        )
        .with_for_update()
    )
    if target is None or target.status != "ready":
        raise IncompleteMemoryIndexError("replacement memory index is not ready")
    _refresh_index_progress(session, campaign_id=campaign_id, profile_id=profile_id)
    if target.status != "ready":
        raise IncompleteMemoryIndexError("replacement memory index is incomplete")
    unfinished = (
        session.scalar(
            select(func.count(MemoryIndexJob.id)).where(
                MemoryIndexJob.campaign_id == campaign_id,
                MemoryIndexJob.profile_id == profile_id,
                MemoryIndexJob.status != "complete",
            )
        )
        or 0
    )
    if unfinished:
        raise IncompleteMemoryIndexError("replacement memory index still has unfinished jobs")
    old_active = session.scalar(
        select(CampaignMemoryIndex)
        .where(
            CampaignMemoryIndex.campaign_id == campaign_id,
            CampaignMemoryIndex.status == "active",
        )
        .with_for_update()
    )
    if old_active is not None and old_active.id != target.id:
        old_active.status = "retired"
        old_active.activated_at = None
        old_active.updated_at = datetime.now(UTC)
        session.flush()
    target.status = "active"
    target.quality_gate = json.loads(json.dumps(quality_gate, sort_keys=True))
    target.activated_at = datetime.now(UTC)
    target.updated_at = target.activated_at
    session.flush()
    return target
