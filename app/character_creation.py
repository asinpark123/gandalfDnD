from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator

AbilityName = Literal[
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]
CharacterSize = Literal["small", "medium"]
Alignment = Literal["LG", "NG", "CG", "LN", "N", "CN", "LE", "NE", "CE"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RuleSource(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    title: str
    section: str
    printed_pages: list[int] = Field(min_length=1)
    url: AnyHttpUrl


class RuleOption(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")
    definition_key: str = Field(pattern=r"^srd-5\.2\.1:[a-z0-9][a-z0-9._-]+$")
    name: str
    beginner_description: str
    source_ids: list[str] = Field(min_length=1)


class AbilityOption(RuleOption):
    id: AbilityName


class SkillOption(RuleOption):
    typical_ability: AbilityName


class StandardArrayDefinition(RuleOption):
    scores: list[int] = Field(min_length=6, max_length=6)


class BackgroundDefinition(RuleOption):
    ability_score_options: list[AbilityName] = Field(min_length=3, max_length=3)
    granted_feat_definition_key: str
    skill_proficiencies: list[str] = Field(min_length=2, max_length=2)
    gaming_set_choice_count: Literal[1]
    equipment_package_definition_key: str


class SpeciesDefinition(RuleOption):
    creature_type: Literal["humanoid"]
    sizes: list[CharacterSize] = Field(min_length=2, max_length=2)
    speed_feet: int = Field(gt=0)
    skill_choice_count: Literal[1]
    origin_feat_choice_count: Literal[1]
    origin_feat_options: list[str] = Field(min_length=1)
    feature_definition_keys: list[str] = Field(min_length=1)


class ClassDefinition(RuleOption):
    level: Literal[1]
    hit_die: Literal[10]
    proficiency_bonus: Literal[2]
    saving_throw_proficiencies: list[AbilityName] = Field(min_length=2, max_length=2)
    skill_choice_count: Literal[2]
    skill_options: list[str] = Field(min_length=2)
    armor_training: list[str] = Field(min_length=1)
    weapon_proficiencies: list[str] = Field(min_length=1)
    fighting_style_choice_count: Literal[1]
    fighting_style_options: list[str] = Field(min_length=1)
    weapon_mastery_choice_count: Literal[3]
    weapon_mastery_options: list[str] = Field(min_length=3)
    feature_definition_keys: list[str] = Field(min_length=1)
    second_wind_uses: Literal[2]
    equipment_package_definition_key: str


class OriginFeatDefinition(RuleOption):
    additional_skill_choice_count: int = Field(ge=0, le=3)


class FightingStyleDefinition(RuleOption):
    effect_summary: str


class WeaponDefinition(RuleOption):
    category: Literal["simple", "martial"]
    mastery: str


class EquipmentItem(StrictModel):
    item_id: str
    name: str
    quantity: int = Field(gt=0)


class EquipmentPackageDefinition(RuleOption):
    items: list[EquipmentItem] = Field(min_length=1)
    gold_pieces: int = Field(ge=0)


class SupportedCharacterProfile(StrictModel):
    species_definition_key: str
    background_definition_key: str
    class_definition_key: str
    ability_method_definition_key: str
    equipment_route_id: str


class CharacterCreationCatalog(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["1.0.0"]
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,99}$")
    ruleset_release_id: Literal["srd-5.2.1"]
    resolver_version: Literal["character-creation-1.0.0"]
    sources: list[RuleSource] = Field(min_length=1)
    abilities: list[AbilityOption] = Field(min_length=6, max_length=6)
    alignments: list[RuleOption] = Field(min_length=9, max_length=9)
    skills: list[SkillOption] = Field(min_length=18, max_length=18)
    languages: list[RuleOption] = Field(min_length=2)
    gaming_sets: list[RuleOption] = Field(min_length=1)
    standard_array: StandardArrayDefinition
    background: BackgroundDefinition
    species: SpeciesDefinition
    character_class: ClassDefinition
    features: list[RuleOption] = Field(min_length=1)
    origin_feats: list[OriginFeatDefinition] = Field(min_length=1)
    fighting_styles: list[FightingStyleDefinition] = Field(min_length=1)
    weapons: list[WeaponDefinition] = Field(min_length=3)
    equipment_packages: list[EquipmentPackageDefinition] = Field(min_length=2)
    supported_profile: SupportedCharacterProfile

    @model_validator(mode="after")
    def validate_references(self) -> CharacterCreationCatalog:
        if {ability.id for ability in self.abilities} != {
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        }:
            raise ValueError("catalog must define all six abilities exactly once")
        if sorted(self.standard_array.scores) != [8, 10, 12, 13, 14, 15]:
            raise ValueError("standard array must contain 15, 14, 13, 12, 10, and 8")

        option_groups = {
            "alignment": self.alignments,
            "skill": self.skills,
            "language": self.languages,
            "gaming set": self.gaming_sets,
            "Origin feat": self.origin_feats,
            "Fighting Style": self.fighting_styles,
            "weapon": self.weapons,
            "equipment package": self.equipment_packages,
        }
        for label, options in option_groups.items():
            option_ids = [option.id for option in options]
            if len(option_ids) != len(set(option_ids)):
                raise ValueError(f"{label} IDs must be unique")
        if {option.id for option in self.alignments} != {
            "lg",
            "ng",
            "cg",
            "ln",
            "n",
            "cn",
            "le",
            "ne",
            "ce",
        }:
            raise ValueError("catalog must define all nine alignments exactly once")
        if "common" not in {option.id for option in self.languages}:
            raise ValueError("catalog must define Common as the granted language")

        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("rule source IDs must be unique")

        definitions: list[RuleOption] = [
            *self.abilities,
            *self.alignments,
            *self.skills,
            *self.languages,
            *self.gaming_sets,
            self.standard_array,
            self.background,
            self.species,
            self.character_class,
            *self.features,
            *self.origin_feats,
            *self.fighting_styles,
            *self.weapons,
            *self.equipment_packages,
        ]
        definition_keys = [definition.definition_key for definition in definitions]
        if len(definition_keys) != len(set(definition_keys)):
            raise ValueError("rule definition keys must be unique")
        known_sources = set(source_ids)
        for definition in definitions:
            if not set(definition.source_ids) <= known_sources:
                raise ValueError(f"definition {definition.definition_key} cites an unknown source")

        known_definitions = set(definition_keys)
        references = {
            self.supported_profile.species_definition_key,
            self.supported_profile.background_definition_key,
            self.supported_profile.class_definition_key,
            self.supported_profile.ability_method_definition_key,
            self.background.granted_feat_definition_key,
            self.background.equipment_package_definition_key,
            self.character_class.equipment_package_definition_key,
            *self.species.origin_feat_options,
            *self.character_class.fighting_style_options,
            *self.character_class.weapon_mastery_options,
        }
        if not references <= known_definitions:
            raise ValueError(
                f"catalog references unknown definitions: {sorted(references - known_definitions)}"
            )
        skill_ids = {option.id for option in self.skills}
        if not set(self.background.skill_proficiencies) <= skill_ids:
            raise ValueError("background references unknown skills")
        if not set(self.character_class.skill_options) <= skill_ids:
            raise ValueError("class references unknown skills")

        origin_feat_keys = {option.definition_key for option in self.origin_feats}
        if self.background.granted_feat_definition_key not in origin_feat_keys:
            raise ValueError("background feat must reference an Origin feat")
        if not set(self.species.origin_feat_options) <= origin_feat_keys:
            raise ValueError("species feat options must reference Origin feats")

        feature_keys = {option.definition_key for option in self.features}
        if not set(self.species.feature_definition_keys) <= feature_keys:
            raise ValueError("species references unknown features")
        if not set(self.character_class.feature_definition_keys) <= feature_keys:
            raise ValueError("class references unknown features")

        style_keys = {option.definition_key for option in self.fighting_styles}
        if not set(self.character_class.fighting_style_options) <= style_keys:
            raise ValueError("class Fighting Style options reference another definition type")
        weapon_keys = {option.definition_key for option in self.weapons}
        if not set(self.character_class.weapon_mastery_options) <= weapon_keys:
            raise ValueError("class weapon mastery options reference another definition type")
        package_keys = {option.definition_key for option in self.equipment_packages}
        if {
            self.background.equipment_package_definition_key,
            self.character_class.equipment_package_definition_key,
        } - package_keys:
            raise ValueError("supported equipment route references unknown packages")
        if self.supported_profile.equipment_route_id != "soldier-a+fighter-a":
            raise ValueError("unsupported equipment route")
        return self


class CharacterFinalizeRequest(StrictModel):
    ruleset_data_catalog_id: str
    species_definition_key: str
    background_definition_key: str
    class_definition_key: str
    ability_method_definition_key: str
    size: CharacterSize
    alignment: Alignment
    languages: list[str] = Field(min_length=2, max_length=2)
    base_ability_scores: dict[AbilityName, int]
    background_ability_increases: dict[AbilityName, int]
    fighter_skills: list[str] = Field(min_length=2, max_length=2)
    human_skill: str
    origin_feat_definition_key: str
    skilled_feat_skills: list[str] = Field(default_factory=list, max_length=3)
    gaming_set: str
    fighting_style_definition_key: str
    weapon_mastery_definition_keys: list[str] = Field(min_length=3, max_length=3)
    equipment_route_id: Literal["soldier-a+fighter-a"]


class AbilityScoreRead(StrictModel):
    base: int
    background_increase: int
    final: int
    modifier: int


class CharacterSheet(StrictModel):
    level: Literal[1]
    species_definition_key: str
    background_definition_key: str
    class_definition_key: str
    ability_method_definition_key: str
    size: CharacterSize
    alignment: Alignment
    languages: list[str]
    abilities: dict[AbilityName, AbilityScoreRead]
    proficiency_bonus: Literal[2]
    skill_proficiencies: list[str]
    saving_throw_proficiencies: list[AbilityName]
    gaming_set_proficiency: str
    armor_training: list[str]
    weapon_proficiencies: list[str]
    origin_feat_definition_keys: list[str]
    fighting_style_definition_key: str
    weapon_mastery_definition_keys: list[str]
    feature_definition_keys: list[str]
    second_wind_uses_max: Literal[2]
    max_hp: int = Field(gt=0)
    equipment_route_id: str
    starting_inventory: dict[str, int]
    ruleset_release_id: str
    ruleset_data_catalog_id: str
    resolver_version: str


class CharacterChoiceError(ValueError):
    pass


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


def _require_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise CharacterChoiceError(f"{label} must not contain duplicates")


def finalize_character_choices(
    catalog: CharacterCreationCatalog, request: CharacterFinalizeRequest
) -> CharacterSheet:
    profile = catalog.supported_profile
    expected = {
        "ruleset_data_catalog_id": catalog.id,
        "species_definition_key": profile.species_definition_key,
        "background_definition_key": profile.background_definition_key,
        "class_definition_key": profile.class_definition_key,
        "ability_method_definition_key": profile.ability_method_definition_key,
        "equipment_route_id": profile.equipment_route_id,
    }
    for field, value in expected.items():
        if getattr(request, field) != value:
            raise CharacterChoiceError(f"{field} is not supported by this catalog")

    ability_names = {ability.id for ability in catalog.abilities}
    if set(request.base_ability_scores) != ability_names:
        raise CharacterChoiceError("base_ability_scores must contain all six abilities")
    if Counter(request.base_ability_scores.values()) != Counter(catalog.standard_array.scores):
        raise CharacterChoiceError("base ability scores must use each standard-array value once")

    increases = request.background_ability_increases
    allowed_increases = set(catalog.background.ability_score_options)
    if not set(increases) <= allowed_increases or any(
        value not in (1, 2) for value in increases.values()
    ):
        raise CharacterChoiceError("background increases must use Soldier ability options")
    if sorted(increases.values()) not in ([1, 1, 1], [1, 2]):
        raise CharacterChoiceError("background increases must be +2/+1 or +1/+1/+1")

    language_ids = {option.id for option in catalog.languages if option.id != "common"}
    _require_unique(request.languages, "languages")
    if not set(request.languages) <= language_ids:
        raise CharacterChoiceError("choose two supported languages other than Common")

    class_skill_options = set(catalog.character_class.skill_options)
    _require_unique(request.fighter_skills, "fighter_skills")
    if not set(request.fighter_skills) <= class_skill_options:
        raise CharacterChoiceError("fighter_skills contain an unsupported Fighter skill")
    background_skills = set(catalog.background.skill_proficiencies)
    if set(request.fighter_skills) & background_skills:
        raise CharacterChoiceError("fighter_skills must add new proficiencies")

    skill_ids = {skill.id for skill in catalog.skills}
    current_skills = background_skills | set(request.fighter_skills)
    if request.human_skill not in skill_ids or request.human_skill in current_skills:
        raise CharacterChoiceError("human_skill must add a supported new skill proficiency")
    current_skills.add(request.human_skill)

    feat_by_key = {feat.definition_key: feat for feat in catalog.origin_feats}
    if request.origin_feat_definition_key not in catalog.species.origin_feat_options:
        raise CharacterChoiceError("origin feat is not supported for this Human profile")
    chosen_feat = feat_by_key[request.origin_feat_definition_key]
    _require_unique(request.skilled_feat_skills, "skilled_feat_skills")
    if len(request.skilled_feat_skills) != chosen_feat.additional_skill_choice_count:
        required_count = chosen_feat.additional_skill_choice_count
        raise CharacterChoiceError(
            f"{chosen_feat.name} requires {required_count} additional skills"
        )
    if (
        not set(request.skilled_feat_skills) <= skill_ids
        or set(request.skilled_feat_skills) & current_skills
    ):
        raise CharacterChoiceError(
            "Skilled feat choices must add supported new skill proficiencies"
        )
    current_skills.update(request.skilled_feat_skills)

    gaming_set_ids = {option.id for option in catalog.gaming_sets}
    if request.gaming_set not in gaming_set_ids:
        raise CharacterChoiceError("gaming_set is not supported")
    if request.size not in catalog.species.sizes:
        raise CharacterChoiceError("size is not supported for Human")
    if request.fighting_style_definition_key not in catalog.character_class.fighting_style_options:
        raise CharacterChoiceError("fighting style is not supported for Fighter")
    _require_unique(request.weapon_mastery_definition_keys, "weapon masteries")
    if not set(request.weapon_mastery_definition_keys) <= set(
        catalog.character_class.weapon_mastery_options
    ):
        raise CharacterChoiceError("weapon masteries contain an unsupported weapon")

    ability_scores: dict[AbilityName, AbilityScoreRead] = {}
    for ability in catalog.abilities:
        base = request.base_ability_scores[ability.id]
        increase = increases.get(ability.id, 0)
        final = base + increase
        if final > 20:
            raise CharacterChoiceError("an ability score cannot exceed 20")
        ability_scores[ability.id] = AbilityScoreRead(
            base=base,
            background_increase=increase,
            final=final,
            modifier=ability_modifier(final),
        )

    packages = {package.definition_key: package for package in catalog.equipment_packages}
    selected_packages = (
        packages[catalog.background.equipment_package_definition_key],
        packages[catalog.character_class.equipment_package_definition_key],
    )
    inventory: dict[str, int] = {}
    gold = 0
    for package in selected_packages:
        gold += package.gold_pieces
        for item in package.items:
            item_name = item.name
            if item.item_id == "chosen_gaming_set":
                item_name = next(
                    option.name for option in catalog.gaming_sets if option.id == request.gaming_set
                )
            inventory[item_name] = inventory.get(item_name, 0) + item.quantity
    if gold:
        inventory["GP"] = gold

    granted_feat = catalog.background.granted_feat_definition_key
    constitution_modifier = ability_scores["constitution"].modifier
    max_hp = catalog.character_class.hit_die + constitution_modifier
    return CharacterSheet(
        level=1,
        species_definition_key=request.species_definition_key,
        background_definition_key=request.background_definition_key,
        class_definition_key=request.class_definition_key,
        ability_method_definition_key=request.ability_method_definition_key,
        size=request.size,
        alignment=request.alignment,
        languages=["common", *request.languages],
        abilities=ability_scores,
        proficiency_bonus=2,
        skill_proficiencies=sorted(current_skills),
        saving_throw_proficiencies=catalog.character_class.saving_throw_proficiencies,
        gaming_set_proficiency=request.gaming_set,
        armor_training=catalog.character_class.armor_training,
        weapon_proficiencies=catalog.character_class.weapon_proficiencies,
        origin_feat_definition_keys=[granted_feat, request.origin_feat_definition_key],
        fighting_style_definition_key=request.fighting_style_definition_key,
        weapon_mastery_definition_keys=request.weapon_mastery_definition_keys,
        feature_definition_keys=[
            *catalog.species.feature_definition_keys,
            *catalog.character_class.feature_definition_keys,
        ],
        second_wind_uses_max=2,
        max_hp=max_hp,
        equipment_route_id=request.equipment_route_id,
        starting_inventory=inventory,
        ruleset_release_id=catalog.ruleset_release_id,
        ruleset_data_catalog_id=catalog.id,
        resolver_version=catalog.resolver_version,
    )
