from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.combat import (
    CombatError,
    resolve_death_save,
    resolve_second_wind,
    resolve_stabilization,
)
from app.combat_turns import _reject_unresolved_reactions
from app.dice import DiceService
from app.models import (
    Campaign,
    Character,
    Combatant,
    CombatCommand,
    CombatDroppedItem,
    CombatEncounter,
    CombatHealthResolution,
    CombatOutcomeResolution,
    CombatTurn,
    DiceRoll,
)
from app.schemas import (
    CombatHealthCreate,
    CombatHealthExecutionRead,
    CombatHealthResolutionRead,
    CombatOutcomeCreate,
    CombatOutcomeExecutionRead,
    CombatOutcomeResolutionRead,
)
from app.services import (
    ConflictError,
    NotFoundError,
    _add_event,
    _campaign_for_update,
    _character_read,
    _combat_encounter_read,
    _combat_event,
    _existing_combat_command,
    _load_combat_catalog,
)


def _record_health_roll(
    session: Session,
    *,
    campaign: Campaign,
    encounter: CombatEncounter,
    command: CombatCommand,
    actor: Combatant,
    notation: str,
    faces: list[int],
    modifier: int,
    total: int,
    purpose: str,
) -> DiceRoll:
    roll = DiceRoll(
        campaign_id=campaign.id,
        ruleset_release_id=encounter.ruleset_release_id,
        ruleset_data_catalog_id=encounter.combat_catalog_id,
        turn_id=None,
        notation=notation,
        rolls=faces,
        modifier=modifier,
        total=total,
        purpose=purpose,
        hidden=False,
        actor_character_id=actor.character_id,
        combat_encounter_id=encounter.id,
        combatant_id=actor.id,
        combat_command_id=command.id,
        roll_index=0,
    )
    session.add(roll)
    session.flush()
    return roll


def _locked_encounter(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    expected_revision: int,
) -> tuple[Campaign, CombatEncounter]:
    campaign = _campaign_for_update(session, campaign_id)
    encounter = session.scalar(
        select(CombatEncounter)
        .where(
            CombatEncounter.id == encounter_id,
            CombatEncounter.campaign_id == campaign_id,
        )
        .with_for_update()
    )
    if encounter is None:
        raise NotFoundError("Combat encounter not found")
    if encounter.status != "active":
        raise ConflictError("Combat health commands require an active encounter")
    if encounter.revision != expected_revision:
        raise ConflictError(
            f"Stale encounter revision: expected {expected_revision}, current {encounter.revision}"
        )
    if encounter.combat_catalog_id != "srd-5.2.1-combat-v2":
        raise ConflictError("Combat health commands require the combat-v2 rules catalog")
    return campaign, encounter


def _locked_combatants(
    session: Session,
    encounter_id: uuid.UUID,
    actor_id: uuid.UUID,
    target_id: uuid.UUID,
) -> tuple[Combatant, Combatant]:
    identifiers = {actor_id, target_id}
    rows = list(
        session.scalars(
            select(Combatant)
            .where(Combatant.encounter_id == encounter_id, Combatant.id.in_(identifiers))
            .order_by(Combatant.id)
            .with_for_update()
        )
    )
    if len(rows) != len(identifiers):
        raise NotFoundError("Acting or target combatant not found")
    by_id = {row.id: row for row in rows}
    return by_id[actor_id], by_id[target_id]


def _active_turn(session: Session, encounter: CombatEncounter, actor: Combatant) -> CombatTurn:
    turn = session.scalar(
        select(CombatTurn)
        .where(CombatTurn.encounter_id == encounter.id, CombatTurn.status == "active")
        .with_for_update()
    )
    if turn is None or turn.combatant_id != actor.id:
        raise ConflictError("Combatant is not the active turn actor")
    return turn


def _sync_character_hp(session: Session, combatant: Combatant) -> Character | None:
    if combatant.character_id is None:
        return None
    character = session.scalar(
        select(Character).where(Character.id == combatant.character_id).with_for_update()
    )
    if character is None:
        raise ConflictError("Canonical character state is unavailable")
    character.hp = combatant.hp
    character.state_revision += 1
    return character


