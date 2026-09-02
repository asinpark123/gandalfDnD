import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class RulesetRelease(TimestampMixin, Base):
    __tablename__ = "ruleset_releases"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    publication_date: Mapped[date] = mapped_column(Date, nullable=False)
    license_id: Mapped[str] = mapped_column(String(40), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    artifact_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    artifact_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    data_schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    support_status: Mapped[str] = mapped_column(String(30), nullable=False)

    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="ruleset_release")
    data_catalogs: Mapped[list["RulesetDataCatalog"]] = relationship(
        back_populates="ruleset_release"
    )

    __table_args__ = (
        CheckConstraint("artifact_size_bytes > 0", name="ruleset_artifact_size_positive"),
        CheckConstraint(
            "support_status IN ('foundation_only', 'character_creation', 'complete')",
            name="ruleset_support_status",
        ),
    )


class RulesetDataCatalog(TimestampMixin, Base):
    __tablename__ = "ruleset_data_catalogs"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ruleset_release_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_releases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    support_status: Mapped[str] = mapped_column(String(30), nullable=False)
    catalog_sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    ruleset_release: Mapped[RulesetRelease] = relationship(back_populates="data_catalogs")

    __table_args__ = (
        CheckConstraint(
            "kind IN ('foundation', 'character_creation', 'character_state', 'rules_resolution')",
            name="ruleset_data_catalog_kind",
        ),
        CheckConstraint(
            "support_status IN ('foundation_only', 'character_creation', 'complete')",
            name="ruleset_data_catalog_support_status",
        ),
    )


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    ruleset_release_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_releases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ruleset_data_catalog_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_data_catalogs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    legacy_ruleset_label: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    play_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="party_commander")
    party_min_active: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    party_max_active: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    world_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    ruleset_release: Mapped[RulesetRelease] = relationship(back_populates="campaigns")
    characters: Mapped[list["Character"]] = relationship(back_populates="campaign")
    locations: Mapped[list["Location"]] = relationship(back_populates="campaign")
    scenes: Mapped[list["Scene"]] = relationship(back_populates="campaign")
    npcs: Mapped[list["NPC"]] = relationship(back_populates="campaign")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'archived')", name="campaign_status"),
        CheckConstraint(
            "play_mode IN ('legacy_single', 'party_commander')", name="campaign_play_mode"
        ),
        CheckConstraint(
            "party_min_active >= 1 AND party_max_active >= party_min_active "
            "AND party_max_active <= 4",
            name="campaign_party_size_bounds",
        ),
        CheckConstraint("world_revision >= 0", name="campaign_world_revision_nonnegative"),
    )


class Location(TimestampMixin, Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    campaign: Mapped[Campaign] = relationship(back_populates="locations")

    __table_args__ = (
        UniqueConstraint("campaign_id", "name", name="uq_locations_campaign_name"),
        Index(
            "uq_locations_one_current_per_campaign",
            "campaign_id",
            unique=True,
            postgresql_where=text("is_current"),
        ),
    )


class Scene(TimestampMixin, Base):
    __tablename__ = "scenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    opened_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="scenes_opened_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )
    closed_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="scenes_closed_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    campaign: Mapped[Campaign] = relationship(back_populates="scenes")
    location: Mapped[Location] = relationship()
    presences: Mapped[list["SceneNPCPresence"]] = relationship(back_populates="scene")

    __table_args__ = (
        UniqueConstraint("campaign_id", "sequence", name="uq_scenes_campaign_sequence"),
        CheckConstraint("sequence > 0", name="scene_sequence_positive"),
        CheckConstraint("status IN ('active', 'closed')", name="scene_status"),
        CheckConstraint("revision >= 0", name="scene_revision_nonnegative"),
        Index(
            "uq_scenes_one_active_per_campaign",
            "campaign_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )


class NPC(TimestampMixin, Base):
    __tablename__ = "npcs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    public_description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    introduced_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="npcs_introduced_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    campaign: Mapped[Campaign] = relationship(back_populates="npcs")
    presences: Mapped[list["SceneNPCPresence"]] = relationship(back_populates="npc")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive')", name="npc_status"),
        CheckConstraint("visibility IN ('player', 'dm_only')", name="npc_visibility"),
        CheckConstraint("revision >= 0", name="npc_revision_nonnegative"),
    )


class SceneNPCPresence(TimestampMixin, Base):
    __tablename__ = "scene_npc_presences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scene_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    npc_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("npcs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="present")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    arrived_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="scene_npc_presences_arrived_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )
    departed_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="scene_npc_presences_departed_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    scene: Mapped[Scene] = relationship(back_populates="presences")
    npc: Mapped[NPC] = relationship(back_populates="presences")

    __table_args__ = (
        CheckConstraint(
            "status IN ('present', 'departed')", name="scene_npc_presence_status"
        ),
        CheckConstraint("revision >= 0", name="scene_npc_presence_revision_nonnegative"),
        Index(
            "uq_scene_npc_one_present_scene",
            "scene_id",
            "npc_id",
            unique=True,
            postgresql_where=text("status = 'present'"),
        ),
        Index(
            "uq_scene_npc_one_current_presence",
            "npc_id",
            unique=True,
            postgresql_where=text("status = 'present'"),
        ),
    )


