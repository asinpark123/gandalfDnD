from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Campaign,
    Combatant,
    CombatCommand,
    CombatEffect,
    CombatEncounter,
    CombatReactionWindow,
    CombatTurn,
)
from app.schemas import (
    CombatActionCreate,
    CombatEncounterRead,
    CombatEndTurnCreate,
    CombatMoveCreate,
    CombatReactionCreate,
)
from app.services import (
    ConflictError,
    NotFoundError,
    _add_event,
    _campaign_for_update,
    _combat_encounter_read,
    _combat_event,
    _create_active_combat_turn,
    _existing_combat_command,
)


def _encounter_actor_turn(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    actor_id: uuid.UUID,
    *,
    expected_encounter_revision: int,
    expected_combatant_revision: int,
    allowed_states: tuple[str, ...] = ("active",),
) -> tuple[Campaign, CombatEncounter, Combatant, CombatTurn]:
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
        raise ConflictError("Combat turn commands require an active encounter")
    if encounter.revision != expected_encounter_revision:
        raise ConflictError(
            f"Stale encounter revision: expected {expected_encounter_revision}, "
            f"current {encounter.revision}"
        )
    actor = session.scalar(
        select(Combatant)
        .where(Combatant.id == actor_id, Combatant.encounter_id == encounter_id)
        .with_for_update()
    )
    if actor is None:
        raise NotFoundError("Acting combatant not found in encounter")
    if actor.revision != expected_combatant_revision:
        raise ConflictError(
            f"Stale combatant revision: expected {expected_combatant_revision}, "
            f"current {actor.revision}"
        )
    if actor.state not in allowed_states:
        raise ConflictError("Acting combatant cannot act in its current state")
    turn = session.scalar(
        select(CombatTurn)
        .where(CombatTurn.encounter_id == encounter_id, CombatTurn.status == "active")
        .with_for_update()
    )
    if turn is None:
        raise ConflictError("Active encounter has no active turn")
    if turn.combatant_id != actor.id or encounter.active_turn_index != actor.initiative_order:
        raise ConflictError("Combatant is not the active turn actor")
    return campaign, encounter, actor, turn


def _unresolved_reaction_windows(
    session: Session, encounter_id: uuid.UUID
) -> list[CombatReactionWindow]:
    return list(
        session.scalars(
            select(CombatReactionWindow)
            .where(
                CombatReactionWindow.encounter_id == encounter_id,
                CombatReactionWindow.status.in_(("pending", "opportunity_attack_pending")),
            )
            .order_by(CombatReactionWindow.created_at, CombatReactionWindow.id)
        )
    )


def _reject_unresolved_reactions(session: Session, encounter_id: uuid.UUID) -> None:
    windows = _unresolved_reaction_windows(session, encounter_id)
    if not windows:
        return
    if any(window.status == "opportunity_attack_pending" for window in windows):
        raise ConflictError(
            "A selected Opportunity Attack must resolve before the active turn can continue"
        )
    raise ConflictError("Every pending reaction window must receive an explicit response")


def _new_command(
    session: Session,
    *,
    command_id: uuid.UUID,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    command_type: str,
    expected_encounter_revision: int,
    payload: dict[str, Any],
    result: dict[str, Any],
) -> CombatCommand:
    command = CombatCommand(
        command_id=command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type=command_type,
        expected_encounter_revision=expected_encounter_revision,
        payload=payload,
        result=result,
    )
    session.add(command)
    session.flush()
    return command


