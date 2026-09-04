import json
from copy import deepcopy
from pathlib import Path

import pytest

from app.combat import (
    CombatError,
    CombatRulesCatalog,
    apply_damage,
    apply_healing,
    apply_temporary_hit_points,
    resolve_character_attack,
    resolve_damage_at_zero,
    resolve_death_save,
    resolve_effect_boundary,
    resolve_initiative,
    resolve_monster_attack,
    resolve_second_wind,
    resolve_stabilization,
)
from app.rulesets import RulesetRegistry

REPOSITORY_ROOT = Path(__file__).parents[1]


def _combat_catalog_raw() -> dict:
    return json.loads((REPOSITORY_ROOT / "rulesets/srd-5.2.1/data/combat-v1.json").read_text())


@pytest.fixture(scope="module")
def combat_catalog() -> CombatRulesCatalog:
    registry = RulesetRegistry.load(REPOSITORY_ROOT / "rulesets/registry.json")
    loaded = registry.get_combat_catalogs(
        "srd-5.2.1",
        "srd-5.2.1-party-state-v1",
        "srd-5.2.1-combat-v1",
    )
    assert isinstance(loaded.combat.document, CombatRulesCatalog)
    return loaded.combat.document


@pytest.fixture(scope="module")
def combat_health_catalog() -> CombatRulesCatalog:
    registry = RulesetRegistry.load(REPOSITORY_ROOT / "rulesets/registry.json")
    loaded = registry.get_combat_catalogs(
        "srd-5.2.1",
        "srd-5.2.1-party-state-v1",
        "srd-5.2.1-combat-v2",
    )
    assert isinstance(loaded.combat.document, CombatRulesCatalog)
    return loaded.combat.document


def test_combat_v2_adds_exact_health_rule_slice_without_mutating_v1(
    combat_health_catalog: CombatRulesCatalog,
) -> None:
    assert combat_health_catalog.schema_version == "1.1.0"
    assert combat_health_catalog.resolver_version == "combat-resolution-1.1.0"
    assert {
        "second_wind",
        "unconscious_at_zero",
        "death_saves",
        "stabilization",
        "damage_at_zero",
        "instant_death",
        "melee_knockout",
        "encounter_outcomes",
    } <= {rule.id for rule in combat_health_catalog.rules}
    assert (
        RulesetRegistry.load(REPOSITORY_ROOT / "rulesets/registry.json")
        .get_data_catalog("srd-5.2.1", "srd-5.2.1-combat-v1")
        .sha256
        == "423b80e84593738d4cadc5537278d208a51fbebacbb074a2d79531f0ee023204"
    )


