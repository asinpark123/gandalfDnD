import uuid
from datetime import date, datetime
from typing import Any

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
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
    narrative_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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
        CheckConstraint("narrative_time_minutes >= 0", name="campaign_narrative_time_nonnegative"),
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
    facts: Mapped[list["WorldFact"]] = relationship(back_populates="subject_npc")

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
        CheckConstraint("status IN ('present', 'departed')", name="scene_npc_presence_status"),
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


class WorldFact(TimestampMixin, Base):
    __tablename__ = "world_facts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_npc_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("npcs.id", ondelete="CASCADE"), index=True
    )
    fact_type: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="current")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    supersedes_fact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("world_facts.id", ondelete="RESTRICT"), unique=True
    )
    created_by_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="world_facts_created_by_event_id_fkey",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        nullable=False,
    )
    superseded_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="world_facts_superseded_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )
    revealed_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="world_facts_revealed_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    subject_npc: Mapped[NPC | None] = relationship(back_populates="facts")

    __table_args__ = (
        CheckConstraint(
            "fact_type IN ('npc_attitude', 'relationship_note', 'promise', 'discovery', 'clue')",
            name="world_fact_type",
        ),
        CheckConstraint("status IN ('current', 'superseded')", name="world_fact_status"),
        CheckConstraint("visibility IN ('player', 'dm_only')", name="world_fact_visibility"),
        CheckConstraint("revision >= 0", name="world_fact_revision_nonnegative"),
        CheckConstraint("char_length(value) BETWEEN 1 AND 2000", name="world_fact_value_length"),
        CheckConstraint(
            "fact_type NOT IN ('npc_attitude', 'relationship_note', 'promise') "
            "OR subject_npc_id IS NOT NULL",
            name="world_fact_npc_subject_required",
        ),
        CheckConstraint(
            "fact_type <> 'npc_attitude' OR value IN ('friendly', 'neutral', 'wary', 'hostile')",
            name="world_fact_attitude_value",
        ),
        Index(
            "ix_world_facts_current_campaign",
            "campaign_id",
            "status",
            "visibility",
        ),
        Index(
            "uq_world_facts_current_npc_attitude",
            "campaign_id",
            "subject_npc_id",
            unique=True,
            postgresql_where=text("status = 'current' AND fact_type = 'npc_attitude'"),
        ),
    )


class Quest(TimestampMixin, Base):
    __tablename__ = "quests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quest_key: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="quests_created_by_event_id_fkey",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        nullable=False,
    )
    transitioned_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="quests_transitioned_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    objectives: Mapped[list["QuestObjective"]] = relationship(
        back_populates="quest", order_by="QuestObjective.position"
    )

    __table_args__ = (
        UniqueConstraint("campaign_id", "quest_key", name="uq_quests_campaign_key"),
        CheckConstraint(
            "status IN ('active', 'completed', 'failed', 'abandoned')",
            name="quest_status",
        ),
        CheckConstraint("visibility IN ('player', 'dm_only')", name="quest_visibility"),
        CheckConstraint("revision >= 0", name="quest_revision_nonnegative"),
        CheckConstraint("quest_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="quest_key_format"),
    )


class QuestObjective(TimestampMixin, Base):
    __tablename__ = "quest_objectives"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    objective_key: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="quest_objectives_created_by_event_id_fkey",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        nullable=False,
    )
    transitioned_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="quest_objectives_transitioned_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    quest: Mapped[Quest] = relationship(back_populates="objectives")

    __table_args__ = (
        UniqueConstraint("quest_id", "objective_key", name="uq_objectives_quest_key"),
        UniqueConstraint("quest_id", "position", name="uq_objectives_quest_position"),
        CheckConstraint(
            "status IN ('pending', 'active', 'completed', 'failed', 'skipped')",
            name="quest_objective_status",
        ),
        CheckConstraint("position BETWEEN 1 AND 10", name="quest_objective_position"),
        CheckConstraint("revision >= 0", name="quest_objective_revision_nonnegative"),
        CheckConstraint(
            "objective_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'",
            name="quest_objective_key_format",
        ),
    )


