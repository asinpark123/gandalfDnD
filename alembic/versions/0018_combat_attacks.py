"""Add immutable deterministic combat attack resolutions.

Revision ID: 0018_combat_attacks
Revises: 0017_combat_turns_movement
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0018_combat_attacks"
down_revision: str | None = "0017_combat_turns_movement"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _reaction_guard() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION gandalfdnd_protect_reaction_window_identity()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' OR
               NEW.encounter_id IS DISTINCT FROM OLD.encounter_id OR
               NEW.mover_combatant_id IS DISTINCT FROM OLD.mover_combatant_id OR
               NEW.reactor_combatant_id IS DISTINCT FROM OLD.reactor_combatant_id OR
               NEW.opened_by_command_id IS DISTINCT FROM OLD.opened_by_command_id OR
               NEW.round_number IS DISTINCT FROM OLD.round_number OR
               NEW.from_x IS DISTINCT FROM OLD.from_x OR NEW.from_y IS DISTINCT FROM OLD.from_y OR
               NEW.to_x IS DISTINCT FROM OLD.to_x OR NEW.to_y IS DISTINCT FROM OLD.to_y OR
               NEW.opened_encounter_revision IS DISTINCT FROM OLD.opened_encounter_revision THEN
                RAISE EXCEPTION 'combat reaction window identity is immutable';
            END IF;
            IF OLD.status = 'pending' AND
               NEW.status IN ('passed', 'opportunity_attack_pending') THEN
                RETURN NEW;
            END IF;
            IF OLD.status = 'opportunity_attack_pending' AND
               NEW.status = 'opportunity_attack_resolved' THEN
                RETURN NEW;
            END IF;
            RAISE EXCEPTION 'combat reaction window transition is invalid';
        END;
        $$;
        """
    )


