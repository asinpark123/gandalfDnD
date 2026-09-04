"""Add deterministic combat turns, movement, effects, and reaction windows.

Revision ID: 0017_combat_turns_movement
Revises: 0016_combat_encounters
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0017_combat_turns_movement"
down_revision: str | None = "0016_combat_encounters"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("combat_command_type", "combat_commands", type_="check")
    op.create_check_constraint(
        "combat_command_type",
        "combat_commands",
        "command_type IN ('create_encounter', 'start_initiative', "
        "'resolve_initiative_tie', 'combat_move', 'combat_action', "
        "'combat_reaction', 'end_combat_turn')",
    )
    op.add_column(
        "combatants",
        sa.Column("reaction_available", sa.Boolean(), server_default=sa.true(), nullable=False),
    )

    op.create_table(
        "combat_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("movement_allowance_feet", sa.Integer(), nullable=False),
        sa.Column("movement_spent_feet", sa.Integer(), nullable=False),
        sa.Column("action_available", sa.Boolean(), nullable=False),
        sa.Column("bonus_action_available", sa.Boolean(), nullable=False),
        sa.Column("free_interaction_available", sa.Boolean(), nullable=False),
        sa.Column("disengaged", sa.Boolean(), nullable=False),
        sa.Column("started_encounter_revision", sa.Integer(), nullable=False),
        sa.Column("completed_encounter_revision", sa.Integer()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("round_number > 0", name="combat_turn_round_positive"),
        sa.CheckConstraint("turn_index >= 0", name="combat_turn_index_nonnegative"),
        sa.CheckConstraint("status IN ('active', 'completed')", name="combat_turn_status"),
        sa.CheckConstraint(
            "movement_allowance_feet >= 0 AND movement_allowance_feet % 5 = 0 "
            "AND movement_spent_feet >= 0 AND movement_spent_feet % 5 = 0 "
            "AND movement_spent_feet <= movement_allowance_feet",
            name="combat_turn_movement_bounds",
        ),
        sa.CheckConstraint(
            "started_encounter_revision >= 0 AND "
            "(completed_encounter_revision IS NULL OR "
            "completed_encounter_revision > started_encounter_revision)",
            name="combat_turn_revision_bounds",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND completed_encounter_revision IS NULL) OR "
            "(status = 'completed' AND completed_encounter_revision IS NOT NULL)",
            name="combat_turn_completion_shape",
        ),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "encounter_id", "round_number", "turn_index", name="uq_combat_turn_position"
        ),
        sa.UniqueConstraint(
            "encounter_id",
            "round_number",
            "combatant_id",
            name="uq_combat_turn_combatant_round",
        ),
    )
    for column in ("encounter_id", "combatant_id"):
        op.create_index(op.f(f"ix_combat_turns_{column}"), "combat_turns", [column])
    op.create_index(
        "uq_combat_turn_one_active_per_encounter",
        "combat_turns",
        ["encounter_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "combat_effects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("effect_id", sa.String(80), nullable=False),
        sa.Column("stacking_key", sa.String(80), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("starts_round", sa.Integer(), nullable=False),
        sa.Column("expires_on_source_turn_start", sa.Boolean(), nullable=False),
        sa.Column("ended_round", sa.Integer()),
        sa.Column("created_by_command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("status IN ('active', 'expired')", name="combat_effect_status"),
        sa.CheckConstraint("starts_round > 0", name="combat_effect_start_round_positive"),
        sa.CheckConstraint(
            "(status = 'active' AND ended_round IS NULL) OR "
            "(status = 'expired' AND ended_round >= starts_round)",
            name="combat_effect_end_shape",
        ),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["created_by_command_id"], ["combat_commands.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("encounter_id", "source_combatant_id", "target_combatant_id"):
        op.create_index(op.f(f"ix_combat_effects_{column}"), "combat_effects", [column])
    op.create_index(
        "uq_combat_effect_active_stack",
        "combat_effects",
        ["encounter_id", "target_combatant_id", "stacking_key"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "combat_reaction_windows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mover_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reactor_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opened_by_command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("responded_by_command_id", postgresql.UUID(as_uuid=True)),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("from_x", sa.Integer(), nullable=False),
        sa.Column("from_y", sa.Integer(), nullable=False),
        sa.Column("to_x", sa.Integer(), nullable=False),
        sa.Column("to_y", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("response", sa.String(30)),
        sa.Column("opened_encounter_revision", sa.Integer(), nullable=False),
        sa.Column("resolved_encounter_revision", sa.Integer()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'passed', 'opportunity_attack_pending')",
            name="combat_reaction_window_status",
        ),
        sa.CheckConstraint(
            "(status = 'pending' AND response IS NULL AND responded_by_command_id IS NULL "
            "AND resolved_encounter_revision IS NULL) OR "
            "(status IN ('passed', 'opportunity_attack_pending') AND response IS NOT NULL "
            "AND responded_by_command_id IS NOT NULL AND resolved_encounter_revision IS NOT NULL)",
            name="combat_reaction_window_response_shape",
        ),
        sa.CheckConstraint(
            "response IS NULL OR response IN ('pass', 'opportunity_attack')",
            name="combat_reaction_window_response",
        ),
        sa.CheckConstraint(
            "opened_encounter_revision >= 0 AND "
            "(resolved_encounter_revision IS NULL OR "
            "resolved_encounter_revision > opened_encounter_revision)",
            name="combat_reaction_window_revision_bounds",
        ),
        sa.CheckConstraint("round_number > 0", name="combat_reaction_window_round_positive"),
        sa.CheckConstraint(
            "from_x >= 0 AND from_y >= 0 AND to_x >= 0 AND to_y >= 0",
            name="combat_reaction_window_position_nonnegative",
        ),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mover_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reactor_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["opened_by_command_id"], ["combat_commands.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["responded_by_command_id"], ["combat_commands.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "encounter_id",
            "mover_combatant_id",
            "reactor_combatant_id",
            "round_number",
            "from_x",
            "from_y",
            "to_x",
            "to_y",
            name="uq_combat_reaction_transition",
        ),
    )
    for column in ("encounter_id", "mover_combatant_id", "reactor_combatant_id"):
        op.create_index(
            op.f(f"ix_combat_reaction_windows_{column}"),
            "combat_reaction_windows",
            [column],
        )

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_validate_combat_turn_scope()
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
        CREATE TRIGGER combat_turn_scope
        BEFORE INSERT OR UPDATE ON combat_turns
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_turn_scope();

        CREATE FUNCTION gandalfdnd_protect_combat_turn_identity()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.encounter_id IS DISTINCT FROM OLD.encounter_id OR
               NEW.combatant_id IS DISTINCT FROM OLD.combatant_id OR
               NEW.round_number IS DISTINCT FROM OLD.round_number OR
               NEW.turn_index IS DISTINCT FROM OLD.turn_index OR
               NEW.started_encounter_revision IS DISTINCT FROM OLD.started_encounter_revision THEN
                RAISE EXCEPTION 'combat turn identity is immutable';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_turn_identity_immutable
        BEFORE UPDATE ON combat_turns
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_combat_turn_identity();

        CREATE FUNCTION gandalfdnd_validate_combat_child_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_TABLE_NAME = 'combat_effects' THEN
                IF NOT EXISTS (
                    SELECT 1 FROM combatants source, combatants target, combat_commands command
                    WHERE source.id = NEW.source_combatant_id
                      AND target.id = NEW.target_combatant_id
                      AND source.encounter_id = NEW.encounter_id
                      AND target.encounter_id = NEW.encounter_id
                      AND command.id = NEW.created_by_command_id
                      AND command.encounter_id = NEW.encounter_id
                ) THEN
                    RAISE EXCEPTION 'combat effect identities must share one encounter';
                END IF;
            ELSE
                IF NOT EXISTS (
                    SELECT 1 FROM combatants mover, combatants reactor, combat_commands command
                    WHERE mover.id = NEW.mover_combatant_id
                      AND reactor.id = NEW.reactor_combatant_id
                      AND mover.encounter_id = NEW.encounter_id
                      AND reactor.encounter_id = NEW.encounter_id
                      AND mover.side <> reactor.side
                      AND command.id = NEW.opened_by_command_id
                      AND command.encounter_id = NEW.encounter_id
                ) THEN
                    RAISE EXCEPTION
                        'reaction window identities must share opposing encounter sides';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_effect_scope
        BEFORE INSERT OR UPDATE ON combat_effects
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_child_scope();
        CREATE TRIGGER combat_reaction_window_scope
        BEFORE INSERT OR UPDATE ON combat_reaction_windows
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_child_scope();

        CREATE FUNCTION gandalfdnd_protect_combat_effect_identity()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' OR
               NEW.encounter_id IS DISTINCT FROM OLD.encounter_id OR
               NEW.source_combatant_id IS DISTINCT FROM OLD.source_combatant_id OR
               NEW.target_combatant_id IS DISTINCT FROM OLD.target_combatant_id OR
               NEW.effect_id IS DISTINCT FROM OLD.effect_id OR
               NEW.stacking_key IS DISTINCT FROM OLD.stacking_key OR
               NEW.starts_round IS DISTINCT FROM OLD.starts_round OR
               NEW.expires_on_source_turn_start IS DISTINCT FROM OLD.expires_on_source_turn_start OR
               NEW.created_by_command_id IS DISTINCT FROM OLD.created_by_command_id OR
               OLD.status = 'expired' OR NEW.status <> 'expired' THEN
                RAISE EXCEPTION 'combat effect source facts are immutable';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_effect_identity_immutable
        BEFORE UPDATE OR DELETE ON combat_effects
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_combat_effect_identity();

        CREATE FUNCTION gandalfdnd_protect_reaction_window_identity()
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
        CREATE TRIGGER combat_reaction_window_identity_immutable
        BEFORE UPDATE OR DELETE ON combat_reaction_windows
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_protect_reaction_window_identity();
        """
    )

    op.execute(
        """
        INSERT INTO combat_turns (
            id, encounter_id, combatant_id, round_number, turn_index, status,
            movement_allowance_feet, movement_spent_feet, action_available,
            bonus_action_available, free_interaction_available, disengaged,
            started_encounter_revision, completed_encounter_revision
        )
        SELECT gen_random_uuid(), encounter.id, combatant.id, encounter.round_number,
               encounter.active_turn_index, 'active', combatant.speed_feet, 0,
               true, true, true, false, encounter.revision, NULL
        FROM combat_encounters encounter
        JOIN combatants combatant
          ON combatant.encounter_id = encounter.id
         AND combatant.initiative_order = encounter.active_turn_index
        WHERE encounter.status = 'active'
          AND encounter.round_number > 0
          AND encounter.active_turn_index IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM combat_turns) OR
               EXISTS (SELECT 1 FROM combat_effects) OR
               EXISTS (SELECT 1 FROM combat_reaction_windows) OR
               EXISTS (
                   SELECT 1 FROM combat_commands
                   WHERE command_type IN (
                       'combat_move', 'combat_action', 'combat_reaction', 'end_combat_turn'
                   )
               ) THEN
                RAISE EXCEPTION 'Cannot downgrade after combat turn data has been recorded';
            END IF;
        END;
        $$;
        """
    )
    op.execute("DROP TRIGGER combat_reaction_window_identity_immutable ON combat_reaction_windows")
    op.execute("DROP FUNCTION gandalfdnd_protect_reaction_window_identity()")
    op.execute("DROP TRIGGER combat_effect_identity_immutable ON combat_effects")
    op.execute("DROP FUNCTION gandalfdnd_protect_combat_effect_identity()")
    op.execute("DROP TRIGGER combat_reaction_window_scope ON combat_reaction_windows")
    op.execute("DROP TRIGGER combat_effect_scope ON combat_effects")
    op.execute("DROP FUNCTION gandalfdnd_validate_combat_child_scope()")
    op.execute("DROP TRIGGER combat_turn_identity_immutable ON combat_turns")
    op.execute("DROP FUNCTION gandalfdnd_protect_combat_turn_identity()")
    op.execute("DROP TRIGGER combat_turn_scope ON combat_turns")
    op.execute("DROP FUNCTION gandalfdnd_validate_combat_turn_scope()")

    op.drop_table("combat_reaction_windows")
    op.drop_table("combat_effects")
    op.drop_table("combat_turns")
    op.drop_column("combatants", "reaction_available")
    op.drop_constraint("combat_command_type", "combat_commands", type_="check")
    op.create_check_constraint(
        "combat_command_type",
        "combat_commands",
        "command_type IN ('create_encounter', 'start_initiative', 'resolve_initiative_tie')",
    )
