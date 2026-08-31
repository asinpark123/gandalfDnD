from pathlib import Path

import pytest

from app.character_creation import (
    CharacterChoiceError,
    CharacterCreationCatalog,
    CharacterFinalizeRequest,
    ability_modifier,
    finalize_character_choices,
)
from app.rulesets import RulesetRegistry

REPOSITORY_ROOT = Path(__file__).parents[1]


def _catalog() -> CharacterCreationCatalog:
    loaded = RulesetRegistry.load(REPOSITORY_ROOT / "rulesets/registry.json").get_data_catalog(
        "srd-5.2.1", "srd-5.2.1-character-creation-v1"
    )
    assert isinstance(loaded.document, CharacterCreationCatalog)
    return loaded.document


def _request_data() -> dict:
    return {
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "species_definition_key": "srd-5.2.1:species.human",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "class_definition_key": "srd-5.2.1:class.fighter",
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "size": "medium",
        "alignment": "NG",
        "languages": ["dwarvish", "elvish"],
        "base_ability_scores": {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 8,
            "wisdom": 10,
            "charisma": 12,
        },
        "background_ability_increases": {"strength": 2, "constitution": 1},
        "fighter_skills": ["perception", "survival"],
        "human_skill": "insight",
        "origin_feat_definition_key": "srd-5.2.1:feat.origin.alert",
        "skilled_feat_skills": [],
        "gaming_set": "dice",
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
            "srd-5.2.1:weapon.javelin",
            "srd-5.2.1:weapon.flail",
            "srd-5.2.1:weapon.greatsword",
        ],
        "equipment_route_id": "soldier-a+fighter-a",
    }


def test_gf_002_and_gf_003_soldier_fighter_derivation() -> None:
    sheet = finalize_character_choices(
        _catalog(), CharacterFinalizeRequest.model_validate(_request_data())
    )

    assert sheet.abilities["strength"].final == 17
    assert sheet.abilities["strength"].modifier == 3
    assert sheet.abilities["dexterity"].final == 14
    assert sheet.abilities["dexterity"].modifier == 2
    assert sheet.abilities["constitution"].final == 14
    assert sheet.abilities["constitution"].modifier == 2
    assert sheet.max_hp == 12
    assert sheet.proficiency_bonus == 2
    assert sheet.saving_throw_proficiencies == ["strength", "constitution"]
    assert sheet.starting_inventory["Javelin"] == 8
    assert sheet.starting_inventory["Dice Set"] == 1
    assert sheet.starting_inventory["GP"] == 18


@pytest.mark.parametrize(
    ("score", "modifier"),
    [(1, -5), (8, -1), (9, -1), (10, 0), (13, 1), (14, 2), (17, 3), (20, 5)],
)
def test_ability_modifier_is_deterministic(score: int, modifier: int) -> None:
    assert ability_modifier(score) == modifier


def test_gf_001_rejects_incomplete_or_illegal_choice_combinations() -> None:
    catalog = _catalog()

    wrong_catalog = _request_data()
    wrong_catalog["ruleset_data_catalog_id"] = "srd-5.2.1-foundation-v1"
    with pytest.raises(CharacterChoiceError, match="ruleset_data_catalog_id"):
        finalize_character_choices(catalog, CharacterFinalizeRequest.model_validate(wrong_catalog))

    duplicate_language = _request_data()
    duplicate_language["languages"] = ["elvish", "elvish"]
    with pytest.raises(CharacterChoiceError, match="languages must not contain duplicates"):
        finalize_character_choices(
            catalog, CharacterFinalizeRequest.model_validate(duplicate_language)
        )

    overlapping_skill = _request_data()
    overlapping_skill["fighter_skills"] = ["athletics", "perception"]
    with pytest.raises(CharacterChoiceError, match="must add new proficiencies"):
        finalize_character_choices(
            catalog, CharacterFinalizeRequest.model_validate(overlapping_skill)
        )


def test_skilled_origin_feat_requires_three_distinct_new_skills() -> None:
    request_data = _request_data()
    request_data["origin_feat_definition_key"] = "srd-5.2.1:feat.origin.skilled"
    request_data["skilled_feat_skills"] = ["arcana", "history", "medicine"]
    sheet = finalize_character_choices(
        _catalog(), CharacterFinalizeRequest.model_validate(request_data)
    )
    assert {"arcana", "history", "medicine"} <= set(sheet.skill_proficiencies)

    request_data["skilled_feat_skills"] = ["arcana", "history"]
    with pytest.raises(CharacterChoiceError, match="requires 3 additional skills"):
        finalize_character_choices(
            _catalog(), CharacterFinalizeRequest.model_validate(request_data)
        )


def test_every_exposed_definition_has_durable_source_provenance() -> None:
    catalog = _catalog()
    known_sources = {source.id for source in catalog.sources}
    definitions = [
        *catalog.abilities,
        *catalog.alignments,
        *catalog.skills,
        *catalog.languages,
        *catalog.gaming_sets,
        catalog.standard_array,
        catalog.background,
        catalog.species,
        catalog.character_class,
        *catalog.features,
        *catalog.origin_feats,
        *catalog.fighting_styles,
        *catalog.weapons,
        *catalog.equipment_packages,
    ]
    assert all(definition.beginner_description for definition in definitions)
    assert all(set(definition.source_ids) <= known_sources for definition in definitions)
    assert all(source.printed_pages for source in catalog.sources)


def test_catalog_rejects_missing_granted_common_language() -> None:
    data = _catalog().model_dump(mode="json", by_alias=True)
    data["languages"] = [language for language in data["languages"] if language["id"] != "common"]

    with pytest.raises(ValueError, match="must define Common"):
        CharacterCreationCatalog.model_validate(data)


def test_catalog_rejects_cross_type_fighting_style_reference() -> None:
    data = _catalog().model_dump(mode="json", by_alias=True)
    data["character_class"]["fighting_style_options"] = ["srd-5.2.1:ability.strength"]

    with pytest.raises(ValueError, match="Fighting Style options"):
        CharacterCreationCatalog.model_validate(data)