def test_combat_catalog_is_strict_source_cited_and_complete(
    combat_catalog: CombatRulesCatalog,
) -> None:
    assert combat_catalog.id == "srd-5.2.1-combat-v1"
    assert combat_catalog.resolver_version == "combat-resolution-1.0.0"
    assert {weapon.id for weapon in combat_catalog.weapons} == {
        "dagger",
        "flail",
        "greatsword",
        "javelin",
        "scimitar",
        "shortbow",
    }
    assert {mastery.id for mastery in combat_catalog.masteries} == {"graze", "sap", "slow"}
    assert {monster.id for monster in combat_catalog.monsters} == {
        "goblin_minion",
        "goblin_warrior",
    }

    weapons = {weapon.id: weapon for weapon in combat_catalog.weapons}
    assert weapons["greatsword"].damage_dice.notation == "2d6"
    assert weapons["greatsword"].properties == ["heavy", "two_handed"]
    assert weapons["javelin"].weapon_kind == "melee"
    assert (weapons["javelin"].normal_range_feet, weapons["javelin"].long_range_feet) == (
        30,
        120,
    )
    assert weapons["dagger"].printed_mastery_id == "nick"
    assert weapons["dagger"].supported_mastery_id is None
    assert {
        weapon.id for weapon in combat_catalog.weapons if weapon.player_character_supported
    } == {
        "flail",
        "greatsword",
        "javelin",
    }

    monsters = {monster.id: monster for monster in combat_catalog.monsters}
    assert (monsters["goblin_minion"].armor_class, monsters["goblin_minion"].hit_points) == (
        12,
        7,
    )
    assert (monsters["goblin_warrior"].armor_class, monsters["goblin_warrior"].hit_points) == (
        15,
        10,
    )
    assert monsters["goblin_warrior"].attacks[0].advantage_bonus_damage_dice is not None
    assert combat_catalog.encounter_budget.model_dump()["high_xp_per_character"] == 100

    raw = _combat_catalog_raw()
    raw["weapons"][0]["unexpected_rule"] = 999
    with pytest.raises(ValueError):
        CombatRulesCatalog.model_validate(raw)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda raw: raw["sources"].append(deepcopy(raw["sources"][0])), "source IDs"),
        (
            lambda raw: raw["rules"][1].update(definition_key=raw["rules"][0]["definition_key"]),
            "definition keys",
        ),
        (lambda raw: raw["rules"][0].update(source_ids=["missing"]), "unknown source"),
        (
            lambda raw: raw["monsters"][0]["attacks"][0].update(source_ids=["missing"]),
            "unknown source",
        ),
        (lambda raw: raw["rules"].pop(), "complete versioned rule slice"),
        (lambda raw: raw["weapons"].pop(), "supported weapons"),
        (
            lambda raw: raw["weapons"][0].update(player_character_supported=False),
            "limit player attacks",
        ),
        (lambda raw: raw["fighting_styles"].pop(), "Fighter styles"),
        (lambda raw: raw["masteries"].pop(), "Graze, Sap, and Slow"),
        (lambda raw: raw["effects"].pop(), "required timed effects"),
        (lambda raw: raw["monsters"].pop(), "both supported Goblins"),
        (
            lambda raw: raw["masteries"][1].update(effect_id="missing"),
            "unsupported effect",
        ),
        (
            lambda raw: raw["monsters"][1]["attacks"][1].update(
                id=raw["monsters"][1]["attacks"][0]["id"]
            ),
            "attack IDs",
        ),
        (
            lambda raw: raw["monsters"][0]["attacks"][0].update(weapon_id="missing"),
            "unsupported weapon",
        ),
    ],
)
def test_combat_catalog_rejects_broken_identity_and_references(mutation, message: str) -> None:
    raw = _combat_catalog_raw()
    mutation(raw)
    with pytest.raises(ValueError, match=message):
        CombatRulesCatalog.model_validate(raw)


@pytest.mark.parametrize(
    ("weapon_update", "message"),
    [
        (
            {"normal_range_feet": None, "long_range_feet": None},
            "must define both ranges",
        ),
        ({"normal_range_feet": 330}, "ordered normal and long"),
        ({"properties": ["two_handed"]}, "must use ammunition"),
        (
            {
                "weapon_kind": "melee",
                "properties": ["ammunition"],
                "normal_range_feet": None,
                "long_range_feet": None,
            },
            "melee weapons cannot use ammunition",
        ),
    ],
)
def test_combat_catalog_rejects_invalid_weapon_range_semantics(
    weapon_update: dict, message: str
) -> None:
    raw = _combat_catalog_raw()
    raw["weapons"][5].update(weapon_update)
    with pytest.raises(ValueError, match=message):
        CombatRulesCatalog.model_validate(raw)


@pytest.mark.parametrize(
    ("mastery_index", "mastery_update", "message"),
    [
        (0, {"effect_id": "sap"}, "Graze-style"),
        (1, {"effect_id": None}, "timed masteries"),
        (1, {"speed_reduction_feet": 10}, "only Slow-style"),
    ],
)
def test_combat_catalog_rejects_invalid_mastery_semantics(
    mastery_index: int, mastery_update: dict, message: str
) -> None:
    raw = _combat_catalog_raw()
    raw["masteries"][mastery_index].update(mastery_update)
    with pytest.raises(ValueError, match=message):
        CombatRulesCatalog.model_validate(raw)


