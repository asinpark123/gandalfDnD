"""Add versioned character catalogs and guided character creation.

Revision ID: 0003_guided_character_creation
Revises: 0002_ruleset_releases
"""

from collections.abc import Sequence
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003_guided_character_creation"
down_revision: str | None = "0002_ruleset_releases"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RELEASE_ID = "srd-5.2.1"
FOUNDATION_CATALOG_ID = "srd-5.2.1-foundation-v1"
CHARACTER_CATALOG_ID = "srd-5.2.1-character-creation-v1"


def _add_catalog_pin(table: str) -> None:
    op.add_column(table, sa.Column("ruleset_data_catalog_id", sa.String(100), nullable=True))
    op.execute(
        sa.text(
            f"""
            UPDATE {table} AS target
            SET ruleset_data_catalog_id = campaigns.ruleset_data_catalog_id
            FROM campaigns
            WHERE campaigns.id = target.campaign_id
            """
        )
    )
    op.alter_column(table, "ruleset_data_catalog_id", nullable=False)
    op.create_foreign_key(
        f"fk_{table}_ruleset_data_catalog_id",
        table,
        "ruleset_data_catalogs",
        ["ruleset_data_catalog_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(op.f(f"ix_{table}_ruleset_data_catalog_id"), table, ["ruleset_data_catalog_id"])


def upgrade() -> None:
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
            ) ON CONFLICT (id) DO NOTHING
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
    op.create_table(
        "ruleset_data_catalogs",
        sa.Column("id", sa.String(100), nullable=False),
        sa.Column("ruleset_release_id", sa.String(80), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("schema_version", sa.String(20), nullable=False),
        sa.Column("support_status", sa.String(30), nullable=False),
        sa.Column("catalog_sha256", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "kind IN ('foundation', 'character_creation')", name="ruleset_data_catalog_kind"
        ),
        sa.CheckConstraint(
            "support_status IN ('foundation_only', 'character_creation', 'complete')",
            name="ruleset_data_catalog_support_status",
        ),
        sa.ForeignKeyConstraint(
            ["ruleset_release_id"], ["ruleset_releases.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ruleset_data_catalogs_ruleset_release_id"),
        "ruleset_data_catalogs",
        ["ruleset_release_id"],
    )
    op.execute(
        sa.text(
            """
            INSERT INTO ruleset_data_catalogs (
                id, ruleset_release_id, kind, schema_version, support_status, catalog_sha256
            ) VALUES
                (:foundation_id, :release_id, 'foundation', '1.0.0', 'foundation_only',
                 :foundation_sha256),
                (:character_id, :release_id, 'character_creation', '1.0.0',
                 'character_creation', :character_sha256)
            """
        ).bindparams(
            foundation_id=FOUNDATION_CATALOG_ID,
            character_id=CHARACTER_CATALOG_ID,
            release_id=RELEASE_ID,
            foundation_sha256="f2014945cb0b81a6dd192e0a6c1e02fb136ba4d4734d35a8160f9e3e5e7a3893",
            character_sha256="ddbd172feeeb191789f1b95f93762c661dda06888dad067e28c7fc6ffda391cb",
        )
    )

    op.add_column("campaigns", sa.Column("ruleset_data_catalog_id", sa.String(100), nullable=True))
    op.execute(
        sa.text("UPDATE campaigns SET ruleset_data_catalog_id = :catalog_id").bindparams(
            catalog_id=FOUNDATION_CATALOG_ID
        )
    )
    op.alter_column("campaigns", "ruleset_data_catalog_id", nullable=False)
    op.create_foreign_key(
        "fk_campaigns_ruleset_data_catalog_id",
        "campaigns",
        "ruleset_data_catalogs",
        ["ruleset_data_catalog_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        op.f("ix_campaigns_ruleset_data_catalog_id"),
        "campaigns",
        ["ruleset_data_catalog_id"],
    )

    op.execute("DROP TRIGGER campaign_events_append_only ON campaign_events")
    for table in ("characters", "campaign_events", "dice_rolls"):
        _add_catalog_pin(table)
    op.execute(
        """
        CREATE TRIGGER campaign_events_append_only
        BEFORE UPDATE OR DELETE ON campaign_events
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_event_mutation()
        """
    )

    op.add_column(
        "characters",
        sa.Column("creation_status", sa.String(20), server_default="legacy", nullable=False),
    )
    op.add_column(
        "characters", sa.Column("revision", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "characters",
        sa.Column("character_sheet", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "characters", sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.alter_column("characters", "max_hp", nullable=True)
    op.alter_column("characters", "hp", nullable=True)
    op.drop_constraint("character_max_hp_positive", "characters", type_="check")
    op.drop_constraint("character_hp_bounds", "characters", type_="check")
    op.create_check_constraint(
        "character_creation_status",
        "characters",
        "creation_status IN ('legacy', 'draft', 'finalized')",
    )
    op.create_check_constraint("character_revision_nonnegative", "characters", "revision >= 0")
    op.create_check_constraint(
        "character_max_hp_positive", "characters", "max_hp IS NULL OR max_hp > 0"
    )
    op.create_check_constraint(
        "character_hp_bounds",
        "characters",
        "(hp IS NULL AND max_hp IS NULL) OR "
        "(hp IS NOT NULL AND max_hp IS NOT NULL AND hp >= 0 AND hp <= max_hp)",
    )

    op.create_table(
        "character_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ruleset_release_id", sa.String(80), nullable=False),
        sa.Column("ruleset_data_catalog_id", sa.String(100), nullable=False),
        sa.Column("acquisition_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("grant_type", sa.String(20), nullable=False),
        sa.Column("choice_slot", sa.String(100), nullable=False),
        sa.Column("definition_key", sa.String(160), nullable=False),
        sa.Column("source_definition_key", sa.String(160), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("revision > 0", name="character_grant_revision_positive"),
        sa.CheckConstraint("grant_type IN ('selection', 'grant')", name="character_grant_type"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["ruleset_release_id"], ["ruleset_releases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["ruleset_data_catalog_id"], ["ruleset_data_catalogs.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["acquisition_event_id"], ["campaign_events.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "character_id",
            "revision",
            "choice_slot",
            "definition_key",
            name="uq_character_grant_revision_slot_definition",
        ),
    )
    for column in (
        "character_id",
        "campaign_id",
        "ruleset_release_id",
        "ruleset_data_catalog_id",
        "acquisition_event_id",
    ):
        op.create_index(op.f(f"ix_character_grants_{column}"), "character_grants", [column])

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_prevent_ruleset_data_catalog_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'ruleset_data_catalogs is immutable';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER ruleset_data_catalogs_immutable
        BEFORE UPDATE OR DELETE ON ruleset_data_catalogs
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_ruleset_data_catalog_mutation()
        """
    )
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_prevent_character_grant_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'character_grants is immutable';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER character_grants_immutable
        BEFORE UPDATE OR DELETE ON character_grants
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_character_grant_mutation()
        """
    )
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_protect_finalized_character_creation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.creation_status = 'finalized' AND (
                NEW.name IS DISTINCT FROM OLD.name OR
                NEW.ruleset_release_id IS DISTINCT FROM OLD.ruleset_release_id OR
                NEW.ruleset_data_catalog_id IS DISTINCT FROM OLD.ruleset_data_catalog_id OR
                NEW.creation_status IS DISTINCT FROM OLD.creation_status OR
                NEW.revision IS DISTINCT FROM OLD.revision OR
                NEW.max_hp IS DISTINCT FROM OLD.max_hp OR
                NEW.character_sheet IS DISTINCT FROM OLD.character_sheet OR
                NEW.finalized_at IS DISTINCT FROM OLD.finalized_at
            ) THEN
                RAISE EXCEPTION 'finalized character creation facts are immutable';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER finalized_character_creation_immutable
        BEFORE UPDATE ON characters
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_finalized_character_creation()
        """
    )
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_protect_campaign_ruleset_pins()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.ruleset_release_id IS DISTINCT FROM OLD.ruleset_release_id OR
               NEW.ruleset_data_catalog_id IS DISTINCT FROM OLD.ruleset_data_catalog_id THEN
                RAISE EXCEPTION 'campaign ruleset pins are immutable';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER campaign_ruleset_pins_immutable
        BEFORE UPDATE ON campaigns
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_campaign_ruleset_pins()
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM characters
                WHERE creation_status <> 'legacy' OR hp IS NULL OR max_hp IS NULL
            ) OR EXISTS (SELECT 1 FROM character_grants) THEN
                RAISE EXCEPTION
                    'Cannot downgrade after guided character creation data has been recorded';
            END IF;
        END;
        $$
        """
    )
    op.execute("DROP TRIGGER IF EXISTS campaign_ruleset_pins_immutable ON campaigns")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_protect_campaign_ruleset_pins()")
    op.execute("DROP TRIGGER IF EXISTS finalized_character_creation_immutable ON characters")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_protect_finalized_character_creation()")
    op.execute("DROP TRIGGER IF EXISTS character_grants_immutable ON character_grants")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_prevent_character_grant_mutation()")
    op.execute("DROP TRIGGER IF EXISTS ruleset_data_catalogs_immutable ON ruleset_data_catalogs")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_prevent_ruleset_data_catalog_mutation()")

    for column in (
        "acquisition_event_id",
        "ruleset_data_catalog_id",
        "ruleset_release_id",
        "campaign_id",
        "character_id",
    ):
        op.drop_index(op.f(f"ix_character_grants_{column}"), table_name="character_grants")
    op.drop_table("character_grants")

    op.drop_constraint("character_hp_bounds", "characters", type_="check")
    op.drop_constraint("character_max_hp_positive", "characters", type_="check")
    op.drop_constraint("character_revision_nonnegative", "characters", type_="check")
    op.drop_constraint("character_creation_status", "characters", type_="check")
    op.alter_column("characters", "hp", nullable=False)
    op.alter_column("characters", "max_hp", nullable=False)
    op.create_check_constraint("character_max_hp_positive", "characters", "max_hp > 0")
    op.create_check_constraint("character_hp_bounds", "characters", "hp >= 0 AND hp <= max_hp")
    op.drop_column("characters", "finalized_at")
    op.drop_column("characters", "character_sheet")
    op.drop_column("characters", "revision")
    op.drop_column("characters", "creation_status")

    for table in ("dice_rolls", "campaign_events", "characters"):
        op.drop_index(op.f(f"ix_{table}_ruleset_data_catalog_id"), table_name=table)
        op.drop_constraint(f"fk_{table}_ruleset_data_catalog_id", table, type_="foreignkey")
        op.drop_column(table, "ruleset_data_catalog_id")

    op.drop_index(op.f("ix_campaigns_ruleset_data_catalog_id"), table_name="campaigns")
    op.drop_constraint("fk_campaigns_ruleset_data_catalog_id", "campaigns", type_="foreignkey")
    op.drop_column("campaigns", "ruleset_data_catalog_id")
    op.drop_index(
        op.f("ix_ruleset_data_catalogs_ruleset_release_id"),
        table_name="ruleset_data_catalogs",
    )
    op.drop_table("ruleset_data_catalogs")