def execute_combat_health(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatHealthCreate,
    dice_service: DiceService | None = None,
) -> CombatHealthExecutionRead:
    payload = data.model_dump(mode="json")
    _campaign_for_update(session, campaign_id)
    existing = _existing_combat_command(
        session, campaign_id, data.command_id, "combat_health", payload
    )
    if existing is not None:
        resolution = session.scalar(
            select(CombatHealthResolution).where(CombatHealthResolution.command_id == existing.id)
        )
        encounter = session.get(CombatEncounter, encounter_id)
        if resolution is None or encounter is None or existing.encounter_id != encounter_id:
            raise ConflictError("Recorded combat health command is incomplete")
        return CombatHealthExecutionRead(
            resolution=CombatHealthResolutionRead.model_validate(resolution),
            encounter=_combat_encounter_read(session, encounter),
        )

    campaign, encounter = _locked_encounter(
        session, campaign_id, encounter_id, data.expected_encounter_revision
    )
    actor, target = _locked_combatants(
        session, encounter_id, data.actor_combatant_id, data.target_combatant_id
    )
    if actor.revision != data.expected_actor_revision:
        raise ConflictError(
            f"Stale acting combatant revision: expected {data.expected_actor_revision}, "
            f"current {actor.revision}"
        )
    if target.revision != data.expected_target_revision:
        raise ConflictError(
            f"Stale target combatant revision: expected {data.expected_target_revision}, "
            f"current {target.revision}"
        )
    _reject_unresolved_reactions(session, encounter_id)
    turn = _active_turn(session, encounter, actor)
    loaded, catalog, creation_catalog, state_catalog = _load_combat_catalog(
        session, campaign, encounter.combat_catalog_id
    )
    if loaded.sha256 != encounter.combat_catalog_sha256:
        raise ConflictError("Pinned combat catalog hash is unavailable")

    actor_before = actor.revision
    target_before = target.revision
    input_snapshot: dict[str, Any] = {
        "actor_hp": actor.hp,
        "target_hp": target.hp,
        "target_temporary_hp": target.temporary_hp,
        "target_state": target.state,
        "target_death_save_successes": target.death_save_successes,
        "target_death_save_failures": target.death_save_failures,
    }
    result: dict[str, Any]
    roll_notation: str | None = None
    roll_faces: list[int] = []
    roll_modifier = 0
    roll_total = 0
    character: Character | None = None
    roller = dice_service or DiceService()
    try:
        if data.action == "second_wind":
            if actor.state != "active" or actor.character_id is None:
                raise ConflictError("Second Wind requires an active player character")
            if not turn.bonus_action_available:
                raise ConflictError("The active turn Bonus Action has already been spent")
            character = session.scalar(
                select(Character).where(Character.id == actor.character_id).with_for_update()
            )
            if character is None:
                raise ConflictError("Canonical character state is unavailable")
            mechanics = _character_read(
                session, character, creation_catalog, state_catalog
            ).mechanical_state
            if mechanics is None:
                raise ConflictError("Character has no canonical mechanical state")
            roll = roller.roll("1d10")
            resolved = resolve_second_wind(
                catalog,
                current_hit_points=actor.hp,
                maximum_hit_points=actor.max_hp,
                temporary_hit_points=actor.temporary_hp,
                uses_remaining=actor.second_wind_remaining or 0,
                die_face=roll.rolls[0],
                fighter_level=mechanics.level,
            )
            actor.hp = resolved.healing.hit_points_after
            actor.second_wind_remaining = resolved.uses_after
            resources = dict(character.resources)
            resources["second_wind"] = resolved.uses_after
            character.resources = resources
            character.hp = actor.hp
            character.state_revision += 1
            turn.bonus_action_available = False
            result = resolved.model_dump(mode="json")
            roll_notation = "1d10"
            roll_faces = [resolved.die_face]
            roll_total = resolved.die_face + resolved.fighter_level
        elif data.action == "death_save":
            if actor.character_id is None or actor.hp != 0 or actor.state != "unconscious":
                raise ConflictError("Death saves require an unconscious player character at 0 HP")
            roll = roller.roll("1d20")
            resolved = resolve_death_save(
                catalog,
                die_face=roll.rolls[0],
                successes=actor.death_save_successes,
                failures=actor.death_save_failures,
            )
            actor.hp = resolved.hit_points_after
            actor.state = resolved.state_after
            actor.death_save_successes = resolved.successes_after
            actor.death_save_failures = resolved.failures_after
            _sync_character_hp(session, actor)
            result = resolved.model_dump(mode="json")
            roll_notation = "1d20"
            roll_faces = [resolved.die_face]
            roll_total = resolved.die_face
        elif data.action == "stabilize":
            if actor.state != "active" or actor.character_id is None:
                raise ConflictError("First aid requires an active player character")
            if target.character_id is None or target.hp != 0 or target.state != "unconscious":
                raise ConflictError(
                    "First aid target must be an unconscious player character at 0 HP"
                )
            if (
                max(
                    abs(actor.position_x - target.position_x),
                    abs(actor.position_y - target.position_y),
                )
                > 1
            ):
                raise ConflictError("First aid target must be within 5 feet")
            if not turn.action_available:
                raise ConflictError("The active turn Action has already been spent")
            character = session.scalar(
                select(Character).where(Character.id == actor.character_id).with_for_update()
            )
            if character is None:
                raise ConflictError("Canonical character state is unavailable")
            mechanics = _character_read(
                session, character, creation_catalog, state_catalog
            ).mechanical_state
            if mechanics is None:
                raise ConflictError("Character has no canonical mechanical state")
            medicine_modifier = mechanics.skills["medicine"].value
            roll = roller.roll("1d20")
            resolved = resolve_stabilization(
                catalog, die_face=roll.rolls[0], medicine_modifier=medicine_modifier
            )
            if resolved.success:
                target.state = "stable"
                target.death_save_successes = 0
                target.death_save_failures = 0
            turn.action_available = False
            result = resolved.model_dump(mode="json")
            roll_notation = "1d20"
            roll_faces = [resolved.d20.selected_die]
            roll_modifier = medicine_modifier
            roll_total = resolved.d20.total
    except CombatError as exc:
        raise ConflictError(str(exc)) from exc

    if actor.id == target.id:
        actor.revision += 1
    else:
        actor.revision += 1
        target.revision += 1
    encounter.revision += 1
    resolution_id = uuid.uuid4()
    command = CombatCommand(
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="combat_health",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=payload,
        result={
            "encounter_id": str(encounter_id),
            "encounter_revision": encounter.revision,
            "health_resolution_id": str(resolution_id),
        },
    )
    session.add(command)
    session.flush()
    roll_id: str | None = None
    if roll_notation is not None:
        recorded = _record_health_roll(
            session,
            campaign=campaign,
            encounter=encounter,
            command=command,
            actor=actor,
            notation=roll_notation,
            faces=roll_faces,
            modifier=roll_modifier,
            total=roll_total,
            purpose=f"combat {data.action}: {actor.instance_name}",
        )
        roll_id = str(recorded.id)
    input_snapshot["dice_roll_id"] = roll_id
    resolution = CombatHealthResolution(
        id=resolution_id,
        encounter_id=encounter_id,
        command_id=command.id,
        actor_combatant_id=actor.id,
        target_combatant_id=target.id,
        resolution_type=data.action,
        ruleset_release_id=encounter.ruleset_release_id,
        combat_catalog_id=encounter.combat_catalog_id,
        resolver_version=encounter.resolver_version,
        actor_revision_before=actor_before,
        actor_revision_after=actor.revision,
        target_revision_before=target_before,
        target_revision_after=target.revision,
        command=payload,
        resolution_input=input_snapshot,
        result=result,
        rng_version=roller.algorithm_version,
    )
    session.add(resolution)
    _combat_event(
        session,
        encounter_id,
        "combat_health_resolved",
        {
            "command_id": str(data.command_id),
            "health_resolution_id": str(resolution_id),
            "action": data.action,
            "actor_combatant_id": str(actor.id),
            "target_combatant_id": str(target.id),
            "result": result,
            "dice_roll_id": roll_id,
            "encounter_revision": encounter.revision,
        },
    )
    _add_event(
        session,
        campaign_id,
        "combat_health_resolved",
        {
            "encounter_id": str(encounter_id),
            "health_resolution_id": str(resolution_id),
            "action": data.action,
            "target_hp": target.hp,
            "target_state": target.state,
            "encounter_revision": encounter.revision,
        },
        actor_character_id=actor.character_id,
    )
    session.commit()
    return CombatHealthExecutionRead(
        resolution=CombatHealthResolutionRead.model_validate(resolution),
        encounter=_combat_encounter_read(session, encounter),
    )