@pytest.mark.parametrize(
    ("style_index", "style_value", "message"),
    [
        (0, None, "must define their numeric value"),
        (3, 1, "cannot define a fixed numeric value"),
    ],
)
def test_combat_catalog_rejects_invalid_fighting_style_values(
    style_index: int, style_value: int | None, message: str
) -> None:
    raw = _combat_catalog_raw()
    raw["fighting_styles"][style_index]["value"] = style_value
    with pytest.raises(ValueError, match=message):
        CombatRulesCatalog.model_validate(raw)


def test_initiative_advantage_disadvantage_and_cancellation(
    combat_catalog: CombatRulesCatalog,
) -> None:
    advantage = resolve_initiative(
        combat_catalog,
        modifier=2,
        dice_faces=[4, 17],
        advantage_sources=["remarkable athlete"],
    )
    assert advantage.d20.advantage_state == "advantage"
    assert advantage.d20.selected_die == 17
    assert advantage.d20.total == 19

    disadvantage = resolve_initiative(
        combat_catalog,
        modifier=-1,
        dice_faces=[4, 17],
        disadvantage_sources=["poisoned"],
    )
    assert disadvantage.d20.advantage_state == "disadvantage"
    assert disadvantage.d20.selected_die == 4
    assert disadvantage.d20.total == 3

    cancelled = resolve_initiative(
        combat_catalog,
        modifier=4,
        dice_faces=[11],
        advantage_sources=["one source", "one source"],
        disadvantage_sources=["another source"],
    )
    assert cancelled.d20.advantage_state == "normal"
    assert cancelled.d20.total == 15
    assert cancelled.d20.advantage_sources == ["one source"]
    with pytest.raises(CombatError, match="exactly 2"):
        resolve_initiative(
            combat_catalog,
            modifier=2,
            dice_faces=[17],
            advantage_sources=["advantage"],
        )


def test_attack_natural_boundaries_equality_and_critical_dice(
    combat_catalog: CombatRulesCatalog,
) -> None:
    natural_one = resolve_character_attack(
        combat_catalog,
        weapon_id="flail",
        attack_mode="melee",
        attack_modifier=99,
        damage_modifier=3,
        target_armor_class=10,
        attack_dice_faces=[1],
        damage_dice_faces=[],
    )
    assert not natural_one.hit
    assert natural_one.miss_reason == "natural_one"
    assert natural_one.damage_total == 0

    equality = resolve_character_attack(
        combat_catalog,
        weapon_id="flail",
        attack_mode="melee",
        attack_modifier=5,
        damage_modifier=3,
        target_armor_class=15,
        attack_dice_faces=[10],
        damage_dice_faces=[4],
    )
    assert equality.hit
    assert not equality.critical
    assert equality.damage_total == 7

    natural_twenty = resolve_character_attack(
        combat_catalog,
        weapon_id="greatsword",
        attack_mode="melee",
        attack_modifier=-10,
        damage_modifier=3,
        target_armor_class=100,
        attack_dice_faces=[20],
        damage_dice_faces=[6, 5, 4, 3],
    )
    assert natural_twenty.hit
    assert natural_twenty.critical
    assert natural_twenty.weapon_damage is not None
    assert natural_twenty.weapon_damage.notation == "4d6"
    assert natural_twenty.weapon_damage.original_faces == [6, 5, 4, 3]
    assert natural_twenty.damage_total == 21


def test_great_weapon_fighting_changes_each_eligible_die_not_modifier(
    combat_catalog: CombatRulesCatalog,
) -> None:
    attack = resolve_character_attack(
        combat_catalog,
        weapon_id="greatsword",
        attack_mode="melee",
        attack_modifier=5,
        damage_modifier=3,
        target_armor_class=15,
        attack_dice_faces=[20],
        damage_dice_faces=[1, 2, 4, 6],
        fighting_style_id="great_weapon_fighting",
    )
    assert attack.weapon_damage is not None
    assert attack.weapon_damage.original_faces == [1, 2, 4, 6]
    assert attack.weapon_damage.adjusted_faces == [3, 3, 4, 6]
    assert attack.weapon_damage.adjustment == "great_weapon_fighting"
    assert attack.damage_total == 19
    assert (
        attack.rule_definition_keys.count("srd-5.2.1:feat.fighting_style.great_weapon_fighting")
        == 1
    )