class Character(TimestampMixin, Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ruleset_release_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_releases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ruleset_data_catalog_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_data_catalogs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    creation_status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_hp: Mapped[int | None] = mapped_column(Integer)
    hp: Mapped[int | None] = mapped_column(Integer)
    inventory: Mapped[dict[str, int]] = mapped_column(JSONB, nullable=False, default=dict)
    character_sheet: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    party_position: Mapped[int] = mapped_column(Integer, nullable=False)
    control_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    party_status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    state_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    equipped_items: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    resources: Mapped[dict[str, int]] = mapped_column(JSONB, nullable=False, default=dict)

    campaign: Mapped[Campaign] = relationship(back_populates="characters")
    grants: Mapped[list["CharacterGrant"]] = relationship(back_populates="character")

    __table_args__ = (
        CheckConstraint(
            "creation_status IN ('legacy', 'draft', 'finalized')", name="character_creation_status"
        ),
        CheckConstraint("revision >= 0", name="character_revision_nonnegative"),
        CheckConstraint("party_position BETWEEN 1 AND 4", name="character_party_position"),
        CheckConstraint("control_mode = 'player'", name="character_control_mode"),
        CheckConstraint("party_status = 'active'", name="character_party_status"),
        CheckConstraint("state_revision >= 0", name="character_state_revision_nonnegative"),
        UniqueConstraint("campaign_id", "party_position", name="uq_characters_campaign_position"),
        CheckConstraint("max_hp IS NULL OR max_hp > 0", name="character_max_hp_positive"),
        CheckConstraint(
            "(hp IS NULL AND max_hp IS NULL) OR "
            "(hp IS NOT NULL AND max_hp IS NOT NULL AND hp >= 0 AND hp <= max_hp)",
            name="character_hp_bounds",
        ),
    )


class Turn(TimestampMixin, Base):
    __tablename__ = "turns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    command_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    player_action: Mapped[str] = mapped_column(Text, nullable=False)
    dm_narration: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(40))
    model: Mapped[str | None] = mapped_column(String(80))
    structured_output: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    actor_character_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL"), index=True
    )
    target_npc_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("npcs.id", ondelete="SET NULL"), index=True
    )
    workflow_version: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    failure_stage: Mapped[str | None] = mapped_column(String(30))
    error_code: Mapped[str | None] = mapped_column(String(80))
    error_detail: Mapped[str | None] = mapped_column(Text)
    resumable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resume_status: Mapped[str | None] = mapped_column(String(30))
    intent_output: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    resolution_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "rule_resolutions.id",
            name="fk_turns_resolution_id_rule_resolutions",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        unique=True,
    )
    state_revision_before: Mapped[int | None] = mapped_column(Integer)
    state_revision_after: Mapped[int | None] = mapped_column(Integer)
    world_revision_before: Mapped[int | None] = mapped_column(Integer)
    world_revision_after: Mapped[int | None] = mapped_column(Integer)
    interpretation_prompt_version: Mapped[str | None] = mapped_column(String(60))
    narration_prompt_version: Mapped[str | None] = mapped_column(String(60))
    stage_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("campaign_id", "sequence", name="uq_turns_campaign_sequence"),
        UniqueConstraint("campaign_id", "command_id", name="uq_turns_campaign_command"),
        CheckConstraint("sequence > 0", name="turn_sequence_positive"),
        CheckConstraint(
            "workflow_version IN ('legacy-turn-1.0.0', 'two-stage-turn-1.0.0')",
            name="turn_workflow_version",
        ),
        CheckConstraint(
            "status IN ('received', 'interpreting', 'intent_ready', 'resolving', 'resolved', "
            "'narrating', 'completed', 'failed', 'cancelled')",
            name="turn_status",
        ),
        CheckConstraint(
            "resume_status IS NULL OR resume_status IN ('received', 'intent_ready', 'resolved')",
            name="turn_resume_status",
        ),
        CheckConstraint(
            "state_revision_before IS NULL OR state_revision_before >= 0",
            name="turn_state_revision_before_nonnegative",
        ),
        CheckConstraint(
            "state_revision_after IS NULL OR state_revision_after >= 0",
            name="turn_state_revision_after_nonnegative",
        ),
        CheckConstraint(
            "world_revision_before IS NULL OR world_revision_before >= 0",
            name="turn_world_revision_before_nonnegative",
        ),
        CheckConstraint(
            "world_revision_after IS NULL OR world_revision_after >= 0",
            name="turn_world_revision_after_nonnegative",
        ),
        CheckConstraint(
            "(status = 'failed' AND failure_stage IS NOT NULL AND error_code IS NOT NULL) OR "
            "(status <> 'failed' AND failure_stage IS NULL AND error_code IS NULL AND "
            "error_detail IS NULL AND resumable = false AND resume_status IS NULL)",
            name="turn_failure_shape",
        ),
        CheckConstraint(
            "status <> 'failed' OR (resumable = (resume_status IS NOT NULL))",
            name="turn_resumable_shape",
        ),
        CheckConstraint(
            "status <> 'completed' OR (dm_narration IS NOT NULL AND structured_output IS NOT NULL "
            "AND completed_at IS NOT NULL)",
            name="turn_completed_shape",
        ),
        CheckConstraint(
            "(status IN ('interpreting', 'resolving', 'narrating') AND "
            "stage_started_at IS NOT NULL) OR "
            "(status NOT IN ('interpreting', 'resolving', 'narrating') AND "
            "stage_started_at IS NULL)",
            name="turn_stage_started_shape",
        ),
        Index(
            "uq_turns_one_active_per_campaign",
            "campaign_id",
            unique=True,
            postgresql_where=text(
                "status IN ('received', 'interpreting', 'intent_ready', 'resolving', "
                "'resolved', 'narrating') OR (status = 'failed' AND resumable)"
            ),
        ),
    )