class DecisionPoint(TimestampMixin, Base):
    __tablename__ = "decision_points"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    decision_key: Mapped[str] = mapped_column(String(80), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    selected_option_key: Mapped[str | None] = mapped_column(String(80))
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="decision_points_created_by_event_id_fkey",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        nullable=False,
    )
    selected_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="decision_points_selected_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    options: Mapped[list["DecisionOption"]] = relationship(
        back_populates="decision", order_by="DecisionOption.position"
    )

    __table_args__ = (
        UniqueConstraint("campaign_id", "decision_key", name="uq_decisions_campaign_key"),
        CheckConstraint("status IN ('open', 'selected')", name="decision_point_status"),
        CheckConstraint("visibility IN ('player', 'dm_only')", name="decision_point_visibility"),
        CheckConstraint("revision >= 0", name="decision_point_revision_nonnegative"),
        CheckConstraint(
            "decision_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="decision_point_key_format"
        ),
        CheckConstraint(
            "(status = 'open' AND selected_option_key IS NULL) OR "
            "(status = 'selected' AND selected_option_key IS NOT NULL)",
            name="decision_point_selection_shape",
        ),
    )


class DecisionOption(TimestampMixin, Base):
    __tablename__ = "decision_options"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    decision_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("decision_points.id", ondelete="CASCADE"), nullable=False, index=True
    )
    option_key: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    consequences: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)

    decision: Mapped[DecisionPoint] = relationship(back_populates="options")

    __table_args__ = (
        UniqueConstraint("decision_id", "option_key", name="uq_decision_options_key"),
        UniqueConstraint("decision_id", "position", name="uq_decision_options_position"),
        CheckConstraint("position BETWEEN 1 AND 4", name="decision_option_position"),
        CheckConstraint(
            "option_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="decision_option_key_format"
        ),
        CheckConstraint(
            "jsonb_typeof(consequences) = 'array' AND jsonb_array_length(consequences) <= 10",
            name="decision_option_consequences_shape",
        ),
    )