def test_archery_does_not_apply_to_thrown_melee_weapon_and_broader_weapons_reject(
    combat_catalog: CombatRulesCatalog,
) -> None:
    thrown_javelin = resolve_character_attack(
        combat_catalog,
        weapon_id="javelin",
        attack_mode="ranged",
        attack_modifier=5,
        damage_modifier=3,
        target_armor_class=20,
        attack_dice_faces=[10],
        damage_dice_faces=[],
        fighting_style_id="archery",
    )
    assert thrown_javelin.d20.modifier == 5
    assert "srd-5.2.1:feat.fighting_style.archery" not in thrown_javelin.rule_definition_keys

    with pytest.raises(CombatError, match="not a supported M5 player-character weapon"):
        resolve_character_attack(
            combat_catalog,
            weapon_id="shortbow",
            attack_mode="ranged",
            attack_modifier=5,
            damage_modifier=3,
            target_armor_class=17,
            attack_dice_faces=[10],
            damage_dice_faces=[3],
            fighting_style_id="archery",
        )


def test_graze_sap_and_slow_have_exact_application_boundaries(
    combat_catalog: CombatRulesCatalog,
) -> None:
    graze = resolve_character_attack(
        combat_catalog,
        weapon_id="greatsword",
        attack_mode="melee",
        attack_modifier=5,
        damage_modifier=3,
        target_armor_class=99,
        attack_dice_faces=[1],
        damage_dice_faces=[],
        mastery_enabled=True,
    )
    assert not graze.hit
    assert graze.mastery_id == "graze"
    assert graze.mastery_applied
    assert graze.damage_total == 3
    assert graze.applied_effect_id is None

    sap = resolve_character_attack(
        combat_catalog,
        weapon_id="flail",
        attack_mode="melee",
        attack_modifier=5,
        damage_modifier=3,
        target_armor_class=15,
        attack_dice_faces=[10],
        damage_dice_faces=[4],
        mastery_enabled=True,
    )
    assert sap.mastery_applied
    assert sap.applied_effect_id == "sap"

    slow = resolve_character_attack(
        combat_catalog,
        weapon_id="javelin",
        attack_mode="ranged",
        attack_modifier=5,
        damage_modifier=0,
        target_armor_class=15,
        attack_dice_faces=[10],
        damage_dice_faces=[1],
        mastery_enabled=True,
    )
    assert slow.mastery_applied
    assert slow.applied_effect_id == "slow"

    no_damage = resolve_character_attack(
        combat_catalog,
        weapon_id="javelin",
        attack_mode="melee",
        attack_modifier=5,
        damage_modifier=-1,
        target_armor_class=15,
        attack_dice_faces=[10],
        damage_dice_faces=[1],
        mastery_enabled=True,
    )
    assert no_damage.hit
    assert no_damage.damage_total == 0
    assert not no_damage.mastery_applied


def test_goblin_attack_uses_catalog_modifiers_and_advantage_damage(
    combat_catalog: CombatRulesCatalog,
) -> None:
    attack = resolve_monster_attack(
        combat_catalog,
        monster_id="goblin_warrior",
        attack_id="scimitar",
        attack_mode="melee",
        target_armor_class=17,
        attack_dice_faces=[12, 18],
        damage_dice_faces=[6],
        bonus_damage_dice_faces=[4],
        advantage_sources=["hidden attacker"],
    )
    assert attack.d20.modifier == 4
    assert attack.hit
    assert attack.damage_total == 12
    assert attack.bonus_damage is not None
    assert attack.bonus_damage.original_faces == [4]
    assert "srd-5.2.1:monster.goblin_warrior" in attack.rule_definition_keys

    critical = resolve_monster_attack(
        combat_catalog,
        monster_id="goblin_warrior",
        attack_id="shortbow",
        attack_mode="ranged",
        target_armor_class=30,
        attack_dice_faces=[5, 20],
        damage_dice_faces=[1, 6],
        bonus_damage_dice_faces=[2, 4],
        advantage_sources=["hidden attacker"],
    )
    assert critical.critical
    assert critical.damage_total == 15
    assert critical.bonus_damage is not None
    assert critical.bonus_damage.critical
    assert critical.weapon_damage is not None
    assert critical.weapon_damage.notation == "2d6"
    assert critical.bonus_damage.notation == "2d4"


