from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import AnyHttpUrl, Field, model_validator

from app.character_creation import (
    AbilityName,
    AbilityScoreRead,
    CharacterCreationCatalog,
    CharacterSheet,
    StrictModel,
)

EquipmentPosition = Literal["carried", "worn", "held"]


class StateRuleSource(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    title: str
    section: str
    printed_pages: list[int] = Field(min_length=1)
    url: AnyHttpUrl


class StateRuleDefinition(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")
    definition_key: str = Field(pattern=r"^srd-5\.2\.1:[a-z0-9][a-z0-9._-]+$")
    name: str
    beginner_description: str
    source_ids: list[str] = Field(min_length=1)


class PartyRules(StrictModel):
    mode: Literal["party_commander"]
    minimum_active_characters: Literal[2]
    maximum_active_characters: Literal[4]
    control_mode: Literal["player"]


class EquipmentStateRule(StateRuleDefinition):
    item_id: str
    item_name: str
    item_type: Literal["armor", "weapon"]
    hands_required: int = Field(ge=0, le=2)
    default_position: EquipmentPosition
    armor_category: Literal["light", "medium", "heavy"] | None = None
    base_armor_class: int | None = Field(default=None, ge=1)
    minimum_strength: int | None = Field(default=None, ge=1)
    stealth_disadvantage: bool = False

    @model_validator(mode="after")
    def validate_equipment_semantics(self) -> EquipmentStateRule:
        if self.item_type == "armor":
            if self.armor_category is None or self.base_armor_class is None:
                raise ValueError("armor must define category and base Armor Class")
            if self.hands_required != 0:
                raise ValueError("armor cannot require hands")
        elif self.armor_category is not None or self.base_armor_class is not None:
            raise ValueError("a weapon cannot define armor fields")
        return self


class ResourceStateRule(StateRuleDefinition):
    maximum: int = Field(gt=0)
    initial_current: int = Field(ge=0)
    die: str | None = Field(default=None, pattern=r"^d(?:[2-9]|[1-9]\d{1,2})$")
    short_rest_recovery: Literal["none", "one", "all"]
    long_rest_recovery: Literal["none", "all"]

    @model_validator(mode="after")
    def validate_initial_current(self) -> ResourceStateRule:
        if self.initial_current > self.maximum:
            raise ValueError("resource initial current cannot exceed its maximum")
        return self


class CharacterStateCatalog(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["1.0.0"]
    id: Literal["srd-5.2.1-party-state-v1"]
    ruleset_release_id: Literal["srd-5.2.1"]
    base_character_creation_catalog_id: Literal["srd-5.2.1-character-creation-v1"]
    base_character_creation_catalog_sha256: Literal[
        "ddbd172feeeb191789f1b95f93762c661dda06888dad067e28c7fc6ffda391cb"
    ]
    resolver_version: Literal["character-state-1.0.0"]
    party: PartyRules
    sources: list[StateRuleSource] = Field(min_length=1)
    rules: list[StateRuleDefinition] = Field(min_length=1)
    equipment: list[EquipmentStateRule] = Field(min_length=1)
    resources: list[ResourceStateRule] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_catalog(self) -> CharacterStateCatalog:
        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("state rule source IDs must be unique")
        definitions: list[StateRuleDefinition] = [
            *self.rules,
            *self.equipment,
            *self.resources,
        ]
        definition_keys = [definition.definition_key for definition in definitions]
        if len(definition_keys) != len(set(definition_keys)):
            raise ValueError("state rule definition keys must be unique")
        known_sources = set(source_ids)
        for definition in definitions:
            if not set(definition.source_ids) <= known_sources:
                raise ValueError(f"definition {definition.definition_key} cites an unknown source")
        if {item.item_id for item in self.equipment} != {
            "chain_mail",
            "flail",
            "greatsword",
            "javelin",
        }:
            raise ValueError("state catalog must define the supported equippable items")
        if {resource.id for resource in self.resources} != {
            "heroic_inspiration",
            "hit_dice",
            "second_wind",
        }:
            raise ValueError("state catalog must define all supported expendable resources")
        return self


class GrantProvenanceFact(StrictModel):
    choice_slot: str
    definition_key: str
    source_definition_key: str
    source_ids: list[str]
    acquisition_event_id: str


class DerivationProvenance(StrictModel):
    formula: str
    definition_keys: list[str]
    source_ids: list[str]
    acquisition_event_ids: list[str]
    character_revision: int
    state_revision: int
    resolver_version: str


class DerivedNumber(StrictModel):
    value: int
    provenance: DerivationProvenance


class ModifierState(DerivedNumber):
    ability: AbilityName
    proficient: bool


class ArmorClassCandidate(StrictModel):
    id: str
    value: int
    selected: bool
    worn_armor_item_id: str | None
    provenance: DerivationProvenance


class ResourceState(StrictModel):
    current: int = Field(ge=0)
    maximum: int = Field(gt=0)
    die: str | None
    short_rest_recovery: str
    long_rest_recovery: str
    provenance: DerivationProvenance


class EquipmentState(StrictModel):
    item_id: str
    name: str
    quantity: int = Field(ge=0)
    equipped_quantity: int = Field(ge=0)
    position: EquipmentPosition
    definition_key: str | None
    provenance_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str]
    acquisition_event_ids: list[str]


class CharacterMechanicalState(StrictModel):
    resolver_version: str
    character_revision: int
    state_revision: int
    level: int
    abilities: dict[AbilityName, AbilityScoreRead]
    proficiency_bonus: DerivedNumber
    saving_throws: dict[AbilityName, ModifierState]
    skills: dict[str, ModifierState]
    armor_class: DerivedNumber
    armor_class_candidates: list[ArmorClassCandidate]
    initiative: ModifierState
    passive_perception: DerivedNumber
    speed_feet: DerivedNumber
    hit_points_current: int
    hit_points_maximum: DerivedNumber
    equipment: list[EquipmentState]
    resources: dict[str, ResourceState]


class Loadout(StrictModel):
    worn_armor_item_id: str | None = None
    held_item_ids: list[str] = Field(default_factory=list, max_length=2)


class CharacterCreationOptions(StrictModel):
    selected_ruleset_data_catalog_id: str
    character_creation: CharacterCreationCatalog
    party: PartyRules | None


class CharacterStateError(ValueError):
    pass


def initial_loadout(catalog: CharacterStateCatalog) -> Loadout:
    armor = next(
        (item.item_id for item in catalog.equipment if item.default_position == "worn"),
        None,
    )
    held = [item.item_id for item in catalog.equipment if item.default_position == "held"]
    return Loadout(worn_armor_item_id=armor, held_item_ids=held)


def initial_resources(catalog: CharacterStateCatalog) -> dict[str, int]:
    return {resource.id: resource.initial_current for resource in catalog.resources}


def _inventory_item_ids(
    character_creation: CharacterCreationCatalog,
) -> dict[str, tuple[str, str]]:
    items: dict[str, tuple[str, str]] = {}
    for package in character_creation.equipment_packages:
        for item in package.items:
            items[item.item_id] = (item.name, package.definition_key)
    return items


def _inventory_provenance(
    character_creation: CharacterCreationCatalog,
    sheet: CharacterSheet,
) -> dict[str, tuple[str, str | None, list[str]]]:
    """Map projected inventory names to IDs and every definition that supplied them."""
    selected_package_keys = {
        character_creation.background.equipment_package_definition_key,
        character_creation.character_class.equipment_package_definition_key,
    }
    selected_packages = [
        package
        for package in character_creation.equipment_packages
        if package.definition_key in selected_package_keys
    ]
    gaming_set = next(
        option
        for option in character_creation.gaming_sets
        if option.id == sheet.gaming_set_proficiency
    )
    metadata: dict[str, tuple[str, str | None, list[str]]] = {}
    gold_definition_keys: list[str] = []
    for package in selected_packages:
        if package.gold_pieces:
            gold_definition_keys.append(package.definition_key)
        for item in package.items:
            if item.item_id == "chosen_gaming_set":
                item_id = gaming_set.name.lower().replace(" ", "_")
                item_name = gaming_set.name
                specific_definition_key: str | None = gaming_set.definition_key
                definition_keys = [gaming_set.definition_key, package.definition_key]
            else:
                item_id = item.item_id
                item_name = item.name
                specific_definition_key = None
                definition_keys = [package.definition_key]
            existing = metadata.get(item_name)
            if existing is not None:
                definition_keys = _unique([*existing[2], *definition_keys])
            metadata[item_name] = (
                item_id,
                specific_definition_key,
                definition_keys,
            )
    if gold_definition_keys:
        metadata["GP"] = ("gp", None, _unique(gold_definition_keys))
    return metadata


def validate_loadout(
    character_creation: CharacterCreationCatalog,
    state_catalog: CharacterStateCatalog,
    inventory: dict[str, int],
    loadout: Loadout,
) -> Loadout:
    equipment_by_id = {item.item_id: item for item in state_catalog.equipment}
    inventory_ids = _inventory_item_ids(character_creation)
    owned_ids = {
        item_id for item_id, (name, _source) in inventory_ids.items() if inventory.get(name, 0) > 0
    }
    if loadout.worn_armor_item_id is not None:
        armor = equipment_by_id.get(loadout.worn_armor_item_id)
        if armor is None or armor.item_type != "armor" or armor.item_id not in owned_ids:
            raise CharacterStateError("worn armor must identify owned supported armor")
    if len(loadout.held_item_ids) != len(set(loadout.held_item_ids)):
        raise CharacterStateError("held items must not contain duplicates")
    hands = 0
    for item_id in loadout.held_item_ids:
        item = equipment_by_id.get(item_id)
        if item is None or item.item_type != "weapon" or item.item_id not in owned_ids:
            raise CharacterStateError("held items must identify owned supported weapons")
        hands += item.hands_required
    if hands > 2:
        raise CharacterStateError("held items require more than two hands")
    return loadout


def _definition_source_map(
    character_creation: CharacterCreationCatalog,
    state_catalog: CharacterStateCatalog,
) -> dict[str, list[str]]:
    creation_definitions = [
        *character_creation.abilities,
        *character_creation.alignments,
        *character_creation.skills,
        *character_creation.languages,
        *character_creation.gaming_sets,
        character_creation.standard_array,
        character_creation.background,
        character_creation.species,
        character_creation.character_class,
        *character_creation.features,
        *character_creation.origin_feats,
        *character_creation.fighting_styles,
        *character_creation.weapons,
        *character_creation.equipment_packages,
    ]
    return {
        definition.definition_key: list(definition.source_ids)
        for definition in [
            *creation_definitions,
            *state_catalog.rules,
            *state_catalog.equipment,
            *state_catalog.resources,
        ]
    }


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def derive_character_state(
    character_creation: CharacterCreationCatalog,
    state_catalog: CharacterStateCatalog,
    sheet: CharacterSheet,
    *,
    hp: int,
    inventory: dict[str, int],
    loadout: Loadout,
    resource_values: dict[str, int],
    grants: list[GrantProvenanceFact],
    character_revision: int,
    state_revision: int,
) -> CharacterMechanicalState:
    validate_loadout(character_creation, state_catalog, inventory, loadout)
    source_map = _definition_source_map(character_creation, state_catalog)
    rules = {rule.id: rule for rule in state_catalog.rules}
    equipment_rules = {item.item_id: item for item in state_catalog.equipment}
    resource_rules = {resource.id: resource for resource in state_catalog.resources}

    def grant_definition_keys(prefix: str) -> list[str]:
        return _unique(
            key
            for grant in grants
            if grant.choice_slot.startswith(prefix)
            for key in (grant.definition_key, grant.source_definition_key)
        )

    def skill_grant_definition_keys(skill_id: str) -> list[str]:
        return _unique(
            key
            for grant in grants
            if grant.choice_slot.startswith("skill.") and grant.choice_slot.endswith(f".{skill_id}")
            for key in (grant.definition_key, grant.source_definition_key)
        )

    def provenance(formula: str, definition_keys: list[str]) -> DerivationProvenance:
        keys = _unique(definition_keys)
        source_ids = _unique(source_id for key in keys for source_id in source_map.get(key, []))
        for grant in grants:
            if grant.definition_key in keys or grant.source_definition_key in keys:
                source_ids = _unique([*source_ids, *grant.source_ids])
        acquisition_event_ids = _unique(
            grant.acquisition_event_id
            for grant in grants
            if grant.definition_key in keys or grant.source_definition_key in keys
        )
        return DerivationProvenance(
            formula=formula,
            definition_keys=keys,
            source_ids=source_ids,
            acquisition_event_ids=acquisition_event_ids,
            character_revision=character_revision,
            state_revision=state_revision,
            resolver_version=state_catalog.resolver_version,
        )

    proficiency_rule = rules["proficiency_bonus"]
    save_rule = rules["saving_throw_modifier"]
    skill_rule = rules["skill_modifier"]
    initiative_rule = rules["initiative"]
    passive_rule = rules["passive_perception"]
    hp_rule = rules["level_one_hit_points"]
    speed_rule = rules["speed"]
    unarmored_rule = rules["unarmored_armor_class"]

    proficiency_bonus = DerivedNumber(
        value=sheet.proficiency_bonus,
        provenance=provenance(
            "level 1 proficiency bonus = 2",
            [proficiency_rule.definition_key, sheet.class_definition_key],
        ),
    )

    ability_by_id = {ability.id: ability for ability in character_creation.abilities}
    saving_throws: dict[AbilityName, ModifierState] = {}
    for ability, score in sheet.abilities.items():
        proficient = ability in sheet.saving_throw_proficiencies
        value = score.modifier + (sheet.proficiency_bonus if proficient else 0)
        saving_throws[ability] = ModifierState(
            value=value,
            ability=ability,
            proficient=proficient,
            provenance=provenance(
                "ability modifier + proficiency bonus when proficient",
                [
                    save_rule.definition_key,
                    ability_by_id[ability].definition_key,
                    *grant_definition_keys(f"saving_throw.{ability}"),
                ],
            ),
        )

    skills: dict[str, ModifierState] = {}
    for skill in character_creation.skills:
        proficient = skill.id in sheet.skill_proficiencies
        ability = skill.typical_ability
        value = sheet.abilities[ability].modifier + (sheet.proficiency_bonus if proficient else 0)
        skills[skill.id] = ModifierState(
            value=value,
            ability=ability,
            proficient=proficient,
            provenance=provenance(
                "typical ability modifier + proficiency bonus when proficient",
                [
                    skill_rule.definition_key,
                    skill.definition_key,
                    ability_by_id[ability].definition_key,
                    *(skill_grant_definition_keys(skill.id) if proficient else []),
                ],
            ),
        )

    alert_key = "srd-5.2.1:feat.origin.alert"
    alert = alert_key in sheet.origin_feat_definition_keys
    initiative_value = sheet.abilities["dexterity"].modifier + (
        sheet.proficiency_bonus if alert else 0
    )
    initiative_keys = [
        initiative_rule.definition_key,
        ability_by_id["dexterity"].definition_key,
    ]
    if alert:
        initiative_keys.append(alert_key)
    initiative = ModifierState(
        value=initiative_value,
        ability="dexterity",
        proficient=alert,
        provenance=provenance(
            "Dexterity modifier + proficiency bonus when Alert grants Initiative proficiency",
            initiative_keys,
        ),
    )

    perception = skills["perception"]
    passive_perception = DerivedNumber(
        value=10 + perception.value,
        provenance=provenance(
            "10 + Wisdom (Perception) check modifier",
            [
                passive_rule.definition_key,
                *perception.provenance.definition_keys,
            ],
        ),
    )

    defense_key = "srd-5.2.1:feat.fighting_style.defense"
    candidates: list[ArmorClassCandidate] = []
    unarmored_value = 10 + sheet.abilities["dexterity"].modifier
    selected_armor = (
        equipment_rules.get(loadout.worn_armor_item_id) if loadout.worn_armor_item_id else None
    )
    candidates.append(
        ArmorClassCandidate(
            id="unarmored",
            value=unarmored_value,
            selected=selected_armor is None,
            worn_armor_item_id=None,
            provenance=provenance(
                "10 + Dexterity modifier",
                [
                    unarmored_rule.definition_key,
                    ability_by_id["dexterity"].definition_key,
                ],
            ),
        )
    )
    selected_ac = unarmored_value
    if selected_armor is not None:
        armor_value = selected_armor.base_armor_class or 0
        armor_keys = [selected_armor.definition_key]
        formula = f"{armor_value} from worn {selected_armor.name}"
        if sheet.fighting_style_definition_key == defense_key:
            armor_value += 1
            armor_keys.append(defense_key)
            formula += " + 1 from Defense while wearing armor"
        selected_ac = armor_value
        candidates.append(
            ArmorClassCandidate(
                id=selected_armor.item_id,
                value=armor_value,
                selected=True,
                worn_armor_item_id=selected_armor.item_id,
                provenance=provenance(formula, armor_keys),
            )
        )

    armor_class = DerivedNumber(
        value=selected_ac,
        provenance=next(candidate.provenance for candidate in candidates if candidate.selected),
    )

    speed = character_creation.species.speed_feet
    speed_keys = [speed_rule.definition_key, character_creation.species.definition_key]
    speed_formula = f"Human base Speed {speed} feet"
    if (
        selected_armor is not None
        and selected_armor.minimum_strength is not None
        and sheet.abilities["strength"].final < selected_armor.minimum_strength
    ):
        speed -= 10
        speed_keys.append(selected_armor.definition_key)
        speed_formula += " - 10 feet for unmet armor Strength requirement"
    speed_feet = DerivedNumber(
        value=speed,
        provenance=provenance(speed_formula, speed_keys),
    )

    hit_points_maximum = DerivedNumber(
        value=sheet.max_hp,
        provenance=provenance(
            "Fighter level-one Hit Points 10 + Constitution modifier",
            [
                hp_rule.definition_key,
                sheet.class_definition_key,
                ability_by_id["constitution"].definition_key,
                *grant_definition_keys("ability.background.constitution"),
            ],
        ),
    )

    inventory_metadata = _inventory_provenance(character_creation, sheet)
    equippable_by_name = {item.item_name: item for item in state_catalog.equipment}
    held_ids = set(loadout.held_item_ids)
    equipment: list[EquipmentState] = []
    for item_name, quantity in sorted(inventory.items()):
        item_rule = equippable_by_name.get(item_name)
        projected_item_id, specific_definition_key, inventory_definition_keys = (
            inventory_metadata.get(
                item_name,
                (item_name.lower().replace(" ", "_"), None, []),
            )
        )
        item_id = item_rule.item_id if item_rule else projected_item_id
        if item_id == loadout.worn_armor_item_id:
            position: EquipmentPosition = "worn"
            equipped_quantity = 1
        elif item_id in held_ids:
            position = "held"
            equipped_quantity = 1
        else:
            position = "carried"
            equipped_quantity = 0
        provenance_definition_keys = _unique(
            [
                item_rule.definition_key if item_rule else "",
                *inventory_definition_keys,
            ]
        )
        if not provenance_definition_keys:
            raise CharacterStateError(f"inventory item {item_name!r} has no source definition")
        source_ids = _unique(
            source_id
            for definition_key in provenance_definition_keys
            for source_id in source_map.get(definition_key, [])
        )
        if not source_ids:
            raise CharacterStateError(f"inventory item {item_name!r} has no source citation")
        acquisition_event_ids = _unique(
            grant.acquisition_event_id
            for grant in grants
            if grant.definition_key in provenance_definition_keys
            or grant.source_definition_key in provenance_definition_keys
        )
        if not acquisition_event_ids:
            raise CharacterStateError(f"inventory item {item_name!r} has no acquisition event")
        equipment.append(
            EquipmentState(
                item_id=item_id,
                name=item_name,
                quantity=quantity,
                equipped_quantity=equipped_quantity,
                position=position,
                definition_key=(item_rule.definition_key if item_rule else specific_definition_key),
                provenance_definition_keys=provenance_definition_keys,
                source_ids=source_ids,
                acquisition_event_ids=acquisition_event_ids,
            )
        )

    resources: dict[str, ResourceState] = {}
    for resource_id, rule in resource_rules.items():
        current = resource_values.get(resource_id, rule.initial_current)
        if not 0 <= current <= rule.maximum:
            raise CharacterStateError(f"resource {resource_id} is outside 0..{rule.maximum}")
        definition_keys = [rule.definition_key]
        if resource_id == "second_wind":
            definition_keys.extend(grant_definition_keys("feature.second_wind"))
        elif resource_id == "heroic_inspiration":
            definition_keys.extend(grant_definition_keys("feature.resourceful"))
        elif resource_id == "hit_dice":
            definition_keys.append(sheet.class_definition_key)
        resources[resource_id] = ResourceState(
            current=current,
            maximum=rule.maximum,
            die=rule.die,
            short_rest_recovery=rule.short_rest_recovery,
            long_rest_recovery=rule.long_rest_recovery,
            provenance=provenance(
                "current resource bounded by its source-defined maximum",
                definition_keys,
            ),
        )

    return CharacterMechanicalState(
        resolver_version=state_catalog.resolver_version,
        character_revision=character_revision,
        state_revision=state_revision,
        level=sheet.level,
        abilities=sheet.abilities,
        proficiency_bonus=proficiency_bonus,
        saving_throws=saving_throws,
        skills=skills,
        armor_class=armor_class,
        armor_class_candidates=candidates,
        initiative=initiative,
        passive_perception=passive_perception,
        speed_feet=speed_feet,
        hit_points_current=hp,
        hit_points_maximum=hit_points_maximum,
        equipment=equipment,
        resources=resources,
    )