class Faction(TimestampMixin, Base):
    __tablename__ = "factions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    faction_key: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="factions_created_by_event_id_fkey",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        nullable=False,
    )

    relationships: Mapped[list["FactionRelationship"]] = relationship(
        back_populates="faction", order_by="FactionRelationship.created_at"
    )

    __table_args__ = (
        UniqueConstraint("campaign_id", "faction_key", name="uq_factions_campaign_key"),
        CheckConstraint("status IN ('active', 'inactive')", name="faction_status"),
        CheckConstraint("visibility IN ('player', 'dm_only')", name="faction_visibility"),
        CheckConstraint("revision >= 0", name="faction_revision_nonnegative"),
        CheckConstraint("faction_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="faction_key_format"),
    )


class FactionRelationship(TimestampMixin, Base):
    __tablename__ = "faction_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    faction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("factions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    character_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )
    npc_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("npcs.id", ondelete="CASCADE"), index=True
    )
    value: Mapped[str] = mapped_column(String(30), nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="faction_relationships_created_by_event_id_fkey",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        nullable=False,
    )
    updated_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "campaign_events.id",
            name="faction_relationships_updated_by_event_id_fkey",
            ondelete="SET NULL",
            use_alter=True,
        )
    )

    faction: Mapped[Faction] = relationship(back_populates="relationships")

    __table_args__ = (
        CheckConstraint(
            "(relation_type = 'attitude' AND character_id IS NULL AND npc_id IS NULL "
            "AND value IN ('friendly', 'neutral', 'wary', 'hostile')) OR "
            "(relation_type = 'membership' AND ((character_id IS NULL) <> (npc_id IS NULL)) "
            "AND value IN ('member', 'associate', 'former_member'))",
            name="faction_relationship_shape",
        ),
        CheckConstraint(
            "visibility IN ('player', 'dm_only')", name="faction_relationship_visibility"
        ),
        CheckConstraint("revision >= 0", name="faction_relationship_revision_nonnegative"),
        Index(
            "uq_faction_party_attitude",
            "faction_id",
            unique=True,
            postgresql_where=text("relation_type = 'attitude'"),
        ),
        Index(
            "uq_faction_character_membership",
            "faction_id",
            "character_id",
            unique=True,
            postgresql_where=text("relation_type = 'membership' AND character_id IS NOT NULL"),
        ),
        Index(
            "uq_faction_npc_membership",
            "faction_id",
            "npc_id",
            unique=True,
            postgresql_where=text("relation_type = 'membership' AND npc_id IS NOT NULL"),
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
    decision_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("decision_points.id", ondelete="SET NULL"), index=True
    )
    decision_option_key: Mapped[str | None] = mapped_column(String(80))
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
            "(decision_id IS NULL AND decision_option_key IS NULL) OR "
            "(decision_id IS NOT NULL AND decision_option_key IS NOT NULL)",
            name="turn_decision_choice_shape",
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


class DecisionSelection(TimestampMixin, Base):
    __tablename__ = "decision_selections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    decision_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("decision_points.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    option_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("decision_options.id", ondelete="RESTRICT"), nullable=False
    )
    turn_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("turns.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    actor_character_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL")
    )
    world_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaign_events.id", ondelete="RESTRICT"), nullable=False
    )

    __table_args__ = (
        CheckConstraint("world_revision > 0", name="decision_selection_world_revision_positive"),
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


class MemoryEmbeddingProfile(TimestampMixin, Base):
    __tablename__ = "memory_embedding_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_key: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    provider_kind: Mapped[str] = mapped_column(String(30), nullable=False)
    model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    model_revision: Mapped[str] = mapped_column(String(120), nullable=False)
    artifact_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    license_id: Mapped[str] = mapped_column(String(80), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    normalization: Mapped[str] = mapped_column(String(20), nullable=False)
    distance_metric: Mapped[str] = mapped_column(String(20), nullable=False, default="cosine")
    adapter_version: Mapped[str] = mapped_column(String(40), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "profile_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'",
            name="memory_profile_key_format",
        ),
        CheckConstraint(
            "provider_kind IN ('deterministic', 'local_onnx')",
            name="memory_profile_provider_kind",
        ),
        CheckConstraint("dimensions BETWEEN 1 AND 4096", name="memory_profile_dimensions"),
        CheckConstraint("normalization IN ('none', 'l2')", name="memory_profile_normalization"),
        CheckConstraint("distance_metric = 'cosine'", name="memory_profile_distance_metric"),
        CheckConstraint(
            "artifact_sha256 ~ '^[0-9a-f]{64}$'", name="memory_profile_artifact_sha256"
        ),
    )


class MemoryDocument(TimestampMixin, Base):
    __tablename__ = "memory_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    source_turn_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("turns.id", ondelete="RESTRICT"), index=True
    )
    source_event_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("campaign_events.id", ondelete="RESTRICT"), index=True
    )
    source_version: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    event_sequence_start: Mapped[int] = mapped_column(Integer, nullable=False)
    event_sequence_end: Mapped[int] = mapped_column(Integer, nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    chunker_version: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    source_world_revision: Mapped[int | None] = mapped_column(Integer)
    source_time_minutes: Mapped[int | None] = mapped_column(Integer)
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), index=True
    )
    npc_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("npcs.id", ondelete="RESTRICT"), index=True
    )
    character_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("characters.id", ondelete="RESTRICT"), index=True
    )
    quest_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("quests.id", ondelete="RESTRICT"), index=True
    )
    decision_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("decision_points.id", ondelete="RESTRICT"), index=True
    )
    faction_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("factions.id", ondelete="RESTRICT"), index=True
    )
    superseded_by_document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("memory_documents.id", ondelete="RESTRICT"), unique=True
    )

    __table_args__ = (
        CheckConstraint(
            "(source_kind = 'turn' AND source_turn_id IS NOT NULL AND source_event_id IS NULL) "
            "OR (source_kind = 'event' AND source_event_id IS NOT NULL AND source_turn_id IS NULL)",
            name="memory_document_source_shape",
        ),
        CheckConstraint("source_version > 0", name="memory_document_source_version_positive"),
        CheckConstraint("chunk_index >= 0", name="memory_document_chunk_index_nonnegative"),
        CheckConstraint(
            "event_sequence_start > 0 AND event_sequence_end >= event_sequence_start",
            name="memory_document_event_sequence_range",
        ),
        CheckConstraint("visibility = 'player'", name="memory_document_player_visible"),
        CheckConstraint(
            "char_length(content) BETWEEN 1 AND 6000", name="memory_document_content_length"
        ),
        CheckConstraint("content_sha256 ~ '^[0-9a-f]{64}$'", name="memory_document_content_sha256"),
        CheckConstraint("status IN ('active', 'superseded')", name="memory_document_status"),
        CheckConstraint(
            "(status = 'active' AND superseded_by_document_id IS NULL) OR "
            "(status = 'superseded' AND superseded_by_document_id IS NOT NULL)",
            name="memory_document_supersession_shape",
        ),
        CheckConstraint(
            "source_world_revision IS NULL OR source_world_revision >= 0",
            name="memory_document_world_revision_nonnegative",
        ),
        CheckConstraint(
            "source_time_minutes IS NULL OR source_time_minutes >= 0",
            name="memory_document_time_nonnegative",
        ),
        Index(
            "uq_memory_documents_turn_version_chunk",
            "campaign_id",
            "source_turn_id",
            "source_version",
            "chunk_index",
            unique=True,
            postgresql_where=text("source_kind = 'turn'"),
        ),
        Index(
            "uq_memory_documents_event_version_chunk",
            "campaign_id",
            "source_event_id",
            "source_version",
            "chunk_index",
            unique=True,
            postgresql_where=text("source_kind = 'event'"),
        ),
        Index(
            "ix_memory_documents_campaign_active_sequence",
            "campaign_id",
            "event_sequence_end",
            postgresql_where=text("status = 'active'"),
        ),
        Index(
            "ix_memory_documents_content_english",
            text("to_tsvector('english'::regconfig, content)"),
            postgresql_using="gin",
        ),
    )