class ProviderCall(TimestampMixin, Base):
    __tablename__ = "provider_calls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    turn_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("turns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(String(30), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str | None] = mapped_column(String(80))
    prompt_version: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    structured_output: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error_code: Mapped[str | None] = mapped_column(String(80))
    error_detail: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("turn_id", "stage", "attempt", name="uq_provider_calls_attempt"),
        CheckConstraint("stage IN ('interpretation', 'narration')", name="provider_call_stage"),
        CheckConstraint("attempt > 0", name="provider_call_attempt_positive"),
        CheckConstraint("status IN ('succeeded', 'failed')", name="provider_call_status"),
        CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0", name="provider_call_latency_nonnegative"
        ),
        CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0", name="provider_call_input_nonnegative"
        ),
        CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0", name="provider_call_output_nonnegative"
        ),
        CheckConstraint(
            "(status = 'succeeded' AND structured_output IS NOT NULL AND error_code IS NULL "
            "AND error_detail IS NULL) OR "
            "(status = 'failed' AND structured_output IS NULL AND error_code IS NOT NULL)",
            name="provider_call_result_shape",
        ),
    )


class CampaignEvent(TimestampMixin, Base):
    __tablename__ = "campaign_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ruleset_release_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_releases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ruleset_data_catalog_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_data_catalogs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    turn_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("turns.id", ondelete="SET NULL"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    actor_character_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL"), index=True
    )

    __table_args__ = (
        UniqueConstraint("campaign_id", "sequence", name="uq_events_campaign_sequence"),
        CheckConstraint("sequence > 0", name="event_sequence_positive"),
        CheckConstraint("visibility IN ('player', 'dm_only')", name="campaign_event_visibility"),
    )


