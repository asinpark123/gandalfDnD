"""Add guarded deterministic combat encounters and initiative evidence.

Revision ID: 0016_combat_encounters
Revises: 0015_memory_summaries
"""

from collections.abc import Sequence
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0016_combat_encounters"
down_revision: str | None = "0015_memory_summaries"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

COMBAT_CATALOG_ID = "srd-5.2.1-combat-v1"
COMBAT_CATALOG_SHA256 = "423b80e84593738d4cadc5537278d208a51fbebacbb074a2d79531f0ee023204"


def upgrade() -> None:
    op.drop_constraint("ruleset_data_catalog_kind", "ruleset_data_catalogs", type_="check")
    op.create_check_constraint(
        "ruleset_data_catalog_kind",
        "ruleset_data_catalogs",
        "kind IN ('foundation', 'character_creation', 'character_state', "
        "'rules_resolution', 'combat')",
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
                :id, 'srd-5.2.1', 'combat', '1.0.0', 'character_creation', :sha256
            ) ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(id=COMBAT_CATALOG_ID, sha256=COMBAT_CATALOG_SHA256)
    )

    op.create_table(
        "combat_encounters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scene_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ruleset_release_id", sa.String(80), nullable=False),
        sa.Column("character_state_catalog_id", sa.String(100), nullable=False),
        sa.Column("combat_catalog_id", sa.String(100), nullable=False),
        sa.Column("combat_catalog_sha256", sa.String(64), nullable=False),
        sa.Column("resolver_version", sa.String(60), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("grid_width", sa.Integer(), nullable=False),
        sa.Column("grid_height", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("active_turn_index", sa.Integer()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('setup', 'tie_pending', 'active', 'completed', 'cancelled')",
            name="combat_encounter_status",
        ),
        sa.CheckConstraint("revision >= 0", name="combat_encounter_revision_nonnegative"),
        sa.CheckConstraint(
            "grid_width BETWEEN 2 AND 40 AND grid_height BETWEEN 2 AND 40",
            name="combat_encounter_grid_bounds",
        ),
        sa.CheckConstraint("round_number >= 0", name="combat_encounter_round_nonnegative"),
        sa.CheckConstraint(
            "active_turn_index IS NULL OR active_turn_index >= 0",
            name="combat_encounter_turn_index_nonnegative",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["ruleset_release_id"], ["ruleset_releases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["character_state_catalog_id"], ["ruleset_data_catalogs.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["combat_catalog_id"], ["ruleset_data_catalogs.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("campaign_id", "scene_id"):
        op.create_index(op.f(f"ix_combat_encounters_{column}"), "combat_encounters", [column])
    op.create_index(
        "uq_combat_encounters_one_open_per_campaign",
        "combat_encounters",
        ["campaign_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('setup', 'tie_pending', 'active')"),
    )

    op.create_table(
        "combatants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("side", sa.String(20), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True)),
        sa.Column("monster_definition_id", sa.String(80)),
        sa.Column("instance_name", sa.String(120), nullable=False),
        sa.Column("source_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("max_hp", sa.Integer(), nullable=False),
        sa.Column("hp", sa.Integer(), nullable=False),
        sa.Column("temporary_hp", sa.Integer(), nullable=False),
        sa.Column("armor_class", sa.Integer(), nullable=False),
        sa.Column("speed_feet", sa.Integer(), nullable=False),
        sa.Column("position_x", sa.Integer(), nullable=False),
        sa.Column("position_y", sa.Integer(), nullable=False),
        sa.Column("initiative_modifier", sa.Integer(), nullable=False),
        sa.Column("initiative_dice_faces", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("initiative_selected_die", sa.Integer()),
        sa.Column("initiative_total", sa.Integer()),
        sa.Column("initiative_order", sa.Integer()),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("side IN ('party', 'enemy')", name="combatant_side"),
        sa.CheckConstraint(
            "(side = 'party' AND character_id IS NOT NULL AND monster_definition_id IS NULL) OR "
            "(side = 'enemy' AND character_id IS NULL AND monster_definition_id IS NOT NULL)",
            name="combatant_identity_shape",
        ),
        sa.CheckConstraint(
            "max_hp > 0 AND hp BETWEEN 0 AND max_hp AND temporary_hp >= 0",
            name="combatant_hit_point_bounds",
        ),
        sa.CheckConstraint("armor_class BETWEEN 1 AND 40", name="combatant_armor_class_bounds"),
        sa.CheckConstraint(
            "speed_feet BETWEEN 0 AND 200 AND speed_feet % 5 = 0", name="combatant_speed_bounds"
        ),
        sa.CheckConstraint(
            "position_x >= 0 AND position_y >= 0", name="combatant_position_nonnegative"
        ),
        sa.CheckConstraint(
            "initiative_dice_faces IS NULL OR "
            "(jsonb_typeof(initiative_dice_faces) = 'array' AND "
            "jsonb_array_length(initiative_dice_faces) BETWEEN 1 AND 2)",
            name="combatant_initiative_dice_shape",
        ),
        sa.CheckConstraint(
            "(initiative_total IS NULL AND initiative_selected_die IS NULL "
            "AND initiative_order IS NULL AND initiative_dice_faces IS NULL) OR "
            "(initiative_total IS NOT NULL AND initiative_selected_die BETWEEN 1 AND 20 "
            "AND initiative_dice_faces IS NOT NULL)",
            name="combatant_initiative_shape",
        ),
        sa.CheckConstraint(
            "initiative_order IS NULL OR initiative_order >= 0",
            name="combatant_initiative_order_nonnegative",
        ),
        sa.CheckConstraint(
            "state IN ('active', 'unconscious', 'stable', 'dead', 'fled', 'surrendered')",
            name="combatant_state",
        ),
        sa.CheckConstraint("revision >= 0", name="combatant_revision_nonnegative"),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "encounter_id", "character_id", name="uq_combatants_encounter_character"
        ),
        sa.UniqueConstraint(
            "encounter_id", "position_x", "position_y", name="uq_combatants_position"
        ),
        sa.UniqueConstraint(
            "encounter_id", "initiative_order", name="uq_combatants_initiative_order"
        ),
    )
    for column in ("encounter_id", "character_id"):
        op.create_index(op.f(f"ix_combatants_{column}"), "combatants", [column])

    op.create_table(
        "combat_commands",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_type", sa.String(40), nullable=False),
        sa.Column("expected_encounter_revision", sa.Integer()),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "command_type IN ('create_encounter', 'start_initiative', 'resolve_initiative_tie')",
            name="combat_command_type",
        ),
        sa.CheckConstraint(
            "expected_encounter_revision IS NULL OR expected_encounter_revision >= 0",
            name="combat_command_expected_revision_nonnegative",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "command_id", name="uq_combat_commands_command"),
    )
    for column in ("campaign_id", "encounter_id"):
        op.create_index(op.f(f"ix_combat_commands_{column}"), "combat_commands", [column])

    op.create_table(
        "combat_initiative_ties",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("initiative_total", sa.Integer(), nullable=False),
        sa.Column("participant_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("decided_order", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'resolved')", name="combat_initiative_tie_status"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(participant_ids) = 'array' AND jsonb_array_length(participant_ids) >= 2",
            name="combat_initiative_tie_participants",
        ),
        sa.CheckConstraint(
            "(status = 'pending' AND decided_order IS NULL) OR "
            "(status = 'resolved' AND jsonb_typeof(decided_order) = 'array' "
            "AND jsonb_array_length(decided_order) = jsonb_array_length(participant_ids))",
            name="combat_initiative_tie_resolution_shape",
        ),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "encounter_id", "initiative_total", name="uq_combat_initiative_tie_total"
        ),
    )
    op.create_index(
        op.f("ix_combat_initiative_ties_encounter_id"),
        "combat_initiative_ties",
        ["encounter_id"],
    )

    op.create_table(
        "combat_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("visibility", sa.String(20), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("sequence > 0", name="combat_event_sequence_positive"),
        sa.CheckConstraint("visibility IN ('player', 'dm_only')", name="combat_event_visibility"),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("encounter_id", "sequence", name="uq_combat_events_encounter_sequence"),
    )
    op.create_index(op.f("ix_combat_events_encounter_id"), "combat_events", ["encounter_id"])

    for name in ("combat_encounter_id", "combatant_id", "combat_command_id"):
        op.add_column("dice_rolls", sa.Column(name, postgresql.UUID(as_uuid=True)))
    op.add_column("dice_rolls", sa.Column("roll_index", sa.Integer()))
    op.create_foreign_key(
        "fk_dice_rolls_combat_encounter_id",
        "dice_rolls",
        "combat_encounters",
        ["combat_encounter_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dice_rolls_combatant_id",
        "dice_rolls",
        "combatants",
        ["combatant_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dice_rolls_combat_command_id",
        "dice_rolls",
        "combat_commands",
        ["combat_command_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    for name in ("combat_encounter_id", "combatant_id", "combat_command_id"):
        op.create_index(op.f(f"ix_dice_rolls_{name}"), "dice_rolls", [name])
    op.create_check_constraint(
        "dice_roll_combat_shape",
        "dice_rolls",
        "(combat_encounter_id IS NULL AND combatant_id IS NULL AND "
        "combat_command_id IS NULL AND roll_index IS NULL) OR "
        "(combat_encounter_id IS NOT NULL AND combatant_id IS NOT NULL "
        "AND combat_command_id IS NOT NULL AND roll_index >= 0)",
    )
    op.create_unique_constraint(
        "uq_dice_rolls_combat_command_index", "dice_rolls", ["combat_command_id", "roll_index"]
    )

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_validate_combat_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE
            encounter_campaign uuid;
        BEGIN
            IF TG_TABLE_NAME = 'combat_encounters' THEN
                IF NOT EXISTS (
                    SELECT 1 FROM scenes
                    WHERE id = NEW.scene_id AND campaign_id = NEW.campaign_id AND status = 'active'
                ) THEN
                    RAISE EXCEPTION 'combat encounter requires the campaign active scene';
                END IF;
                RETURN NEW;
            END IF;

            SELECT campaign_id INTO encounter_campaign
            FROM combat_encounters WHERE id = NEW.encounter_id;
            IF encounter_campaign IS NULL THEN
                RAISE EXCEPTION 'combat record requires an encounter';
            END IF;
            IF TG_TABLE_NAME = 'combatants' THEN
                IF NEW.position_x >= (
                       SELECT grid_width FROM combat_encounters WHERE id = NEW.encounter_id
                   ) OR NEW.position_y >= (
                       SELECT grid_height FROM combat_encounters WHERE id = NEW.encounter_id
                   ) THEN
                    RAISE EXCEPTION 'combatant starting cell is outside the encounter grid';
                END IF;
                IF NEW.character_id IS NOT NULL AND NOT EXISTS (
                    SELECT 1 FROM characters
                    WHERE id = NEW.character_id AND campaign_id = encounter_campaign
                      AND creation_status = 'finalized' AND party_status = 'active'
                ) THEN
                    RAISE EXCEPTION 'party combatant must be a finalized active campaign character';
                END IF;
            ELSIF TG_TABLE_NAME = 'combat_commands' AND NEW.campaign_id <> encounter_campaign THEN
                RAISE EXCEPTION 'combat command campaign does not match its encounter';
            END IF;
            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER combat_encounters_scope
        BEFORE INSERT ON combat_encounters
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_scope();
        CREATE TRIGGER combatants_scope
        BEFORE INSERT OR UPDATE ON combatants
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_scope();
        CREATE TRIGGER combat_commands_scope
        BEFORE INSERT ON combat_commands
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_scope();

        CREATE FUNCTION gandalfdnd_validate_combat_dice_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.combat_encounter_id IS NULL THEN
                RETURN NEW;
            END IF;
            IF NOT EXISTS (
                SELECT 1
                FROM combat_encounters encounter
                JOIN combatants combatant
                  ON combatant.id = NEW.combatant_id
                 AND combatant.encounter_id = encounter.id
                JOIN combat_commands command
                  ON command.id = NEW.combat_command_id
                 AND command.encounter_id = encounter.id
                 AND command.campaign_id = encounter.campaign_id
                WHERE encounter.id = NEW.combat_encounter_id
                  AND encounter.campaign_id = NEW.campaign_id
                  AND encounter.ruleset_release_id = NEW.ruleset_release_id
                  AND encounter.combat_catalog_id = NEW.ruleset_data_catalog_id
                  AND combatant.character_id IS NOT DISTINCT FROM NEW.actor_character_id
            ) THEN
                RAISE EXCEPTION 'combat die must match its encounter, command, combatant, and pins';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_dice_scope
        BEFORE INSERT OR UPDATE ON dice_rolls
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_dice_scope();

        CREATE FUNCTION gandalfdnd_protect_combat_audit()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION '% is immutable', TG_TABLE_NAME;
        END;
        $$;
        CREATE TRIGGER combat_commands_immutable
        BEFORE UPDATE OR DELETE ON combat_commands
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_combat_audit();
        CREATE TRIGGER combat_events_immutable
        BEFORE UPDATE OR DELETE ON combat_events
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_combat_audit();

        CREATE FUNCTION gandalfdnd_protect_combat_pins()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.campaign_id IS DISTINCT FROM OLD.campaign_id OR
               NEW.scene_id IS DISTINCT FROM OLD.scene_id OR
               NEW.ruleset_release_id IS DISTINCT FROM OLD.ruleset_release_id OR
               NEW.character_state_catalog_id IS DISTINCT FROM OLD.character_state_catalog_id OR
               NEW.combat_catalog_id IS DISTINCT FROM OLD.combat_catalog_id OR
               NEW.combat_catalog_sha256 IS DISTINCT FROM OLD.combat_catalog_sha256 OR
               NEW.resolver_version IS DISTINCT FROM OLD.resolver_version OR
               NEW.grid_width IS DISTINCT FROM OLD.grid_width OR
               NEW.grid_height IS DISTINCT FROM OLD.grid_height THEN
                RAISE EXCEPTION 'combat encounter pins are immutable';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_encounter_pins_immutable
        BEFORE UPDATE ON combat_encounters
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_combat_pins();

        CREATE FUNCTION gandalfdnd_protect_combatant_source()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.encounter_id IS DISTINCT FROM OLD.encounter_id OR
               NEW.side IS DISTINCT FROM OLD.side OR
               NEW.character_id IS DISTINCT FROM OLD.character_id OR
               NEW.monster_definition_id IS DISTINCT FROM OLD.monster_definition_id OR
               NEW.instance_name IS DISTINCT FROM OLD.instance_name OR
               NEW.source_snapshot IS DISTINCT FROM OLD.source_snapshot OR
               NEW.max_hp IS DISTINCT FROM OLD.max_hp OR
               NEW.armor_class IS DISTINCT FROM OLD.armor_class OR
               NEW.speed_feet IS DISTINCT FROM OLD.speed_feet OR
               NEW.initiative_modifier IS DISTINCT FROM OLD.initiative_modifier THEN
                RAISE EXCEPTION 'combatant source facts are immutable';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combatant_source_immutable
        BEFORE UPDATE ON combatants
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_combatant_source();

        CREATE FUNCTION gandalfdnd_protect_initiative_tie()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'initiative ties cannot be deleted';
            END IF;
            IF NEW.encounter_id IS DISTINCT FROM OLD.encounter_id OR
               NEW.initiative_total IS DISTINCT FROM OLD.initiative_total OR
               NEW.participant_ids IS DISTINCT FROM OLD.participant_ids THEN
                RAISE EXCEPTION 'initiative tie participants are immutable';
            END IF;
            IF OLD.status = 'resolved' THEN
                RAISE EXCEPTION 'resolved initiative tie is immutable';
            END IF;
            IF NEW.status <> 'resolved' OR NEW.decided_order IS NULL OR
               NOT (NEW.decided_order @> OLD.participant_ids AND
                    OLD.participant_ids @> NEW.decided_order) THEN
                RAISE EXCEPTION 'initiative tie must resolve to the exact participant set';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_initiative_tie_guard
        BEFORE UPDATE OR DELETE ON combat_initiative_ties
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_initiative_tie();

        CREATE FUNCTION gandalfdnd_protect_combat_dice()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.combat_encounter_id IS NOT NULL THEN
                RAISE EXCEPTION 'combat dice rolls are immutable';
            END IF;
            RETURN OLD;
        END;
        $$;
        CREATE TRIGGER combat_dice_immutable
        BEFORE UPDATE OR DELETE ON dice_rolls
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_combat_dice();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM combat_encounters) OR
               EXISTS (SELECT 1 FROM dice_rolls WHERE combat_encounter_id IS NOT NULL) THEN
                RAISE EXCEPTION 'Cannot downgrade after combat encounter data has been recorded';
            END IF;
        END;
        $$;
        """
    )
    op.execute("DROP TRIGGER combat_dice_immutable ON dice_rolls")
    op.execute("DROP FUNCTION gandalfdnd_protect_combat_dice()")
    op.execute("DROP TRIGGER IF EXISTS combat_initiative_tie_guard ON combat_initiative_ties")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_protect_initiative_tie()")
    op.execute("DROP TRIGGER combatant_source_immutable ON combatants")
    op.execute("DROP FUNCTION gandalfdnd_protect_combatant_source()")
    op.execute("DROP TRIGGER combat_encounter_pins_immutable ON combat_encounters")
    op.execute("DROP FUNCTION gandalfdnd_protect_combat_pins()")
    op.execute("DROP TRIGGER combat_events_immutable ON combat_events")
    op.execute("DROP TRIGGER combat_commands_immutable ON combat_commands")
    op.execute("DROP FUNCTION gandalfdnd_protect_combat_audit()")
    op.execute("DROP TRIGGER combat_commands_scope ON combat_commands")
    op.execute("DROP TRIGGER combatants_scope ON combatants")
    op.execute("DROP TRIGGER combat_encounters_scope ON combat_encounters")
    op.execute("DROP FUNCTION gandalfdnd_validate_combat_scope()")
    op.execute("DROP TRIGGER IF EXISTS combat_dice_scope ON dice_rolls")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_validate_combat_dice_scope()")

    op.drop_constraint("uq_dice_rolls_combat_command_index", "dice_rolls", type_="unique")
    op.drop_constraint("dice_roll_combat_shape", "dice_rolls", type_="check")
    for name in ("combat_command_id", "combatant_id", "combat_encounter_id"):
        op.drop_index(op.f(f"ix_dice_rolls_{name}"), table_name="dice_rolls")
        op.drop_constraint(f"fk_dice_rolls_{name}", "dice_rolls", type_="foreignkey")
    op.drop_column("dice_rolls", "roll_index")
    for name in ("combat_command_id", "combatant_id", "combat_encounter_id"):
        op.drop_column("dice_rolls", name)

    op.drop_table("combat_events")
    op.drop_table("combat_initiative_ties")
    op.drop_table("combat_commands")
    op.drop_table("combatants")
    op.drop_table("combat_encounters")

    op.execute("DROP TRIGGER ruleset_data_catalogs_immutable ON ruleset_data_catalogs")
    op.execute(
        sa.text("DELETE FROM ruleset_data_catalogs WHERE id = :id").bindparams(id=COMBAT_CATALOG_ID)
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
        "kind IN ('foundation', 'character_creation', 'character_state', 'rules_resolution')",
    )