def upgrade() -> None:
    op.drop_constraint("combat_command_type", "combat_commands", type_="check")
    op.create_check_constraint(
        "combat_command_type",
        "combat_commands",
        "command_type IN ('create_encounter', 'start_initiative', "
        "'resolve_initiative_tie', 'combat_move', 'combat_action', "
        "'combat_reaction', 'end_combat_turn', 'combat_attack')",
    )
    op.drop_constraint(
        "combat_reaction_window_response_shape", "combat_reaction_windows", type_="check"
    )
    op.drop_constraint("combat_reaction_window_status", "combat_reaction_windows", type_="check")
    op.create_check_constraint(
        "combat_reaction_window_status",
        "combat_reaction_windows",
        "status IN ('pending', 'passed', 'opportunity_attack_pending', "
        "'opportunity_attack_resolved')",
    )
    op.create_check_constraint(
        "combat_reaction_window_response_shape",
        "combat_reaction_windows",
        "(status = 'pending' AND response IS NULL AND responded_by_command_id IS NULL "
        "AND resolved_encounter_revision IS NULL) OR "
        "(status IN ('passed', 'opportunity_attack_pending', "
        "'opportunity_attack_resolved') AND response IS NOT NULL "
        "AND responded_by_command_id IS NOT NULL AND resolved_encounter_revision IS NOT NULL)",
    )
    _reaction_guard()
    op.execute(
        """
        CREATE OR REPLACE FUNCTION gandalfdnd_validate_combat_turn_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM combat_encounters encounter
                JOIN combatants combatant
                  ON combatant.id = NEW.combatant_id
                 AND combatant.encounter_id = encounter.id
                WHERE encounter.id = NEW.encounter_id
                  AND combatant.initiative_order = NEW.turn_index
                  AND NEW.movement_allowance_feet
                      BETWEEN GREATEST(0, combatant.speed_feet - 10)
                          AND combatant.speed_feet * 2
            ) THEN
                RAISE EXCEPTION 'combat turn must match encounter order and movement allowance';
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )

    op.create_table(
        "combat_attack_resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reaction_window_id", postgresql.UUID(as_uuid=True)),
        sa.Column("ruleset_release_id", sa.String(80), nullable=False),
        sa.Column("combat_catalog_id", sa.String(100), nullable=False),
        sa.Column("resolver_version", sa.String(60), nullable=False),
        sa.Column("actor_revision_before", sa.Integer(), nullable=False),
        sa.Column("actor_revision_after", sa.Integer(), nullable=False),
        sa.Column("target_revision_before", sa.Integer(), nullable=False),
        sa.Column("target_revision_after", sa.Integer(), nullable=False),
        sa.Column("command", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("resolution_input", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("attack_result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("damage_result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rng_version", sa.String(60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "actor_combatant_id <> target_combatant_id",
            name="combat_attack_distinct_target",
        ),
        sa.CheckConstraint(
            "actor_revision_after > actor_revision_before AND "
            "target_revision_after > target_revision_before",
            name="combat_attack_revision_progress",
        ),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["command_id"], ["combat_commands.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["actor_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["reaction_window_id"], ["combat_reaction_windows.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["ruleset_release_id"], ["ruleset_releases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["combat_catalog_id"], ["ruleset_data_catalogs.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("command_id"),
    )
    for column in (
        "encounter_id",
        "actor_combatant_id",
        "target_combatant_id",
        "reaction_window_id",
    ):
        op.create_index(
            op.f(f"ix_combat_attack_resolutions_{column}"),
            "combat_attack_resolutions",
            [column],
        )
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_validate_combat_attack_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM combat_encounters encounter
                JOIN combatants actor
                  ON actor.id = NEW.actor_combatant_id
                 AND actor.encounter_id = encounter.id
                JOIN combatants target
                  ON target.id = NEW.target_combatant_id
                 AND target.encounter_id = encounter.id
                 AND target.side <> actor.side
                JOIN combat_commands command
                  ON command.id = NEW.command_id
                 AND command.encounter_id = encounter.id
                 AND command.command_type = 'combat_attack'
                WHERE encounter.id = NEW.encounter_id
                  AND encounter.ruleset_release_id = NEW.ruleset_release_id
                  AND encounter.combat_catalog_id = NEW.combat_catalog_id
            ) THEN
                RAISE EXCEPTION 'combat attack identities and pins must share one encounter';
            END IF;
            IF NEW.reaction_window_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM combat_reaction_windows reaction_window
                WHERE reaction_window.id = NEW.reaction_window_id
                  AND reaction_window.encounter_id = NEW.encounter_id
                  AND reaction_window.reactor_combatant_id = NEW.actor_combatant_id
                  AND reaction_window.mover_combatant_id = NEW.target_combatant_id
                  AND reaction_window.response = 'opportunity_attack'
            ) THEN
                RAISE EXCEPTION 'combat attack reaction window does not match actor and target';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_attack_scope
        BEFORE INSERT ON combat_attack_resolutions
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_attack_scope();

        CREATE FUNCTION gandalfdnd_prevent_combat_attack_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'combat_attack_resolutions is immutable';
        END;
        $$;
        CREATE TRIGGER combat_attack_resolutions_immutable
        BEFORE UPDATE OR DELETE ON combat_attack_resolutions
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_combat_attack_mutation();
        """
    )
    op.execute(
        """
        CREATE FUNCTION gandalfdnd_validate_combatant_character_hp()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.character_id IS NOT NULL AND EXISTS (
                SELECT 1
                FROM combat_encounters encounter
                JOIN characters character ON character.id = NEW.character_id
                WHERE encounter.id = NEW.encounter_id
                  AND encounter.status IN ('setup', 'tie_pending', 'active')
                  AND character.hp <> NEW.hp
            ) THEN
                RAISE EXCEPTION 'active combatant HP must match canonical character HP';
            END IF;
            RETURN NULL;
        END;
        $$;
        CREATE CONSTRAINT TRIGGER combatant_character_hp_consistency
        AFTER INSERT OR UPDATE ON combatants
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combatant_character_hp();

        CREATE FUNCTION gandalfdnd_validate_character_combat_hp()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM combatants combatant
                JOIN combat_encounters encounter ON encounter.id = combatant.encounter_id
                WHERE combatant.character_id = NEW.id
                  AND encounter.status IN ('setup', 'tie_pending', 'active')
                  AND combatant.hp <> NEW.hp
            ) THEN
                RAISE EXCEPTION 'canonical character HP must match active combatant HP';
            END IF;
            RETURN NULL;
        END;
        $$;
        CREATE CONSTRAINT TRIGGER character_combat_hp_consistency
        AFTER UPDATE ON characters
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_character_combat_hp();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM combat_attack_resolutions) OR
               EXISTS (
                   SELECT 1 FROM combat_commands WHERE command_type = 'combat_attack'
               ) THEN
                RAISE EXCEPTION 'Cannot downgrade after combat attacks have been recorded';
            END IF;
        END;
        $$;
        """
    )
    op.execute("DROP TRIGGER character_combat_hp_consistency ON characters")
    op.execute("DROP FUNCTION gandalfdnd_validate_character_combat_hp()")
    op.execute("DROP TRIGGER combatant_character_hp_consistency ON combatants")
    op.execute("DROP FUNCTION gandalfdnd_validate_combatant_character_hp()")
    op.execute("DROP TRIGGER combat_attack_resolutions_immutable ON combat_attack_resolutions")
    op.execute("DROP FUNCTION gandalfdnd_prevent_combat_attack_mutation()")
    op.execute("DROP TRIGGER combat_attack_scope ON combat_attack_resolutions")
    op.execute("DROP FUNCTION gandalfdnd_validate_combat_attack_scope()")
    for column in (
        "reaction_window_id",
        "target_combatant_id",
        "actor_combatant_id",
        "encounter_id",
    ):
        op.drop_index(
            op.f(f"ix_combat_attack_resolutions_{column}"),
            table_name="combat_attack_resolutions",
        )
    op.drop_table("combat_attack_resolutions")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION gandalfdnd_validate_combat_turn_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM combat_encounters encounter
                JOIN combatants combatant
                  ON combatant.id = NEW.combatant_id
                 AND combatant.encounter_id = encounter.id
                WHERE encounter.id = NEW.encounter_id
                  AND combatant.initiative_order = NEW.turn_index
                  AND NEW.movement_allowance_feet BETWEEN combatant.speed_feet
                                                      AND combatant.speed_feet * 2
            ) THEN
                RAISE EXCEPTION 'combat turn must match encounter order and movement allowance';
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )

    op.drop_constraint(
        "combat_reaction_window_response_shape", "combat_reaction_windows", type_="check"
    )
    op.drop_constraint("combat_reaction_window_status", "combat_reaction_windows", type_="check")
    op.create_check_constraint(
        "combat_reaction_window_status",
        "combat_reaction_windows",
        "status IN ('pending', 'passed', 'opportunity_attack_pending')",
    )
    op.create_check_constraint(
        "combat_reaction_window_response_shape",
        "combat_reaction_windows",
        "(status = 'pending' AND response IS NULL AND responded_by_command_id IS NULL "
        "AND resolved_encounter_revision IS NULL) OR "
        "(status IN ('passed', 'opportunity_attack_pending') AND response IS NOT NULL "
        "AND responded_by_command_id IS NOT NULL AND resolved_encounter_revision IS NOT NULL)",
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION gandalfdnd_protect_reaction_window_identity()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' OR OLD.status <> 'pending' OR
               NEW.encounter_id IS DISTINCT FROM OLD.encounter_id OR
               NEW.mover_combatant_id IS DISTINCT FROM OLD.mover_combatant_id OR
               NEW.reactor_combatant_id IS DISTINCT FROM OLD.reactor_combatant_id OR
               NEW.opened_by_command_id IS DISTINCT FROM OLD.opened_by_command_id OR
               NEW.round_number IS DISTINCT FROM OLD.round_number OR
               NEW.from_x IS DISTINCT FROM OLD.from_x OR NEW.from_y IS DISTINCT FROM OLD.from_y OR
               NEW.to_x IS DISTINCT FROM OLD.to_x OR NEW.to_y IS DISTINCT FROM OLD.to_y OR
               NEW.opened_encounter_revision IS DISTINCT FROM OLD.opened_encounter_revision THEN
                RAISE EXCEPTION 'combat reaction window identity is immutable';
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.drop_constraint("combat_command_type", "combat_commands", type_="check")
    op.create_check_constraint(
        "combat_command_type",
        "combat_commands",
        "command_type IN ('create_encounter', 'start_initiative', "
        "'resolve_initiative_tie', 'combat_move', 'combat_action', "
        "'combat_reaction', 'end_combat_turn')",
    )
