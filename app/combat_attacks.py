from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.character_creation import CharacterSheet
from app.character_state import Loadout
from app.combat import (
    CombatError,
    CombatRulesCatalog,
    apply_damage,
    resolve_character_attack,
    resolve_damage_at_zero,
    resolve_monster_attack,
)
from app.combat_turns import _reject_unresolved_reactions
from app.dice import DiceService
from app.models import (
    Campaign,
    Character,
    Combatant,
    CombatAttackResolution,
    CombatCommand,
    CombatDroppedItem,
    CombatEffect,
    CombatEncounter,
    CombatReactionWindow,
    CombatTurn,
    DiceRoll,
)
from app.resolution import determine_advantage_state
from app.schemas import (
    CombatAttackCreate,
    CombatAttackExecutionRead,
    CombatAttackReplayRead,
    CombatAttackResolutionRead,
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


def _distance_feet(first: Combatant, second: Combatant) -> int:
    return (
        max(
            abs(first.position_x - second.position_x),
            abs(first.position_y - second.position_y),
        )
        * 5
    )


def _record_roll(
    session: Session,
    *,
    campaign: Campaign,
    encounter: CombatEncounter,
    command: CombatCommand,
    actor: Combatant,
    index: int,
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
        roll_index=index,
    )
    session.add(roll)
    session.flush()
    return roll


def _attack_read(resolution: CombatAttackResolution) -> CombatAttackResolutionRead:
    return CombatAttackResolutionRead.model_validate(resolution)


def _existing_attack(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatAttackCreate,
) -> CombatAttackExecutionRead | None:
    payload = data.model_dump(mode="json")
    command = _existing_combat_command(
        session, campaign_id, data.command_id, "combat_attack", payload
    )
    if command is None:
        return None
    if command.encounter_id != encounter_id:
        raise ConflictError("Existing combat command belongs to a different encounter")
    resolution = session.scalar(
        select(CombatAttackResolution).where(CombatAttackResolution.command_id == command.id)
    )
    encounter = session.get(CombatEncounter, encounter_id)
    if resolution is None or encounter is None:
        raise ConflictError("Recorded combat attack is incomplete")
    return CombatAttackExecutionRead(
        resolution=_attack_read(resolution),
        encounter=_combat_encounter_read(session, encounter),
    )


def execute_combat_attack(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatAttackCreate,
    dice_service: DiceService | None = None,
) -> CombatAttackExecutionRead:
    _campaign_for_update(session, campaign_id)
    existing = _existing_attack(session, campaign_id, encounter_id, data)
    if existing is not None:
        return existing
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
        raise ConflictError("Combat attacks require an active encounter")
    if encounter.revision != data.expected_encounter_revision:
        raise ConflictError(
            f"Stale encounter revision: expected {data.expected_encounter_revision}, "
            f"current {encounter.revision}"
        )
    participants = list(
        session.scalars(
            select(Combatant)
            .where(
                Combatant.encounter_id == encounter_id,
                Combatant.id.in_((data.actor_combatant_id, data.target_combatant_id)),
            )
            .order_by(Combatant.id)
            .with_for_update()
        )
    )
    if len(participants) != 2:
        raise NotFoundError("Attacking or target combatant not found")
    actor, target = participants
    if actor.id != data.actor_combatant_id:
        actor, target = target, actor
    if actor.revision != data.expected_actor_revision:
        raise ConflictError(
            f"Stale attacking combatant revision: expected {data.expected_actor_revision}, "
            f"current {actor.revision}"
        )
    if target.revision != data.expected_target_revision:
        raise ConflictError(
            f"Stale target combatant revision: expected {data.expected_target_revision}, "
            f"current {target.revision}"
        )
    if actor.side == target.side:
        raise ConflictError("Combat attacks require an opposing-side target")
    if actor.state != "active":
        raise ConflictError("Attacker must be active")
    if target.state not in {"active", "unconscious", "stable"}:
        raise ConflictError("Target cannot be attacked in its current state")

    campaign = session.get(Campaign, campaign_id)
    assert campaign is not None
    loaded, catalog, creation_catalog, state_catalog = _load_combat_catalog(
        session, campaign, encounter.combat_catalog_id
    )
    if (
        not isinstance(catalog, CombatRulesCatalog)
        or loaded.sha256 != encounter.combat_catalog_sha256
    ):
        raise ConflictError("Pinned combat catalog is unavailable")
    if target.state != "active" and catalog.id != "srd-5.2.1-combat-v2":
        raise ConflictError("Damage at 0 HP requires the combat-v2 rules catalog")
    if data.knock_out and catalog.id != "srd-5.2.1-combat-v2":
        raise ConflictError("Knockout requires the combat-v2 rules catalog")
    if data.knock_out and data.attack_mode != "melee":
        raise ConflictError("Only a melee attack can knock a creature out")
    turn = session.scalar(
        select(CombatTurn)
        .where(CombatTurn.encounter_id == encounter_id, CombatTurn.status == "active")
        .with_for_update()
    )
    if turn is None:
        raise ConflictError("Active encounter has no active turn")
    reaction_window: CombatReactionWindow | None = None
    if data.reaction_window_id is None:
        _reject_unresolved_reactions(session, encounter_id)
        if turn.combatant_id != actor.id:
            raise ConflictError("Combatant is not the active turn actor")
        if not turn.action_available:
            raise ConflictError("The active turn Action has already been spent")
    else:
        reaction_window = session.scalar(
            select(CombatReactionWindow)
            .where(
                CombatReactionWindow.id == data.reaction_window_id,
                CombatReactionWindow.encounter_id == encounter_id,
            )
            .with_for_update()
        )
        if reaction_window is None:
            raise NotFoundError("Opportunity Attack window not found")
        if (
            reaction_window.status != "opportunity_attack_pending"
            or reaction_window.reactor_combatant_id != actor.id
            or reaction_window.mover_combatant_id != target.id
        ):
            raise ConflictError("Opportunity Attack window does not match actor and target")
        if data.attack_mode != "melee":
            raise ConflictError("Opportunity Attacks must use a melee attack")

    weapons = {weapon.id: weapon for weapon in catalog.weapons}
    fighting_style_id: str | None = None
    mastery_enabled = False
    character: Character | None = None
    monster_id: str | None = None
    attack_modifier: int
    damage_modifier: int
    if actor.character_id is not None:
        character = session.scalar(
            select(Character)
            .where(Character.id == actor.character_id, Character.campaign_id == campaign_id)
            .with_for_update()
        )
        if character is None:
            raise ConflictError("Attacking character is unavailable")
        if data.attack_definition_id not in {"greatsword", "flail", "javelin"}:
            raise ConflictError("Unsupported player-character attack definition")
        weapon = weapons[data.attack_definition_id]
        if character.inventory.get(weapon.name, 0) < 1:
            raise ConflictError(f"Character has no {weapon.name} available")
        character_read = _character_read(session, character, creation_catalog, state_catalog)
        mechanics = character_read.mechanical_state
        if mechanics is None:
            raise ConflictError("Attacking character has no canonical mechanical state")
        attack_modifier = (
            mechanics.ability_modifiers["strength"].value + mechanics.proficiency_bonus.value
        )
        damage_modifier = mechanics.ability_modifiers["strength"].value
        sheet = CharacterSheet.model_validate(character.character_sheet)
        style_by_key = {
            "srd-5.2.1:feat.fighting_style.archery": "archery",
            "srd-5.2.1:feat.fighting_style.defense": "defense",
            "srd-5.2.1:feat.fighting_style.great_weapon_fighting": "great_weapon_fighting",
            "srd-5.2.1:feat.fighting_style.two_weapon_fighting": "two_weapon_fighting",
        }
        fighting_style_id = style_by_key.get(sheet.fighting_style_definition_key)
        mastery_enabled = data.use_mastery and (
            f"srd-5.2.1:weapon.{weapon.id}" in sheet.weapon_mastery_definition_keys
        )
        loadout = Loadout.model_validate(character.equipped_items)
        if weapon.id not in loadout.held_item_ids:
            if not turn.free_interaction_available:
                raise ConflictError("No free interaction remains to equip the attack weapon")
            loadout.held_item_ids = [weapon.id]
            character.equipped_items = loadout.model_dump(mode="json")
            character.state_revision += 1
            turn.free_interaction_available = False
    else:
        monster_id = actor.monster_definition_id
        monster = next((item for item in catalog.monsters if item.id == monster_id), None)
        if monster is None:
            raise ConflictError("Attacking monster definition is unavailable")
        attack = next(
            (item for item in monster.attacks if item.id == data.attack_definition_id),
            None,
        )
        if attack is None:
            raise ConflictError("Unsupported attack for this monster")
        weapon = weapons[attack.weapon_id]
        attack_modifier = attack.attack_modifier
        damage_modifier = attack.damage_modifier

    distance = _distance_feet(actor, target)
    target_state_before = target.state
    target_was_down = target.hp == 0 and target.state in {"unconscious", "stable"}
    critical_on_hit = target_was_down and distance <= 5
    disadvantage_sources: list[str] = []
    advantage_sources: list[str] = []
    if data.attack_mode == "melee":
        if distance > weapon.reach_feet:
            raise ConflictError("Melee target is outside weapon reach")
    else:
        if weapon.normal_range_feet is None or weapon.long_range_feet is None:
            raise ConflictError("Selected weapon has no ranged attack")
        if distance > weapon.long_range_feet:
            raise ConflictError("Ranged target is beyond the weapon's long range")
        if distance > weapon.normal_range_feet:
            disadvantage_sources.append("long_range")
        hostile_adjacent = session.scalar(
            select(Combatant.id).where(
                Combatant.encounter_id == encounter_id,
                Combatant.side != actor.side,
                Combatant.state == "active",
                Combatant.position_x.between(actor.position_x - 1, actor.position_x + 1),
                Combatant.position_y.between(actor.position_y - 1, actor.position_y + 1),
            )
        )
        if hostile_adjacent is not None:
            disadvantage_sources.append("hostile_within_5_feet")
    if target_was_down:
        advantage_sources.append("target_unconscious")
    dodge_effect = session.scalar(
        select(CombatEffect).where(
            CombatEffect.encounter_id == encounter_id,
            CombatEffect.target_combatant_id == target.id,
            CombatEffect.effect_id == "dodge",
            CombatEffect.status == "active",
        )
    )
    if dodge_effect is not None:
        disadvantage_sources.append("target_dodging")
    sap_effect = session.scalar(
        select(CombatEffect)
        .where(
            CombatEffect.encounter_id == encounter_id,
            CombatEffect.target_combatant_id == actor.id,
            CombatEffect.effect_id == "sap",
            CombatEffect.status == "active",
        )
        .with_for_update()
    )
    if sap_effect is not None:
        disadvantage_sources.append("sap")

    advantage_state = determine_advantage_state(
        has_advantage=bool(advantage_sources),
        has_disadvantage=bool(disadvantage_sources),
    )
    roller = dice_service or DiceService()
    attack_roll = roller.roll("1d20" if advantage_state == "normal" else "2d20")
    selected = (
        max(attack_roll.rolls)
        if advantage_state == "advantage"
        else min(attack_roll.rolls)
        if advantage_state == "disadvantage"
        else attack_roll.rolls[0]
    )
    applied_attack_modifier = attack_modifier
    if fighting_style_id == "archery" and weapon.weapon_kind == "ranged":
        applied_attack_modifier += 2
    hit = selected == 20 or (
        selected != 1 and selected + applied_attack_modifier >= target.armor_class
    )
    critical = selected == 20 or (critical_on_hit and hit)
    damage_faces: list[int] = []
    bonus_faces: list[int] = []
    if hit:
        count = weapon.damage_dice.count * (2 if critical else 1)
        damage_faces = roller.roll(f"{count}d{weapon.damage_dice.sides}").rolls
        if monster_id is not None:
            monster = next(item for item in catalog.monsters if item.id == monster_id)
            attack = next(item for item in monster.attacks if item.id == data.attack_definition_id)
            if attack.advantage_bonus_damage_dice is not None and advantage_state == "advantage":
                bonus_count = attack.advantage_bonus_damage_dice.count * (2 if critical else 1)
                bonus_faces = roller.roll(
                    f"{bonus_count}d{attack.advantage_bonus_damage_dice.sides}"
                ).rolls

    try:
        if character is not None:
            resolved = resolve_character_attack(
                catalog,
                weapon_id=weapon.id,
                attack_mode=data.attack_mode,
                attack_modifier=attack_modifier,
                damage_modifier=damage_modifier,
                target_armor_class=target.armor_class,
                attack_dice_faces=attack_roll.rolls,
                damage_dice_faces=damage_faces,
                advantage_sources=advantage_sources,
                disadvantage_sources=disadvantage_sources,
                fighting_style_id=fighting_style_id,
                mastery_enabled=mastery_enabled,
                critical_on_hit=critical_on_hit,
            )
        else:
            assert monster_id is not None
            resolved = resolve_monster_attack(
                catalog,
                monster_id=monster_id,
                attack_id=data.attack_definition_id,
                attack_mode=data.attack_mode,
                target_armor_class=target.armor_class,
                attack_dice_faces=attack_roll.rolls,
                damage_dice_faces=damage_faces,
                bonus_damage_dice_faces=bonus_faces,
                advantage_sources=advantage_sources,
                disadvantage_sources=disadvantage_sources,
                critical_on_hit=critical_on_hit,
            )
        damage = apply_damage(
            catalog,
            current_hit_points=target.hp,
            maximum_hit_points=target.max_hp,
            temporary_hit_points=target.temporary_hp,
            damage=resolved.damage_total,
        )
    except CombatError as exc:
        raise ConflictError(str(exc)) from exc

    actor_before = actor.revision
    target_before = target.revision
    next_revision = encounter.revision + 1
    resolution_id = uuid.uuid4()
    command = CombatCommand(
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="combat_attack",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=data.model_dump(mode="json"),
        result={
            "encounter_id": str(encounter_id),
            "encounter_revision": next_revision,
            "attack_resolution_id": str(resolution_id),
        },
    )
    session.add(command)
    session.flush()
    attack_dice = _record_roll(
        session,
        campaign=campaign,
        encounter=encounter,
        command=command,
        actor=actor,
        index=0,
        notation="1d20" if resolved.d20.advantage_state == "normal" else "2d20",
        faces=resolved.d20.dice_faces,
        modifier=resolved.d20.modifier,
        total=resolved.d20.total,
        purpose=f"combat attack: {actor.instance_name} -> {target.instance_name}",
    )
    damage_dice: DiceRoll | None = None
    if resolved.weapon_damage is not None:
        damage_dice = _record_roll(
            session,
            campaign=campaign,
            encounter=encounter,
            command=command,
            actor=actor,
            index=1,
            notation=resolved.weapon_damage.notation,
            faces=resolved.weapon_damage.original_faces,
            modifier=resolved.damage_modifier,
            total=resolved.weapon_damage.subtotal + resolved.damage_modifier,
            purpose=f"combat damage: {actor.instance_name} -> {target.instance_name}",
        )
    bonus_dice: DiceRoll | None = None
    if resolved.bonus_damage is not None:
        bonus_dice = _record_roll(
            session,
            campaign=campaign,
            encounter=encounter,
            command=command,
            actor=actor,
            index=2,
            notation=resolved.bonus_damage.notation,
            faces=resolved.bonus_damage.original_faces,
            modifier=0,
            total=resolved.bonus_damage.subtotal,
            purpose=f"combat bonus damage: {actor.instance_name} -> {target.instance_name}",
        )
    if data.reaction_window_id is None:
        turn.action_available = False
    else:
        assert reaction_window is not None
        reaction_window.status = "opportunity_attack_resolved"
    if sap_effect is not None:
        sap_effect.status = "expired"
        sap_effect.ended_round = encounter.round_number
    target.hp = damage.hit_points_after
    target.temporary_hp = damage.temporary_hit_points_after
    damage_at_zero: dict | None = None
    knocked_out = False
    if (
        data.knock_out
        and resolved.hit
        and target_was_down is False
        and damage.hit_points_after == 0
    ):
        target.hp = 1
        target.state = "unconscious"
        target.death_save_successes = 0
        target.death_save_failures = 0
        knocked_out = True
    elif target_was_down and damage.after_vulnerability > damage.temporary_hit_points_absorbed:
        zero_result = resolve_damage_at_zero(
            catalog,
            damage=damage.after_vulnerability - damage.temporary_hit_points_absorbed,
            maximum_hit_points=target.max_hp,
            failures=target.death_save_failures,
            critical=resolved.critical,
        )
        target.death_save_failures = zero_result.failures_after
        target.state = zero_result.state_after
        damage_at_zero = zero_result.model_dump(mode="json")
    elif target.hp == 0:
        if target.character_id is None or damage.excess_damage >= target.max_hp:
            target.state = "dead"
        else:
            target.state = "unconscious"
            target.death_save_successes = 0
            target.death_save_failures = 0
    if target.character_id is not None and resolved.damage_total > 0:
        target_character = session.scalar(
            select(Character).where(Character.id == target.character_id).with_for_update()
        )
        if target_character is None:
            raise ConflictError("Target character state is unavailable")
        target_character.hp = target.hp
        target_character.state_revision += 1
    if character is not None and data.attack_mode == "ranged" and weapon.id == "javelin":
        inventory = dict(character.inventory)
        inventory[weapon.name] -= 1
        if inventory[weapon.name] == 0:
            inventory.pop(weapon.name)
        character.inventory = inventory
        character.state_revision += 1
    actor.revision += 1
    target.revision += 1
    encounter.revision = next_revision
    if resolved.applied_effect_id is not None:
        existing_effect = session.scalar(
            select(CombatEffect).where(
                CombatEffect.encounter_id == encounter_id,
                CombatEffect.target_combatant_id == target.id,
                CombatEffect.stacking_key == resolved.applied_effect_id,
                CombatEffect.status == "active",
            )
        )
        if existing_effect is not None:
            existing_effect.status = "expired"
            existing_effect.ended_round = encounter.round_number
            session.flush()
        session.add(
            CombatEffect(
                encounter_id=encounter_id,
                source_combatant_id=actor.id,
                target_combatant_id=target.id,
                effect_id=resolved.applied_effect_id,
                stacking_key=resolved.applied_effect_id,
                status="active",
                starts_round=encounter.round_number,
                expires_on_source_turn_start=True,
                ended_round=None,
                created_by_command_id=command.id,
            )
        )
        if resolved.applied_effect_id == "slow" and turn.combatant_id == target.id:
            turn.movement_allowance_feet = max(
                turn.movement_spent_feet, turn.movement_allowance_feet - 10
            )
    resolution_input = {
        "actor_kind": "character" if character is not None else "monster",
        "monster_id": monster_id,
        "weapon_id": weapon.id,
        "attack_definition_id": data.attack_definition_id,
        "attack_mode": data.attack_mode,
        "attack_modifier": attack_modifier,
        "damage_modifier": damage_modifier,
        "target_armor_class": target.armor_class,
        "advantage_sources": advantage_sources,
        "disadvantage_sources": disadvantage_sources,
        "fighting_style_id": fighting_style_id,
        "mastery_enabled": mastery_enabled,
        "critical_on_hit": critical_on_hit,
        "target_state_before": target_state_before,
        "target_hp_before": damage.hit_points_before,
        "target_max_hp": target.max_hp,
        "target_temporary_hp_before": damage.temporary_hit_points_before,
        "attack_roll_id": str(attack_dice.id),
        "damage_roll_id": str(damage_dice.id) if damage_dice else None,
        "bonus_damage_roll_id": str(bonus_dice.id) if bonus_dice else None,
        "knock_out": data.knock_out,
    }
    resolution = CombatAttackResolution(
        id=resolution_id,
        encounter_id=encounter_id,
        command_id=command.id,
        actor_combatant_id=actor.id,
        target_combatant_id=target.id,
        reaction_window_id=data.reaction_window_id,
        ruleset_release_id=encounter.ruleset_release_id,
        combat_catalog_id=encounter.combat_catalog_id,
        resolver_version=encounter.resolver_version,
        actor_revision_before=actor_before,
        actor_revision_after=actor.revision,
        target_revision_before=target_before,
        target_revision_after=target.revision,
        command=data.model_dump(mode="json"),
        resolution_input=resolution_input,
        attack_result=resolved.model_dump(mode="json"),
        damage_result=damage.model_dump(mode="json"),
        rng_version=roller.algorithm_version,
    )
    session.add(resolution)
    session.flush()
    if character is not None and data.attack_mode == "ranged" and weapon.id == "javelin":
        session.add(
            CombatDroppedItem(
                encounter_id=encounter_id,
                attack_resolution_id=resolution.id,
                owner_character_id=character.id,
                item_id=weapon.id,
                item_name=weapon.name,
                quantity=1,
                recovered=False,
            )
        )
    _combat_event(
        session,
        encounter_id,
        "combat_attack_resolved",
        {
            "command_id": str(data.command_id),
            "attack_resolution_id": str(resolution.id),
            "actor_combatant_id": str(actor.id),
            "target_combatant_id": str(target.id),
            "reaction_window_id": (
                str(data.reaction_window_id) if data.reaction_window_id else None
            ),
            "attack": resolution.attack_result,
            "damage": resolution.damage_result,
            "damage_at_zero": damage_at_zero,
            "knocked_out": knocked_out,
            "dice_roll_ids": [
                str(item.id) for item in (attack_dice, damage_dice, bonus_dice) if item is not None
            ],
            "encounter_revision": encounter.revision,
        },
    )
    _add_event(
        session,
        campaign_id,
        "combat_attack_resolved",
        {
            "encounter_id": str(encounter_id),
            "attack_resolution_id": str(resolution.id),
            "actor_combatant_id": str(actor.id),
            "target_combatant_id": str(target.id),
            "hit": resolved.hit,
            "critical": resolved.critical,
            "damage_total": resolved.damage_total,
            "target_hp_after": target.hp,
            "target_state_after": target.state,
            "damage_at_zero": damage_at_zero,
            "knocked_out": knocked_out,
            "encounter_revision": encounter.revision,
        },
        actor_character_id=actor.character_id,
    )
    from app.combat_health import maybe_complete_combat_encounter

    if catalog.id == "srd-5.2.1-combat-v2":
        maybe_complete_combat_encounter(session, campaign, encounter, command)
    session.commit()
    return CombatAttackExecutionRead(
        resolution=_attack_read(resolution),
        encounter=_combat_encounter_read(session, encounter),
    )


def replay_combat_attack(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    resolution_id: uuid.UUID,
) -> CombatAttackReplayRead:
    resolution = session.scalar(
        select(CombatAttackResolution).where(
            CombatAttackResolution.id == resolution_id,
            CombatAttackResolution.encounter_id == encounter_id,
        )
    )
    encounter = session.scalar(
        select(CombatEncounter).where(
            CombatEncounter.id == encounter_id,
            CombatEncounter.campaign_id == campaign_id,
        )
    )
    if resolution is None or encounter is None:
        raise NotFoundError("Combat attack resolution not found")
    campaign = session.get(Campaign, campaign_id)
    assert campaign is not None
    _loaded, catalog, _creation, _state = _load_combat_catalog(
        session, campaign, resolution.combat_catalog_id
    )
    inputs = dict(resolution.resolution_input)
    attack_roll = session.get(DiceRoll, uuid.UUID(inputs["attack_roll_id"]))
    damage_roll = (
        session.get(DiceRoll, uuid.UUID(inputs["damage_roll_id"]))
        if inputs["damage_roll_id"]
        else None
    )
    bonus_roll = (
        session.get(DiceRoll, uuid.UUID(inputs["bonus_damage_roll_id"]))
        if inputs["bonus_damage_roll_id"]
        else None
    )
    if attack_roll is None:
        raise ConflictError("Stored combat attack dice are unavailable")
    try:
        if inputs["actor_kind"] == "character":
            replayed = resolve_character_attack(
                catalog,
                weapon_id=inputs["weapon_id"],
                attack_mode=inputs["attack_mode"],
                attack_modifier=inputs["attack_modifier"],
                damage_modifier=inputs["damage_modifier"],
                target_armor_class=inputs["target_armor_class"],
                attack_dice_faces=list(attack_roll.rolls),
                damage_dice_faces=list(damage_roll.rolls) if damage_roll else [],
                advantage_sources=inputs["advantage_sources"],
                disadvantage_sources=inputs["disadvantage_sources"],
                fighting_style_id=inputs["fighting_style_id"],
                mastery_enabled=inputs["mastery_enabled"],
                critical_on_hit=inputs.get("critical_on_hit", False),
            )
        else:
            replayed = resolve_monster_attack(
                catalog,
                monster_id=inputs["monster_id"],
                attack_id=inputs["attack_definition_id"],
                attack_mode=inputs["attack_mode"],
                target_armor_class=inputs["target_armor_class"],
                attack_dice_faces=list(attack_roll.rolls),
                damage_dice_faces=list(damage_roll.rolls) if damage_roll else [],
                bonus_damage_dice_faces=list(bonus_roll.rolls) if bonus_roll else [],
                advantage_sources=inputs["advantage_sources"],
                disadvantage_sources=inputs["disadvantage_sources"],
                critical_on_hit=inputs.get("critical_on_hit", False),
            )
        damage = apply_damage(
            catalog,
            current_hit_points=inputs["target_hp_before"],
            maximum_hit_points=inputs["target_max_hp"],
            temporary_hit_points=inputs["target_temporary_hp_before"],
            damage=replayed.damage_total,
        )
    except CombatError as exc:
        raise ConflictError(str(exc)) from exc
    equivalent = (
        replayed.model_dump(mode="json") == resolution.attack_result
        and damage.model_dump(mode="json") == resolution.damage_result
        and replayed.resolver_version == resolution.resolver_version
    )
    return CombatAttackReplayRead(
        resolution_id=resolution.id,
        equivalent=equivalent,
        encounter_id=encounter_id,
    )