class DiceRoll(TimestampMixin, Base):
    __tablename__ = "dice_rolls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ruleset_release_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_releases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ruleset_data_catalog_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_data_catalogs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    turn_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("turns.id", ondelete="SET NULL"), index=True
    )
    notation: Mapped[str] = mapped_column(String(20), nullable=False)
    rolls: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    modifier: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    purpose: Mapped[str] = mapped_column(String(160), nullable=False)
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    actor_character_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL"), index=True
    )


class RuleResolution(TimestampMixin, Base):
    __tablename__ = "rule_resolutions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    command_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actor_character_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ruleset_release_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_releases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    character_state_catalog_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_data_catalogs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ruleset_data_catalog_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_data_catalogs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    dice_roll_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dice_rolls.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    character_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    state_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_type: Mapped[str] = mapped_column(String(30), nullable=False)
    ability: Mapped[str] = mapped_column(String(20), nullable=False)
    skill: Mapped[str | None] = mapped_column(String(40))
    difficulty_class: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_definition_keys: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    source_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    command: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    modifier_formula: Mapped[str] = mapped_column(Text, nullable=False)
    modifier_components: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    advantage_sources: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    disadvantage_sources: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    advantage_state: Mapped[str] = mapped_column(String(20), nullable=False)
    dice_notation: Mapped[str] = mapped_column(String(20), nullable=False)
    dice_faces: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    selected_die: Mapped[int] = mapped_column(Integer, nullable=False)
    modifier: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    resolver_version: Mapped[str] = mapped_column(String(60), nullable=False)
    rng_version: Mapped[str] = mapped_column(String(60), nullable=False)

    __table_args__ = (
        UniqueConstraint("campaign_id", "command_id", name="uq_rule_resolutions_command"),
        CheckConstraint(
            "character_revision > 0 AND state_revision > 0",
            name="rule_resolution_revisions_positive",
        ),
        CheckConstraint(
            "resolution_type IN ('ability_check', 'saving_throw')",
            name="rule_resolution_type",
        ),
        CheckConstraint(
            "resolution_type = 'ability_check' OR skill IS NULL",
            name="rule_resolution_save_has_no_skill",
        ),
        CheckConstraint(
            "ability IN ('strength', 'dexterity', 'constitution', 'intelligence', "
            "'wisdom', 'charisma')",
            name="rule_resolution_ability",
        ),
        CheckConstraint(
            "difficulty_class BETWEEN 1 AND 100", name="rule_resolution_difficulty_class"
        ),
        CheckConstraint(
            "advantage_state IN ('normal', 'advantage', 'disadvantage')",
            name="rule_resolution_advantage_state",
        ),
        CheckConstraint("dice_notation IN ('1d20', '2d20')", name="rule_resolution_dice_notation"),
        CheckConstraint(
            "jsonb_typeof(dice_faces) = 'array' AND "
            "((dice_notation = '1d20' AND jsonb_array_length(dice_faces) = 1) OR "
            "(dice_notation = '2d20' AND jsonb_array_length(dice_faces) = 2))",
            name="rule_resolution_dice_count",
        ),
        CheckConstraint("selected_die BETWEEN 1 AND 20", name="rule_resolution_selected_die"),
        CheckConstraint("outcome IN ('success', 'failure')", name="rule_resolution_outcome"),
    )


class CharacterGrant(TimestampMixin, Base):
    __tablename__ = "character_grants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ruleset_release_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_releases.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ruleset_data_catalog_id: Mapped[str] = mapped_column(
        ForeignKey("ruleset_data_catalogs.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    acquisition_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaign_events.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    grant_type: Mapped[str] = mapped_column(String(20), nullable=False)
    choice_slot: Mapped[str] = mapped_column(String(100), nullable=False)
    definition_key: Mapped[str] = mapped_column(String(160), nullable=False)
    source_definition_key: Mapped[str] = mapped_column(String(160), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    character: Mapped[Character] = relationship(back_populates="grants")

    __table_args__ = (
        CheckConstraint("revision > 0", name="character_grant_revision_positive"),
        CheckConstraint("grant_type IN ('selection', 'grant')", name="character_grant_type"),
        UniqueConstraint(
            "character_id",
            "revision",
            "choice_slot",
            "definition_key",
            name="uq_character_grant_revision_slot_definition",
        ),
    )