def execute_combat_action(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatActionCreate,
) -> CombatEncounterRead:
    payload = data.model_dump(mode="json")
    _campaign_for_update(session, campaign_id)
    existing = _existing_combat_command(
        session, campaign_id, data.command_id, "combat_action", payload
    )
    if existing is not None:
        if existing.encounter_id != encounter_id:
            raise ConflictError("Existing combat command belongs to a different encounter")
        encounter = session.get(CombatEncounter, encounter_id)
        if encounter is None:
            raise ConflictError("Recorded combat command has no encounter")
        return _combat_encounter_read(session, encounter)
    campaign, encounter, actor, turn = _encounter_actor_turn(
        session,
        campaign_id,
        encounter_id,
        data.actor_combatant_id,
        expected_encounter_revision=data.expected_encounter_revision,
        expected_combatant_revision=data.expected_combatant_revision,
    )
    _reject_unresolved_reactions(session, encounter_id)
    if not turn.action_available:
        raise ConflictError("The active turn Action has already been spent")

    next_revision = encounter.revision + 1
    command = _new_command(
        session,
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="combat_action",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=payload,
        result={
            "encounter_id": str(encounter_id),
            "encounter_revision": next_revision,
            "action": data.action,
        },
    )
    turn.action_available = False
    if data.action == "dash":
        turn.movement_allowance_feet += actor.speed_feet
    elif data.action == "disengage":
        turn.disengaged = True
    else:
        existing_dodge = session.scalar(
            select(CombatEffect).where(
                CombatEffect.encounter_id == encounter_id,
                CombatEffect.target_combatant_id == actor.id,
                CombatEffect.stacking_key == "dodge",
                CombatEffect.status == "active",
            )
        )
        if existing_dodge is not None:
            raise ConflictError("Dodge is already active for this combatant")
        session.add(
            CombatEffect(
                encounter_id=encounter_id,
                source_combatant_id=actor.id,
                target_combatant_id=actor.id,
                effect_id="dodge",
                stacking_key="dodge",
                status="active",
                starts_round=encounter.round_number,
                expires_on_source_turn_start=True,
                ended_round=None,
                created_by_command_id=command.id,
            )
        )
    encounter.revision = next_revision
    actor.revision += 1
    session.flush()
    _combat_event(
        session,
        encounter_id,
        "combat_action_used",
        {
            "command_id": str(data.command_id),
            "actor_combatant_id": str(actor.id),
            "action": data.action,
            "action_available": False,
            "movement_allowance_feet": turn.movement_allowance_feet,
            "disengaged": turn.disengaged,
            "encounter_revision": encounter.revision,
            "combatant_revision": actor.revision,
        },
    )
    _add_event(
        session,
        campaign_id,
        "combat_action_used",
        {
            "encounter_id": str(encounter_id),
            "actor_combatant_id": str(actor.id),
            "action": data.action,
            "encounter_revision": encounter.revision,
        },
        actor_character_id=actor.character_id,
    )
    session.commit()
    return _combat_encounter_read(session, encounter)


def _distance_cells(ax: int, ay: int, bx: int, by: int) -> int:
    return max(abs(ax - bx), abs(ay - by))


