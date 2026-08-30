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
            "kind IN ('foundation', 'character_creation')", name="ruleset_data_catalog_kind"
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

    ruleset_release: Mapped[RulesetRelease] = relationship(back_populates="campaigns")
    characters: Mapped[list["Character"]] = relationship(back_populates="campaign")
    locations: Mapped[list["Location"]] = relationship(back_populates="campaign")

    __table_args__ = (CheckConstraint("status IN ('active', 'archived')", name="campaign_status"),)


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


class Character(TimestampMixin, Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, unique=True
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

    campaign: Mapped[Campaign] = relationship(back_populates="characters")
    grants: Mapped[list["CharacterGrant"]] = relationship(back_populates="character")

    __table_args__ = (
        CheckConstraint(
            "creation_status IN ('legacy', 'draft', 'finalized')", name="character_creation_status"
        ),
        CheckConstraint("revision >= 0", name="character_revision_nonnegative"),
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
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    player_action: Mapped[str] = mapped_column(Text, nullable=False)
    dm_narration: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str | None] = mapped_column(String(80))
    structured_output: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint("campaign_id", "sequence", name="uq_turns_campaign_sequence"),
        CheckConstraint("sequence > 0", name="turn_sequence_positive"),
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