class MemoryEmbedding(TimestampMixin, Base):
    __tablename__ = "memory_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_documents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_embedding_profiles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    document_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(), nullable=False)
    embedded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("document_id", "profile_id", name="uq_memory_embeddings_document_profile"),
        CheckConstraint(
            "document_sha256 ~ '^[0-9a-f]{64}$'", name="memory_embedding_document_sha256"
        ),
    )


class CampaignMemoryIndex(TimestampMixin, Base):
    __tablename__ = "campaign_memory_indexes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_embedding_profiles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="building")
    indexed_through_event_sequence: Mapped[int | None] = mapped_column(Integer)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error_code: Mapped[str | None] = mapped_column(String(80))
    last_error_detail: Mapped[str | None] = mapped_column(Text)
    quality_gate: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("campaign_id", "profile_id", name="uq_campaign_memory_index_profile"),
        CheckConstraint(
            "status IN ('building', 'ready', 'active', 'failed', 'retired')",
            name="campaign_memory_index_status",
        ),
        CheckConstraint(
            "indexed_through_event_sequence IS NULL OR indexed_through_event_sequence >= 0",
            name="campaign_memory_index_sequence_nonnegative",
        ),
        CheckConstraint("source_count >= 0", name="campaign_memory_index_source_count"),
        CheckConstraint(
            "(status = 'failed' AND last_error_code IS NOT NULL) OR "
            "(status <> 'failed' AND last_error_code IS NULL AND last_error_detail IS NULL)",
            name="campaign_memory_index_error_shape",
        ),
        CheckConstraint(
            "(status = 'active' AND activated_at IS NOT NULL AND quality_gate IS NOT NULL) OR "
            "(status <> 'active' AND activated_at IS NULL)",
            name="campaign_memory_index_activation_shape",
        ),
        Index(
            "uq_campaign_memory_indexes_one_active",
            "campaign_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )


class MemoryIndexJob(TimestampMixin, Base):
    __tablename__ = "memory_index_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_embedding_profiles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lease_owner: Mapped[str | None] = mapped_column(String(120))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(80))
    error_detail: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("document_id", "profile_id", name="uq_memory_index_jobs_document_profile"),
        CheckConstraint(
            "status IN ('pending', 'claimed', 'complete', 'failed')",
            name="memory_index_job_status",
        ),
        CheckConstraint("attempt_count >= 0", name="memory_index_job_attempt_count"),
        CheckConstraint(
            "(status = 'claimed' AND lease_owner IS NOT NULL AND lease_expires_at IS NOT NULL "
            "AND error_code IS NULL AND error_detail IS NULL) OR "
            "(status = 'failed' AND lease_owner IS NULL AND lease_expires_at IS NULL "
            "AND error_code IS NOT NULL) OR "
            "(status IN ('pending', 'complete') AND lease_owner IS NULL "
            "AND lease_expires_at IS NULL AND error_code IS NULL AND error_detail IS NULL)",
            name="memory_index_job_state_shape",
        ),
        Index("ix_memory_index_jobs_claim", "status", "next_attempt_at", "created_at"),
    )