def test_attack_rejects_impossible_modes_and_inconsistent_dice(
    combat_catalog: CombatRulesCatalog,
) -> None:
    with pytest.raises(CombatError, match="does not support ranged"):
        resolve_character_attack(
            combat_catalog,
            weapon_id="greatsword",
            attack_mode="ranged",
            attack_modifier=5,
            damage_modifier=3,
            target_armor_class=10,
            attack_dice_faces=[10],
            damage_dice_faces=[4],
        )
    with pytest.raises(CombatError, match="missed attack"):
        resolve_character_attack(
            combat_catalog,
            weapon_id="flail",
            attack_mode="melee",
            attack_modifier=0,
            damage_modifier=3,
            target_armor_class=20,
            attack_dice_faces=[2],
            damage_dice_faces=[8],
        )
    with pytest.raises(CombatError, match="exactly 4"):
        resolve_character_attack(
            combat_catalog,
            weapon_id="greatsword",
            attack_mode="melee",
            attack_modifier=5,
            damage_modifier=3,
            target_armor_class=10,
            attack_dice_faces=[20],
            damage_dice_faces=[6, 6],
        )
    with pytest.raises(CombatError, match="not a supported M5 player-character weapon"):
        resolve_character_attack(
            combat_catalog,
            weapon_id="dagger",
            attack_mode="melee",
            attack_modifier=5,
            damage_modifier=3,
            target_armor_class=10,
            attack_dice_faces=[10],
            damage_dice_faces=[4],
            mastery_enabled=True,
        )


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"weapon_id": "unknown"}, "unsupported weapon"),
        ({"fighting_style_id": "unknown"}, "unsupported Fighting Style"),
        ({"attack_mode": "ranged"}, "does not support ranged"),
        ({"attack_mode": "magic"}, "attack mode"),
        ({"target_armor_class": 0}, "Armor Class"),
        ({"target_armor_class": True}, "Armor Class"),
        ({"attack_modifier": True}, "attack modifier"),
        ({"damage_modifier": True}, "damage modifier"),
        ({"attack_dice_faces": [21]}, "d20 faces"),
        ({"damage_dice_faces": [9]}, "within the die range"),
    ],
)
def test_character_attack_rejects_invalid_canonical_inputs(overrides: dict, message: str) -> None:
    catalog = CombatRulesCatalog.model_validate(_combat_catalog_raw())
    inputs = {
        "weapon_id": "flail",
        "attack_mode": "melee",
        "attack_modifier": 5,
        "damage_modifier": 3,
        "target_armor_class": 15,
        "attack_dice_faces": [10],
        "damage_dice_faces": [4],
    }
    inputs.update(overrides)
    with pytest.raises(CombatError, match=message):
        resolve_character_attack(catalog, **inputs)


def test_monster_attack_rejects_unknown_identity_and_unearned_bonus_dice(
    combat_catalog: CombatRulesCatalog,
) -> None:
    common = {
        "attack_mode": "melee",
        "target_armor_class": 12,
        "attack_dice_faces": [10],
        "damage_dice_faces": [3],
    }
    with pytest.raises(CombatError, match="unsupported monster"):
        resolve_monster_attack(
            combat_catalog,
            monster_id="unknown",
            attack_id="dagger",
            **common,
        )
    with pytest.raises(CombatError, match="unsupported attack"):
        resolve_monster_attack(
            combat_catalog,
            monster_id="goblin_minion",
            attack_id="unknown",
            **common,
        )
    with pytest.raises(CombatError, match="bonus damage does not apply"):
        resolve_monster_attack(
            combat_catalog,
            monster_id="goblin_warrior",
            attack_id="scimitar",
            bonus_damage_dice_faces=[4],
            **common,
        )


