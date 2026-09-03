"""Add typed factions and bounded narrative time.

Revision ID: 0011_factions_time
Revises: 0010_quests_decisions
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0011_factions_time"
down_revision: str | None = "0010_quests_decisions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "campaigns",
        sa.Column("narrative_time_minutes", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_check_constraint(
        "campaign_narrative_time_nonnegative",
        "campaigns",
        "narrative_time_minutes >= 0",
    )

    op.create_table(
        "factions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("faction_key", sa.String(80), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_by_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("status IN ('active', 'inactive')", name="faction_status"),
        sa.CheckConstraint("visibility IN ('player', 'dm_only')", name="faction_visibility"),
        sa.CheckConstraint("revision >= 0", name="faction_revision_nonnegative"),
        sa.CheckConstraint(
            "faction_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="faction_key_format"
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["created_by_event_id"], ["campaign_events.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "faction_key", name="uq_factions_campaign_key"),
    )
    op.create_index(op.f("ix_factions_campaign_id"), "factions", ["campaign_id"])

    op.create_table(
        "faction_relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("faction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relation_type", sa.String(20), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("npc_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("value", sa.String(30), nullable=False),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_by_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(relation_type = 'attitude' AND character_id IS NULL AND npc_id IS NULL "
            "AND value IN ('friendly', 'neutral', 'wary', 'hostile')) OR "
            "(relation_type = 'membership' AND ((character_id IS NULL) <> (npc_id IS NULL)) "
            "AND value IN ('member', 'associate', 'former_member'))",
            name="faction_relationship_shape",
        ),
        sa.CheckConstraint(
            "visibility IN ('player', 'dm_only')", name="faction_relationship_visibility"
        ),
        sa.CheckConstraint("revision >= 0", name="faction_relationship_revision_nonnegative"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["faction_id"], ["factions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["npc_id"], ["npcs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["created_by_event_id"], ["campaign_events.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_faction_relationships_campaign_id"),
        "faction_relationships",
        ["campaign_id"],
    )
    op.create_index(
        op.f("ix_faction_relationships_faction_id"),
        "faction_relationships",
        ["faction_id"],
    )
    op.create_index(
        op.f("ix_faction_relationships_character_id"),
        "faction_relationships",
        ["character_id"],
    )
    op.create_index(
        op.f("ix_faction_relationships_npc_id"),
        "faction_relationships",
        ["npc_id"],
    )
    op.create_index(
        "uq_faction_party_attitude",
        "faction_relationships",
        ["faction_id"],
        unique=True,
        postgresql_where=sa.text("relation_type = 'attitude'"),
    )
    op.create_index(
        "uq_faction_character_membership",
        "faction_relationships",
        ["faction_id", "character_id"],
        unique=True,
        postgresql_where=sa.text("relation_type = 'membership' AND character_id IS NOT NULL"),
    )
    op.create_index(
        "uq_faction_npc_membership",
        "faction_relationships",
        ["faction_id", "npc_id"],
        unique=True,
        postgresql_where=sa.text("relation_type = 'membership' AND npc_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM factions)
               OR EXISTS (SELECT 1 FROM campaigns WHERE narrative_time_minutes <> 0) THEN
                RAISE EXCEPTION
                    'Cannot downgrade after M3.4 faction or narrative time data has been recorded';
            END IF;
        END;
        $$
        """
    )
    op.drop_table("faction_relationships")
    op.drop_table("factions")
    op.drop_constraint("campaign_narrative_time_nonnegative", "campaigns", type_="check")
    op.drop_column("campaigns", "narrative_time_minutes")
