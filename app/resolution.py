from __future__ import annotations

import uuid
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, Field, StringConstraints, model_validator

from app.character_creation import AbilityName, CharacterCreationCatalog, StrictModel
from app.character_state import (
    CharacterMechanicalState,
    CharacterStateCatalog,
    DerivationProvenance,
)

ResolutionType = Literal["ability_check", "saving_throw"]
AdvantageState = Literal["normal", "advantage", "disadvantage"]
ResolutionOutcome = Literal["success", "failure"]
ReasonText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class ResolutionRuleSource(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    title: str
    section: str
    printed_pages: list[int] = Field(min_length=1)
    url: AnyHttpUrl


class ResolutionRuleDefinition(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,79}$")
    definition_key: str = Field(pattern=r"^srd-5\.2\.1:[a-z0-9][a-z0-9._-]+$")
    name: str
    beginner_description: str
    source_ids: list[str] = Field(min_length=1)


class ResolutionRulesCatalog(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["1.0.0"]
    id: Literal["srd-5.2.1-check-save-resolution-v1"]
    ruleset_release_id: Literal["srd-5.2.1"]
    base_character_state_catalog_id: Literal["srd-5.2.1-party-state-v1"]
    base_character_state_catalog_sha256: Literal[
        "aba4fcdbffb037eece88c862c76be988ffc60808b46361cc9a9dda0730fe763b"
    ]
    resolver_version: Literal["check-save-resolution-1.0.0"]
    sources: list[ResolutionRuleSource] = Field(min_length=1)
    rules: list[ResolutionRuleDefinition] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_catalog(self) -> ResolutionRulesCatalog:
        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("resolution source IDs must be unique")
        rule_ids = [rule.id for rule in self.rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("resolution rule IDs must be unique")
        definition_keys = [rule.definition_key for rule in self.rules]
        if len(definition_keys) != len(set(definition_keys)):
            raise ValueError("resolution definition keys must be unique")
        known_sources = set(source_ids)
        for rule in self.rules:
            if not set(rule.source_ids) <= known_sources:
                raise ValueError(f"definition {rule.definition_key} cites an unknown source")
        required = {
            "ability_check",
            "advantage",
            "d20_test",
            "difficulty_class",
            "disadvantage",
            "saving_throw",
        }
        if set(rule_ids) != required:
            raise ValueError("resolution catalog must define the complete check/save rule slice")
        return self


class ResolutionCreate(StrictModel):
    command_id: uuid.UUID
    actor_character_id: uuid.UUID
    ruleset_release_id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    character_state_catalog_id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,99}$")
    resolution_catalog_id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,99}$")
    resolution_type: ResolutionType
    ability: AbilityName
    skill: str | None = Field(default=None, pattern=r"^[a-z][a-z_]{1,39}$")
    difficulty_class: int = Field(ge=1, le=100)
    advantage_reasons: list[ReasonText] = Field(default_factory=list, max_length=10)
    disadvantage_reasons: list[ReasonText] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def validate_resolution_shape(self) -> ResolutionCreate:
        if self.resolution_type == "saving_throw" and self.skill is not None:
            raise ValueError("saving throws cannot use a skill")
        return self


class ModifierComponent(StrictModel):
    kind: Literal["ability", "proficiency"]
    label: str
    value: int
    applied: bool
    multiplier: int = Field(ge=0, le=2)
    provenance: DerivationProvenance


class AppliedAdjustmentSource(StrictModel):
    definition_key: str
    reason: str
    source_ids: list[str] = Field(min_length=1)
    automatic: bool


class ResolvedD20Test(StrictModel):
    resolution_type: ResolutionType
    ability: AbilityName
    skill: str | None
    difficulty_class: int
    rule_definition_keys: list[str] = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    character_revision: int
    state_revision: int
    modifier: int
    modifier_formula: str
    modifier_components: list[ModifierComponent] = Field(min_length=2)
    advantage_sources: list[AppliedAdjustmentSource]
    disadvantage_sources: list[AppliedAdjustmentSource]
    advantage_state: AdvantageState
    dice_notation: Literal["1d20", "2d20"]
    dice_faces: list[int] = Field(min_length=1, max_length=2)
    selected_die: int = Field(ge=1, le=20)
    total: int
    outcome: ResolutionOutcome
    resolver_version: str


class ResolutionError(ValueError):
    pass


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _combined_provenance(
    formula: str,
    provenances: list[DerivationProvenance],
    *,
    definition_keys: list[str] | None = None,
) -> DerivationProvenance:
    first = provenances[0]
    return DerivationProvenance(
        formula=formula,
        definition_keys=_unique(
            definition_keys
            if definition_keys is not None
            else [key for provenance in provenances for key in provenance.definition_keys]
        ),
        source_ids=_unique(
            [source_id for provenance in provenances for source_id in provenance.source_ids]
        ),
        acquisition_event_ids=_unique(
            [
                event_id
                for provenance in provenances
                for event_id in provenance.acquisition_event_ids
            ]
        ),
        character_revision=first.character_revision,
        state_revision=first.state_revision,
        resolver_version=first.resolver_version,
    )


def _modifier_components(
    command: ResolutionCreate,
    state: CharacterMechanicalState,
    creation_catalog: CharacterCreationCatalog,
    state_catalog: CharacterStateCatalog,
) -> tuple[int, str, list[ModifierComponent]]:
    ability_component = state.ability_modifiers[command.ability]
    ability = ModifierComponent(
        kind="ability",
        label=f"{command.ability.replace('_', ' ').title()} modifier",
        value=ability_component.value,
        applied=True,
        multiplier=1,
        provenance=ability_component.provenance,
    )
    proficiency_bonus = state.proficiency_bonus

    if command.resolution_type == "saving_throw":
        save = state.saving_throws[command.ability]
        proficient = save.proficient
        proficiency_provenance = _combined_provenance(
            "Proficiency Bonus applies once when proficient in the selected saving throw",
            [proficiency_bonus.provenance, save.provenance],
        )
        label = f"{command.ability.replace('_', ' ').title()} saving throw proficiency"
        formula = "ability modifier + Proficiency Bonus when save-proficient"
    else:
        if command.skill is None:
            proficient = False
            proficiency_provenance = _combined_provenance(
                "No skill or tool proficiency was selected for this ability check",
                [proficiency_bonus.provenance, ability_component.provenance],
                definition_keys=proficiency_bonus.provenance.definition_keys,
            )
            label = "No applicable proficiency"
            formula = "ability modifier; no applicable proficiency"
        else:
            skill = next(
                (
                    candidate
                    for candidate in creation_catalog.skills
                    if candidate.id == command.skill
                ),
                None,
            )
            if skill is None:
                raise ResolutionError(f"Unknown skill for this ruleset: {command.skill}")
            skill_state = state.skills[command.skill]
            proficient = skill_state.proficient
            skill_rule = next(rule for rule in state_catalog.rules if rule.id == "skill_modifier")
            ability_definition_keys = {
                ability.definition_key for ability in creation_catalog.abilities
            }
            skill_keys = [
                key
                for key in skill_state.provenance.definition_keys
                if key not in ability_definition_keys
            ]
            proficiency_provenance = _combined_provenance(
                "Proficiency Bonus applies once when proficient in the selected skill",
                [proficiency_bonus.provenance, skill_state.provenance],
                definition_keys=_unique(
                    [
                        skill_rule.definition_key,
                        skill.definition_key,
                        *skill_keys,
                        *proficiency_bonus.provenance.definition_keys,
                    ]
                ),
            )
            label = f"{skill.name} proficiency"
            formula = (
                f"{command.ability.replace('_', ' ').title()} modifier + Proficiency Bonus "
                f"when proficient in {skill.name}"
            )

    proficiency_value = proficiency_bonus.value if proficient else 0
    proficiency = ModifierComponent(
        kind="proficiency",
        label=label,
        value=proficiency_value,
        applied=proficient,
        multiplier=1 if proficient else 0,
        provenance=proficiency_provenance,
    )
    return ability.value + proficiency_value, formula, [ability, proficiency]


def determine_advantage_state(
    *,
    has_advantage: bool,
    has_disadvantage: bool,
) -> AdvantageState:
    if has_advantage and has_disadvantage:
        return "normal"
    if has_advantage:
        return "advantage"
    if has_disadvantage:
        return "disadvantage"
    return "normal"


def replay_d20_values(
    advantage_state: AdvantageState,
    dice_faces: list[int],
    modifier: int,
    difficulty_class: int,
) -> tuple[int, int, ResolutionOutcome]:
    expected_dice_count = 1 if advantage_state == "normal" else 2
    if len(dice_faces) != expected_dice_count:
        raise ResolutionError(
            f"{advantage_state} resolution requires exactly {expected_dice_count} d20 result(s)"
        )
    if any(face < 1 or face > 20 for face in dice_faces):
        raise ResolutionError("d20 results must be between 1 and 20")
    if advantage_state == "advantage":
        selected_die = max(dice_faces)
    elif advantage_state == "disadvantage":
        selected_die = min(dice_faces)
    else:
        selected_die = dice_faces[0]
    total = selected_die + modifier
    return selected_die, total, "success" if total >= difficulty_class else "failure"


def resolve_d20_test(
    command: ResolutionCreate,
    state: CharacterMechanicalState,
    creation_catalog: CharacterCreationCatalog,
    state_catalog: CharacterStateCatalog,
    resolution_catalog: ResolutionRulesCatalog,
    dice_faces: list[int],
    *,
    automatic_advantage_sources: list[AppliedAdjustmentSource] | None = None,
    automatic_disadvantage_sources: list[AppliedAdjustmentSource] | None = None,
) -> ResolvedD20Test:
    rules = {rule.id: rule for rule in resolution_catalog.rules}
    advantage_rule = rules["advantage"]
    disadvantage_rule = rules["disadvantage"]
    advantage_sources = [
        AppliedAdjustmentSource(
            definition_key=advantage_rule.definition_key,
            reason=reason,
            source_ids=list(advantage_rule.source_ids),
            automatic=False,
        )
        for reason in command.advantage_reasons
    ]
    advantage_sources.extend(automatic_advantage_sources or [])
    disadvantage_sources = [
        AppliedAdjustmentSource(
            definition_key=disadvantage_rule.definition_key,
            reason=reason,
            source_ids=list(disadvantage_rule.source_ids),
            automatic=False,
        )
        for reason in command.disadvantage_reasons
    ]
    disadvantage_sources.extend(automatic_disadvantage_sources or [])

    advantage_state = determine_advantage_state(
        has_advantage=bool(advantage_sources),
        has_disadvantage=bool(disadvantage_sources),
    )
    expected_dice_count = 1 if advantage_state == "normal" else 2

    modifier, modifier_formula, components = _modifier_components(
        command, state, creation_catalog, state_catalog
    )
    selected_die, total, outcome = replay_d20_values(
        advantage_state,
        dice_faces,
        modifier,
        command.difficulty_class,
    )
    return ResolvedD20Test(
        resolution_type=command.resolution_type,
        ability=command.ability,
        skill=command.skill,
        difficulty_class=command.difficulty_class,
        rule_definition_keys=_unique(
            [
                rules["d20_test"].definition_key,
                rules[command.resolution_type].definition_key,
                rules["difficulty_class"].definition_key,
                *([rules["advantage"].definition_key] if advantage_sources else []),
                *([rules["disadvantage"].definition_key] if disadvantage_sources else []),
            ]
        ),
        source_ids=_unique(
            [
                source_id
                for rule_id in (
                    "d20_test",
                    command.resolution_type,
                    "difficulty_class",
                    *(["advantage"] if advantage_sources else []),
                    *(["disadvantage"] if disadvantage_sources else []),
                )
                for source_id in rules[rule_id].source_ids
            ]
        ),
        character_revision=state.character_revision,
        state_revision=state.state_revision,
        modifier=modifier,
        modifier_formula=modifier_formula,
        modifier_components=components,
        advantage_sources=advantage_sources,
        disadvantage_sources=disadvantage_sources,
        advantage_state=advantage_state,
        dice_notation="1d20" if expected_dice_count == 1 else "2d20",
        dice_faces=dice_faces,
        selected_die=selected_die,
        total=total,
        outcome=outcome,
        resolver_version=resolution_catalog.resolver_version,
    )
