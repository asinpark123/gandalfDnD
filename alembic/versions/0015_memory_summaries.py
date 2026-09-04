"""Add append-only source-cited memory summaries.

Revision ID: 0015_memory_summaries
Revises: 0014_memory_retrieval
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0015_memory_summaries"
down_revision: str | None = "0014_memory_retrieval"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "memory_summaries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("retrieval_id", sa.UUID(), nullable=False),
        sa.Column("profile_id", sa.UUID(), nullable=False),
        sa.Column("source_window_sha256", sa.String(length=64), nullable=False),
        sa.Column("input_sha256", sa.String(length=64), nullable=False),
        sa.Column("audience", sa.String(length=20), nullable=False),
        sa.Column("provider", sa.String(length=60), nullable=False),
        sa.Column("model", sa.String(length=160), nullable=True),
        sa.Column("prompt_version", sa.String(length=60), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_sha256", sa.String(length=64), nullable=True),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("event_sequence_start", sa.Integer(), nullable=False),
        sa.Column("event_sequence_end", sa.Integer(), nullable=False),
        sa.Column("replaces_summary_id", sa.UUID(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("attempt > 0", name="memory_summary_attempt_positive"),
        sa.CheckConstraint("audience = 'player'", name="memory_summary_player_visible"),
        sa.CheckConstraint(
            "event_sequence_start > 0 AND event_sequence_end >= event_sequence_start",
            name="memory_summary_event_sequence_range",
        ),
        sa.CheckConstraint("input_sha256 ~ '^[0-9a-f]{64}$'", name="memory_summary_input_sha256"),
        sa.CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0", name="memory_summary_input_nonnegative"
        ),
        sa.CheckConstraint("latency_ms >= 0", name="memory_summary_latency_nonnegative"),
        sa.CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0", name="memory_summary_output_nonnegative"
        ),
        sa.CheckConstraint(
            "(status = 'succeeded' AND content IS NOT NULL "
            "AND char_length(content) BETWEEN 1 AND 3000 "
            "AND content_sha256 ~ '^[0-9a-f]{64}$' AND error_code IS NULL) OR "
            "(status = 'failed' AND content IS NULL AND content_sha256 IS NULL "
            "AND error_code IS NOT NULL AND replaces_summary_id IS NULL)",
            name="memory_summary_result_shape",
        ),
        sa.CheckConstraint("source_count BETWEEN 1 AND 8", name="memory_summary_source_count"),
        sa.CheckConstraint(
            "source_window_sha256 ~ '^[0-9a-f]{64}$'",
            name="memory_summary_source_window_sha256",
        ),
        sa.CheckConstraint("status IN ('succeeded', 'failed')", name="memory_summary_status"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["profile_id"], ["memory_embedding_profiles.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["replaces_summary_id"], ["memory_summaries.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["retrieval_id"], ["memory_retrievals.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("replaces_summary_id"),
        sa.UniqueConstraint(
            "retrieval_id", "attempt", name="uq_memory_summaries_retrieval_attempt"
        ),
    )
    for column in ("campaign_id", "profile_id", "retrieval_id", "source_window_sha256"):
        op.create_index(
            op.f(f"ix_memory_summaries_{column}"),
            "memory_summaries",
            [column],
            unique=False,
        )
    op.create_table(
        "memory_summary_sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("summary_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("selected_chars", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("position BETWEEN 1 AND 8", name="memory_summary_source_position"),
        sa.CheckConstraint(
            "selected_chars BETWEEN 1 AND 6000", name="memory_summary_source_selected_chars"
        ),
        sa.ForeignKeyConstraint(["document_id"], ["memory_documents.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["summary_id"], ["memory_summaries.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("summary_id", "document_id", name="uq_memory_summary_sources_document"),
        sa.UniqueConstraint("summary_id", "position", name="uq_memory_summary_sources_position"),
    )
    op.create_index(
        op.f("ix_memory_summary_sources_document_id"),
        "memory_summary_sources",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_summary_sources_summary_id"),
        "memory_summary_sources",
        ["summary_id"],
        unique=False,
    )
    op.create_table(
        "memory_summary_uses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("retrieval_id", sa.UUID(), nullable=False),
        sa.Column("summary_id", sa.UUID(), nullable=False),
        sa.Column("turn_id", sa.UUID(), nullable=False),
        sa.Column("stage", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "stage IN ('interpretation', 'narration')", name="memory_summary_use_stage"
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["retrieval_id"], ["memory_retrievals.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["summary_id"], ["memory_summaries.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["turn_id"], ["turns.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("retrieval_id"),
    )
    for column in ("campaign_id", "summary_id", "turn_id"):
        op.create_index(
            op.f(f"ix_memory_summary_uses_{column}"),
            "memory_summary_uses",
            [column],
            unique=False,
        )

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_validate_memory_summary_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM memory_retrievals retrieval
                WHERE retrieval.id = NEW.retrieval_id
                  AND retrieval.campaign_id = NEW.campaign_id
                  AND retrieval.profile_id = NEW.profile_id
                  AND retrieval.status = 'succeeded'
            ) THEN
                RAISE EXCEPTION
                    'memory summary retrieval must be successful in its campaign and profile';
            END IF;
            IF NEW.replaces_summary_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM memory_summaries previous
                WHERE previous.id = NEW.replaces_summary_id
                  AND previous.campaign_id = NEW.campaign_id
                  AND previous.source_window_sha256 = NEW.source_window_sha256
                  AND previous.status = 'succeeded'
            ) THEN
                RAISE EXCEPTION 'replacement memory summary must cite a successful matching window';
            END IF;
            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER memory_summaries_scope
        BEFORE INSERT ON memory_summaries
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_memory_summary_scope();

        CREATE FUNCTION gandalfdnd_validate_memory_summary_source_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM memory_summaries summary
                JOIN memory_documents document
                  ON document.id = NEW.document_id
                 AND document.campaign_id = summary.campaign_id
                 AND document.visibility = 'player'
                JOIN memory_retrieval_items item
                  ON item.retrieval_id = summary.retrieval_id
                 AND item.document_id = document.id
                WHERE summary.id = NEW.summary_id
                  AND summary.status = 'succeeded'
            ) THEN
                RAISE EXCEPTION 'memory summary source must be a player-visible retrieved document';
            END IF;
            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER memory_summary_sources_scope
        BEFORE INSERT ON memory_summary_sources
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_memory_summary_source_scope();

        CREATE FUNCTION gandalfdnd_validate_memory_summary_use_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM memory_summaries summary
                JOIN memory_retrievals retrieval
                  ON retrieval.id = NEW.retrieval_id
                 AND retrieval.campaign_id = summary.campaign_id
                 AND retrieval.profile_id = summary.profile_id
                 AND retrieval.status = 'succeeded'
                JOIN turns turn
                  ON turn.id = NEW.turn_id
                 AND turn.campaign_id = summary.campaign_id
                WHERE summary.id = NEW.summary_id
                  AND summary.campaign_id = NEW.campaign_id
                  AND summary.status = 'succeeded'
                  AND retrieval.turn_id = NEW.turn_id
            ) THEN
                RAISE EXCEPTION 'memory summary use must match its campaign, turn, and retrieval';
            END IF;
            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER memory_summary_uses_scope
        BEFORE INSERT ON memory_summary_uses
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_memory_summary_use_scope();

        CREATE FUNCTION gandalfdnd_validate_memory_summary_coverage()
        RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE
            target_summary_id uuid;
            expected_count integer;
            actual_count integer;
            summary_status text;
        BEGIN
            IF TG_TABLE_NAME = 'memory_summaries' THEN
                target_summary_id := NEW.id;
            ELSE
                target_summary_id := NEW.summary_id;
            END IF;
            SELECT status, source_count INTO summary_status, expected_count
            FROM memory_summaries WHERE id = target_summary_id;
            IF summary_status = 'succeeded' THEN
                SELECT count(*) INTO actual_count
                FROM memory_summary_sources WHERE summary_id = target_summary_id;
                IF actual_count IS DISTINCT FROM expected_count THEN
                    RAISE EXCEPTION 'memory summary source coverage mismatch: expected %, found %',
                        expected_count, actual_count;
                END IF;
            END IF;
            RETURN NULL;
        END;
        $$;

        CREATE CONSTRAINT TRIGGER memory_summaries_coverage
        AFTER INSERT ON memory_summaries
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_memory_summary_coverage();

        CREATE CONSTRAINT TRIGGER memory_summary_sources_coverage
        AFTER INSERT ON memory_summary_sources
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_memory_summary_coverage();
        """
    )
    for table in ("memory_summaries", "memory_summary_sources", "memory_summary_uses"):
        op.execute(
            f"""
            CREATE TRIGGER {table}_immutable
            BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_memory_audit_mutation()
            """
        )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM memory_summaries)
               OR EXISTS (SELECT 1 FROM memory_summary_sources)
               OR EXISTS (SELECT 1 FROM memory_summary_uses) THEN
                RAISE EXCEPTION 'Cannot downgrade after M4.4 memory summary data exists';
            END IF;
        END;
        $$;
        """
    )
    op.execute("DROP TRIGGER memory_summary_uses_immutable ON memory_summary_uses")
    op.execute("DROP TRIGGER memory_summary_sources_immutable ON memory_summary_sources")
    op.execute("DROP TRIGGER memory_summaries_immutable ON memory_summaries")
    op.execute("DROP TRIGGER memory_summary_sources_coverage ON memory_summary_sources")
    op.execute("DROP TRIGGER memory_summaries_coverage ON memory_summaries")
    op.execute("DROP TRIGGER memory_summary_uses_scope ON memory_summary_uses")
    op.execute("DROP TRIGGER memory_summary_sources_scope ON memory_summary_sources")
    op.execute("DROP TRIGGER memory_summaries_scope ON memory_summaries")
    op.execute("DROP FUNCTION gandalfdnd_validate_memory_summary_coverage()")
    op.execute("DROP FUNCTION gandalfdnd_validate_memory_summary_use_scope()")
    op.execute("DROP FUNCTION gandalfdnd_validate_memory_summary_source_scope()")
    op.execute("DROP FUNCTION gandalfdnd_validate_memory_summary_scope()")
    op.drop_table("memory_summary_uses")
    op.drop_table("memory_summary_sources")
    op.drop_table("memory_summaries")