def test_damage_applies_resistance_then_vulnerability_then_temporary_hp(
    combat_catalog: CombatRulesCatalog,
) -> None:
    result = apply_damage(
        combat_catalog,
        current_hit_points=10,
        maximum_hit_points=10,
        temporary_hit_points=4,
        damage=7,
        resistant=True,
        vulnerable=True,
    )
    assert result.after_resistance == 3
    assert result.after_vulnerability == 6
    assert result.temporary_hit_points_absorbed == 4
    assert result.temporary_hit_points_after == 0
    assert result.hit_points_lost == 2
    assert result.hit_points_after == 8
    assert result.excess_damage == 0

    excess = apply_damage(
        combat_catalog,
        current_hit_points=3,
        maximum_hit_points=10,
        temporary_hit_points=0,
        damage=8,
    )
    assert excess.hit_points_after == 0
    assert excess.hit_points_lost == 3
    assert excess.excess_damage == 5


def test_healing_caps_at_maximum_and_does_not_change_temporary_hp(
    combat_catalog: CombatRulesCatalog,
) -> None:
    result = apply_healing(
        combat_catalog,
        current_hit_points=7,
        maximum_hit_points=10,
        temporary_hit_points=4,
        healing=8,
    )
    assert result.hit_points_restored == 3
    assert result.hit_points_after == 10
    assert result.temporary_hit_points_unchanged == 4


def test_health_resolvers_reject_invalid_state(combat_catalog: CombatRulesCatalog) -> None:
    with pytest.raises(CombatError, match="damage must be a nonnegative integer"):
        apply_damage(
            combat_catalog,
            current_hit_points=5,
            maximum_hit_points=10,
            temporary_hit_points=0,
            damage=-1,
        )
    with pytest.raises(CombatError, match="within zero and a positive maximum"):
        apply_damage(
            combat_catalog,
            current_hit_points=11,
            maximum_hit_points=10,
            temporary_hit_points=0,
            damage=1,
        )
    with pytest.raises(CombatError, match="within zero and a positive maximum"):
        apply_healing(
            combat_catalog,
            current_hit_points=0,
            maximum_hit_points=0,
            temporary_hit_points=0,
            healing=1,
        )


def test_temporary_hit_points_keep_or_replace_never_stack(
    combat_catalog: CombatRulesCatalog,
) -> None:
    kept = apply_temporary_hit_points(
        combat_catalog,
        current_temporary_hit_points=6,
        offered_temporary_hit_points=4,
        choice="keep",
    )
    assert kept.temporary_hit_points_after == 6
    assert kept.discarded_temporary_hit_points == 4

    replaced = apply_temporary_hit_points(
        combat_catalog,
        current_temporary_hit_points=6,
        offered_temporary_hit_points=4,
        choice="replace",
    )
    assert replaced.temporary_hit_points_after == 4
    assert replaced.discarded_temporary_hit_points == 6
    with pytest.raises(CombatError, match="must be 'keep' or 'replace'"):
        apply_temporary_hit_points(
            combat_catalog,
            current_temporary_hit_points=1,
            offered_temporary_hit_points=2,
            choice="stack",  # type: ignore[arg-type]
        )


def test_timed_effects_consume_expire_and_ignore_unrelated_boundaries(
    combat_catalog: CombatRulesCatalog,
) -> None:
    consumed = resolve_effect_boundary(
        combat_catalog,
        effect_id="sap",
        source_combatant_id="fighter-a",
        target_combatant_id="goblin-a",
        boundary="attack_roll_started",
        acting_combatant_id="goblin-a",
    )
    assert consumed.applies_to_event
    assert not consumed.active_after
    assert consumed.end_reason == "consumed"

    expired = resolve_effect_boundary(
        combat_catalog,
        effect_id="sap",
        source_combatant_id="fighter-a",
        target_combatant_id="goblin-a",
        boundary="turn_started",
        acting_combatant_id="fighter-a",
    )
    assert not expired.applies_to_event
    assert not expired.active_after
    assert expired.end_reason == "expired"

    unrelated = resolve_effect_boundary(
        combat_catalog,
        effect_id="slow",
        source_combatant_id="fighter-a",
        target_combatant_id="goblin-a",
        boundary="turn_started",
        acting_combatant_id="fighter-b",
    )
    assert unrelated.active_after
    assert unrelated.end_reason == "active"


