"""Add revisioned scenes, NPCs, and scene presence.

Revision ID: 0008_world_presence
Revises: 0007_turn_stage_recovery
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0008_world_presence"
down_revision: str | None = "0007_turn_stage_recovery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "campaigns",
        sa.Column("world_revision", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_check_constraint(
        "campaign_world_revision_nonnegative", "campaigns", "world_revision >= 0"
    )

    op.create_table(
        "scenes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), server_default="0", nullable=False),
        sa.Column("opened_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("closed_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("sequence > 0", name="scene_sequence_positive"),
        sa.CheckConstraint("status IN ('active', 'closed')", name="scene_status"),
        sa.CheckConstraint("revision >= 0", name="scene_revision_nonnegative"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["opened_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["closed_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "sequence", name="uq_scenes_campaign_sequence"),
    )
    op.create_index(op.f("ix_scenes_campaign_id"), "scenes", ["campaign_id"])
    op.create_index(op.f("ix_scenes_location_id"), "scenes", ["location_id"])
    op.create_index(
        "uq_scenes_one_active_per_campaign",
        "scenes",
        ["campaign_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "npcs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("public_description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), server_default="0", nullable=False),
        sa.Column("introduced_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("status IN ('active', 'inactive')", name="npc_status"),
        sa.CheckConstraint("visibility IN ('player', 'dm_only')", name="npc_visibility"),
        sa.CheckConstraint("revision >= 0", name="npc_revision_nonnegative"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["introduced_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_npcs_campaign_id"), "npcs", ["campaign_id"])

    op.create_table(
        "scene_npc_presences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scene_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("npc_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), server_default="0", nullable=False),
        sa.Column("arrived_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("departed_by_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("status IN ('present', 'departed')", name="scene_npc_presence_status"),
        sa.CheckConstraint("revision >= 0", name="scene_npc_presence_revision_nonnegative"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["npc_id"], ["npcs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["arrived_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["departed_by_event_id"], ["campaign_events.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_scene_npc_presences_campaign_id"), "scene_npc_presences", ["campaign_id"]
    )
    op.create_index(op.f("ix_scene_npc_presences_scene_id"), "scene_npc_presences", ["scene_id"])
    op.create_index(op.f("ix_scene_npc_presences_npc_id"), "scene_npc_presences", ["npc_id"])
    op.create_index(
        "uq_scene_npc_one_present_scene",
        "scene_npc_presences",
        ["scene_id", "npc_id"],
        unique=True,
        postgresql_where=sa.text("status = 'present'"),
    )
    op.create_index(
        "uq_scene_npc_one_current_presence",
        "scene_npc_presences",
        ["npc_id"],
        unique=True,
        postgresql_where=sa.text("status = 'present'"),
    )

    op.add_column("turns", sa.Column("target_npc_id", postgresql.UUID(as_uuid=True)))
    op.add_column("turns", sa.Column("world_revision_before", sa.Integer()))
    op.add_column("turns", sa.Column("world_revision_after", sa.Integer()))
    op.create_foreign_key(
        "fk_turns_target_npc_id_npcs",
        "turns",
        "npcs",
        ["target_npc_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_turns_target_npc_id"), "turns", ["target_npc_id"])
    op.create_check_constraint(
        "turn_world_revision_before_nonnegative",
        "turns",
        "world_revision_before IS NULL OR world_revision_before >= 0",
    )
    op.create_check_constraint(
        "turn_world_revision_after_nonnegative",
        "turns",
        "world_revision_after IS NULL OR world_revision_after >= 0",
    )

    op.execute(
        """
        INSERT INTO scenes (
            id, campaign_id, location_id, sequence, title, summary, status, revision
        )
        SELECT md5(c.id::text || 'm3.1-scene')::uuid,
               c.id, l.id, 1, l.name, l.description, 'active', 0
        FROM campaigns c
        JOIN locations l ON l.campaign_id = c.id AND l.is_current
        WHERE NOT EXISTS (SELECT 1 FROM scenes s WHERE s.campaign_id = c.id)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM npcs) OR
               EXISTS (SELECT 1 FROM scene_npc_presences) OR
               EXISTS (SELECT 1 FROM turns WHERE target_npc_id IS NOT NULL) OR
               EXISTS (SELECT 1 FROM campaigns WHERE world_revision <> 0) OR
               EXISTS (
                   SELECT 1 FROM scenes s JOIN locations l ON l.id = s.location_id
                   WHERE s.sequence <> 1 OR s.status <> 'active' OR s.revision <> 0
                      OR s.title <> l.name
                      OR coalesce(s.summary, '') <> coalesce(l.description, '')
               ) THEN
                RAISE EXCEPTION 'Cannot downgrade after M3 world data has been recorded';
            END IF;
        END;
        $$
        """
    )
    op.drop_constraint("turn_world_revision_after_nonnegative", "turns", type_="check")
    op.drop_constraint("turn_world_revision_before_nonnegative", "turns", type_="check")
    op.drop_index(op.f("ix_turns_target_npc_id"), table_name="turns")
    op.drop_constraint("fk_turns_target_npc_id_npcs", "turns", type_="foreignkey")
    op.drop_column("turns", "world_revision_after")
    op.drop_column("turns", "world_revision_before")
    op.drop_column("turns", "target_npc_id")
    op.drop_index("uq_scene_npc_one_current_presence", table_name="scene_npc_presences")
    op.drop_index("uq_scene_npc_one_present_scene", table_name="scene_npc_presences")
    op.drop_index(op.f("ix_scene_npc_presences_npc_id"), table_name="scene_npc_presences")
    op.drop_index(op.f("ix_scene_npc_presences_scene_id"), table_name="scene_npc_presences")
    op.drop_index(op.f("ix_scene_npc_presences_campaign_id"), table_name="scene_npc_presences")
    op.drop_table("scene_npc_presences")
    op.drop_index(op.f("ix_npcs_campaign_id"), table_name="npcs")
    op.drop_table("npcs")
    op.drop_index("uq_scenes_one_active_per_campaign", table_name="scenes")
    op.drop_index(op.f("ix_scenes_location_id"), table_name="scenes")
    op.drop_index(op.f("ix_scenes_campaign_id"), table_name="scenes")
    op.drop_table("scenes")
    op.drop_constraint("campaign_world_revision_nonnegative", "campaigns", type_="check")
    op.drop_column("campaigns", "world_revision")
