"""Split memory lifecycle identity triggers by record shape.

Revision ID: 0013_memory_lifecycle
Revises: 0012_memory_foundation
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0013_memory_lifecycle"
down_revision: str | None = "0012_memory_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS campaign_memory_indexes_identity_immutable "
        "ON campaign_memory_indexes"
    )
    op.execute("DROP TRIGGER IF EXISTS memory_index_jobs_identity_immutable ON memory_index_jobs")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_protect_memory_work_identity()")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION gandalfdnd_protect_campaign_memory_index_identity()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION '% cannot be deleted', TG_TABLE_NAME;
            END IF;
            IF ROW(OLD.campaign_id, OLD.profile_id, OLD.created_at)
               IS DISTINCT FROM
               ROW(NEW.campaign_id, NEW.profile_id, NEW.created_at) THEN
                RAISE EXCEPTION 'campaign memory index identity is immutable';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION gandalfdnd_protect_memory_index_job_identity()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION '% cannot be deleted', TG_TABLE_NAME;
            END IF;
            IF ROW(OLD.campaign_id, OLD.document_id, OLD.profile_id, OLD.created_at)
               IS DISTINCT FROM
               ROW(NEW.campaign_id, NEW.document_id, NEW.profile_id, NEW.created_at) THEN
                RAISE EXCEPTION 'memory index job identity is immutable';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER campaign_memory_indexes_identity_immutable
        BEFORE UPDATE OR DELETE ON campaign_memory_indexes
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_campaign_memory_index_identity()
        """
    )
    op.execute(
        """
        CREATE TRIGGER memory_index_jobs_identity_immutable
        BEFORE UPDATE OR DELETE ON memory_index_jobs
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_memory_index_job_identity()
        """
    )


def downgrade() -> None:
    # The corrected 0012 definition uses these same table-specific functions. Keeping them is the
    # accurate 0012 state for both fresh databases and databases repaired by this migration.
    pass