def test_second_wind_caps_healing_and_spends_exactly_one_use(
    combat_health_catalog: CombatRulesCatalog,
) -> None:
    resolved = resolve_second_wind(
        combat_health_catalog,
        current_hit_points=8,
        maximum_hit_points=12,
        temporary_hit_points=3,
        uses_remaining=2,
        die_face=7,
        fighter_level=1,
    )
    assert resolved.uses_after == 1
    assert resolved.healing.hit_points_restored == 4
    assert resolved.healing.hit_points_after == 12
    assert resolved.healing.temporary_hit_points_unchanged == 3
    with pytest.raises(CombatError, match="remaining use"):
        resolve_second_wind(
            combat_health_catalog,
            current_hit_points=8,
            maximum_hit_points=12,
            temporary_hit_points=0,
            uses_remaining=0,
            die_face=7,
            fighter_level=1,
        )


@pytest.mark.parametrize(
    ("die_face", "successes", "failures", "outcome", "state", "hp"),
    [
        (1, 0, 1, "dead", "dead", 0),
        (9, 0, 2, "dead", "dead", 0),
        (10, 2, 0, "stable", "stable", 0),
        (20, 1, 1, "revived", "active", 1),
    ],
)
def test_death_save_natural_and_three_result_boundaries(
    combat_health_catalog: CombatRulesCatalog,
    die_face: int,
    successes: int,
    failures: int,
    outcome: str,
    state: str,
    hp: int,
) -> None:
    result = resolve_death_save(
        combat_health_catalog,
        die_face=die_face,
        successes=successes,
        failures=failures,
    )
    assert (result.outcome, result.state_after, result.hit_points_after) == (
        outcome,
        state,
        hp,
    )


def test_stabilization_and_damage_at_zero_are_exact(
    combat_health_catalog: CombatRulesCatalog,
) -> None:
    assert resolve_stabilization(combat_health_catalog, die_face=9, medicine_modifier=1).success
    assert not resolve_stabilization(combat_health_catalog, die_face=8, medicine_modifier=1).success
    critical = resolve_damage_at_zero(
        combat_health_catalog,
        damage=3,
        maximum_hit_points=12,
        failures=0,
        critical=True,
    )
    assert critical.failures_after == 2
    assert critical.state_after == "unconscious"
    massive = resolve_damage_at_zero(
        combat_health_catalog,
        damage=12,
        maximum_hit_points=12,
        failures=0,
        critical=False,
    )
    assert massive.instant_death
    assert massive.state_after == "dead"
    with pytest.raises(CombatError, match="unsupported timed effect"):
        resolve_effect_boundary(
            combat_health_catalog,
            effect_id="unknown",
            source_combatant_id="fighter-a",
            target_combatant_id="goblin-a",
            boundary="other",
            acting_combatant_id=None,
        )
    with pytest.raises(CombatError, match="unsupported effect boundary"):
        resolve_effect_boundary(
            combat_health_catalog,
            effect_id="slow",
            source_combatant_id="fighter-a",
            target_combatant_id="goblin-a",
            boundary="invalid",  # type: ignore[arg-type]
            acting_combatant_id=None,
        )


def test_fixed_inputs_replay_to_identical_semantic_results(
    combat_catalog: CombatRulesCatalog,
) -> None:
    inputs = {
        "weapon_id": "greatsword",
        "attack_mode": "melee",
        "attack_modifier": 5,
        "damage_modifier": 3,
        "target_armor_class": 15,
        "attack_dice_faces": [16],
        "damage_dice_faces": [2, 5],
        "fighting_style_id": "great_weapon_fighting",
        "mastery_enabled": True,
    }
    first = resolve_character_attack(combat_catalog, **inputs)
    second = resolve_character_attack(combat_catalog, **inputs)
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
