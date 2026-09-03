"""Add typed narrative world facts and reveal history.

Revision ID: 0009_world_facts
Revises: 0008_world_presence
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0009_world_facts"
down_revision: str | None = "0008_world_presence"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "world_facts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_npc_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("fact_type", sa.String(30), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("supersedes_fact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("superseded_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revealed_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "fact_type IN ('npc_attitude', 'relationship_note', 'promise', 'discovery', 'clue')",
            name="world_fact_type",
        ),
        sa.CheckConstraint("status IN ('current', 'superseded')", name="world_fact_status"),
        sa.CheckConstraint("visibility IN ('player', 'dm_only')", name="world_fact_visibility"),
        sa.CheckConstraint("revision >= 0", name="world_fact_revision_nonnegative"),
        sa.CheckConstraint("char_length(value) BETWEEN 1 AND 2000", name="world_fact_value_length"),
        sa.CheckConstraint(
            "fact_type NOT IN ('npc_attitude', 'relationship_note', 'promise') "
            "OR subject_npc_id IS NOT NULL",
            name="world_fact_npc_subject_required",
        ),
        sa.CheckConstraint(
            "fact_type <> 'npc_attitude' OR value IN ('friendly', 'neutral', 'wary', 'hostile')",
            name="world_fact_attitude_value",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_npc_id"], ["npcs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["supersedes_fact_id"], ["world_facts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["created_by_event_id"], ["campaign_events.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["superseded_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["revealed_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("supersedes_fact_id", name="uq_world_facts_supersedes_once"),
    )
    op.create_index(op.f("ix_world_facts_campaign_id"), "world_facts", ["campaign_id"])
    op.create_index(op.f("ix_world_facts_subject_npc_id"), "world_facts", ["subject_npc_id"])
    op.create_index(
        "ix_world_facts_current_campaign",
        "world_facts",
        ["campaign_id", "status", "visibility"],
    )
    op.create_index(
        "uq_world_facts_current_npc_attitude",
        "world_facts",
        ["campaign_id", "subject_npc_id"],
        unique=True,
        postgresql_where=sa.text("status = 'current' AND fact_type = 'npc_attitude'"),
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM world_facts) THEN
                RAISE EXCEPTION 'Cannot downgrade after M3.2 world facts have been recorded';
            END IF;
        END;
        $$
        """
    )
    op.drop_index("uq_world_facts_current_npc_attitude", table_name="world_facts")
    op.drop_index("ix_world_facts_current_campaign", table_name="world_facts")
    op.drop_index(op.f("ix_world_facts_subject_npc_id"), table_name="world_facts")
    op.drop_index(op.f("ix_world_facts_campaign_id"), table_name="world_facts")
    op.drop_table("world_facts")
