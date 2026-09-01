"""Add immutable ability-check and saving-throw resolutions.

Revision ID: 0005_check_save_resolution
Revises: 0004_party_commander_state
"""

from collections.abc import Sequence
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005_check_save_resolution"
down_revision: str | None = "0004_party_commander_state"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RESOLUTION_CATALOG_ID = "srd-5.2.1-check-save-resolution-v1"
RESOLUTION_CATALOG_SHA256 = "09d2b0a963a5fba5c28a0a018b8114bcad25dd65717efcf5e1b791cc4f751448"


def upgrade() -> None:
    op.drop_constraint("ruleset_data_catalog_kind", "ruleset_data_catalogs", type_="check")
    op.create_check_constraint(
        "ruleset_data_catalog_kind",
        "ruleset_data_catalogs",
        "kind IN ('foundation', 'character_creation', 'character_state', 'rules_resolution')",
    )
    op.execute(
        sa.text(
            """
            INSERT INTO ruleset_releases (
                id, title, version, publication_date, license_id, source_url,
                artifact_sha256, artifact_size_bytes, manifest_sha256,
                data_schema_version, support_status
            ) VALUES (
                'srd-5.2.1', 'System Reference Document 5.2.1', '5.2.1',
                :publication_date, 'CC-BY-4.0', 'https://www.dndbeyond.com/srd',
                '8974902d109d6e63672d7c490bde9ccf052410503d9cfa768237154fbc5e3d87',
                6031375,
                '0c1290bda7ba55e998bc989d96afd81a3f2d19f41888dc71e07c704c5d3d43ef',
                '1.0.0', 'foundation_only'
            ) ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(publication_date=date(2025, 5, 1))
    )
    op.execute(
        sa.text(
            """
            INSERT INTO ruleset_data_catalogs (
                id, ruleset_release_id, kind, schema_version, support_status, catalog_sha256
            ) VALUES (
                :id, 'srd-5.2.1', 'rules_resolution', '1.0.0',
                'character_creation', :sha256
            ) ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(id=RESOLUTION_CATALOG_ID, sha256=RESOLUTION_CATALOG_SHA256)
    )

    op.create_table(
        "rule_resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ruleset_release_id", sa.String(length=80), nullable=False),
        sa.Column("character_state_catalog_id", sa.String(length=100), nullable=False),
        sa.Column("ruleset_data_catalog_id", sa.String(length=100), nullable=False),
        sa.Column("dice_roll_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_revision", sa.Integer(), nullable=False),
        sa.Column("state_revision", sa.Integer(), nullable=False),
        sa.Column("resolution_type", sa.String(length=30), nullable=False),
        sa.Column("ability", sa.String(length=20), nullable=False),
        sa.Column("skill", sa.String(length=40), nullable=True),
        sa.Column("difficulty_class", sa.Integer(), nullable=False),
        sa.Column("rule_definition_keys", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("command", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("modifier_formula", sa.Text(), nullable=False),
        sa.Column("modifier_components", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("advantage_sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("disadvantage_sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("advantage_state", sa.String(length=20), nullable=False),
        sa.Column("dice_notation", sa.String(length=20), nullable=False),
        sa.Column("dice_faces", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("selected_die", sa.Integer(), nullable=False),
        sa.Column("modifier", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("resolver_version", sa.String(length=60), nullable=False),
        sa.Column("rng_version", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "character_revision > 0 AND state_revision > 0",
            name="rule_resolution_revisions_positive",
        ),
        sa.CheckConstraint(
            "resolution_type IN ('ability_check', 'saving_throw')",
            name="rule_resolution_type",
        ),
        sa.CheckConstraint(
            "resolution_type = 'ability_check' OR skill IS NULL",
            name="rule_resolution_save_has_no_skill",
        ),
        sa.CheckConstraint(
            "ability IN ('strength', 'dexterity', 'constitution', 'intelligence', "
            "'wisdom', 'charisma')",
            name="rule_resolution_ability",
        ),
        sa.CheckConstraint(
            "difficulty_class BETWEEN 1 AND 100",
            name="rule_resolution_difficulty_class",
        ),
        sa.CheckConstraint(
            "advantage_state IN ('normal', 'advantage', 'disadvantage')",
            name="rule_resolution_advantage_state",
        ),
        sa.CheckConstraint(
            "dice_notation IN ('1d20', '2d20')",
            name="rule_resolution_dice_notation",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(dice_faces) = 'array' AND "
            "((dice_notation = '1d20' AND jsonb_array_length(dice_faces) = 1) OR "
            "(dice_notation = '2d20' AND jsonb_array_length(dice_faces) = 2))",
            name="rule_resolution_dice_count",
        ),
        sa.CheckConstraint(
            "selected_die BETWEEN 1 AND 20",
            name="rule_resolution_selected_die",
        ),
        sa.CheckConstraint("outcome IN ('success', 'failure')", name="rule_resolution_outcome"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_character_id"], ["characters.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["ruleset_release_id"], ["ruleset_releases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["character_state_catalog_id"], ["ruleset_data_catalogs.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["ruleset_data_catalog_id"], ["ruleset_data_catalogs.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["dice_roll_id"], ["dice_rolls.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "command_id", name="uq_rule_resolutions_command"),
        sa.UniqueConstraint("dice_roll_id"),
    )
    for column in (
        "campaign_id",
        "actor_character_id",
        "ruleset_release_id",
        "character_state_catalog_id",
        "ruleset_data_catalog_id",
    ):
        op.create_index(op.f(f"ix_rule_resolutions_{column}"), "rule_resolutions", [column])

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_prevent_rule_resolution_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'rule_resolutions is immutable';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER rule_resolutions_immutable
        BEFORE UPDATE OR DELETE ON rule_resolutions
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_rule_resolution_mutation()
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM rule_resolutions) OR
               EXISTS (
                   SELECT 1 FROM dice_rolls
                   WHERE ruleset_data_catalog_id = 'srd-5.2.1-check-save-resolution-v1'
               ) THEN
                RAISE EXCEPTION 'Cannot downgrade after rule resolutions have been recorded';
            END IF;
        END;
        $$
        """
    )
    op.execute("DROP TRIGGER rule_resolutions_immutable ON rule_resolutions")
    op.execute("DROP FUNCTION gandalfdnd_prevent_rule_resolution_mutation()")
    for column in (
        "ruleset_data_catalog_id",
        "character_state_catalog_id",
        "ruleset_release_id",
        "actor_character_id",
        "campaign_id",
    ):
        op.drop_index(op.f(f"ix_rule_resolutions_{column}"), table_name="rule_resolutions")
    op.drop_table("rule_resolutions")

    op.execute("DROP TRIGGER ruleset_data_catalogs_immutable ON ruleset_data_catalogs")
    op.execute(
        sa.text("DELETE FROM ruleset_data_catalogs WHERE id = :id").bindparams(
            id=RESOLUTION_CATALOG_ID
        )
    )
    op.execute(
        """
        CREATE TRIGGER ruleset_data_catalogs_immutable
        BEFORE UPDATE OR DELETE ON ruleset_data_catalogs
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_ruleset_data_catalog_mutation()
        """
    )
    op.drop_constraint("ruleset_data_catalog_kind", "ruleset_data_catalogs", type_="check")
    op.create_check_constraint(
        "ruleset_data_catalog_kind",
        "ruleset_data_catalogs",
        "kind IN ('foundation', 'character_creation', 'character_state')",
    )