def _recover_dropped_items(session: Session, encounter_id: uuid.UUID) -> list[dict[str, Any]]:
    recovered: list[dict[str, Any]] = []
    drops = list(
        session.scalars(
            select(CombatDroppedItem)
            .where(
                CombatDroppedItem.encounter_id == encounter_id,
                CombatDroppedItem.recovered.is_(False),
            )
            .with_for_update()
        )
    )
    for drop in drops:
        character = session.scalar(
            select(Character).where(Character.id == drop.owner_character_id).with_for_update()
        )
        if character is None:
            raise ConflictError("Thrown item owner is unavailable")
        inventory = dict(character.inventory)
        inventory[drop.item_name] = inventory.get(drop.item_name, 0) + drop.quantity
        character.inventory = inventory
        character.state_revision += 1
        drop.recovered = True
        recovered.append(
            {
                "character_id": str(character.id),
                "item_id": drop.item_id,
                "item_name": drop.item_name,
                "quantity": drop.quantity,
            }
        )
    return recovered


def complete_combat_encounter(
    session: Session,
    campaign: Campaign,
    encounter: CombatEncounter,
    command: CombatCommand,
    *,
    outcome: str,
    affected_side: str | None = None,
    resolution_id: uuid.UUID | None = None,
) -> CombatOutcomeResolution:
    if encounter.status == "completed":
        existing = session.scalar(
            select(CombatOutcomeResolution).where(
                CombatOutcomeResolution.encounter_id == encounter.id
            )
        )
        if existing is None:
            raise ConflictError("Completed encounter has no outcome evidence")
        return existing
    if outcome in {"surrender", "flight"}:
        assert affected_side is not None
        new_state = "surrendered" if outcome == "surrender" else "fled"
        for combatant in session.scalars(
            select(Combatant)
            .where(
                Combatant.encounter_id == encounter.id,
                Combatant.side == affected_side,
                Combatant.state.notin_(("dead", "fled", "surrendered")),
            )
            .with_for_update()
        ):
            combatant.state = new_state
            combatant.revision += 1
    recover_items = outcome in {"victory", "agreement"} or (
        outcome == "surrender" and affected_side == "enemy"
    )
    recovered = _recover_dropped_items(session, encounter.id) if recover_items else []
    combatants = list(
        session.scalars(select(Combatant).where(Combatant.encounter_id == encounter.id))
    )
    summary = {
        "outcome": outcome,
        "affected_side": affected_side,
        "rounds": encounter.round_number,
        "difficulty": {
            "label": encounter.difficulty_label,
            "enemy_xp": encounter.enemy_xp,
            "low_xp_budget": encounter.low_xp_budget,
            "moderate_xp_budget": encounter.moderate_xp_budget,
            "high_xp_budget": encounter.high_xp_budget,
            "interpretation": "published XP input, not a guaranteed balance result",
        },
        "party": [
            {"combatant_id": str(row.id), "hp": row.hp, "state": row.state}
            for row in combatants
            if row.side == "party"
        ],
        "enemies": [
            {"combatant_id": str(row.id), "hp": row.hp, "state": row.state}
            for row in combatants
            if row.side == "enemy"
        ],
        "recovered_items": recovered,
    }
    active_turn = session.scalar(
        select(CombatTurn).where(
            CombatTurn.encounter_id == encounter.id, CombatTurn.status == "active"
        )
    )
    if active_turn is not None:
        active_turn.status = "completed"
        active_turn.completed_encounter_revision = encounter.revision
    encounter.status = "completed"
    encounter.active_turn_index = None
    encounter.outcome = outcome
    encounter.outcome_summary = summary
    encounter.completed_at = datetime.now(UTC)
    campaign.world_revision += 1
    resolution = CombatOutcomeResolution(
        id=resolution_id or uuid.uuid4(),
        encounter_id=encounter.id,
        command_id=command.id,
        outcome=outcome,
        summary=summary,
    )
    session.add(resolution)
    session.flush()
    _combat_event(
        session,
        encounter.id,
        "combat_encounter_completed",
        {
            "outcome_resolution_id": str(resolution.id),
            "command_id": str(command.command_id),
            **summary,
            "world_revision": campaign.world_revision,
        },
    )
    _add_event(
        session,
        campaign.id,
        "combat_encounter_completed",
        {
            "encounter_id": str(encounter.id),
            "outcome_resolution_id": str(resolution.id),
            **summary,
            "world_revision": campaign.world_revision,
        },
    )
    return resolution


