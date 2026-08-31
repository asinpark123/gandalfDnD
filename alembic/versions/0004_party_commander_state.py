"""Add Party Commander and reproducible character state.

Revision ID: 0004_party_commander_state
Revises: 0003_guided_character_creation
"""

from collections.abc import Sequence
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004_party_commander_state"
down_revision: str | None = "0003_guided_character_creation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

STATE_CATALOG_ID = "srd-5.2.1-party-state-v1"
STATE_CATALOG_SHA256 = "aba4fcdbffb037eece88c862c76be988ffc60808b46361cc9a9dda0730fe763b"


def _add_actor_column(table: str) -> None:
    op.add_column(table, sa.Column("actor_character_id", postgresql.UUID(as_uuid=True)))
    op.create_foreign_key(
        f"fk_{table}_actor_character_id",
        table,
        "characters",
        ["actor_character_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f(f"ix_{table}_actor_character_id"), table, ["actor_character_id"])


def upgrade() -> None:
    op.drop_constraint("ruleset_data_catalog_kind", "ruleset_data_catalogs", type_="check")
    op.create_check_constraint(
        "ruleset_data_catalog_kind",
        "ruleset_data_catalogs",
        "kind IN ('foundation', 'character_creation', 'character_state')",
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
                :id, 'srd-5.2.1', 'character_state', '1.0.0',
                'character_creation', :sha256
            ) ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(id=STATE_CATALOG_ID, sha256=STATE_CATALOG_SHA256)
    )

    op.add_column(
        "campaigns",
        sa.Column("play_mode", sa.String(30), server_default="legacy_single", nullable=False),
    )
    op.add_column(
        "campaigns", sa.Column("party_min_active", sa.Integer(), server_default="1", nullable=False)
    )
    op.add_column(
        "campaigns", sa.Column("party_max_active", sa.Integer(), server_default="1", nullable=False)
    )
    op.create_check_constraint(
        "campaign_play_mode",
        "campaigns",
        "play_mode IN ('legacy_single', 'party_commander')",
    )
    op.create_check_constraint(
        "campaign_party_size_bounds",
        "campaigns",
        "party_min_active >= 1 AND party_max_active >= party_min_active AND party_max_active <= 4",
    )

    op.drop_constraint("characters_campaign_id_key", "characters", type_="unique")
    op.create_index(op.f("ix_characters_campaign_id"), "characters", ["campaign_id"])
    op.add_column(
        "characters", sa.Column("party_position", sa.Integer(), server_default="1", nullable=False)
    )
    op.add_column(
        "characters",
        sa.Column("control_mode", sa.String(20), server_default="player", nullable=False),
    )
    op.add_column(
        "characters",
        sa.Column("party_status", sa.String(20), server_default="active", nullable=False),
    )
    op.add_column(
        "characters", sa.Column("state_revision", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "characters",
        sa.Column(
            "equipped_items",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text('\'{"worn_armor_item_id": null, "held_item_ids": []}\'::jsonb'),
            nullable=False,
        ),
    )
    op.add_column(
        "characters",
        sa.Column(
            "resources",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "character_party_position", "characters", "party_position BETWEEN 1 AND 4"
    )
    op.create_check_constraint("character_control_mode", "characters", "control_mode = 'player'")
    op.create_check_constraint("character_party_status", "characters", "party_status = 'active'")
    op.create_check_constraint(
        "character_state_revision_nonnegative", "characters", "state_revision >= 0"
    )
    op.create_unique_constraint(
        "uq_characters_campaign_position", "characters", ["campaign_id", "party_position"]
    )
    op.execute("DROP TRIGGER finalized_character_creation_immutable ON characters")
    op.execute("DROP FUNCTION gandalfdnd_protect_finalized_character_creation()")
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_protect_finalized_character_creation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.creation_status = 'finalized' AND (
                NEW.campaign_id IS DISTINCT FROM OLD.campaign_id OR
                NEW.name IS DISTINCT FROM OLD.name OR
                NEW.ruleset_release_id IS DISTINCT FROM OLD.ruleset_release_id OR
                NEW.ruleset_data_catalog_id IS DISTINCT FROM OLD.ruleset_data_catalog_id OR
                NEW.creation_status IS DISTINCT FROM OLD.creation_status OR
                NEW.revision IS DISTINCT FROM OLD.revision OR
                NEW.max_hp IS DISTINCT FROM OLD.max_hp OR
                NEW.character_sheet IS DISTINCT FROM OLD.character_sheet OR
                NEW.finalized_at IS DISTINCT FROM OLD.finalized_at OR
                NEW.party_position IS DISTINCT FROM OLD.party_position OR
                NEW.control_mode IS DISTINCT FROM OLD.control_mode
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

    for table in ("turns", "campaign_events", "dice_rolls"):
        _add_actor_column(table)
    op.execute("DROP TRIGGER campaign_events_append_only ON campaign_events")
    op.execute(
        """
        UPDATE campaign_events AS event
        SET actor_character_id = character.id
        FROM characters AS character
        WHERE character.campaign_id = event.campaign_id
        """
    )
    op.execute(
        """
        UPDATE turns AS turn_record
        SET actor_character_id = character.id
        FROM characters AS character
        WHERE character.campaign_id = turn_record.campaign_id
        """
    )
    op.execute(
        """
        UPDATE dice_rolls AS roll
        SET actor_character_id = character.id
        FROM characters AS character
        WHERE character.campaign_id = roll.campaign_id
        """
    )
    op.execute(
        """
        CREATE TRIGGER campaign_events_append_only
        BEFORE UPDATE OR DELETE ON campaign_events
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_event_mutation()
        """
    )

    op.execute("DROP TRIGGER campaign_ruleset_pins_immutable ON campaigns")
    op.execute("DROP FUNCTION gandalfdnd_protect_campaign_ruleset_pins()")
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_protect_campaign_ruleset_pins()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.ruleset_release_id IS DISTINCT FROM OLD.ruleset_release_id OR
               NEW.ruleset_data_catalog_id IS DISTINCT FROM OLD.ruleset_data_catalog_id OR
               NEW.play_mode IS DISTINCT FROM OLD.play_mode OR
               NEW.party_min_active IS DISTINCT FROM OLD.party_min_active OR
               NEW.party_max_active IS DISTINCT FROM OLD.party_max_active THEN
                RAISE EXCEPTION 'campaign ruleset and play-mode pins are immutable';
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
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM campaigns WHERE play_mode = 'party_commander') OR
                   EXISTS (
                       SELECT campaign_id FROM characters GROUP BY campaign_id HAVING count(*) > 1
                   ) THEN
                    RAISE EXCEPTION 'Cannot downgrade after Party Commander data has been recorded';
                END IF;
            END;
            $$
            """
        )
    )
    op.execute("DROP TRIGGER campaign_ruleset_pins_immutable ON campaigns")
    op.execute("DROP FUNCTION gandalfdnd_protect_campaign_ruleset_pins()")
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

    op.execute("DROP TRIGGER finalized_character_creation_immutable ON characters")
    op.execute("DROP FUNCTION gandalfdnd_protect_finalized_character_creation()")
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
        CREATE TRIGGER campaign_ruleset_pins_immutable
        BEFORE UPDATE ON campaigns
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_campaign_ruleset_pins()
        """
    )

    for table in ("dice_rolls", "campaign_events", "turns"):
        op.drop_index(op.f(f"ix_{table}_actor_character_id"), table_name=table)
        op.drop_constraint(f"fk_{table}_actor_character_id", table, type_="foreignkey")
        op.drop_column(table, "actor_character_id")

    op.drop_constraint("uq_characters_campaign_position", "characters", type_="unique")
    for name in (
        "character_state_revision_nonnegative",
        "character_party_status",
        "character_control_mode",
        "character_party_position",
    ):
        op.drop_constraint(name, "characters", type_="check")
    for column in (
        "resources",
        "equipped_items",
        "state_revision",
        "party_status",
        "control_mode",
        "party_position",
    ):
        op.drop_column("characters", column)
    op.drop_index(op.f("ix_characters_campaign_id"), table_name="characters")
    op.create_unique_constraint("characters_campaign_id_key", "characters", ["campaign_id"])

    op.drop_constraint("campaign_party_size_bounds", "campaigns", type_="check")
    op.drop_constraint("campaign_play_mode", "campaigns", type_="check")
    op.drop_column("campaigns", "party_max_active")
    op.drop_column("campaigns", "party_min_active")
    op.drop_column("campaigns", "play_mode")

    op.execute("DROP TRIGGER ruleset_data_catalogs_immutable ON ruleset_data_catalogs")
    op.execute(
        sa.text("DELETE FROM ruleset_data_catalogs WHERE id = :id").bindparams(id=STATE_CATALOG_ID)
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
        "kind IN ('foundation', 'character_creation')",
    )
