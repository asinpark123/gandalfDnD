"""Add the PostgreSQL lexical index used by M4.3 hybrid retrieval.

Revision ID: 0014_memory_retrieval
Revises: 0013_memory_lifecycle
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0014_memory_retrieval"
down_revision: str | None = "0013_memory_lifecycle"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_memory_documents_content_english",
        "memory_documents",
        [sa.text("to_tsvector('english'::regconfig, content)")],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_memory_documents_content_english",
        table_name="memory_documents",
        postgresql_using="gin",
    )
