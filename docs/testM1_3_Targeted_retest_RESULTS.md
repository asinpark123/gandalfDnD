Actions and results:
Action1.
Curl
curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/state' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/state
Server response
Code	200	
Response body
{
  "campaign": {
    "id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
    "name": "hello world",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "status": "active",
    "play_mode": "party_commander",
    "party_min_active": 2,
    "party_max_active": 4,
    "created_at": "2026-08-31T22:37:43.654285+12:00"
  },
  "character": null,
  "characters": [
    {
      "id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
      "name": "SugarHigh",
      "creation_status": "finalized",
      "revision": 1,
      "hp": 12,
      "max_hp": 12,
      "inventory": {
        "GP": 18,
        "Arrow": 20,
        "Flail": 1,
        "Spear": 1,
        "Quiver": 1,
        "Javelin": 8,
        "Dice Set": 1,
        "Shortbow": 1,
        "Chain Mail": 1,
        "Greatsword": 1,
        "Healer's Kit": 1,
        "Dungeoneer's Pack": 1,
        "Traveler's Clothes": 1
      },
      "character_sheet": {
        "level": 1,
        "species_definition_key": "srd-5.2.1:species.human",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "class_definition_key": "srd-5.2.1:class.fighter",
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "size": "medium",
        "alignment": "NG",
        "languages": [
          "common",
          "dwarvish",
          "elvish"
        ],
        "abilities": {
          "wisdom": {
            "base": 10,
            "background_increase": 0,
            "final": 10,
            "modifier": 0
          },
          "charisma": {
            "base": 12,
            "background_increase": 0,
            "final": 12,
            "modifier": 1
          },
          "strength": {
            "base": 15,
            "background_increase": 2,
            "final": 17,
            "modifier": 3
          },
          "dexterity": {
            "base": 14,
            "background_increase": 0,
            "final": 14,
            "modifier": 2
          },
          "constitution": {
            "base": 13,
            "background_increase": 1,
            "final": 14,
            "modifier": 2
          },
          "intelligence": {
            "base": 8,
            "background_increase": 0,
            "final": 8,
            "modifier": -1
          }
        },
        "proficiency_bonus": 2,
        "skill_proficiencies": [
          "athletics",
          "insight",
          "intimidation",
          "perception",
          "survival"
        ],
        "saving_throw_proficiencies": [
          "strength",
          "constitution"
        ],
        "gaming_set_proficiency": "dice",
        "armor_training": [
          "light",
          "medium",
          "heavy",
          "shields"
        ],
        "weapon_proficiencies": [
          "simple",
          "martial"
        ],
        "origin_feat_definition_keys": [
          "srd-5.2.1:feat.origin.savage_attacker",
          "srd-5.2.1:feat.origin.alert"
        ],
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
          "srd-5.2.1:weapon.javelin",
          "srd-5.2.1:weapon.flail",
          "srd-5.2.1:weapon.greatsword"
        ],
        "feature_definition_keys": [
          "srd-5.2.1:species_feature.human.resourceful",
          "srd-5.2.1:species_feature.human.skillful",
          "srd-5.2.1:species_feature.human.versatile",
          "srd-5.2.1:class_feature.fighter.fighting_style",
          "srd-5.2.1:class_feature.fighter.second_wind",
          "srd-5.2.1:class_feature.fighter.weapon_mastery"
        ],
        "second_wind_uses_max": 2,
        "max_hp": 12,
        "equipment_route_id": "soldier-a+fighter-a",
        "starting_inventory": {
          "GP": 18,
          "Arrow": 20,
          "Flail": 1,
          "Spear": 1,
          "Quiver": 1,
          "Javelin": 8,
          "Dice Set": 1,
          "Shortbow": 1,
          "Chain Mail": 1,
          "Greatsword": 1,
          "Healer's Kit": 1,
          "Dungeoneer's Pack": 1,
          "Traveler's Clothes": 1
        },
        "ruleset_release_id": "srd-5.2.1",
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "resolver_version": "character-creation-1.0.0"
      },
      "finalized_at": "2026-08-31T22:55:22.788199+12:00",
      "party_position": 1,
      "control_mode": "player",
      "party_status": "active",
      "state_revision": 2,
      "equipped_items": {
        "worn_armor_item_id": null,
        "held_item_ids": [
          "greatsword"
        ]
      },
      "resources": {
        "hit_dice": 1,
        "second_wind": 2,
        "heroic_inspiration": 1
      },
      "mechanical_state": {
        "resolver_version": "character-state-1.0.0",
        "character_revision": 1,
        "state_revision": 2,
        "level": 1,
        "abilities": {
          "wisdom": {
            "base": 10,
            "background_increase": 0,
            "final": 10,
            "modifier": 0
          },
          "charisma": {
            "base": 12,
            "background_increase": 0,
            "final": 12,
            "modifier": 1
          },
          "strength": {
            "base": 15,
            "background_increase": 2,
            "final": 17,
            "modifier": 3
          },
          "dexterity": {
            "base": 14,
            "background_increase": 0,
            "final": 14,
            "modifier": 2
          },
          "constitution": {
            "base": 13,
            "background_increase": 1,
            "final": 14,
            "modifier": 2
          },
          "intelligence": {
            "base": 8,
            "background_increase": 0,
            "final": 8,
            "modifier": -1
          }
        },
        "proficiency_bonus": {
          "value": 2,
          "provenance": {
            "formula": "level 1 proficiency bonus = 2",
            "definition_keys": [
              "srd-5.2.1:rule.proficiency_bonus",
              "srd-5.2.1:class.fighter"
            ],
            "source_ids": [
              "srd-d20",
              "srd-character-details",
              "srd-fighter",
              "srd-character-creation",
              "srd-core-d20"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ],
            "character_revision": 1,
            "state_revision": 2,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "saving_throws": {
          "wisdom": {
            "value": 0,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.wisdom"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": false
          },
          "charisma": {
            "value": 1,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "strength": {
            "value": 5,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.strength",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation",
                "srd-fighter",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "strength",
            "proficient": true
          },
          "dexterity": {
            "value": 2,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "constitution": {
            "value": 4,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.constitution",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation",
                "srd-fighter",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "constitution",
            "proficient": true
          },
          "intelligence": {
            "value": -1,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          }
        },
        "skills": {
          "acrobatics": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.acrobatics",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "animal_handling": {
            "value": 0,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.animal_handling",
                "srd-5.2.1:ability.wisdom"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": false
          },
          "arcana": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.arcana",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "athletics": {
            "value": 5,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.athletics",
                "srd-5.2.1:ability.strength",
                "srd-5.2.1:background.soldier"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-soldier",
                "srd-feats",
                "srd-equipment"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "strength",
            "proficient": true
          },
          "deception": {
            "value": 1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.deception",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "history": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.history",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "insight": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.insight",
                "srd-5.2.1:ability.wisdom",
                "srd-5.2.1:species_feature.human.skillful"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-human"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": true
          },
          "intimidation": {
            "value": 3,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.intimidation",
                "srd-5.2.1:ability.charisma",
                "srd-5.2.1:background.soldier"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-soldier",
                "srd-feats",
                "srd-equipment"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": true
          },
          "investigation": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.investigation",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "medicine": {
            "value": 0,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.medicine",
                "srd-5.2.1:ability.wisdom"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": false
          },
          "nature": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.nature",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "perception": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.perception",
                "srd-5.2.1:ability.wisdom",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-fighter"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": true
          },
          "performance": {
            "value": 1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.performance",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "persuasion": {
            "value": 1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.persuasion",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "religion": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.religion",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "sleight_of_hand": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.sleight_of_hand",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "stealth": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.stealth",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "survival": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.survival",
                "srd-5.2.1:ability.wisdom",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-fighter"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": true
          }
        },
        "armor_class": {
          "value": 12,
          "provenance": {
            "formula": "10 + Dexterity modifier",
            "definition_keys": [
              "srd-5.2.1:rule.armor_class.unarmored",
              "srd-5.2.1:ability.dexterity"
            ],
            "source_ids": [
              "srd-character-details",
              "srd-character-creation"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ],
            "character_revision": 1,
            "state_revision": 2,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "armor_class_candidates": [
          {
            "id": "unarmored",
            "value": 12,
            "selected": true,
            "worn_armor_item_id": null,
            "provenance": {
              "formula": "10 + Dexterity modifier",
              "definition_keys": [
                "srd-5.2.1:rule.armor_class.unarmored",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            }
          }
        ],
        "initiative": {
          "value": 4,
          "provenance": {
            "formula": "Dexterity modifier + proficiency bonus when Alert grants Initiative proficiency",
            "definition_keys": [
              "srd-5.2.1:rule.initiative",
              "srd-5.2.1:ability.dexterity",
              "srd-5.2.1:feat.origin.alert"
            ],
            "source_ids": [
              "srd-character-details",
              "srd-feat-state",
              "srd-character-creation",
              "srd-feats"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ],
            "character_revision": 1,
            "state_revision": 2,
            "resolver_version": "character-state-1.0.0"
          },
          "ability": "dexterity",
          "proficient": true
        },
        "passive_perception": {
          "value": 12,
          "provenance": {
            "formula": "10 + Wisdom (Perception) check modifier",
            "definition_keys": [
              "srd-5.2.1:rule.passive_perception",
              "srd-5.2.1:rule.skill_modifier",
              "srd-5.2.1:skill.perception",
              "srd-5.2.1:ability.wisdom",
              "srd-5.2.1:class.fighter"
            ],
            "source_ids": [
              "srd-character-details",
              "srd-core-d20",
              "srd-character-creation",
              "srd-fighter"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ],
            "character_revision": 1,
            "state_revision": 2,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "speed_feet": {
          "value": 30,
          "provenance": {
            "formula": "Human base Speed 30 feet",
            "definition_keys": [
              "srd-5.2.1:rule.speed",
              "srd-5.2.1:species.human"
            ],
            "source_ids": [
              "srd-human-state",
              "srd-equipment-state",
              "srd-human",
              "srd-character-creation"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ],
            "character_revision": 1,
            "state_revision": 2,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "hit_points_current": 12,
        "hit_points_maximum": {
          "value": 12,
          "provenance": {
            "formula": "Fighter level-one Hit Points 10 + Constitution modifier",
            "definition_keys": [
              "srd-5.2.1:rule.hit_points.level_one",
              "srd-5.2.1:class.fighter",
              "srd-5.2.1:ability.constitution",
              "srd-5.2.1:background.soldier"
            ],
            "source_ids": [
              "srd-character-details",
              "srd-fighter-state",
              "srd-fighter",
              "srd-character-creation",
              "srd-soldier",
              "srd-feats",
              "srd-core-d20",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ],
            "character_revision": 1,
            "state_revision": 2,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "equipment": [
          {
            "item_id": "arrow",
            "name": "Arrow",
            "quantity": 20,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "chain_mail",
            "name": "Chain Mail",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.chain_mail",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.chain_mail",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "dice_set",
            "name": "Dice Set",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:tool.gaming_set.dice",
            "provenance_definition_keys": [
              "srd-5.2.1:tool.gaming_set.dice",
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-equipment",
              "srd-soldier"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "dungeoneers_pack",
            "name": "Dungeoneer's Pack",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "flail",
            "name": "Flail",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.flail.state",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.flail.state",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "gp",
            "name": "GP",
            "quantity": 18,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment",
              "srd-fighter"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "greatsword",
            "name": "Greatsword",
            "quantity": 1,
            "equipped_quantity": 1,
            "position": "held",
            "definition_key": "srd-5.2.1:equipment.greatsword.state",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.greatsword.state",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "healers_kit",
            "name": "Healer's Kit",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "javelin",
            "name": "Javelin",
            "quantity": 8,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.javelin.state",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.javelin.state",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "quiver",
            "name": "Quiver",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "shortbow",
            "name": "Shortbow",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "spear",
            "name": "Spear",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          },
          {
            "item_id": "travelers_clothes",
            "name": "Traveler's Clothes",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
            ]
          }
        ],
        "resources": {
          "second_wind": {
            "current": 2,
            "maximum": 2,
            "die": "d10",
            "short_rest_recovery": "one",
            "long_rest_recovery": "all",
            "provenance": {
              "formula": "current resource bounded by its source-defined maximum",
              "definition_keys": [
                "srd-5.2.1:resource.fighter.second_wind",
                "srd-5.2.1:class_feature.fighter.second_wind",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-fighter-state",
                "srd-fighter",
                "srd-character-creation",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            }
          },
          "heroic_inspiration": {
            "current": 1,
            "maximum": 1,
            "die": null,
            "short_rest_recovery": "none",
            "long_rest_recovery": "none",
            "provenance": {
              "formula": "current resource bounded by its source-defined maximum",
              "definition_keys": [
                "srd-5.2.1:resource.human.heroic_inspiration",
                "srd-5.2.1:species_feature.human.resourceful",
                "srd-5.2.1:species.human"
              ],
              "source_ids": [
                "srd-d20",
                "srd-human-state",
                "srd-human",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            }
          },
          "hit_dice": {
            "current": 1,
            "maximum": 1,
            "die": "d10",
            "short_rest_recovery": "none",
            "long_rest_recovery": "all",
            "provenance": {
              "formula": "current resource bounded by its source-defined maximum",
              "definition_keys": [
                "srd-5.2.1:resource.fighter.hit_dice",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-fighter-state",
                "srd-fighter",
                "srd-character-creation",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 2,
              "resolver_version": "character-state-1.0.0"
            }
          }
        }
      }
    },
    {
      "id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
      "name": "LooneyHigh",
      "creation_status": "finalized",
      "revision": 1,
      "hp": 12,
      "max_hp": 12,
      "inventory": {
        "GP": 18,
        "Arrow": 20,
        "Flail": 1,
        "Spear": 1,
        "Quiver": 1,
        "Javelin": 8,
        "Dice Set": 1,
        "Shortbow": 1,
        "Chain Mail": 1,
        "Greatsword": 1,
        "Healer's Kit": 1,
        "Dungeoneer's Pack": 1,
        "Traveler's Clothes": 1
      },
      "character_sheet": {
        "level": 1,
        "species_definition_key": "srd-5.2.1:species.human",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "class_definition_key": "srd-5.2.1:class.fighter",
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "size": "medium",
        "alignment": "NG",
        "languages": [
          "common",
          "dwarvish",
          "elvish"
        ],
        "abilities": {
          "wisdom": {
            "base": 10,
            "background_increase": 0,
            "final": 10,
            "modifier": 0
          },
          "charisma": {
            "base": 12,
            "background_increase": 0,
            "final": 12,
            "modifier": 1
          },
          "strength": {
            "base": 15,
            "background_increase": 2,
            "final": 17,
            "modifier": 3
          },
          "dexterity": {
            "base": 14,
            "background_increase": 0,
            "final": 14,
            "modifier": 2
          },
          "constitution": {
            "base": 13,
            "background_increase": 1,
            "final": 14,
            "modifier": 2
          },
          "intelligence": {
            "base": 8,
            "background_increase": 0,
            "final": 8,
            "modifier": -1
          }
        },
        "proficiency_bonus": 2,
        "skill_proficiencies": [
          "athletics",
          "insight",
          "intimidation",
          "perception",
          "survival"
        ],
        "saving_throw_proficiencies": [
          "strength",
          "constitution"
        ],
        "gaming_set_proficiency": "dice",
        "armor_training": [
          "light",
          "medium",
          "heavy",
          "shields"
        ],
        "weapon_proficiencies": [
          "simple",
          "martial"
        ],
        "origin_feat_definition_keys": [
          "srd-5.2.1:feat.origin.savage_attacker",
          "srd-5.2.1:feat.origin.alert"
        ],
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
          "srd-5.2.1:weapon.javelin",
          "srd-5.2.1:weapon.flail",
          "srd-5.2.1:weapon.greatsword"
        ],
        "feature_definition_keys": [
          "srd-5.2.1:species_feature.human.resourceful",
          "srd-5.2.1:species_feature.human.skillful",
          "srd-5.2.1:species_feature.human.versatile",
          "srd-5.2.1:class_feature.fighter.fighting_style",
          "srd-5.2.1:class_feature.fighter.second_wind",
          "srd-5.2.1:class_feature.fighter.weapon_mastery"
        ],
        "second_wind_uses_max": 2,
        "max_hp": 12,
        "equipment_route_id": "soldier-a+fighter-a",
        "starting_inventory": {
          "GP": 18,
          "Arrow": 20,
          "Flail": 1,
          "Spear": 1,
          "Quiver": 1,
          "Javelin": 8,
          "Dice Set": 1,
          "Shortbow": 1,
          "Chain Mail": 1,
          "Greatsword": 1,
          "Healer's Kit": 1,
          "Dungeoneer's Pack": 1,
          "Traveler's Clothes": 1
        },
        "ruleset_release_id": "srd-5.2.1",
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "resolver_version": "character-creation-1.0.0"
      },
      "finalized_at": "2026-08-31T23:02:55.175375+12:00",
      "party_position": 2,
      "control_mode": "player",
      "party_status": "active",
      "state_revision": 1,
      "equipped_items": {
        "worn_armor_item_id": "chain_mail",
        "held_item_ids": []
      },
      "resources": {
        "hit_dice": 1,
        "second_wind": 2,
        "heroic_inspiration": 1
      },
      "mechanical_state": {
        "resolver_version": "character-state-1.0.0",
        "character_revision": 1,
        "state_revision": 1,
        "level": 1,
        "abilities": {
          "wisdom": {
            "base": 10,
            "background_increase": 0,
            "final": 10,
            "modifier": 0
          },
          "charisma": {
            "base": 12,
            "background_increase": 0,
            "final": 12,
            "modifier": 1
          },
          "strength": {
            "base": 15,
            "background_increase": 2,
            "final": 17,
            "modifier": 3
          },
          "dexterity": {
            "base": 14,
            "background_increase": 0,
            "final": 14,
            "modifier": 2
          },
          "constitution": {
            "base": 13,
            "background_increase": 1,
            "final": 14,
            "modifier": 2
          },
          "intelligence": {
            "base": 8,
            "background_increase": 0,
            "final": 8,
            "modifier": -1
          }
        },
        "proficiency_bonus": {
          "value": 2,
          "provenance": {
            "formula": "level 1 proficiency bonus = 2",
            "definition_keys": [
              "srd-5.2.1:rule.proficiency_bonus",
              "srd-5.2.1:class.fighter"
            ],
            "source_ids": [
              "srd-d20",
              "srd-character-details",
              "srd-fighter",
              "srd-character-creation",
              "srd-core-d20"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ],
            "character_revision": 1,
            "state_revision": 1,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "saving_throws": {
          "wisdom": {
            "value": 0,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.wisdom"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": false
          },
          "charisma": {
            "value": 1,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "strength": {
            "value": 5,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.strength",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation",
                "srd-fighter",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "strength",
            "proficient": true
          },
          "dexterity": {
            "value": 2,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "constitution": {
            "value": 4,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.constitution",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation",
                "srd-fighter",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "constitution",
            "proficient": true
          },
          "intelligence": {
            "value": -1,
            "provenance": {
              "formula": "ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.saving_throw_modifier",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          }
        },
        "skills": {
          "acrobatics": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.acrobatics",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "animal_handling": {
            "value": 0,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.animal_handling",
                "srd-5.2.1:ability.wisdom"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": false
          },
          "arcana": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.arcana",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "athletics": {
            "value": 5,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.athletics",
                "srd-5.2.1:ability.strength",
                "srd-5.2.1:background.soldier"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-soldier",
                "srd-feats",
                "srd-equipment"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "strength",
            "proficient": true
          },
          "deception": {
            "value": 1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.deception",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "history": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.history",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "insight": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.insight",
                "srd-5.2.1:ability.wisdom",
                "srd-5.2.1:species_feature.human.skillful"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-human"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": true
          },
          "intimidation": {
            "value": 3,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.intimidation",
                "srd-5.2.1:ability.charisma",
                "srd-5.2.1:background.soldier"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-soldier",
                "srd-feats",
                "srd-equipment"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": true
          },
          "investigation": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.investigation",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "medicine": {
            "value": 0,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.medicine",
                "srd-5.2.1:ability.wisdom"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": false
          },
          "nature": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.nature",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "perception": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.perception",
                "srd-5.2.1:ability.wisdom",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-fighter"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": true
          },
          "performance": {
            "value": 1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.performance",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "persuasion": {
            "value": 1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.persuasion",
                "srd-5.2.1:ability.charisma"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "charisma",
            "proficient": false
          },
          "religion": {
            "value": -1,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.religion",
                "srd-5.2.1:ability.intelligence"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "intelligence",
            "proficient": false
          },
          "sleight_of_hand": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.sleight_of_hand",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "stealth": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.stealth",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "dexterity",
            "proficient": false
          },
          "survival": {
            "value": 2,
            "provenance": {
              "formula": "typical ability modifier + proficiency bonus when proficient",
              "definition_keys": [
                "srd-5.2.1:rule.skill_modifier",
                "srd-5.2.1:skill.survival",
                "srd-5.2.1:ability.wisdom",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-core-d20",
                "srd-character-creation",
                "srd-fighter"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            },
            "ability": "wisdom",
            "proficient": true
          }
        },
        "armor_class": {
          "value": 17,
          "provenance": {
            "formula": "16 from worn Chain Mail State + 1 from Defense while wearing armor",
            "definition_keys": [
              "srd-5.2.1:equipment.chain_mail",
              "srd-5.2.1:feat.fighting_style.defense"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-feats"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ],
            "character_revision": 1,
            "state_revision": 1,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "armor_class_candidates": [
          {
            "id": "unarmored",
            "value": 12,
            "selected": false,
            "worn_armor_item_id": null,
            "provenance": {
              "formula": "10 + Dexterity modifier",
              "definition_keys": [
                "srd-5.2.1:rule.armor_class.unarmored",
                "srd-5.2.1:ability.dexterity"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            }
          },
          {
            "id": "chain_mail",
            "value": 17,
            "selected": true,
            "worn_armor_item_id": "chain_mail",
            "provenance": {
              "formula": "16 from worn Chain Mail State + 1 from Defense while wearing armor",
              "definition_keys": [
                "srd-5.2.1:equipment.chain_mail",
                "srd-5.2.1:feat.fighting_style.defense"
              ],
              "source_ids": [
                "srd-equipment-state",
                "srd-feats"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            }
          }
        ],
        "initiative": {
          "value": 4,
          "provenance": {
            "formula": "Dexterity modifier + proficiency bonus when Alert grants Initiative proficiency",
            "definition_keys": [
              "srd-5.2.1:rule.initiative",
              "srd-5.2.1:ability.dexterity",
              "srd-5.2.1:feat.origin.alert"
            ],
            "source_ids": [
              "srd-character-details",
              "srd-feat-state",
              "srd-character-creation",
              "srd-feats"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ],
            "character_revision": 1,
            "state_revision": 1,
            "resolver_version": "character-state-1.0.0"
          },
          "ability": "dexterity",
          "proficient": true
        },
        "passive_perception": {
          "value": 12,
          "provenance": {
            "formula": "10 + Wisdom (Perception) check modifier",
            "definition_keys": [
              "srd-5.2.1:rule.passive_perception",
              "srd-5.2.1:rule.skill_modifier",
              "srd-5.2.1:skill.perception",
              "srd-5.2.1:ability.wisdom",
              "srd-5.2.1:class.fighter"
            ],
            "source_ids": [
              "srd-character-details",
              "srd-core-d20",
              "srd-character-creation",
              "srd-fighter"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ],
            "character_revision": 1,
            "state_revision": 1,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "speed_feet": {
          "value": 30,
          "provenance": {
            "formula": "Human base Speed 30 feet",
            "definition_keys": [
              "srd-5.2.1:rule.speed",
              "srd-5.2.1:species.human"
            ],
            "source_ids": [
              "srd-human-state",
              "srd-equipment-state",
              "srd-human",
              "srd-character-creation"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ],
            "character_revision": 1,
            "state_revision": 1,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "hit_points_current": 12,
        "hit_points_maximum": {
          "value": 12,
          "provenance": {
            "formula": "Fighter level-one Hit Points 10 + Constitution modifier",
            "definition_keys": [
              "srd-5.2.1:rule.hit_points.level_one",
              "srd-5.2.1:class.fighter",
              "srd-5.2.1:ability.constitution",
              "srd-5.2.1:background.soldier"
            ],
            "source_ids": [
              "srd-character-details",
              "srd-fighter-state",
              "srd-fighter",
              "srd-character-creation",
              "srd-soldier",
              "srd-feats",
              "srd-core-d20",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ],
            "character_revision": 1,
            "state_revision": 1,
            "resolver_version": "character-state-1.0.0"
          }
        },
        "equipment": [
          {
            "item_id": "arrow",
            "name": "Arrow",
            "quantity": 20,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "chain_mail",
            "name": "Chain Mail",
            "quantity": 1,
            "equipped_quantity": 1,
            "position": "worn",
            "definition_key": "srd-5.2.1:equipment.chain_mail",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.chain_mail",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "dice_set",
            "name": "Dice Set",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:tool.gaming_set.dice",
            "provenance_definition_keys": [
              "srd-5.2.1:tool.gaming_set.dice",
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-equipment",
              "srd-soldier"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "dungeoneers_pack",
            "name": "Dungeoneer's Pack",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "flail",
            "name": "Flail",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.flail.state",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.flail.state",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "gp",
            "name": "GP",
            "quantity": 18,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment",
              "srd-fighter"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "greatsword",
            "name": "Greatsword",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.greatsword.state",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.greatsword.state",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "healers_kit",
            "name": "Healer's Kit",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "javelin",
            "name": "Javelin",
            "quantity": 8,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.javelin.state",
            "provenance_definition_keys": [
              "srd-5.2.1:equipment.javelin.state",
              "srd-5.2.1:equipment_package.fighter.a"
            ],
            "source_ids": [
              "srd-equipment-state",
              "srd-fighter",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "quiver",
            "name": "Quiver",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "shortbow",
            "name": "Shortbow",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "spear",
            "name": "Spear",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          },
          {
            "item_id": "travelers_clothes",
            "name": "Traveler's Clothes",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
            "provenance_definition_keys": [
              "srd-5.2.1:equipment_package.soldier.a"
            ],
            "source_ids": [
              "srd-soldier",
              "srd-equipment"
            ],
            "acquisition_event_ids": [
              "fe2b2c1e-9757-4f32-a650-db1ba5211619"
            ]
          }
        ],
        "resources": {
          "second_wind": {
            "current": 2,
            "maximum": 2,
            "die": "d10",
            "short_rest_recovery": "one",
            "long_rest_recovery": "all",
            "provenance": {
              "formula": "current resource bounded by its source-defined maximum",
              "definition_keys": [
                "srd-5.2.1:resource.fighter.second_wind",
                "srd-5.2.1:class_feature.fighter.second_wind",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-fighter-state",
                "srd-fighter",
                "srd-character-creation",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            }
          },
          "heroic_inspiration": {
            "current": 1,
            "maximum": 1,
            "die": null,
            "short_rest_recovery": "none",
            "long_rest_recovery": "none",
            "provenance": {
              "formula": "current resource bounded by its source-defined maximum",
              "definition_keys": [
                "srd-5.2.1:resource.human.heroic_inspiration",
                "srd-5.2.1:species_feature.human.resourceful",
                "srd-5.2.1:species.human"
              ],
              "source_ids": [
                "srd-d20",
                "srd-human-state",
                "srd-human",
                "srd-character-creation"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            }
          },
          "hit_dice": {
            "current": 1,
            "maximum": 1,
            "die": "d10",
            "short_rest_recovery": "none",
            "long_rest_recovery": "all",
            "provenance": {
              "formula": "current resource bounded by its source-defined maximum",
              "definition_keys": [
                "srd-5.2.1:resource.fighter.hit_dice",
                "srd-5.2.1:class.fighter"
              ],
              "source_ids": [
                "srd-character-details",
                "srd-fighter-state",
                "srd-fighter",
                "srd-character-creation",
                "srd-core-d20"
              ],
              "acquisition_event_ids": [
                "fe2b2c1e-9757-4f32-a650-db1ba5211619"
              ],
              "character_revision": 1,
              "state_revision": 1,
              "resolver_version": "character-state-1.0.0"
            }
          }
        }
      }
    }
  ],
  "party_ready": true,
  "location": {
    "id": "4a872d66-ad82-4c09-ba17-9385e552c5da",
    "name": "Roadside Inn",
    "description": "The campaign's starting point."
  },
  "turn_count": 1
}
Response headers
 content-length: 50322 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:57:35 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action2.
Curl
curl -X 'POST' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/turns' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "action": "SugarHigh scouts ahead."
}'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/turns
Server response
Code	409
Undocumented
Error: Conflict
Response body
{
  "detail": "Party Commander turns require actor_character_id"
}
Response headers
 content-length: 61 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:59:44 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action3.
Curl
curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/events' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/events
Server response
Code	200	
Response body
[
  {
    "id": "b90c2db5-16c9-45df-98dc-aba7bea7e946",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 1,
    "event_type": "campaign_created",
    "visibility": "player",
    "payload": {
      "name": "hello world",
      "play_mode": "party_commander",
      "party_size": {
        "maximum": 4,
        "minimum": 2
      },
      "starting_location": "Roadside Inn",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-08-31T22:37:43.654285+12:00"
  },
  {
    "id": "5f517f72-d45f-472f-bf49-165c41477f86",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 2,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "SugarHigh",
      "character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "control_mode": "player",
      "party_position": 1,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-08-31T22:43:50.755672+12:00"
  },
  {
    "id": "f8d8d544-6639-4f3c-a873-585136d27ff0",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 3,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "LooneyHigh",
      "character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "control_mode": "player",
      "party_position": 2,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-08-31T22:45:46.061860+12:00"
  },
  {
    "id": "7da975fb-7ea4-4ee0-8a09-963294af2d7e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 4,
    "event_type": "character_finalized",
    "visibility": "player",
    "payload": {
      "sheet": {
        "size": "medium",
        "level": 1,
        "max_hp": 12,
        "abilities": {
          "wisdom": {
            "base": 10,
            "final": 10,
            "modifier": 0,
            "background_increase": 0
          },
          "charisma": {
            "base": 12,
            "final": 12,
            "modifier": 1,
            "background_increase": 0
          },
          "strength": {
            "base": 15,
            "final": 17,
            "modifier": 3,
            "background_increase": 2
          },
          "dexterity": {
            "base": 14,
            "final": 14,
            "modifier": 2,
            "background_increase": 0
          },
          "constitution": {
            "base": 13,
            "final": 14,
            "modifier": 2,
            "background_increase": 1
          },
          "intelligence": {
            "base": 8,
            "final": 8,
            "modifier": -1,
            "background_increase": 0
          }
        },
        "alignment": "NG",
        "languages": [
          "common",
          "dwarvish",
          "elvish"
        ],
        "armor_training": [
          "light",
          "medium",
          "heavy",
          "shields"
        ],
        "resolver_version": "character-creation-1.0.0",
        "proficiency_bonus": 2,
        "equipment_route_id": "soldier-a+fighter-a",
        "ruleset_release_id": "srd-5.2.1",
        "starting_inventory": {
          "GP": 18,
          "Arrow": 20,
          "Flail": 1,
          "Spear": 1,
          "Quiver": 1,
          "Javelin": 8,
          "Dice Set": 1,
          "Shortbow": 1,
          "Chain Mail": 1,
          "Greatsword": 1,
          "Healer's Kit": 1,
          "Dungeoneer's Pack": 1,
          "Traveler's Clothes": 1
        },
        "skill_proficiencies": [
          "athletics",
          "insight",
          "intimidation",
          "perception",
          "survival"
        ],
        "class_definition_key": "srd-5.2.1:class.fighter",
        "second_wind_uses_max": 2,
        "weapon_proficiencies": [
          "simple",
          "martial"
        ],
        "gaming_set_proficiency": "dice",
        "species_definition_key": "srd-5.2.1:species.human",
        "feature_definition_keys": [
          "srd-5.2.1:species_feature.human.resourceful",
          "srd-5.2.1:species_feature.human.skillful",
          "srd-5.2.1:species_feature.human.versatile",
          "srd-5.2.1:class_feature.fighter.fighting_style",
          "srd-5.2.1:class_feature.fighter.second_wind",
          "srd-5.2.1:class_feature.fighter.weapon_mastery"
        ],
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "saving_throw_proficiencies": [
          "strength",
          "constitution"
        ],
        "origin_feat_definition_keys": [
          "srd-5.2.1:feat.origin.savage_attacker",
          "srd-5.2.1:feat.origin.alert"
        ],
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
          "srd-5.2.1:weapon.javelin",
          "srd-5.2.1:weapon.flail",
          "srd-5.2.1:weapon.greatsword"
        ]
      },
      "choices": {
        "size": "medium",
        "alignment": "NG",
        "languages": [
          "dwarvish",
          "elvish"
        ],
        "gaming_set": "dice",
        "human_skill": "insight",
        "fighter_skills": [
          "perception",
          "survival"
        ],
        "equipment_route_id": "soldier-a+fighter-a",
        "base_ability_scores": {
          "wisdom": 10,
          "charisma": 12,
          "strength": 15,
          "dexterity": 14,
          "constitution": 13,
          "intelligence": 8
        },
        "skilled_feat_skills": [],
        "class_definition_key": "srd-5.2.1:class.fighter",
        "species_definition_key": "srd-5.2.1:species.human",
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "origin_feat_definition_key": "srd-5.2.1:feat.origin.alert",
        "background_ability_increases": {
          "strength": 2,
          "constitution": 1
        },
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
          "srd-5.2.1:weapon.javelin",
          "srd-5.2.1:weapon.flail",
          "srd-5.2.1:weapon.greatsword"
        ]
      },
      "loadout": {
        "held_item_ids": [],
        "worn_armor_item_id": "chain_mail"
      },
      "revision": 1,
      "resources": {
        "hit_dice": 1,
        "second_wind": 2,
        "heroic_inspiration": 1
      },
      "character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "party_position": 1
    },
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "created_at": "2026-08-31T22:55:23.229963+12:00"
  },
  {
    "id": "fe2b2c1e-9757-4f32-a650-db1ba5211619",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 5,
    "event_type": "character_finalized",
    "visibility": "player",
    "payload": {
      "sheet": {
        "size": "medium",
        "level": 1,
        "max_hp": 12,
        "abilities": {
          "wisdom": {
            "base": 10,
            "final": 10,
            "modifier": 0,
            "background_increase": 0
          },
          "charisma": {
            "base": 12,
            "final": 12,
            "modifier": 1,
            "background_increase": 0
          },
          "strength": {
            "base": 15,
            "final": 17,
            "modifier": 3,
            "background_increase": 2
          },
          "dexterity": {
            "base": 14,
            "final": 14,
            "modifier": 2,
            "background_increase": 0
          },
          "constitution": {
            "base": 13,
            "final": 14,
            "modifier": 2,
            "background_increase": 1
          },
          "intelligence": {
            "base": 8,
            "final": 8,
            "modifier": -1,
            "background_increase": 0
          }
        },
        "alignment": "NG",
        "languages": [
          "common",
          "dwarvish",
          "elvish"
        ],
        "armor_training": [
          "light",
          "medium",
          "heavy",
          "shields"
        ],
        "resolver_version": "character-creation-1.0.0",
        "proficiency_bonus": 2,
        "equipment_route_id": "soldier-a+fighter-a",
        "ruleset_release_id": "srd-5.2.1",
        "starting_inventory": {
          "GP": 18,
          "Arrow": 20,
          "Flail": 1,
          "Spear": 1,
          "Quiver": 1,
          "Javelin": 8,
          "Dice Set": 1,
          "Shortbow": 1,
          "Chain Mail": 1,
          "Greatsword": 1,
          "Healer's Kit": 1,
          "Dungeoneer's Pack": 1,
          "Traveler's Clothes": 1
        },
        "skill_proficiencies": [
          "athletics",
          "insight",
          "intimidation",
          "perception",
          "survival"
        ],
        "class_definition_key": "srd-5.2.1:class.fighter",
        "second_wind_uses_max": 2,
        "weapon_proficiencies": [
          "simple",
          "martial"
        ],
        "gaming_set_proficiency": "dice",
        "species_definition_key": "srd-5.2.1:species.human",
        "feature_definition_keys": [
          "srd-5.2.1:species_feature.human.resourceful",
          "srd-5.2.1:species_feature.human.skillful",
          "srd-5.2.1:species_feature.human.versatile",
          "srd-5.2.1:class_feature.fighter.fighting_style",
          "srd-5.2.1:class_feature.fighter.second_wind",
          "srd-5.2.1:class_feature.fighter.weapon_mastery"
        ],
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "saving_throw_proficiencies": [
          "strength",
          "constitution"
        ],
        "origin_feat_definition_keys": [
          "srd-5.2.1:feat.origin.savage_attacker",
          "srd-5.2.1:feat.origin.alert"
        ],
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
          "srd-5.2.1:weapon.javelin",
          "srd-5.2.1:weapon.flail",
          "srd-5.2.1:weapon.greatsword"
        ]
      },
      "choices": {
        "size": "medium",
        "alignment": "NG",
        "languages": [
          "dwarvish",
          "elvish"
        ],
        "gaming_set": "dice",
        "human_skill": "insight",
        "fighter_skills": [
          "perception",
          "survival"
        ],
        "equipment_route_id": "soldier-a+fighter-a",
        "base_ability_scores": {
          "wisdom": 10,
          "charisma": 12,
          "strength": 15,
          "dexterity": 14,
          "constitution": 13,
          "intelligence": 8
        },
        "skilled_feat_skills": [],
        "class_definition_key": "srd-5.2.1:class.fighter",
        "species_definition_key": "srd-5.2.1:species.human",
        "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
        "background_definition_key": "srd-5.2.1:background.soldier",
        "origin_feat_definition_key": "srd-5.2.1:feat.origin.alert",
        "background_ability_increases": {
          "strength": 2,
          "constitution": 1
        },
        "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
        "fighting_style_definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "weapon_mastery_definition_keys": [
          "srd-5.2.1:weapon.javelin",
          "srd-5.2.1:weapon.flail",
          "srd-5.2.1:weapon.greatsword"
        ]
      },
      "loadout": {
        "held_item_ids": [],
        "worn_armor_item_id": "chain_mail"
      },
      "revision": 1,
      "resources": {
        "hit_dice": 1,
        "second_wind": 2,
        "heroic_inspiration": 1
      },
      "character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "party_position": 2
    },
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "created_at": "2026-08-31T23:02:55.624350+12:00"
  },
  {
    "id": "2018a577-ed4c-4e8a-8137-7ab4363458cc",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 6,
    "event_type": "character_loadout_changed",
    "visibility": "player",
    "payload": {
      "loadout": {
        "held_item_ids": [
          "greatsword"
        ],
        "worn_armor_item_id": null
      },
      "character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "state_revision": 2
    },
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "created_at": "2026-08-31T23:09:53.257653+12:00"
  },
  {
    "id": "118a4649-5fdb-43a6-ae70-48a9cef69ca3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 7,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin carefully searches the room for anything unusual.",
      "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1"
    },
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "created_at": "2026-08-31T23:16:23.426236+12:00"
  },
  {
    "id": "b0097efb-0752-4d09-a295-617d870e3fe9",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 8,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "narration": "At Roadside Inn, the world responds to your choice: Arin carefully searches the room for anything unusual. The next moment is yours to shape."
    },
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "created_at": "2026-08-31T23:16:23.426236+12:00"
  }
]
Response headers
 content-length: 9958 
 content-type: application/json 
 date: Mon,31 Aug 2026 12:00:41 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 