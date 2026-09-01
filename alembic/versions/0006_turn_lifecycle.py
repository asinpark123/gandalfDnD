"""Add resumable two-stage turn lifecycle storage.

Revision ID: 0006_turn_lifecycle
Revises: 0005_check_save_resolution
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006_turn_lifecycle"
down_revision: str | None = "0005_check_save_resolution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("turns", sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column(
        "turns",
        sa.Column(
            "workflow_version", sa.String(40), server_default="legacy-turn-1.0.0", nullable=False
        ),
    )
    op.add_column(
        "turns", sa.Column("status", sa.String(30), server_default="completed", nullable=False)
    )
    op.add_column("turns", sa.Column("failure_stage", sa.String(30), nullable=True))
    op.add_column("turns", sa.Column("error_code", sa.String(80), nullable=True))
    op.add_column("turns", sa.Column("error_detail", sa.Text(), nullable=True))
    op.add_column(
        "turns", sa.Column("resumable", sa.Boolean(), server_default=sa.false(), nullable=False)
    )
    op.add_column("turns", sa.Column("resume_status", sa.String(30), nullable=True))
    op.add_column("turns", sa.Column("intent_output", postgresql.JSONB(), nullable=True))
    op.add_column("turns", sa.Column("resolution_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("turns", sa.Column("state_revision_before", sa.Integer(), nullable=True))
    op.add_column("turns", sa.Column("state_revision_after", sa.Integer(), nullable=True))
    op.add_column("turns", sa.Column("interpretation_prompt_version", sa.String(60), nullable=True))
    op.add_column("turns", sa.Column("narration_prompt_version", sa.String(60), nullable=True))
    op.add_column("turns", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE turns SET command_id = id, completed_at = created_at")
    op.alter_column("turns", "command_id", nullable=False)
    op.alter_column("turns", "dm_narration", existing_type=sa.Text(), nullable=True)
    op.alter_column("turns", "provider", existing_type=sa.String(40), nullable=True)
    op.alter_column("turns", "structured_output", existing_type=postgresql.JSONB(), nullable=True)
    op.create_unique_constraint("uq_turns_campaign_command", "turns", ["campaign_id", "command_id"])
    op.create_unique_constraint("uq_turns_resolution_id", "turns", ["resolution_id"])
    op.create_foreign_key(
        "fk_turns_resolution_id_rule_resolutions",
        "turns",
        "rule_resolutions",
        ["resolution_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "turn_workflow_version",
        "turns",
        "workflow_version IN ('legacy-turn-1.0.0', 'two-stage-turn-1.0.0')",
    )
    op.create_check_constraint(
        "turn_status",
        "turns",
        "status IN ('received', 'interpreting', 'intent_ready', 'resolving', 'resolved', "
        "'narrating', 'completed', 'failed', 'cancelled')",
    )
    op.create_check_constraint(
        "turn_resume_status",
        "turns",
        "resume_status IS NULL OR resume_status IN ('received', 'intent_ready', 'resolved')",
    )
    op.create_check_constraint(
        "turn_state_revision_before_nonnegative",
        "turns",
        "state_revision_before IS NULL OR state_revision_before >= 0",
    )
    op.create_check_constraint(
        "turn_state_revision_after_nonnegative",
        "turns",
        "state_revision_after IS NULL OR state_revision_after >= 0",
    )
    op.create_check_constraint(
        "turn_failure_shape",
        "turns",
        "(status = 'failed' AND failure_stage IS NOT NULL AND error_code IS NOT NULL) OR "
        "(status <> 'failed' AND failure_stage IS NULL AND error_code IS NULL AND "
        "error_detail IS NULL AND resumable = false AND resume_status IS NULL)",
    )
    op.create_check_constraint(
        "turn_resumable_shape",
        "turns",
        "status <> 'failed' OR (resumable = (resume_status IS NOT NULL))",
    )
    op.create_check_constraint(
        "turn_completed_shape",
        "turns",
        "status <> 'completed' OR (dm_narration IS NOT NULL AND "
        "structured_output IS NOT NULL AND completed_at IS NOT NULL)",
    )
    op.create_index(
        "uq_turns_one_active_per_campaign",
        "turns",
        ["campaign_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('received', 'interpreting', 'intent_ready', 'resolving', "
            "'resolved', 'narrating') OR (status = 'failed' AND resumable)"
        ),
    )

    op.create_table(
        "provider_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("turn_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage", sa.String(30), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("model", sa.String(80), nullable=True),
        sa.Column("prompt_version", sa.String(60), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("structured_output", postgresql.JSONB(), nullable=True),
        sa.Column("error_code", sa.String(80), nullable=True),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("stage IN ('interpretation', 'narration')", name="provider_call_stage"),
        sa.CheckConstraint("attempt > 0", name="provider_call_attempt_positive"),
        sa.CheckConstraint("status IN ('succeeded', 'failed')", name="provider_call_status"),
        sa.CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0", name="provider_call_latency_nonnegative"
        ),
        sa.CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0", name="provider_call_input_nonnegative"
        ),
        sa.CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0", name="provider_call_output_nonnegative"
        ),
        sa.CheckConstraint(
            "(status = 'succeeded' AND structured_output IS NOT NULL AND "
            "error_code IS NULL AND error_detail IS NULL) OR "
            "(status = 'failed' AND structured_output IS NULL AND error_code IS NOT NULL)",
            name="provider_call_result_shape",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["turn_id"], ["turns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("turn_id", "stage", "attempt", name="uq_provider_calls_attempt"),
    )
    op.create_index(op.f("ix_provider_calls_campaign_id"), "provider_calls", ["campaign_id"])
    op.create_index(op.f("ix_provider_calls_turn_id"), "provider_calls", ["turn_id"])
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_prevent_provider_call_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'provider_calls is immutable';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER provider_calls_immutable
        BEFORE UPDATE OR DELETE ON provider_calls
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_provider_call_mutation()
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM provider_calls) OR
               EXISTS (SELECT 1 FROM turns WHERE workflow_version <> 'legacy-turn-1.0.0') THEN
                RAISE EXCEPTION 'Cannot downgrade after two-stage turns have been recorded';
            END IF;
        END;
        $$
        """
    )
    op.execute("DROP TRIGGER provider_calls_immutable ON provider_calls")
    op.execute("DROP FUNCTION gandalfdnd_prevent_provider_call_mutation()")
    op.drop_index(op.f("ix_provider_calls_turn_id"), table_name="provider_calls")
    op.drop_index(op.f("ix_provider_calls_campaign_id"), table_name="provider_calls")
    op.drop_table("provider_calls")
    op.drop_index("uq_turns_one_active_per_campaign", table_name="turns")
    for name in (
        "turn_completed_shape",
        "turn_resumable_shape",
        "turn_failure_shape",
        "turn_state_revision_after_nonnegative",
        "turn_state_revision_before_nonnegative",
        "turn_resume_status",
        "turn_status",
        "turn_workflow_version",
    ):
        op.drop_constraint(name, "turns", type_="check")
    op.drop_constraint("fk_turns_resolution_id_rule_resolutions", "turns", type_="foreignkey")
    op.drop_constraint("uq_turns_resolution_id", "turns", type_="unique")
    op.drop_constraint("uq_turns_campaign_command", "turns", type_="unique")
    op.alter_column("turns", "structured_output", existing_type=postgresql.JSONB(), nullable=False)
    op.alter_column("turns", "provider", existing_type=sa.String(40), nullable=False)
    op.alter_column("turns", "dm_narration", existing_type=sa.Text(), nullable=False)
    for column in (
        "completed_at",
        "narration_prompt_version",
        "interpretation_prompt_version",
        "state_revision_after",
        "state_revision_before",
        "resolution_id",
        "intent_output",
        "resume_status",
        "resumable",
        "error_detail",
        "error_code",
        "failure_stage",
        "status",
        "workflow_version",
        "command_id",
    ):
        op.drop_column("turns", column)
