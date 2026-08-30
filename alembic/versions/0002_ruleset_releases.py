"""Pin campaigns and mechanical records to immutable ruleset releases.

Revision ID: 0002_ruleset_releases
Revises: 0001_phase_0
"""

from collections.abc import Sequence
from datetime import date

import sqlalchemy as sa

from alembic import op

revision: str = "0002_ruleset_releases"
down_revision: str | None = "0001_phase_0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RELEASE_ID = "srd-5.2.1"


def upgrade() -> None:
    op.create_table(
        "ruleset_releases",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("publication_date", sa.Date(), nullable=False),
        sa.Column("license_id", sa.String(length=40), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("artifact_sha256", sa.String(length=64), nullable=False),
        sa.Column("artifact_size_bytes", sa.Integer(), nullable=False),
        sa.Column("manifest_sha256", sa.String(length=64), nullable=False),
        sa.Column("data_schema_version", sa.String(length=20), nullable=False),
        sa.Column("support_status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("artifact_size_bytes > 0", name="ruleset_artifact_size_positive"),
        sa.CheckConstraint(
            "support_status IN ('foundation_only', 'character_creation', 'complete')",
            name="ruleset_support_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        sa.text(
            """
            INSERT INTO ruleset_releases (
                id, title, version, publication_date, license_id, source_url,
                artifact_sha256, artifact_size_bytes, manifest_sha256,
                data_schema_version, support_status
            ) VALUES (
                :id, :title, :version, :publication_date, :license_id, :source_url,
                :artifact_sha256, :artifact_size_bytes, :manifest_sha256,
                :data_schema_version, :support_status
            )
            """
        ).bindparams(
            id=RELEASE_ID,
            title="System Reference Document 5.2.1",
            version="5.2.1",
            publication_date=date(2025, 5, 1),
            license_id="CC-BY-4.0",
            source_url="https://www.dndbeyond.com/srd",
            artifact_sha256="8974902d109d6e63672d7c490bde9ccf052410503d9cfa768237154fbc5e3d87",
            artifact_size_bytes=6031375,
            manifest_sha256="0c1290bda7ba55e998bc989d96afd81a3f2d19f41888dc71e07c704c5d3d43ef",
            data_schema_version="1.0.0",
            support_status="foundation_only",
        )
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM campaigns
                WHERE ruleset NOT IN ('SRD 5.2.1', 'srd-5.2.1')
            ) THEN
                RAISE EXCEPTION
                    'M1.1 migration found an unmapped legacy campaign ruleset; no data changed';
            END IF;
        END;
        $$
        """
    )

    op.add_column("campaigns", sa.Column("ruleset_release_id", sa.String(80), nullable=True))
    op.execute(
        sa.text("UPDATE campaigns SET ruleset_release_id = :release_id").bindparams(
            release_id=RELEASE_ID
        )
    )
    op.alter_column("campaigns", "ruleset_release_id", nullable=False)
    op.create_foreign_key(
        "fk_campaigns_ruleset_release_id",
        "campaigns",
        "ruleset_releases",
        ["ruleset_release_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(op.f("ix_campaigns_ruleset_release_id"), "campaigns", ["ruleset_release_id"])
    op.alter_column("campaigns", "ruleset", new_column_name="legacy_ruleset_label")
    op.alter_column("campaigns", "legacy_ruleset_label", nullable=True)

    op.execute("DROP TRIGGER campaign_events_append_only ON campaign_events")

    for table in ("characters", "campaign_events", "dice_rolls"):
        op.add_column(table, sa.Column("ruleset_release_id", sa.String(80), nullable=True))
        op.execute(
            sa.text(
                f"""
                UPDATE {table} AS target
                SET ruleset_release_id = campaigns.ruleset_release_id
                FROM campaigns
                WHERE campaigns.id = target.campaign_id
                """
            )
        )
        op.alter_column(table, "ruleset_release_id", nullable=False)
        op.create_foreign_key(
            f"fk_{table}_ruleset_release_id",
            table,
            "ruleset_releases",
            ["ruleset_release_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        op.create_index(op.f(f"ix_{table}_ruleset_release_id"), table, ["ruleset_release_id"])

    op.execute(
        """
        CREATE TRIGGER campaign_events_append_only
        BEFORE UPDATE OR DELETE ON campaign_events
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_event_mutation()
        """
    )

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_prevent_ruleset_release_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'ruleset_releases is immutable';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER ruleset_releases_immutable
        BEFORE UPDATE OR DELETE ON ruleset_releases
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_ruleset_release_mutation()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS ruleset_releases_immutable ON ruleset_releases")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_prevent_ruleset_release_mutation()")

    for table in ("dice_rolls", "campaign_events", "characters"):
        op.drop_index(op.f(f"ix_{table}_ruleset_release_id"), table_name=table)
        op.drop_constraint(f"fk_{table}_ruleset_release_id", table, type_="foreignkey")
        op.drop_column(table, "ruleset_release_id")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM campaigns
                WHERE ruleset_release_id <> 'srd-5.2.1'
            ) THEN
                RAISE EXCEPTION
                    'Cannot downgrade while campaigns use a post-Phase-0 ruleset release';
            END IF;
        END;
        $$
        """
    )
    op.execute(
        "UPDATE campaigns SET legacy_ruleset_label = 'SRD 5.2.1' WHERE legacy_ruleset_label IS NULL"
    )
    op.alter_column("campaigns", "legacy_ruleset_label", nullable=False)
    op.alter_column("campaigns", "legacy_ruleset_label", new_column_name="ruleset")
    op.drop_index(op.f("ix_campaigns_ruleset_release_id"), table_name="campaigns")
    op.drop_constraint("fk_campaigns_ruleset_release_id", "campaigns", type_="foreignkey")
    op.drop_column("campaigns", "ruleset_release_id")
    op.drop_table("ruleset_releases")
