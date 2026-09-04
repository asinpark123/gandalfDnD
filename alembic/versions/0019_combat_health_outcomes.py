"""Add deterministic combat health, recovery, and encounter outcomes.

Revision ID: 0019_combat_health_outcomes
Revises: 0018_combat_attacks
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0019_combat_health_outcomes"
down_revision: str | None = "0018_combat_attacks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "combat_encounters",
        sa.Column("difficulty_label", sa.String(20), server_default="favorable", nullable=False),
    )
    op.add_column(
        "combat_encounters", sa.Column("enemy_xp", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "combat_encounters",
        sa.Column("low_xp_budget", sa.Integer(), server_default="100", nullable=False),
    )
    op.add_column(
        "combat_encounters",
        sa.Column("moderate_xp_budget", sa.Integer(), server_default="150", nullable=False),
    )
    op.add_column(
        "combat_encounters",
        sa.Column("high_xp_budget", sa.Integer(), server_default="200", nullable=False),
    )
    op.add_column("combat_encounters", sa.Column("outcome", sa.String(20)))
    op.add_column(
        "combat_encounters",
        sa.Column("outcome_summary", postgresql.JSONB(astext_type=sa.Text())),
    )
    op.add_column("combat_encounters", sa.Column("completed_at", sa.DateTime(timezone=True)))
    op.create_check_constraint(
        "combat_encounter_difficulty_label",
        "combat_encounters",
        "difficulty_label IN ('favorable', 'low', 'moderate', 'high')",
    )
    op.create_check_constraint(
        "combat_encounter_xp_budgets",
        "combat_encounters",
        "enemy_xp >= 0 AND low_xp_budget > 0 AND moderate_xp_budget > low_xp_budget "
        "AND high_xp_budget > moderate_xp_budget",
    )
    op.create_check_constraint(
        "combat_encounter_outcome",
        "combat_encounters",
        "outcome IS NULL OR outcome IN ('victory', 'defeat', 'surrender', 'flight', 'agreement')",
    )
    op.create_check_constraint(
        "combat_encounter_completion_shape",
        "combat_encounters",
        "(status = 'completed' AND outcome IS NOT NULL AND outcome_summary IS NOT NULL "
        "AND completed_at IS NOT NULL AND active_turn_index IS NULL) OR "
        "(status <> 'completed' AND outcome IS NULL AND outcome_summary IS NULL "
        "AND completed_at IS NULL)",
    )

    op.add_column(
        "combatants",
        sa.Column("death_save_successes", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "combatants",
        sa.Column("death_save_failures", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("combatants", sa.Column("second_wind_remaining", sa.Integer()))
    op.create_check_constraint(
        "combatant_death_save_bounds",
        "combatants",
        "death_save_successes BETWEEN 0 AND 3 AND death_save_failures BETWEEN 0 AND 3",
    )
    op.create_check_constraint(
        "combatant_second_wind_shape",
        "combatants",
        "(side = 'party' AND second_wind_remaining BETWEEN 0 AND 2) OR "
        "(side = 'enemy' AND second_wind_remaining IS NULL)",
    )
    # Perform the backfill only after all ALTER TABLE operations on combatants.
    # Existing deferred character/combatant consistency triggers queue events for
    # updated rows, and PostgreSQL will not alter that table while those events wait.
    op.execute(
        """
        UPDATE combatants combatant
        SET second_wind_remaining = COALESCE((character.resources ->> 'second_wind')::integer, 0)
        FROM characters character
        WHERE combatant.character_id = character.id
        """
    )

    op.drop_constraint("combat_command_type", "combat_commands", type_="check")
    op.create_check_constraint(
        "combat_command_type",
        "combat_commands",
        "command_type IN ('create_encounter', 'start_initiative', "
        "'resolve_initiative_tie', 'combat_move', 'combat_action', "
        "'combat_reaction', 'end_combat_turn', 'combat_attack', "
        "'combat_health', 'combat_outcome')",
    )

    op.create_table(
        "combat_health_resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_combatant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resolution_type", sa.String(30), nullable=False),
        sa.Column("ruleset_release_id", sa.String(80), nullable=False),
        sa.Column("combat_catalog_id", sa.String(100), nullable=False),
        sa.Column("resolver_version", sa.String(60), nullable=False),
        sa.Column("actor_revision_before", sa.Integer(), nullable=False),
        sa.Column("actor_revision_after", sa.Integer(), nullable=False),
        sa.Column("target_revision_before", sa.Integer(), nullable=False),
        sa.Column("target_revision_after", sa.Integer(), nullable=False),
        sa.Column("command", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("resolution_input", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rng_version", sa.String(60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "resolution_type IN ('second_wind', 'death_save', 'stabilize')",
            name="combat_health_resolution_type",
        ),
        sa.CheckConstraint(
            "actor_revision_after >= actor_revision_before AND "
            "target_revision_after > target_revision_before",
            name="combat_health_revision_progress",
        ),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["command_id"], ["combat_commands.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["actor_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["target_combatant_id"], ["combatants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["ruleset_release_id"], ["ruleset_releases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["combat_catalog_id"], ["ruleset_data_catalogs.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("command_id"),
    )
    for column in ("encounter_id", "actor_combatant_id", "target_combatant_id"):
        op.create_index(
            op.f(f"ix_combat_health_resolutions_{column}"),
            "combat_health_resolutions",
            [column],
        )

    op.create_table(
        "combat_outcome_resolutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "outcome IN ('victory', 'defeat', 'surrender', 'flight', 'agreement')",
            name="combat_outcome_resolution_outcome",
        ),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["command_id"], ["combat_commands.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("encounter_id"),
        sa.UniqueConstraint("command_id"),
    )

    op.create_table(
        "combat_dropped_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attack_resolution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_id", sa.String(80), nullable=False),
        sa.Column("item_name", sa.String(120), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("recovered", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("quantity > 0", name="combat_dropped_item_quantity_positive"),
        sa.ForeignKeyConstraint(["encounter_id"], ["combat_encounters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["attack_resolution_id"], ["combat_attack_resolutions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["owner_character_id"], ["characters.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attack_resolution_id"),
    )
    op.create_index(
        op.f("ix_combat_dropped_items_encounter_id"), "combat_dropped_items", ["encounter_id"]
    )
    op.create_index(
        op.f("ix_combat_dropped_items_owner_character_id"),
        "combat_dropped_items",
        ["owner_character_id"],
    )

    op.execute(
        """
        CREATE FUNCTION gandalfdnd_prevent_combat_health_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'combat_health_resolutions is immutable';
        END;
        $$;
        CREATE TRIGGER combat_health_resolutions_immutable
        BEFORE UPDATE OR DELETE ON combat_health_resolutions
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_combat_health_mutation();

        CREATE FUNCTION gandalfdnd_prevent_combat_outcome_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'combat_outcome_resolutions is immutable';
        END;
        $$;
        CREATE TRIGGER combat_outcome_resolutions_immutable
        BEFORE UPDATE OR DELETE ON combat_outcome_resolutions
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_prevent_combat_outcome_mutation();

        CREATE FUNCTION gandalfdnd_validate_combat_health_scope()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM combat_encounters encounter
                JOIN combatants actor ON actor.id = NEW.actor_combatant_id
                                     AND actor.encounter_id = encounter.id
                JOIN combatants target ON target.id = NEW.target_combatant_id
                                      AND target.encounter_id = encounter.id
                JOIN combat_commands command ON command.id = NEW.command_id
                                            AND command.encounter_id = encounter.id
                                            AND command.command_type = 'combat_health'
                WHERE encounter.id = NEW.encounter_id
                  AND encounter.ruleset_release_id = NEW.ruleset_release_id
                  AND encounter.combat_catalog_id = NEW.combat_catalog_id
            ) THEN
                RAISE EXCEPTION 'combat health identities and pins must share one encounter';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER combat_health_scope
        BEFORE INSERT ON combat_health_resolutions
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combat_health_scope();

        CREATE FUNCTION gandalfdnd_validate_combatant_second_wind()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.character_id IS NOT NULL AND EXISTS (
                SELECT 1
                FROM combat_encounters encounter
                JOIN characters character ON character.id = NEW.character_id
                WHERE encounter.id = NEW.encounter_id
                  AND encounter.status IN ('setup', 'tie_pending', 'active')
                  AND COALESCE((character.resources ->> 'second_wind')::integer, 0)
                      <> NEW.second_wind_remaining
            ) THEN
                RAISE EXCEPTION 'active combatant Second Wind must match canonical character state';
            END IF;
            RETURN NULL;
        END;
        $$;
        CREATE CONSTRAINT TRIGGER combatant_character_second_wind_consistency
        AFTER INSERT OR UPDATE ON combatants
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_combatant_second_wind();

        CREATE FUNCTION gandalfdnd_validate_character_combat_second_wind()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM combatants combatant
                JOIN combat_encounters encounter ON encounter.id = combatant.encounter_id
                WHERE combatant.character_id = NEW.id
                  AND encounter.status IN ('setup', 'tie_pending', 'active')
                  AND combatant.second_wind_remaining
                      <> COALESCE((NEW.resources ->> 'second_wind')::integer, 0)
            ) THEN
                RAISE EXCEPTION
                    'canonical Second Wind must match active combatant state';
            END IF;
            RETURN NULL;
        END;
        $$;
        CREATE CONSTRAINT TRIGGER character_combat_second_wind_consistency
        AFTER UPDATE ON characters
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION gandalfdnd_validate_character_combat_second_wind();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM combat_health_resolutions) OR
               EXISTS (SELECT 1 FROM combat_outcome_resolutions) OR
               EXISTS (SELECT 1 FROM combat_dropped_items) OR
               EXISTS (SELECT 1 FROM combat_encounters WHERE outcome IS NOT NULL) THEN
                RAISE EXCEPTION
                    'Cannot downgrade after combat health or outcomes have been recorded';
            END IF;
        END;
        $$;
        """
    )
    # ``IF EXISTS`` keeps the downgrade recoverable if development was interrupted
    # after this revision was applied but before a newly added guard was installed.
    op.execute("DROP TRIGGER IF EXISTS character_combat_second_wind_consistency ON characters")
    op.execute("DROP FUNCTION IF EXISTS gandalfdnd_validate_character_combat_second_wind()")
    op.execute("DROP TRIGGER combatant_character_second_wind_consistency ON combatants")
    op.execute("DROP FUNCTION gandalfdnd_validate_combatant_second_wind()")
    op.execute("DROP TRIGGER combat_health_scope ON combat_health_resolutions")
    op.execute("DROP FUNCTION gandalfdnd_validate_combat_health_scope()")
    op.execute("DROP TRIGGER combat_outcome_resolutions_immutable ON combat_outcome_resolutions")
    op.execute("DROP FUNCTION gandalfdnd_prevent_combat_outcome_mutation()")
    op.execute("DROP TRIGGER combat_health_resolutions_immutable ON combat_health_resolutions")
    op.execute("DROP FUNCTION gandalfdnd_prevent_combat_health_mutation()")
    op.drop_index(
        op.f("ix_combat_dropped_items_owner_character_id"),
        table_name="combat_dropped_items",
    )
    op.drop_index(op.f("ix_combat_dropped_items_encounter_id"), table_name="combat_dropped_items")
    op.drop_table("combat_dropped_items")
    op.drop_table("combat_outcome_resolutions")
    for column in ("target_combatant_id", "actor_combatant_id", "encounter_id"):
        op.drop_index(
            op.f(f"ix_combat_health_resolutions_{column}"),
            table_name="combat_health_resolutions",
        )
    op.drop_table("combat_health_resolutions")
    op.drop_constraint("combat_command_type", "combat_commands", type_="check")
    op.create_check_constraint(
        "combat_command_type",
        "combat_commands",
        "command_type IN ('create_encounter', 'start_initiative', "
        "'resolve_initiative_tie', 'combat_move', 'combat_action', "
        "'combat_reaction', 'end_combat_turn', 'combat_attack')",
    )
    op.drop_constraint("combatant_second_wind_shape", "combatants", type_="check")
    op.drop_constraint("combatant_death_save_bounds", "combatants", type_="check")
    op.drop_column("combatants", "second_wind_remaining")
    op.drop_column("combatants", "death_save_failures")
    op.drop_column("combatants", "death_save_successes")
    op.drop_constraint("combat_encounter_completion_shape", "combat_encounters", type_="check")
    op.drop_constraint("combat_encounter_outcome", "combat_encounters", type_="check")
    op.drop_constraint("combat_encounter_xp_budgets", "combat_encounters", type_="check")
    op.drop_constraint("combat_encounter_difficulty_label", "combat_encounters", type_="check")
    for column in (
        "completed_at",
        "outcome_summary",
        "outcome",
        "high_xp_budget",
        "moderate_xp_budget",
        "low_xp_budget",
        "enemy_xp",
        "difficulty_label",
    ):
        op.drop_column("combat_encounters", column)