class MemoryRetrieval(TimestampMixin, Base):
    __tablename__ = "memory_retrievals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    turn_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("turns.id", ondelete="SET NULL"), index=True
    )
    provider_call_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("provider_calls.id", ondelete="SET NULL"), index=True
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_embedding_profiles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ranking_policy: Mapped[str] = mapped_column(String(60), nullable=False)
    query_source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    filters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False)
    returned_count: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    context_budget_chars: Mapped[int] = mapped_column(Integer, nullable=False)
    truncated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(80))

    __table_args__ = (
        CheckConstraint(
            "query_source_sha256 ~ '^[0-9a-f]{64}$'",
            name="memory_retrieval_query_source_sha256",
        ),
        CheckConstraint(
            "requested_count BETWEEN 1 AND 50 AND returned_count BETWEEN 0 AND requested_count",
            name="memory_retrieval_count_bounds",
        ),
        CheckConstraint("latency_ms >= 0", name="memory_retrieval_latency_nonnegative"),
        CheckConstraint(
            "context_budget_chars BETWEEN 1 AND 24000", name="memory_retrieval_context_budget"
        ),
        CheckConstraint(
            "(status = 'succeeded' AND error_code IS NULL) OR "
            "(status = 'failed' AND error_code IS NOT NULL AND returned_count = 0)",
            name="memory_retrieval_result_shape",
        ),
    )


class MemoryRetrievalItem(TimestampMixin, Base):
    __tablename__ = "memory_retrieval_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retrieval_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_retrievals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_documents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    semantic_score: Mapped[float | None] = mapped_column(Float)
    lexical_score: Mapped[float | None] = mapped_column(Float)
    recency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    entity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    combined_score: Mapped[float] = mapped_column(Float, nullable=False)
    selected_chars: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("retrieval_id", "rank", name="uq_memory_retrieval_items_rank"),
        UniqueConstraint("retrieval_id", "document_id", name="uq_memory_retrieval_items_document"),
        CheckConstraint("rank BETWEEN 1 AND 50", name="memory_retrieval_item_rank"),
        CheckConstraint(
            "semantic_score IS NOT NULL OR lexical_score IS NOT NULL",
            name="memory_retrieval_item_candidate_score",
        ),
        CheckConstraint(
            "recency_score >= 0 AND entity_score >= 0 AND combined_score >= 0",
            name="memory_retrieval_item_score_nonnegative",
        ),
        CheckConstraint(
            "selected_chars BETWEEN 1 AND 6000", name="memory_retrieval_item_selected_chars"
        ),
    )


