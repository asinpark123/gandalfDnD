"""Add timestamps for safe recovery of interrupted turn stages.

Revision ID: 0007_turn_stage_recovery
Revises: 0006_turn_lifecycle
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_turn_stage_recovery"
down_revision: str | None = "0006_turn_lifecycle"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("turns", sa.Column("stage_started_at", sa.DateTime(timezone=True), nullable=True))
    op.execute(
        "UPDATE turns SET stage_started_at = now() "
        "WHERE status IN ('interpreting', 'resolving', 'narrating')"
    )
    op.create_check_constraint(
        "turn_stage_started_shape",
        "turns",
        "(status IN ('interpreting', 'resolving', 'narrating') AND "
        "stage_started_at IS NOT NULL) OR "
        "(status NOT IN ('interpreting', 'resolving', 'narrating') AND "
        "stage_started_at IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("turn_stage_started_shape", "turns", type_="check")
    op.drop_column("turns", "stage_started_at")
