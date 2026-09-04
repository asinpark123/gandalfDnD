from __future__ import annotations

from typing import Literal

from pydantic import AnyHttpUrl, Field, model_validator

from app.character_creation import StrictModel

AdvantageState = Literal["normal", "advantage", "disadvantage"]
AttackMode = Literal["melee", "ranged"]
DamageType = Literal["bludgeoning", "piercing", "slashing"]
EffectBoundary = Literal["turn_started", "attack_roll_started", "other"]
EffectEndReason = Literal["active", "consumed", "expired"]
TemporaryHitPointChoice = Literal["keep", "replace"]
WeaponProperty = Literal[
    "ammunition",
    "finesse",
    "heavy",
    "light",
    "thrown",
    "two_handed",
]


class CombatError(ValueError):
    pass


class CombatRuleSource(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    title: str
    section: str
    printed_pages: list[int] = Field(min_length=1)
    url: AnyHttpUrl


class CombatRuleDefinition(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")
    definition_key: str = Field(pattern=r"^srd-5\.2\.1:[a-z0-9][a-z0-9._-]+$")
    name: str
    beginner_description: str
    source_ids: list[str] = Field(min_length=1)


class DiceExpression(StrictModel):
    count: int = Field(ge=1, le=20)
    sides: int = Field(ge=2, le=100)

    @property
    def notation(self) -> str:
        return f"{self.count}d{self.sides}"


class WeaponAttackDefinition(CombatRuleDefinition):
    item_id: str
    player_character_supported: bool
    category: Literal["simple", "martial"]
    weapon_kind: Literal["melee", "ranged"]
    damage_dice: DiceExpression
    damage_type: DamageType
    properties: list[WeaponProperty]
    printed_mastery_id: Literal["graze", "nick", "sap", "slow", "vex"]
    supported_mastery_id: Literal["graze", "sap", "slow"] | None
    reach_feet: int = Field(ge=5, le=20, multiple_of=5)
    normal_range_feet: int | None = Field(default=None, ge=5, le=1_000)
    long_range_feet: int | None = Field(default=None, ge=5, le=2_000)

    @model_validator(mode="after")
    def validate_range(self) -> WeaponAttackDefinition:
        ranged_capable = self.weapon_kind == "ranged" or "thrown" in self.properties
        has_range = self.normal_range_feet is not None or self.long_range_feet is not None
        if ranged_capable != has_range:
            raise ValueError("ranged and thrown weapons must define both ranges")
        if has_range and (
            self.normal_range_feet is None
            or self.long_range_feet is None
            or self.long_range_feet < self.normal_range_feet
        ):
            raise ValueError("weapon range must define ordered normal and long distances")
        if self.weapon_kind == "ranged" and "ammunition" not in self.properties:
            raise ValueError("supported ranged weapons must use ammunition")
        if self.weapon_kind == "melee" and "ammunition" in self.properties:
            raise ValueError("melee weapons cannot use ammunition")
        return self


class FightingStyleCombatDefinition(CombatRuleDefinition):
    mechanic: Literal[
        "ranged_weapon_attack_bonus",
        "armored_ac_bonus",
        "two_handed_melee_damage_floor",
        "light_extra_attack_damage_modifier",
    ]
    value: int | None = Field(default=None, ge=1, le=3)

    @model_validator(mode="after")
    def validate_value(self) -> FightingStyleCombatDefinition:
        if self.mechanic == "light_extra_attack_damage_modifier":
            if self.value is not None:
                raise ValueError("ability-modifier styles cannot define a fixed numeric value")
        elif self.value is None:
            raise ValueError("fixed Fighting Style mechanics must define their numeric value")
        return self


class WeaponMasteryDefinition(CombatRuleDefinition):
    mechanic: Literal["miss_ability_damage", "next_attack_disadvantage", "speed_reduction"]
    effect_id: str | None = None
    speed_reduction_feet: int | None = Field(default=None, ge=5, le=30, multiple_of=5)

    @model_validator(mode="after")
    def validate_mechanic(self) -> WeaponMasteryDefinition:
        if self.mechanic == "miss_ability_damage":
            if self.effect_id is not None or self.speed_reduction_feet is not None:
                raise ValueError("Graze-style mastery cannot create a timed effect")
        elif self.effect_id is None:
            raise ValueError("timed masteries must reference an effect")
        if (self.mechanic == "speed_reduction") != (self.speed_reduction_feet is not None):
            raise ValueError("only Slow-style mastery defines a Speed reduction")
        return self


class TimedEffectDefinition(CombatRuleDefinition):
    stacking_key: str
    maximum_stacks: Literal[1]
    expires_on_source_turn_start: bool
    consumed_on_target_attack_roll: bool


class MonsterAttackDefinition(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_]{0,79}$")
    definition_key: str = Field(pattern=r"^srd-5\.2\.1:[a-z0-9][a-z0-9._-]+$")
    name: str
    weapon_id: str
    attack_modifier: int = Field(ge=-10, le=30)
    damage_modifier: int = Field(ge=-10, le=30)
    advantage_bonus_damage_dice: DiceExpression | None = None
    source_ids: list[str] = Field(min_length=1)


class MonsterCombatDefinition(CombatRuleDefinition):
    size: Literal["small"]
    creature_type: Literal["fey"]
    armor_class: int = Field(ge=1, le=40)
    hit_points: int = Field(gt=0, le=1_000)
    initiative_modifier: int = Field(ge=-10, le=30)
    initiative_score: int = Field(ge=1, le=50)
    speed_feet: int = Field(ge=5, le=200, multiple_of=5)
    passive_perception: int = Field(ge=1, le=40)
    challenge_rating: str
    experience_points: int = Field(gt=0)
    attacks: list[MonsterAttackDefinition] = Field(min_length=1)
    supported_bonus_actions: list[Literal["disengage"]]


class EncounterBudgetDefinition(CombatRuleDefinition):
    character_level: Literal[1]
    low_xp_per_character: Literal[50]
    moderate_xp_per_character: Literal[75]
    high_xp_per_character: Literal[100]


class CombatRulesCatalog(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["1.0.0", "1.1.0"]
    id: Literal["srd-5.2.1-combat-v1", "srd-5.2.1-combat-v2"]
    ruleset_release_id: Literal["srd-5.2.1"]
    base_character_state_catalog_id: Literal["srd-5.2.1-party-state-v1"]
    base_character_state_catalog_sha256: Literal[
        "aba4fcdbffb037eece88c862c76be988ffc60808b46361cc9a9dda0730fe763b"
    ]
    resolver_version: Literal["combat-resolution-1.0.0", "combat-resolution-1.1.0"]
    sources: list[CombatRuleSource] = Field(min_length=1)
    rules: list[CombatRuleDefinition] = Field(min_length=1)
    weapons: list[WeaponAttackDefinition] = Field(min_length=1)
    fighting_styles: list[FightingStyleCombatDefinition] = Field(min_length=1)
    masteries: list[WeaponMasteryDefinition] = Field(min_length=1)
    effects: list[TimedEffectDefinition] = Field(min_length=1)
    monsters: list[MonsterCombatDefinition] = Field(min_length=1)
    encounter_budget: EncounterBudgetDefinition

    @model_validator(mode="after")
    def validate_catalog(self) -> CombatRulesCatalog:
        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("combat source IDs must be unique")

        definitions: list[CombatRuleDefinition] = [
            *self.rules,
            *self.weapons,
            *self.fighting_styles,
            *self.masteries,
            *self.effects,
            *self.monsters,
            self.encounter_budget,
        ]
        definition_keys = [
            *[definition.definition_key for definition in definitions],
            *[attack.definition_key for monster in self.monsters for attack in monster.attacks],
        ]
        if len(definition_keys) != len(set(definition_keys)):
            raise ValueError("combat definition keys must be unique")
        known_sources = set(source_ids)
        for definition in definitions:
            if not set(definition.source_ids) <= known_sources:
                raise ValueError(f"definition {definition.definition_key} cites an unknown source")
        for monster in self.monsters:
            for attack in monster.attacks:
                if not set(attack.source_ids) <= known_sources:
                    raise ValueError(f"monster attack {attack.id} cites an unknown source")

        foundation_rules = {
            "attack_roll",
            "critical_hit",
            "damage",
            "healing",
            "initiative",
            "natural_one_twenty",
            "resistance",
            "temporary_hit_points",
            "vulnerability",
        }
        health_rules = {
            "damage_at_zero",
            "death_saves",
            "encounter_outcomes",
            "instant_death",
            "melee_knockout",
            "second_wind",
            "stabilization",
            "unconscious_at_zero",
        }
        expected_identity = {
            "srd-5.2.1-combat-v1": (
                "1.0.0",
                "combat-resolution-1.0.0",
                foundation_rules,
            ),
            "srd-5.2.1-combat-v2": (
                "1.1.0",
                "combat-resolution-1.1.0",
                foundation_rules | health_rules,
            ),
        }
        expected_schema, expected_resolver, expected_rules = expected_identity[self.id]
        if self.schema_version != expected_schema or self.resolver_version != expected_resolver:
            raise ValueError("combat catalog identity, schema, and resolver versions must agree")
        if {rule.id for rule in self.rules} != expected_rules:
            raise ValueError("combat catalog must define its complete versioned rule slice")
        if {weapon.id for weapon in self.weapons} != {
            "dagger",
            "flail",
            "greatsword",
            "javelin",
            "scimitar",
            "shortbow",
        }:
            raise ValueError("combat catalog must define the supported weapons exactly once")
        if {weapon.id for weapon in self.weapons if weapon.player_character_supported} != {
            "flail",
            "greatsword",
            "javelin",
        }:
            raise ValueError("combat catalog must limit player attacks to the M5 weapon slice")
        if {style.id for style in self.fighting_styles} != {
            "archery",
            "defense",
            "great_weapon_fighting",
            "two_weapon_fighting",
        }:
            raise ValueError("combat catalog must define all current Fighter styles")
        styles = {style.id: (style.mechanic, style.value) for style in self.fighting_styles}
        if styles != {
            "archery": ("ranged_weapon_attack_bonus", 2),
            "defense": ("armored_ac_bonus", 1),
            "great_weapon_fighting": ("two_handed_melee_damage_floor", 3),
            "two_weapon_fighting": ("light_extra_attack_damage_modifier", None),
        }:
            raise ValueError("Fighter style mechanics must match the M5 source definitions")
        if {mastery.id for mastery in self.masteries} != {"graze", "sap", "slow"}:
            raise ValueError("combat catalog must define Graze, Sap, and Slow")
        if {effect.id for effect in self.effects} != {"dodge", "sap", "slow"}:
            raise ValueError("combat catalog must define the required timed effects")
        if {monster.id for monster in self.monsters} != {
            "goblin_minion",
            "goblin_warrior",
        }:
            raise ValueError("combat catalog must define both supported Goblins")

        mastery_ids = {mastery.id for mastery in self.masteries}
        effect_ids = {effect.id for effect in self.effects}
        weapon_ids = {weapon.id for weapon in self.weapons}
        if any(
            weapon.supported_mastery_id is not None
            and weapon.supported_mastery_id not in mastery_ids
            for weapon in self.weapons
        ):
            raise ValueError("weapon references an unsupported mastery")
        if any(
            mastery.effect_id is not None and mastery.effect_id not in effect_ids
            for mastery in self.masteries
        ):
            raise ValueError("mastery references an unsupported effect")
        for monster in self.monsters:
            attack_ids = [attack.id for attack in monster.attacks]
            if len(attack_ids) != len(set(attack_ids)):
                raise ValueError(f"monster {monster.id} attack IDs must be unique")
            if any(attack.weapon_id not in weapon_ids for attack in monster.attacks):
                raise ValueError(f"monster {monster.id} references an unsupported weapon")
        return self


class ResolvedD20Roll(StrictModel):
    advantage_state: AdvantageState
    advantage_sources: list[str]
    disadvantage_sources: list[str]
    dice_faces: list[int] = Field(min_length=1, max_length=2)
    selected_die: int = Field(ge=1, le=20)
    modifier: int
    total: int


class ResolvedInitiative(StrictModel):
    d20: ResolvedD20Roll
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedDamageDice(StrictModel):
    notation: str
    original_faces: list[int]
    adjusted_faces: list[int]
    subtotal: int = Field(ge=0)
    critical: bool
    adjustment: Literal["none", "great_weapon_fighting"]


class ResolvedAttack(StrictModel):
    weapon_id: str
    attack_mode: AttackMode
    d20: ResolvedD20Roll
    target_armor_class: int
    hit: bool
    critical: bool
    miss_reason: Literal["natural_one", "below_armor_class"] | None
    weapon_damage: ResolvedDamageDice | None
    bonus_damage: ResolvedDamageDice | None
    damage_modifier: int
    damage_total: int = Field(ge=0)
    mastery_id: str | None
    mastery_applied: bool
    applied_effect_id: str | None
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedDamageApplication(StrictModel):
    requested_damage: int = Field(ge=0)
    after_resistance: int = Field(ge=0)
    after_vulnerability: int = Field(ge=0)
    temporary_hit_points_before: int = Field(ge=0)
    temporary_hit_points_absorbed: int = Field(ge=0)
    temporary_hit_points_after: int = Field(ge=0)
    hit_points_before: int = Field(ge=0)
    hit_points_lost: int = Field(ge=0)
    hit_points_after: int = Field(ge=0)
    excess_damage: int = Field(ge=0)
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedHealing(StrictModel):
    requested_healing: int = Field(ge=0)
    hit_points_before: int = Field(ge=0)
    hit_points_restored: int = Field(ge=0)
    hit_points_after: int = Field(ge=0)
    temporary_hit_points_unchanged: int = Field(ge=0)
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedTemporaryHitPoints(StrictModel):
    choice: TemporaryHitPointChoice
    temporary_hit_points_before: int = Field(ge=0)
    offered_temporary_hit_points: int = Field(ge=0)
    temporary_hit_points_after: int = Field(ge=0)
    discarded_temporary_hit_points: int = Field(ge=0)
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedEffectBoundary(StrictModel):
    effect_id: str
    applies_to_event: bool
    active_after: bool
    end_reason: EffectEndReason
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedSecondWind(StrictModel):
    die_face: int = Field(ge=1, le=10)
    fighter_level: int = Field(ge=1, le=20)
    healing: ResolvedHealing
    uses_before: int = Field(ge=1, le=2)
    uses_after: int = Field(ge=0, le=1)
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedDeathSave(StrictModel):
    die_face: int = Field(ge=1, le=20)
    outcome: Literal["success", "failure", "critical_failure", "revived", "stable", "dead"]
    successes_before: int = Field(ge=0, le=2)
    failures_before: int = Field(ge=0, le=2)
    successes_after: int = Field(ge=0, le=3)
    failures_after: int = Field(ge=0, le=3)
    hit_points_after: Literal[0, 1]
    state_after: Literal["active", "unconscious", "stable", "dead"]
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedStabilization(StrictModel):
    d20: ResolvedD20Roll
    difficulty_class: Literal[10]
    success: bool
    state_after: Literal["unconscious", "stable"]
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


class ResolvedDamageAtZero(StrictModel):
    damage: int = Field(gt=0)
    critical: bool
    failures_before: int = Field(ge=0, le=2)
    failures_after: int = Field(ge=0, le=3)
    instant_death: bool
    state_after: Literal["unconscious", "dead"]
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    catalog_id: str
    resolver_version: str


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _definition_sources(
    catalog: CombatRulesCatalog, definitions: list[CombatRuleDefinition]
) -> tuple[list[str], list[str]]:
    keys = _unique([definition.definition_key for definition in definitions])
    source_ids = _unique(
        [source_id for definition in definitions for source_id in definition.source_ids]
    )
    return keys, source_ids


def _rule(catalog: CombatRulesCatalog, rule_id: str) -> CombatRuleDefinition:
    try:
        return next(rule for rule in catalog.rules if rule.id == rule_id)
    except StopIteration as exc:
        raise CombatError(f"combat catalog has no rule {rule_id!r}") from exc


def _require_nonnegative(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CombatError(f"{label} must be a nonnegative integer")


def _resolve_d20(
    *,
    modifier: int,
    dice_faces: list[int],
    advantage_sources: list[str],
    disadvantage_sources: list[str],
) -> ResolvedD20Roll:
    if isinstance(modifier, bool) or not isinstance(modifier, int):
        raise CombatError("modifier must be an integer")
    advantage_sources = _unique(advantage_sources)
    disadvantage_sources = _unique(disadvantage_sources)
    advantage_state: AdvantageState = "normal"
    if advantage_sources and not disadvantage_sources:
        advantage_state = "advantage"
    elif disadvantage_sources and not advantage_sources:
        advantage_state = "disadvantage"
    expected_count = 1 if advantage_state == "normal" else 2
    if len(dice_faces) != expected_count:
        raise CombatError(f"{advantage_state} requires exactly {expected_count} d20 face(s)")
    if any(
        isinstance(face, bool) or not isinstance(face, int) or not 1 <= face <= 20
        for face in dice_faces
    ):
        raise CombatError("d20 faces must be integers from 1 through 20")
    if advantage_state == "advantage":
        selected = max(dice_faces)
    elif advantage_state == "disadvantage":
        selected = min(dice_faces)
    else:
        selected = dice_faces[0]
    return ResolvedD20Roll(
        advantage_state=advantage_state,
        advantage_sources=advantage_sources,
        disadvantage_sources=disadvantage_sources,
        dice_faces=list(dice_faces),
        selected_die=selected,
        modifier=modifier,
        total=selected + modifier,
    )


def _damage_dice(
    expression: DiceExpression,
    faces: list[int],
    *,
    critical: bool,
    great_weapon_fighting: bool,
) -> ResolvedDamageDice:
    expected_count = expression.count * (2 if critical else 1)
    if len(faces) != expected_count:
        raise CombatError(f"{expression.notation} damage requires exactly {expected_count} face(s)")
    if any(
        isinstance(face, bool) or not isinstance(face, int) or not 1 <= face <= expression.sides
        for face in faces
    ):
        raise CombatError(f"{expression.notation} faces must be within the die range")
    adjusted = [3 if great_weapon_fighting and face in (1, 2) else face for face in faces]
    return ResolvedDamageDice(
        notation=f"{expected_count}d{expression.sides}",
        original_faces=list(faces),
        adjusted_faces=adjusted,
        subtotal=sum(adjusted),
        critical=critical,
        adjustment="great_weapon_fighting" if great_weapon_fighting else "none",
    )


def resolve_initiative(
    catalog: CombatRulesCatalog,
    *,
    modifier: int,
    dice_faces: list[int],
    advantage_sources: list[str] | None = None,
    disadvantage_sources: list[str] | None = None,
) -> ResolvedInitiative:
    d20 = _resolve_d20(
        modifier=modifier,
        dice_faces=dice_faces,
        advantage_sources=advantage_sources or [],
        disadvantage_sources=disadvantage_sources or [],
    )
    rule = _rule(catalog, "initiative")
    keys, source_ids = _definition_sources(catalog, [rule])
    return ResolvedInitiative(
        d20=d20,
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def _find_weapon(catalog: CombatRulesCatalog, weapon_id: str) -> WeaponAttackDefinition:
    try:
        return next(weapon for weapon in catalog.weapons if weapon.id == weapon_id)
    except StopIteration as exc:
        raise CombatError(f"unsupported weapon: {weapon_id}") from exc


def _find_style(
    catalog: CombatRulesCatalog, style_id: str | None
) -> FightingStyleCombatDefinition | None:
    if style_id is None:
        return None
    try:
        return next(style for style in catalog.fighting_styles if style.id == style_id)
    except StopIteration as exc:
        raise CombatError(f"unsupported Fighting Style: {style_id}") from exc


def _find_mastery(catalog: CombatRulesCatalog, mastery_id: str) -> WeaponMasteryDefinition:
    try:
        return next(mastery for mastery in catalog.masteries if mastery.id == mastery_id)
    except StopIteration as exc:
        raise CombatError(f"unsupported mastery: {mastery_id}") from exc


def _resolve_attack(
    catalog: CombatRulesCatalog,
    *,
    weapon: WeaponAttackDefinition,
    attack_mode: AttackMode,
    attack_modifier: int,
    damage_modifier: int,
    target_armor_class: int,
    attack_dice_faces: list[int],
    damage_dice_faces: list[int],
    advantage_sources: list[str],
    disadvantage_sources: list[str],
    fighting_style: FightingStyleCombatDefinition | None,
    mastery_enabled: bool,
    bonus_damage_expression: DiceExpression | None,
    bonus_damage_dice_faces: list[int],
    critical_on_hit: bool,
) -> ResolvedAttack:
    if attack_mode not in ("melee", "ranged"):
        raise CombatError("attack mode must be 'melee' or 'ranged'")
    if attack_mode == "melee" and weapon.weapon_kind != "melee":
        raise CombatError(f"{weapon.name} does not support melee attacks")
    if attack_mode == "ranged" and not (
        weapon.weapon_kind == "ranged" or "thrown" in weapon.properties
    ):
        raise CombatError(f"{weapon.name} does not support ranged attacks")
    if (
        isinstance(target_armor_class, bool)
        or not isinstance(target_armor_class, int)
        or not 1 <= target_armor_class <= 100
    ):
        raise CombatError("target Armor Class must be from 1 through 100")
    if isinstance(attack_modifier, bool) or not isinstance(attack_modifier, int):
        raise CombatError("attack modifier must be an integer")
    if isinstance(damage_modifier, bool) or not isinstance(damage_modifier, int):
        raise CombatError("damage modifier must be an integer")

    applied_attack_modifier = attack_modifier
    style_definitions: list[CombatRuleDefinition] = []
    great_weapon_fighting = False
    if fighting_style is not None:
        if (
            fighting_style.mechanic == "ranged_weapon_attack_bonus"
            and weapon.weapon_kind == "ranged"
        ):
            assert fighting_style.value is not None
            applied_attack_modifier += fighting_style.value
            style_definitions.append(fighting_style)
        elif (
            fighting_style.mechanic == "two_handed_melee_damage_floor"
            and attack_mode == "melee"
            and weapon.weapon_kind == "melee"
            and bool({"two_handed"} & set(weapon.properties))
        ):
            great_weapon_fighting = True
            style_definitions.append(fighting_style)

    d20 = _resolve_d20(
        modifier=applied_attack_modifier,
        dice_faces=attack_dice_faces,
        advantage_sources=advantage_sources,
        disadvantage_sources=disadvantage_sources,
    )
    natural_critical = d20.selected_die == 20
    if d20.selected_die == 1:
        hit = False
        miss_reason: Literal["natural_one", "below_armor_class"] | None = "natural_one"
    elif natural_critical or d20.total >= target_armor_class:
        hit = True
        miss_reason = None
    else:
        hit = False
        miss_reason = "below_armor_class"
    critical = natural_critical or (critical_on_hit and hit)

    if mastery_enabled and weapon.supported_mastery_id is None:
        raise CombatError(f"{weapon.name} mastery is outside the M5 combat slice")
    mastery = (
        _find_mastery(catalog, weapon.supported_mastery_id)
        if mastery_enabled and weapon.supported_mastery_id is not None
        else None
    )
    mastery_applied = False
    applied_effect_id: str | None = None
    weapon_damage: ResolvedDamageDice | None = None
    bonus_damage: ResolvedDamageDice | None = None
    damage_total = 0
    if hit:
        weapon_damage = _damage_dice(
            weapon.damage_dice,
            damage_dice_faces,
            critical=critical,
            great_weapon_fighting=great_weapon_fighting,
        )
        damage_total = max(0, weapon_damage.subtotal + damage_modifier)
        if bonus_damage_expression is not None and d20.advantage_state == "advantage":
            bonus_damage = _damage_dice(
                bonus_damage_expression,
                bonus_damage_dice_faces,
                critical=critical,
                great_weapon_fighting=False,
            )
            damage_total += bonus_damage.subtotal
        elif bonus_damage_dice_faces:
            raise CombatError("bonus damage dice were supplied when bonus damage does not apply")
        if mastery is not None and (
            mastery.mechanic == "next_attack_disadvantage"
            or (mastery.mechanic == "speed_reduction" and damage_total > 0)
        ):
            mastery_applied = True
            applied_effect_id = mastery.effect_id
    else:
        if damage_dice_faces or bonus_damage_dice_faces:
            raise CombatError("a missed attack cannot include rolled damage dice")
        if mastery is not None and mastery.mechanic == "miss_ability_damage":
            mastery_applied = True
            damage_total = max(0, damage_modifier)

    definitions: list[CombatRuleDefinition] = [
        _rule(catalog, "attack_roll"),
        _rule(catalog, "natural_one_twenty"),
        weapon,
        *style_definitions,
    ]
    if hit or damage_total > 0:
        definitions.append(_rule(catalog, "damage"))
    if critical:
        definitions.append(_rule(catalog, "critical_hit"))
    if mastery_applied and mastery is not None:
        definitions.append(mastery)
    keys, source_ids = _definition_sources(catalog, definitions)
    return ResolvedAttack(
        weapon_id=weapon.id,
        attack_mode=attack_mode,
        d20=d20,
        target_armor_class=target_armor_class,
        hit=hit,
        critical=critical,
        miss_reason=miss_reason,
        weapon_damage=weapon_damage,
        bonus_damage=bonus_damage,
        damage_modifier=damage_modifier,
        damage_total=damage_total,
        mastery_id=mastery.id if mastery is not None else None,
        mastery_applied=mastery_applied,
        applied_effect_id=applied_effect_id,
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def resolve_character_attack(
    catalog: CombatRulesCatalog,
    *,
    weapon_id: str,
    attack_mode: AttackMode,
    attack_modifier: int,
    damage_modifier: int,
    target_armor_class: int,
    attack_dice_faces: list[int],
    damage_dice_faces: list[int],
    advantage_sources: list[str] | None = None,
    disadvantage_sources: list[str] | None = None,
    fighting_style_id: str | None = None,
    mastery_enabled: bool = False,
    critical_on_hit: bool = False,
) -> ResolvedAttack:
    weapon = _find_weapon(catalog, weapon_id)
    if not weapon.player_character_supported:
        raise CombatError(f"{weapon.name} is not a supported M5 player-character weapon")
    return _resolve_attack(
        catalog,
        weapon=weapon,
        attack_mode=attack_mode,
        attack_modifier=attack_modifier,
        damage_modifier=damage_modifier,
        target_armor_class=target_armor_class,
        attack_dice_faces=attack_dice_faces,
        damage_dice_faces=damage_dice_faces,
        advantage_sources=advantage_sources or [],
        disadvantage_sources=disadvantage_sources or [],
        fighting_style=_find_style(catalog, fighting_style_id),
        mastery_enabled=mastery_enabled,
        bonus_damage_expression=None,
        bonus_damage_dice_faces=[],
        critical_on_hit=critical_on_hit,
    )


def resolve_monster_attack(
    catalog: CombatRulesCatalog,
    *,
    monster_id: str,
    attack_id: str,
    attack_mode: AttackMode,
    target_armor_class: int,
    attack_dice_faces: list[int],
    damage_dice_faces: list[int],
    bonus_damage_dice_faces: list[int] | None = None,
    advantage_sources: list[str] | None = None,
    disadvantage_sources: list[str] | None = None,
    critical_on_hit: bool = False,
) -> ResolvedAttack:
    try:
        monster = next(monster for monster in catalog.monsters if monster.id == monster_id)
    except StopIteration as exc:
        raise CombatError(f"unsupported monster: {monster_id}") from exc
    try:
        attack = next(attack for attack in monster.attacks if attack.id == attack_id)
    except StopIteration as exc:
        raise CombatError(f"unsupported attack for {monster_id}: {attack_id}") from exc
    resolved = _resolve_attack(
        catalog,
        weapon=_find_weapon(catalog, attack.weapon_id),
        attack_mode=attack_mode,
        attack_modifier=attack.attack_modifier,
        damage_modifier=attack.damage_modifier,
        target_armor_class=target_armor_class,
        attack_dice_faces=attack_dice_faces,
        damage_dice_faces=damage_dice_faces,
        advantage_sources=advantage_sources or [],
        disadvantage_sources=disadvantage_sources or [],
        fighting_style=None,
        mastery_enabled=False,
        bonus_damage_expression=attack.advantage_bonus_damage_dice,
        bonus_damage_dice_faces=bonus_damage_dice_faces or [],
        critical_on_hit=critical_on_hit,
    )
    keys = _unique([*resolved.rule_definition_keys, monster.definition_key, attack.definition_key])
    sources = _unique([*resolved.source_ids, *monster.source_ids, *attack.source_ids])
    return resolved.model_copy(update={"rule_definition_keys": keys, "source_ids": sources})


def apply_damage(
    catalog: CombatRulesCatalog,
    *,
    current_hit_points: int,
    maximum_hit_points: int,
    temporary_hit_points: int,
    damage: int,
    resistant: bool = False,
    vulnerable: bool = False,
) -> ResolvedDamageApplication:
    for value, label in (
        (current_hit_points, "current Hit Points"),
        (maximum_hit_points, "maximum Hit Points"),
        (temporary_hit_points, "Temporary Hit Points"),
        (damage, "damage"),
    ):
        _require_nonnegative(value, label)
    if maximum_hit_points == 0 or current_hit_points > maximum_hit_points:
        raise CombatError("Hit Points must be within zero and a positive maximum")

    after_resistance = damage // 2 if resistant else damage
    after_vulnerability = after_resistance * 2 if vulnerable else after_resistance
    absorbed = min(temporary_hit_points, after_vulnerability)
    remaining_damage = after_vulnerability - absorbed
    hit_points_lost = min(current_hit_points, remaining_damage)
    excess_damage = remaining_damage - hit_points_lost
    definitions = [_rule(catalog, "damage"), _rule(catalog, "temporary_hit_points")]
    if resistant:
        definitions.append(_rule(catalog, "resistance"))
    if vulnerable:
        definitions.append(_rule(catalog, "vulnerability"))
    keys, source_ids = _definition_sources(catalog, definitions)
    return ResolvedDamageApplication(
        requested_damage=damage,
        after_resistance=after_resistance,
        after_vulnerability=after_vulnerability,
        temporary_hit_points_before=temporary_hit_points,
        temporary_hit_points_absorbed=absorbed,
        temporary_hit_points_after=temporary_hit_points - absorbed,
        hit_points_before=current_hit_points,
        hit_points_lost=hit_points_lost,
        hit_points_after=current_hit_points - hit_points_lost,
        excess_damage=excess_damage,
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def apply_healing(
    catalog: CombatRulesCatalog,
    *,
    current_hit_points: int,
    maximum_hit_points: int,
    temporary_hit_points: int,
    healing: int,
) -> ResolvedHealing:
    for value, label in (
        (current_hit_points, "current Hit Points"),
        (maximum_hit_points, "maximum Hit Points"),
        (temporary_hit_points, "Temporary Hit Points"),
        (healing, "healing"),
    ):
        _require_nonnegative(value, label)
    if maximum_hit_points == 0 or current_hit_points > maximum_hit_points:
        raise CombatError("Hit Points must be within zero and a positive maximum")
    restored = min(healing, maximum_hit_points - current_hit_points)
    rule = _rule(catalog, "healing")
    keys, source_ids = _definition_sources(catalog, [rule])
    return ResolvedHealing(
        requested_healing=healing,
        hit_points_before=current_hit_points,
        hit_points_restored=restored,
        hit_points_after=current_hit_points + restored,
        temporary_hit_points_unchanged=temporary_hit_points,
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def apply_temporary_hit_points(
    catalog: CombatRulesCatalog,
    *,
    current_temporary_hit_points: int,
    offered_temporary_hit_points: int,
    choice: TemporaryHitPointChoice,
) -> ResolvedTemporaryHitPoints:
    _require_nonnegative(current_temporary_hit_points, "current Temporary Hit Points")
    _require_nonnegative(offered_temporary_hit_points, "offered Temporary Hit Points")
    if choice == "keep":
        after = current_temporary_hit_points
        discarded = offered_temporary_hit_points
    elif choice == "replace":
        after = offered_temporary_hit_points
        discarded = current_temporary_hit_points
    else:
        raise CombatError("Temporary Hit Point choice must be 'keep' or 'replace'")
    rule = _rule(catalog, "temporary_hit_points")
    keys, source_ids = _definition_sources(catalog, [rule])
    return ResolvedTemporaryHitPoints(
        choice=choice,
        temporary_hit_points_before=current_temporary_hit_points,
        offered_temporary_hit_points=offered_temporary_hit_points,
        temporary_hit_points_after=after,
        discarded_temporary_hit_points=discarded,
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def resolve_effect_boundary(
    catalog: CombatRulesCatalog,
    *,
    effect_id: str,
    source_combatant_id: str,
    target_combatant_id: str,
    boundary: EffectBoundary,
    acting_combatant_id: str | None,
) -> ResolvedEffectBoundary:
    if boundary not in ("turn_started", "attack_roll_started", "other"):
        raise CombatError("unsupported effect boundary")
    try:
        effect = next(effect for effect in catalog.effects if effect.id == effect_id)
    except StopIteration as exc:
        raise CombatError(f"unsupported timed effect: {effect_id}") from exc
    applies = (
        boundary == "attack_roll_started"
        and effect.consumed_on_target_attack_roll
        and acting_combatant_id == target_combatant_id
    )
    expired = (
        boundary == "turn_started"
        and effect.expires_on_source_turn_start
        and acting_combatant_id == source_combatant_id
    )
    active_after = not (applies or expired)
    end_reason: EffectEndReason = "consumed" if applies else "expired" if expired else "active"
    keys, source_ids = _definition_sources(catalog, [effect])
    return ResolvedEffectBoundary(
        effect_id=effect.id,
        applies_to_event=applies,
        active_after=active_after,
        end_reason=end_reason,
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def resolve_second_wind(
    catalog: CombatRulesCatalog,
    *,
    current_hit_points: int,
    maximum_hit_points: int,
    temporary_hit_points: int,
    uses_remaining: int,
    die_face: int,
    fighter_level: int,
) -> ResolvedSecondWind:
    if uses_remaining not in (1, 2):
        raise CombatError("Second Wind requires at least one remaining use")
    if not 1 <= die_face <= 10:
        raise CombatError("Second Wind d10 face must be from 1 through 10")
    if not 1 <= fighter_level <= 20:
        raise CombatError("Fighter level must be from 1 through 20")
    if current_hit_points == 0:
        raise CombatError("Second Wind cannot be used while unconscious")
    healing = apply_healing(
        catalog,
        current_hit_points=current_hit_points,
        maximum_hit_points=maximum_hit_points,
        temporary_hit_points=temporary_hit_points,
        healing=die_face + fighter_level,
    )
    rule = _rule(catalog, "second_wind")
    keys, source_ids = _definition_sources(catalog, [rule])
    return ResolvedSecondWind(
        die_face=die_face,
        fighter_level=fighter_level,
        healing=healing,
        uses_before=uses_remaining,
        uses_after=uses_remaining - 1,
        rule_definition_keys=_unique([*keys, *healing.rule_definition_keys]),
        source_ids=_unique([*source_ids, *healing.source_ids]),
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def resolve_death_save(
    catalog: CombatRulesCatalog,
    *,
    die_face: int,
    successes: int,
    failures: int,
) -> ResolvedDeathSave:
    if not 1 <= die_face <= 20:
        raise CombatError("death save d20 face must be from 1 through 20")
    if not 0 <= successes <= 2 or not 0 <= failures <= 2:
        raise CombatError("pending death save counters must be from zero through two")
    successes_after = successes
    failures_after = failures
    hit_points_after: Literal[0, 1] = 0
    state_after: Literal["active", "unconscious", "stable", "dead"] = "unconscious"
    if die_face == 20:
        outcome = "revived"
        hit_points_after = 1
        state_after = "active"
        successes_after = 0
        failures_after = 0
    elif die_face == 1:
        failures_after = min(3, failures + 2)
        outcome = "dead" if failures_after == 3 else "critical_failure"
        state_after = "dead" if failures_after == 3 else "unconscious"
    elif die_face >= 10:
        successes_after = successes + 1
        outcome = "stable" if successes_after == 3 else "success"
        state_after = "stable" if successes_after == 3 else "unconscious"
        if successes_after == 3:
            successes_after = 0
            failures_after = 0
    else:
        failures_after = failures + 1
        outcome = "dead" if failures_after == 3 else "failure"
        state_after = "dead" if failures_after == 3 else "unconscious"
    definitions = [_rule(catalog, "death_saves"), _rule(catalog, "unconscious_at_zero")]
    keys, source_ids = _definition_sources(catalog, definitions)
    return ResolvedDeathSave(
        die_face=die_face,
        outcome=outcome,
        successes_before=successes,
        failures_before=failures,
        successes_after=successes_after,
        failures_after=failures_after,
        hit_points_after=hit_points_after,
        state_after=state_after,
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def resolve_stabilization(
    catalog: CombatRulesCatalog, *, die_face: int, medicine_modifier: int
) -> ResolvedStabilization:
    d20 = _resolve_d20(
        modifier=medicine_modifier,
        dice_faces=[die_face],
        advantage_sources=[],
        disadvantage_sources=[],
    )
    success = d20.total >= 10
    rule = _rule(catalog, "stabilization")
    keys, source_ids = _definition_sources(catalog, [rule])
    return ResolvedStabilization(
        d20=d20,
        difficulty_class=10,
        success=success,
        state_after="stable" if success else "unconscious",
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )


def resolve_damage_at_zero(
    catalog: CombatRulesCatalog,
    *,
    damage: int,
    maximum_hit_points: int,
    failures: int,
    critical: bool,
) -> ResolvedDamageAtZero:
    if damage <= 0:
        raise CombatError("damage at zero Hit Points must be positive")
    if maximum_hit_points <= 0:
        raise CombatError("maximum Hit Points must be positive")
    if not 0 <= failures <= 2:
        raise CombatError("pending death save failures must be from zero through two")
    instant_death = damage >= maximum_hit_points
    failures_after = min(3, failures + (2 if critical else 1))
    dead = instant_death or failures_after == 3
    definitions = [_rule(catalog, "damage_at_zero")]
    if instant_death:
        definitions.append(_rule(catalog, "instant_death"))
    keys, source_ids = _definition_sources(catalog, definitions)
    return ResolvedDamageAtZero(
        damage=damage,
        critical=critical,
        failures_before=failures,
        failures_after=failures_after,
        instant_death=instant_death,
        state_after="dead" if dead else "unconscious",
        rule_definition_keys=keys,
        source_ids=source_ids,
        catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )
