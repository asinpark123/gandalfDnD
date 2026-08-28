"""Create the Phase 0 campaign state and audit log.

Revision ID: 0001_phase_0
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_phase_0"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("ruleset", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("status IN ('active', 'archived')", name="campaign_status"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "name", name="uq_locations_campaign_name"),
    )
    op.create_index(op.f("ix_locations_campaign_id"), "locations", ["campaign_id"])
    op.create_index(
        "uq_locations_one_current_per_campaign",
        "locations",
        ["campaign_id"],
        unique=True,
        postgresql_where=sa.text("is_current"),
    )
    op.create_table(
        "characters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("max_hp", sa.Integer(), nullable=False),
        sa.Column("hp", sa.Integer(), nullable=False),
        sa.Column(
            "inventory",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("hp >= 0 AND hp <= max_hp", name="character_hp_bounds"),
        sa.CheckConstraint("max_hp > 0", name="character_max_hp_positive"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id"),
    )
    op.create_table(
        "turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("player_action", sa.Text(), nullable=False),
        sa.Column("dm_narration", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=True),
        sa.Column("structured_output", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("sequence > 0", name="turn_sequence_positive"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "sequence", name="uq_turns_campaign_sequence"),
    )
    op.create_index(op.f("ix_turns_campaign_id"), "turns", ["campaign_id"])
    op.create_table(
        "campaign_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("turn_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("visibility", sa.String(length=20), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("sequence > 0", name="event_sequence_positive"),
        sa.CheckConstraint("visibility IN ('player', 'dm_only')", name="campaign_event_visibility"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["turn_id"], ["turns.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "sequence", name="uq_events_campaign_sequence"),
    )
    op.create_index(op.f("ix_campaign_events_campaign_id"), "campaign_events", ["campaign_id"])
    op.create_index(op.f("ix_campaign_events_turn_id"), "campaign_events", ["turn_id"])
    op.create_table(
        "dice_rolls",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("turn_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notation", sa.String(length=20), nullable=False),
        sa.Column("rolls", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("modifier", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(length=160), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["turn_id"], ["turns.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dice_rolls_campaign_id"), "dice_rolls", ["campaign_id"])
    op.create_index(op.f("ix_dice_rolls_turn_id"), "dice_rolls", ["turn_id"])

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_prevent_event_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'campaign_events is append-only';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER campaign_events_append_only
        BEFORE UPDATE OR DELETE ON campaign_events
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_event_mutation()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS campaign_events_append_only ON campaign_events")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_prevent_event_mutation()")
    op.drop_index(op.f("ix_dice_rolls_turn_id"), table_name="dice_rolls")
    op.drop_index(op.f("ix_dice_rolls_campaign_id"), table_name="dice_rolls")
    op.drop_table("dice_rolls")
    op.drop_index(op.f("ix_campaign_events_turn_id"), table_name="campaign_events")
    op.drop_index(op.f("ix_campaign_events_campaign_id"), table_name="campaign_events")
    op.drop_table("campaign_events")
    op.drop_index(op.f("ix_turns_campaign_id"), table_name="turns")
    op.drop_table("turns")
    op.drop_table("characters")
    op.drop_index("uq_locations_one_current_per_campaign", table_name="locations")
    op.drop_index(op.f("ix_locations_campaign_id"), table_name="locations")
    op.drop_table("locations")
    op.drop_table("campaigns")