def move_combatant(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatMoveCreate,
) -> CombatEncounterRead:
    payload = data.model_dump(mode="json")
    _campaign_for_update(session, campaign_id)
    existing = _existing_combat_command(
        session, campaign_id, data.command_id, "combat_move", payload
    )
    if existing is not None:
        if existing.encounter_id != encounter_id:
            raise ConflictError("Existing combat command belongs to a different encounter")
        encounter = session.get(CombatEncounter, encounter_id)
        if encounter is None:
            raise ConflictError("Recorded combat command has no encounter")
        return _combat_encounter_read(session, encounter)
    _campaign, encounter, actor, turn = _encounter_actor_turn(
        session,
        campaign_id,
        encounter_id,
        data.actor_combatant_id,
        expected_encounter_revision=data.expected_encounter_revision,
        expected_combatant_revision=data.expected_combatant_revision,
    )
    _reject_unresolved_reactions(session, encounter_id)
    requested_feet = len(data.path) * 5
    if turn.movement_spent_feet + requested_feet > turn.movement_allowance_feet:
        raise ConflictError("Movement path exceeds the active turn's remaining movement")
    combatants = list(
        session.scalars(
            select(Combatant).where(Combatant.encounter_id == encounter_id).with_for_update()
        )
    )
    occupied = {
        (item.position_x, item.position_y)
        for item in combatants
        if item.id != actor.id and item.state not in ("dead", "fled", "surrendered")
    }
    x, y = actor.position_x, actor.position_y
    triggers: list[tuple[Combatant, int, int, int, int]] = []
    for cell in data.path:
        if not (0 <= cell.x < encounter.grid_width and 0 <= cell.y < encounter.grid_height):
            raise ConflictError("Movement path leaves the encounter grid")
        if _distance_cells(x, y, cell.x, cell.y) != 1:
            raise ConflictError("Every movement path step must enter one adjacent 5-foot cell")
        if (cell.x, cell.y) in occupied:
            raise ConflictError("Movement path enters an occupied cell")
        if not turn.disengaged:
            for reactor in combatants:
                if (
                    reactor.side == actor.side
                    or reactor.state != "active"
                    or not reactor.reaction_available
                ):
                    continue
                leaving_reach = (
                    _distance_cells(x, y, reactor.position_x, reactor.position_y) <= 1
                    and _distance_cells(cell.x, cell.y, reactor.position_x, reactor.position_y) > 1
                )
                if not leaving_reach:
                    continue
                prior = session.scalar(
                    select(CombatReactionWindow).where(
                        CombatReactionWindow.encounter_id == encounter_id,
                        CombatReactionWindow.mover_combatant_id == actor.id,
                        CombatReactionWindow.reactor_combatant_id == reactor.id,
                        CombatReactionWindow.round_number == encounter.round_number,
                        CombatReactionWindow.from_x == x,
                        CombatReactionWindow.from_y == y,
                        CombatReactionWindow.to_x == cell.x,
                        CombatReactionWindow.to_y == cell.y,
                    )
                )
                if prior is None:
                    triggers.append((reactor, x, y, cell.x, cell.y))
                elif prior.status == "opportunity_attack_pending":
                    raise ConflictError(
                        "A selected Opportunity Attack must resolve before movement"
                    )
                elif prior.status == "pending":
                    raise ConflictError("Movement has an unanswered reaction window")
        x, y = cell.x, cell.y

    next_revision = encounter.revision + 1
    command = _new_command(
        session,
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="combat_move",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=payload,
        result={
            "encounter_id": str(encounter_id),
            "encounter_revision": next_revision,
            "movement_status": "reaction_pending" if triggers else "moved",
        },
    )
    encounter.revision = next_revision
    if triggers:
        windows: list[CombatReactionWindow] = []
        for reactor, from_x, from_y, to_x, to_y in triggers:
            window = CombatReactionWindow(
                encounter_id=encounter_id,
                mover_combatant_id=actor.id,
                reactor_combatant_id=reactor.id,
                opened_by_command_id=command.id,
                responded_by_command_id=None,
                round_number=encounter.round_number,
                from_x=from_x,
                from_y=from_y,
                to_x=to_x,
                to_y=to_y,
                status="pending",
                response=None,
                opened_encounter_revision=data.expected_encounter_revision,
                resolved_encounter_revision=None,
            )
            session.add(window)
            windows.append(window)
        session.flush()
        _combat_event(
            session,
            encounter_id,
            "reaction_windows_opened",
            {
                "command_id": str(data.command_id),
                "mover_combatant_id": str(actor.id),
                "reaction_window_ids": [str(window.id) for window in windows],
                "movement_committed": False,
                "encounter_revision": encounter.revision,
            },
        )
    else:
        actor.position_x = x
        actor.position_y = y
        actor.revision += 1
        turn.movement_spent_feet += requested_feet
        session.flush()
        _combat_event(
            session,
            encounter_id,
            "combatant_moved",
            {
                "command_id": str(data.command_id),
                "actor_combatant_id": str(actor.id),
                "path": [cell.model_dump(mode="json") for cell in data.path],
                "movement_spent_feet": turn.movement_spent_feet,
                "movement_remaining_feet": (
                    turn.movement_allowance_feet - turn.movement_spent_feet
                ),
                "position": {"x": actor.position_x, "y": actor.position_y},
                "encounter_revision": encounter.revision,
                "combatant_revision": actor.revision,
            },
        )
    session.commit()
    return _combat_encounter_read(session, encounter)


def respond_to_combat_reaction(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    window_id: uuid.UUID,
    data: CombatReactionCreate,
) -> CombatEncounterRead:
    payload = {**data.model_dump(mode="json"), "reaction_window_id": str(window_id)}
    _campaign_for_update(session, campaign_id)
    existing = _existing_combat_command(
        session, campaign_id, data.command_id, "combat_reaction", payload
    )
    if existing is not None:
        if existing.encounter_id != encounter_id:
            raise ConflictError("Existing combat command belongs to a different encounter")
        encounter = session.get(CombatEncounter, encounter_id)
        if encounter is None:
            raise ConflictError("Recorded combat command has no encounter")
        return _combat_encounter_read(session, encounter)
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
        raise ConflictError("Reaction responses require an active encounter")
    if encounter.revision != data.expected_encounter_revision:
        raise ConflictError(
            f"Stale encounter revision: expected {data.expected_encounter_revision}, "
            f"current {encounter.revision}"
        )
    window = session.scalar(
        select(CombatReactionWindow)
        .where(
            CombatReactionWindow.id == window_id,
            CombatReactionWindow.encounter_id == encounter_id,
        )
        .with_for_update()
    )
    if window is None:
        raise NotFoundError("Combat reaction window not found")
    if window.status != "pending":
        raise ConflictError("Combat reaction window has already received a response")
    if window.reactor_combatant_id != data.reactor_combatant_id:
        raise ConflictError("Only the named reactor can answer this reaction window")
    reactor = session.scalar(
        select(Combatant)
        .where(
            Combatant.id == data.reactor_combatant_id,
            Combatant.encounter_id == encounter_id,
        )
        .with_for_update()
    )
    if reactor is None:
        raise NotFoundError("Reacting combatant not found")
    if reactor.revision != data.expected_combatant_revision:
        raise ConflictError(
            f"Stale combatant revision: expected {data.expected_combatant_revision}, "
            f"current {reactor.revision}"
        )
    if reactor.state != "active" or not reactor.reaction_available:
        raise ConflictError("Reacting combatant has no available Reaction")
    next_revision = encounter.revision + 1
    command = _new_command(
        session,
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="combat_reaction",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=payload,
        result={
            "encounter_id": str(encounter_id),
            "encounter_revision": next_revision,
            "reaction_window_id": str(window_id),
            "response": data.response,
        },
    )
    window.responded_by_command_id = command.id
    window.response = data.response
    window.resolved_encounter_revision = next_revision
    if data.response == "pass":
        window.status = "passed"
    else:
        window.status = "opportunity_attack_pending"
        reactor.reaction_available = False
        reactor.revision += 1
    encounter.revision = next_revision
    session.flush()
    _combat_event(
        session,
        encounter_id,
        "reaction_response_recorded",
        {
            "command_id": str(data.command_id),
            "reaction_window_id": str(window.id),
            "reactor_combatant_id": str(reactor.id),
            "response": data.response,
            "reaction_available": reactor.reaction_available,
            "encounter_revision": encounter.revision,
            "combatant_revision": reactor.revision,
        },
    )
    session.commit()
    return _combat_encounter_read(session, encounter)


