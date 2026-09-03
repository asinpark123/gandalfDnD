"""Add durable quests, objectives, and branching decisions.

Revision ID: 0010_quests_decisions
Revises: 0009_world_facts
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0010_quests_decisions"
down_revision: str | None = "0009_world_facts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _event_foreign_key(name: str) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint([name], ["campaign_events.id"], ondelete="RESTRICT")


def upgrade() -> None:
    op.create_table(
        "quests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quest_key", sa.String(80), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_by_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transitioned_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'failed', 'abandoned')", name="quest_status"
        ),
        sa.CheckConstraint("visibility IN ('player', 'dm_only')", name="quest_visibility"),
        sa.CheckConstraint("revision >= 0", name="quest_revision_nonnegative"),
        sa.CheckConstraint("quest_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="quest_key_format"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        _event_foreign_key("created_by_event_id"),
        sa.ForeignKeyConstraint(
            ["transitioned_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "quest_key", name="uq_quests_campaign_key"),
    )
    op.create_index(op.f("ix_quests_campaign_id"), "quests", ["campaign_id"])

    op.create_table(
        "quest_objectives",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quest_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("objective_key", sa.String(80), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_by_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transitioned_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'completed', 'failed', 'skipped')",
            name="quest_objective_status",
        ),
        sa.CheckConstraint("position BETWEEN 1 AND 10", name="quest_objective_position"),
        sa.CheckConstraint("revision >= 0", name="quest_objective_revision_nonnegative"),
        sa.CheckConstraint(
            "objective_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="quest_objective_key_format"
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quest_id"], ["quests.id"], ondelete="CASCADE"),
        _event_foreign_key("created_by_event_id"),
        sa.ForeignKeyConstraint(
            ["transitioned_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quest_id", "objective_key", name="uq_objectives_quest_key"),
        sa.UniqueConstraint("quest_id", "position", name="uq_objectives_quest_position"),
    )
    op.create_index(op.f("ix_quest_objectives_campaign_id"), "quest_objectives", ["campaign_id"])
    op.create_index(op.f("ix_quest_objectives_quest_id"), "quest_objectives", ["quest_id"])

    op.create_table(
        "decision_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_key", sa.String(80), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("selected_option_key", sa.String(80), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_by_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("selected_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("status IN ('open', 'selected')", name="decision_point_status"),
        sa.CheckConstraint("visibility IN ('player', 'dm_only')", name="decision_point_visibility"),
        sa.CheckConstraint("revision >= 0", name="decision_point_revision_nonnegative"),
        sa.CheckConstraint(
            "decision_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="decision_point_key_format"
        ),
        sa.CheckConstraint(
            "(status = 'open' AND selected_option_key IS NULL) OR "
            "(status = 'selected' AND selected_option_key IS NOT NULL)",
            name="decision_point_selection_shape",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        _event_foreign_key("created_by_event_id"),
        sa.ForeignKeyConstraint(
            ["selected_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "decision_key", name="uq_decisions_campaign_key"),
    )
    op.create_index(op.f("ix_decision_points_campaign_id"), "decision_points", ["campaign_id"])

    op.create_table(
        "decision_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("option_key", sa.String(80), nullable=False),
        sa.Column("label", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("consequences", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("position BETWEEN 1 AND 4", name="decision_option_position"),
        sa.CheckConstraint(
            "option_key ~ '^[a-z0-9][a-z0-9._-]{0,79}$'", name="decision_option_key_format"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(consequences) = 'array' AND jsonb_array_length(consequences) <= 10",
            name="decision_option_consequences_shape",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["decision_id"], ["decision_points.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("decision_id", "option_key", name="uq_decision_options_key"),
        sa.UniqueConstraint("decision_id", "position", name="uq_decision_options_position"),
    )
    op.create_index(op.f("ix_decision_options_campaign_id"), "decision_options", ["campaign_id"])
    op.create_index(op.f("ix_decision_options_decision_id"), "decision_options", ["decision_id"])

    op.add_column("turns", sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("turns", sa.Column("decision_option_key", sa.String(80), nullable=True))
    op.create_foreign_key(
        "turns_decision_id_fkey",
        "turns",
        "decision_points",
        ["decision_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_turns_decision_id"), "turns", ["decision_id"])
    op.create_check_constraint(
        "turn_decision_choice_shape",
        "turns",
        "(decision_id IS NULL AND decision_option_key IS NULL) OR "
        "(decision_id IS NOT NULL AND decision_option_key IS NOT NULL)",
    )

    op.create_table(
        "decision_selections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("option_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("turn_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_character_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("world_revision", sa.Integer(), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("world_revision > 0", name="decision_selection_world_revision_positive"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["decision_id"], ["decision_points.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["option_id"], ["decision_options.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["turn_id"], ["turns.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["actor_character_id"], ["characters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["event_id"], ["campaign_events.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("decision_id"),
        sa.UniqueConstraint("turn_id"),
    )
    op.create_index(
        op.f("ix_decision_selections_campaign_id"), "decision_selections", ["campaign_id"]
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM quests) OR EXISTS (SELECT 1 FROM decision_points)
               OR EXISTS (SELECT 1 FROM turns WHERE decision_id IS NOT NULL) THEN
                RAISE EXCEPTION
                    'Cannot downgrade after M3.3 quest or decision data has been recorded';
            END IF;
        END;
        $$
        """
    )
    op.drop_table("decision_selections")
    op.drop_constraint("turn_decision_choice_shape", "turns", type_="check")
    op.drop_index(op.f("ix_turns_decision_id"), table_name="turns")
    op.drop_constraint("turns_decision_id_fkey", "turns", type_="foreignkey")
    op.drop_column("turns", "decision_option_key")
    op.drop_column("turns", "decision_id")
    op.drop_table("decision_options")
    op.drop_table("decision_points")
    op.drop_table("quest_objectives")
    op.drop_table("quests")