class MemorySummary(TimestampMixin, Base):
    __tablename__ = "memory_summaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    retrieval_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_retrievals.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_embedding_profiles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    source_window_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    input_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    audience: Mapped[str] = mapped_column(String(20), nullable=False, default="player")
    provider: Mapped[str] = mapped_column(String(60), nullable=False)
    model: Mapped[str | None] = mapped_column(String(160))
    prompt_version: Mapped[str] = mapped_column(String(60), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    content_sha256: Mapped[str | None] = mapped_column(String(64))
    source_count: Mapped[int] = mapped_column(Integer, nullable=False)
    event_sequence_start: Mapped[int] = mapped_column(Integer, nullable=False)
    event_sequence_end: Mapped[int] = mapped_column(Integer, nullable=False)
    replaces_summary_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("memory_summaries.id", ondelete="RESTRICT"), unique=True
    )
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    error_code: Mapped[str | None] = mapped_column(String(80))

    __table_args__ = (
        UniqueConstraint("retrieval_id", "attempt", name="uq_memory_summaries_retrieval_attempt"),
        CheckConstraint(
            "source_window_sha256 ~ '^[0-9a-f]{64}$'",
            name="memory_summary_source_window_sha256",
        ),
        CheckConstraint("input_sha256 ~ '^[0-9a-f]{64}$'", name="memory_summary_input_sha256"),
        CheckConstraint("audience = 'player'", name="memory_summary_player_visible"),
        CheckConstraint("attempt > 0", name="memory_summary_attempt_positive"),
        CheckConstraint("status IN ('succeeded', 'failed')", name="memory_summary_status"),
        CheckConstraint(
            "(status = 'succeeded' AND content IS NOT NULL "
            "AND char_length(content) BETWEEN 1 AND 3000 "
            "AND content_sha256 ~ '^[0-9a-f]{64}$' AND error_code IS NULL) OR "
            "(status = 'failed' AND content IS NULL AND content_sha256 IS NULL "
            "AND error_code IS NOT NULL AND replaces_summary_id IS NULL)",
            name="memory_summary_result_shape",
        ),
        CheckConstraint("source_count BETWEEN 1 AND 8", name="memory_summary_source_count"),
        CheckConstraint(
            "event_sequence_start > 0 AND event_sequence_end >= event_sequence_start",
            name="memory_summary_event_sequence_range",
        ),
        CheckConstraint("latency_ms >= 0", name="memory_summary_latency_nonnegative"),
        CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0", name="memory_summary_input_nonnegative"
        ),
        CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0", name="memory_summary_output_nonnegative"
        ),
    )


class MemorySummarySource(TimestampMixin, Base):
    __tablename__ = "memory_summary_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_summaries.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_documents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    selected_chars: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("summary_id", "document_id", name="uq_memory_summary_sources_document"),
        UniqueConstraint("summary_id", "position", name="uq_memory_summary_sources_position"),
        CheckConstraint("position BETWEEN 1 AND 8", name="memory_summary_source_position"),
        CheckConstraint(
            "selected_chars BETWEEN 1 AND 6000", name="memory_summary_source_selected_chars"
        ),
    )


class MemorySummaryUse(TimestampMixin, Base):
    __tablename__ = "memory_summary_uses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    retrieval_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_retrievals.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    summary_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("memory_summaries.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    turn_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("turns.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "stage IN ('interpretation', 'narration')", name="memory_summary_use_stage"
        ),
    )