def end_combat_turn(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatEndTurnCreate,
) -> CombatEncounterRead:
    payload = data.model_dump(mode="json")
    _campaign_for_update(session, campaign_id)
    existing = _existing_combat_command(
        session, campaign_id, data.command_id, "end_combat_turn", payload
    )
    if existing is not None:
        if existing.encounter_id != encounter_id:
            raise ConflictError("Existing combat command belongs to a different encounter")
        encounter = session.get(CombatEncounter, encounter_id)
        if encounter is None:
            raise ConflictError("Recorded combat command has no encounter")
        return _combat_encounter_read(session, encounter)
    campaign, encounter, actor, turn = _encounter_actor_turn(
        session,
        campaign_id,
        encounter_id,
        data.actor_combatant_id,
        expected_encounter_revision=data.expected_encounter_revision,
        expected_combatant_revision=data.expected_combatant_revision,
        allowed_states=("active", "unconscious", "stable"),
    )
    _reject_unresolved_reactions(session, encounter_id)
    combatants = list(
        session.scalars(
            select(Combatant)
            .where(Combatant.encounter_id == encounter_id)
            .order_by(Combatant.initiative_order)
            .with_for_update()
        )
    )
    ordered = [
        item
        for item in combatants
        if item.initiative_order is not None and item.state not in ("dead", "fled", "surrendered")
    ]
    if not ordered:
        raise ConflictError("Encounter has no combatants able to take another turn")
    next_revision = encounter.revision + 1
    _new_command(
        session,
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="end_combat_turn",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=payload,
        result={
            "encounter_id": str(encounter_id),
            "encounter_revision": next_revision,
        },
    )
    turn.status = "completed"
    turn.completed_encounter_revision = next_revision
    encounter.revision = next_revision
    current_position = next(index for index, item in enumerate(ordered) if item.id == actor.id)
    next_position = (current_position + 1) % len(ordered)
    if next_position == 0:
        encounter.round_number += 1
    next_actor = ordered[next_position]
    encounter.active_turn_index = next_actor.initiative_order
    session.flush()
    next_turn = _create_active_combat_turn(session, encounter, combatants)
    _combat_event(
        session,
        encounter_id,
        "combat_turn_ended",
        {
            "command_id": str(data.command_id),
            "actor_combatant_id": str(actor.id),
            "completed_round": turn.round_number,
            "completed_turn_index": turn.turn_index,
            "next_combatant_id": str(next_actor.id),
            "round_number": encounter.round_number,
            "turn_index": encounter.active_turn_index,
            "encounter_revision": encounter.revision,
        },
    )
    _combat_event(
        session,
        encounter_id,
        "combat_turn_started",
        {
            "combat_turn_id": str(next_turn.id),
            "combatant_id": str(next_actor.id),
            "round_number": encounter.round_number,
            "turn_index": encounter.active_turn_index,
            "movement_allowance_feet": next_turn.movement_allowance_feet,
            "encounter_revision": encounter.revision,
        },
    )
    _add_event(
        session,
        campaign.id,
        "combat_turn_advanced",
        {
            "encounter_id": str(encounter_id),
            "next_combatant_id": str(next_actor.id),
            "round_number": encounter.round_number,
            "turn_index": encounter.active_turn_index,
            "encounter_revision": encounter.revision,
        },
        actor_character_id=actor.character_id,
    )
    session.commit()
    return _combat_encounter_read(session, encounter)