def maybe_complete_combat_encounter(
    session: Session,
    campaign: Campaign,
    encounter: CombatEncounter,
    command: CombatCommand,
) -> CombatOutcomeResolution | None:
    combatants = list(
        session.scalars(select(Combatant).where(Combatant.encounter_id == encounter.id))
    )
    party_can_fight = any(row.side == "party" and row.state == "active" for row in combatants)
    enemy_can_fight = any(row.side == "enemy" and row.state == "active" for row in combatants)
    if not enemy_can_fight:
        return complete_combat_encounter(session, campaign, encounter, command, outcome="victory")
    if not party_can_fight:
        return complete_combat_encounter(session, campaign, encounter, command, outcome="defeat")
    return None


def resolve_combat_outcome(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatOutcomeCreate,
) -> CombatOutcomeExecutionRead:
    payload = data.model_dump(mode="json")
    _campaign_for_update(session, campaign_id)
    existing = _existing_combat_command(
        session, campaign_id, data.command_id, "combat_outcome", payload
    )
    if existing is not None:
        resolution = session.scalar(
            select(CombatOutcomeResolution).where(CombatOutcomeResolution.command_id == existing.id)
        )
        encounter = session.get(CombatEncounter, encounter_id)
        if resolution is None or encounter is None or existing.encounter_id != encounter_id:
            raise ConflictError("Recorded combat outcome command is incomplete")
        return CombatOutcomeExecutionRead(
            resolution=CombatOutcomeResolutionRead.model_validate(resolution),
            encounter=_combat_encounter_read(session, encounter),
        )
    campaign, encounter = _locked_encounter(
        session, campaign_id, encounter_id, data.expected_encounter_revision
    )
    _reject_unresolved_reactions(session, encounter_id)
    encounter.revision += 1
    resolution_id = uuid.uuid4()
    command = CombatCommand(
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="combat_outcome",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=payload,
        result={
            "encounter_id": str(encounter_id),
            "encounter_revision": encounter.revision,
            "outcome_resolution_id": str(resolution_id),
            "outcome": data.outcome,
        },
    )
    session.add(command)
    session.flush()
    resolution = complete_combat_encounter(
        session,
        campaign,
        encounter,
        command,
        outcome=data.outcome,
        affected_side=data.affected_side,
        resolution_id=resolution_id,
    )
    session.commit()
    return CombatOutcomeExecutionRead(
        resolution=CombatOutcomeResolutionRead.model_validate(resolution),
        encounter=_combat_encounter_read(session, encounter),
    )
