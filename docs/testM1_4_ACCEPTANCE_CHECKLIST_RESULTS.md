# M1.4 Deterministic Resolution Acceptance Results

- **Owner run:** 2026-09-01
- **Analysed and accepted:** 2026-09-02
- **Outcome:** All nine actions passed; no defect or targeted retest required
- **Restart evidence:** The owner confirmed the API was restarted immediately before action 8

The raw responses below verify canonical modifiers and provenance, idempotency and command conflict,
modifier rejection, automatic Chain Mail Dexterity (Stealth) Disadvantage, Advantage cancellation,
contextual Strength (Stealth), resolution listing/reading, actor-attributed events, post-restart
equivalent replay, and independent actor attribution.

Both characters used for action 9 share the same relevant Strength/save build, so their equal `+5`
modifiers are correct. Their actor IDs, acquisition-event IDs, and state revisions are distinct. The
automated M1.4 fixture with contrasting ability arrays supplies the complementary unequal-modifier
isolation proof.

## Raw actions and results

Action1.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "command_id": "86316713-3663-45de-a955-580b7becfc59",
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "resolution_type": "saving_throw",
    "ability": "strength",
    "skill": null,
    "difficulty_class": 13,
    "advantage_reasons": [],
    "disadvantage_reasons": []
  }'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code	201
  Response body
  {
    "id": "4f65fe28-63cb-4f89-8cdc-e0c47d8f3ada",
    "command_id": "86316713-3663-45de-a955-580b7becfc59",
    "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "dice_roll_id": "7a134fe4-8f58-47d2-8fb9-dbec1a9be08a",
    "character_revision": 1,
    "state_revision": 2,
    "resolution_type": "saving_throw",
    "ability": "strength",
    "skill": null,
    "difficulty_class": 13,
    "rule_definition_keys": [
      "srd-5.2.1:rule.d20_test",
      "srd-5.2.1:rule.saving_throw",
      "srd-5.2.1:rule.difficulty_class"
    ],
    "source_ids": [
      "srd-check-save-resolution"
    ],
    "command": {
      "command_id": "86316713-3663-45de-a955-580b7becfc59",
      "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "saving_throw",
      "ability": "strength",
      "skill": null,
      "difficulty_class": 13,
      "advantage_reasons": [],
      "disadvantage_reasons": []
    },
    "modifier_formula": "ability modifier + Proficiency Bonus when save-proficient",
    "modifier_components": [
      {
        "kind": "ability",
        "label": "Strength modifier",
        "value": 3,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "floor((ability score - 10) / 2)",
          "definition_keys": [
            "srd-5.2.1:rule.ability_modifier",
            "srd-5.2.1:ability.strength",
            "srd-5.2.1:ability_method.standard_array",
            "srd-5.2.1:background.soldier"
          ],
          "source_ids": [
            "srd-character-details",
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
      {
        "kind": "proficiency",
        "label": "Strength saving throw proficiency",
        "value": 2,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "Proficiency Bonus applies once when proficient in the selected saving throw",
          "definition_keys": [
            "srd-5.2.1:rule.proficiency_bonus",
            "srd-5.2.1:class.fighter",
            "srd-5.2.1:rule.saving_throw_modifier",
            "srd-5.2.1:ability.strength"
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
      }
    ],
    "advantage_sources": [],
    "disadvantage_sources": [],
    "advantage_state": "normal",
    "dice_notation": "1d20",
    "dice_faces": [
      11
    ],
    "selected_die": 11,
    "modifier": 5,
    "total": 16,
    "outcome": "success",
    "resolver_version": "check-save-resolution-1.0.0",
    "rng_version": "system-random-1.0.0",
    "created_at": "2026-09-01T22:07:19.507785+12:00"
  }
  Response headers
  content-length: 2717
  content-type: application/json
  date: Tue,01 Sep 2026 10:07:19 GMT
  server: uvicorn

Action2.1.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "command_id": "86316713-3663-45de-a955-580b7becfc59",
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "resolution_type": "saving_throw",
    "ability": "strength",
    "skill": null,
    "difficulty_class": 13,
    "advantage_reasons": [],
    "disadvantage_reasons": []
  }'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code	201
  Response body
  {
    "id": "4f65fe28-63cb-4f89-8cdc-e0c47d8f3ada",
    "command_id": "86316713-3663-45de-a955-580b7becfc59",
    "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "dice_roll_id": "7a134fe4-8f58-47d2-8fb9-dbec1a9be08a",
    "character_revision": 1,
    "state_revision": 2,
    "resolution_type": "saving_throw",
    "ability": "strength",
    "skill": null,
    "difficulty_class": 13,
    "rule_definition_keys": [
      "srd-5.2.1:rule.d20_test",
      "srd-5.2.1:rule.saving_throw",
      "srd-5.2.1:rule.difficulty_class"
    ],
    "source_ids": [
      "srd-check-save-resolution"
    ],
    "command": {
      "command_id": "86316713-3663-45de-a955-580b7becfc59",
      "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "saving_throw",
      "ability": "strength",
      "skill": null,
      "difficulty_class": 13,
      "advantage_reasons": [],
      "disadvantage_reasons": []
    },
    "modifier_formula": "ability modifier + Proficiency Bonus when save-proficient",
    "modifier_components": [
      {
        "kind": "ability",
        "label": "Strength modifier",
        "value": 3,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "floor((ability score - 10) / 2)",
          "definition_keys": [
            "srd-5.2.1:rule.ability_modifier",
            "srd-5.2.1:ability.strength",
            "srd-5.2.1:ability_method.standard_array",
            "srd-5.2.1:background.soldier"
          ],
          "source_ids": [
            "srd-character-details",
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
      {
        "kind": "proficiency",
        "label": "Strength saving throw proficiency",
        "value": 2,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "Proficiency Bonus applies once when proficient in the selected saving throw",
          "definition_keys": [
            "srd-5.2.1:rule.proficiency_bonus",
            "srd-5.2.1:class.fighter",
            "srd-5.2.1:rule.saving_throw_modifier",
            "srd-5.2.1:ability.strength"
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
      }
    ],
    "advantage_sources": [],
    "disadvantage_sources": [],
    "advantage_state": "normal",
    "dice_notation": "1d20",
    "dice_faces": [
      11
    ],
    "selected_die": 11,
    "modifier": 5,
    "total": 16,
    "outcome": "success",
    "resolver_version": "check-save-resolution-1.0.0",
    "rng_version": "system-random-1.0.0",
    "created_at": "2026-09-01T22:07:19.507785+12:00"
  }
  Response headers
  content-length: 2717
  content-type: application/json
  date: Tue,01 Sep 2026 10:12:33 GMT
  server: uvicorn

Action2.2.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "command_id": "86316713-3663-45de-a955-580b7becfc59",
    "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "resolution_type": "saving_throw",
    "ability": "strength",
    "skill": null,
    "difficulty_class": 14,
    "advantage_reasons": [],
    "disadvantage_reasons": []
  }'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code	Details
  409
  Undocumented
  Error: Conflict
  Response body
  {
    "detail": "command_id was already used for a different resolution command"
  }
  Response headers
  content-length: 75
  content-type: application/json
  date: Tue,01 Sep 2026 10:15:28 GMT
  server: uvicorn

Action3.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "command_id": "9e5fa19b-160a-466b-b9bc-e8129bd2b618",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "resolution_type": "saving_throw",
    "ability": "strength",
    "skill": null,
    "difficulty_class": 14,
    "advantage_reasons": [],
    "disadvantage_reasons": [],
    "modifier": 99
  }'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code	Details
  422
  Error: Unprocessable Entity
  Response body
  {
    "detail": [
      {
        "type": "extra_forbidden",
        "loc": [
          "body",
          "modifier"
        ],
        "msg": "Extra inputs are not permitted",
        "input": 99
      }
    ]
  }
  Response headers
  content-length: 115
  content-type: application/json
  date: Tue,01 Sep 2026 10:18:54 GMT
  server: uvicorn

Action4.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "resolution_type": "ability_check",
    "ability": "dexterity",
    "skill": "stealth",
    "difficulty_class": 13,
    "advantage_reasons": [],
    "disadvantage_reasons": []
  }'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code  201
  Response body
  {
    "id": "71eb03a0-3af0-472f-b7cf-02fc7cf3472f",
    "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
    "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "dice_roll_id": "14c53724-65f5-4fc8-b3be-b51013dc0369",
    "character_revision": 1,
    "state_revision": 1,
    "resolution_type": "ability_check",
    "ability": "dexterity",
    "skill": "stealth",
    "difficulty_class": 13,
    "rule_definition_keys": [
      "srd-5.2.1:rule.d20_test",
      "srd-5.2.1:rule.ability_check",
      "srd-5.2.1:rule.difficulty_class",
      "srd-5.2.1:rule.disadvantage"
    ],
    "source_ids": [
      "srd-check-save-resolution"
    ],
    "command": {
      "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "ability_check",
      "ability": "dexterity",
      "skill": "stealth",
      "difficulty_class": 13,
      "advantage_reasons": [],
      "disadvantage_reasons": []
    },
    "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
    "modifier_components": [
      {
        "kind": "ability",
        "label": "Dexterity modifier",
        "value": 2,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "floor((ability score - 10) / 2)",
          "definition_keys": [
            "srd-5.2.1:rule.ability_modifier",
            "srd-5.2.1:ability.dexterity",
            "srd-5.2.1:ability_method.standard_array"
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
        "kind": "proficiency",
        "label": "Stealth proficiency",
        "value": 0,
        "applied": false,
        "multiplier": 0,
        "provenance": {
          "formula": "Proficiency Bonus applies once when proficient in the selected skill",
          "definition_keys": [
            "srd-5.2.1:rule.skill_modifier",
            "srd-5.2.1:skill.stealth",
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
      }
    ],
    "advantage_sources": [],
    "disadvantage_sources": [
      {
        "definition_key": "srd-5.2.1:equipment.chain_mail",
        "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
        "source_ids": [
          "srd-equipment-state"
        ],
        "automatic": true
      }
    ],
    "advantage_state": "disadvantage",
    "dice_notation": "2d20",
    "dice_faces": [
      17,
      8
    ],
    "selected_die": 8,
    "modifier": 2,
    "total": 10,
    "outcome": "failure",
    "resolver_version": "check-save-resolution-1.0.0",
    "rng_version": "system-random-1.0.0",
    "created_at": "2026-09-01T22:28:11.737959+12:00"
  }
  Response headers
  content-length: 2832
  content-type: application/json
  date: Tue,01 Sep 2026 10:28:10 GMT
  server: uvicorn

Action5.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "command_id": "4a88bb4a-4502-4d7a-bd62-10273168876f",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "resolution_type": "ability_check",
    "ability": "dexterity",
    "skill": "stealth",
    "difficulty_class": 13,
    "advantage_reasons": ["ally_help"],
    "disadvantage_reasons": []
  }'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code  201
  Response body
  {
    "id": "86ac3310-0f24-42c1-9c42-ad3dfe75c9d6",
    "command_id": "4a88bb4a-4502-4d7a-bd62-10273168876f",
    "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "dice_roll_id": "56dca024-dda5-4b0b-9f11-efd19a2ca1e8",
    "character_revision": 1,
    "state_revision": 1,
    "resolution_type": "ability_check",
    "ability": "dexterity",
    "skill": "stealth",
    "difficulty_class": 13,
    "rule_definition_keys": [
      "srd-5.2.1:rule.d20_test",
      "srd-5.2.1:rule.ability_check",
      "srd-5.2.1:rule.difficulty_class",
      "srd-5.2.1:rule.advantage",
      "srd-5.2.1:rule.disadvantage"
    ],
    "source_ids": [
      "srd-check-save-resolution"
    ],
    "command": {
      "command_id": "4a88bb4a-4502-4d7a-bd62-10273168876f",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "ability_check",
      "ability": "dexterity",
      "skill": "stealth",
      "difficulty_class": 13,
      "advantage_reasons": [
        "ally_help"
      ],
      "disadvantage_reasons": []
    },
    "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
    "modifier_components": [
      {
        "kind": "ability",
        "label": "Dexterity modifier",
        "value": 2,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "floor((ability score - 10) / 2)",
          "definition_keys": [
            "srd-5.2.1:rule.ability_modifier",
            "srd-5.2.1:ability.dexterity",
            "srd-5.2.1:ability_method.standard_array"
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
        "kind": "proficiency",
        "label": "Stealth proficiency",
        "value": 0,
        "applied": false,
        "multiplier": 0,
        "provenance": {
          "formula": "Proficiency Bonus applies once when proficient in the selected skill",
          "definition_keys": [
            "srd-5.2.1:rule.skill_modifier",
            "srd-5.2.1:skill.stealth",
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
      }
    ],
    "advantage_sources": [
      {
        "definition_key": "srd-5.2.1:rule.advantage",
        "reason": "ally_help",
        "source_ids": [
          "srd-check-save-resolution"
        ],
        "automatic": false
      }
    ],
    "disadvantage_sources": [
      {
        "definition_key": "srd-5.2.1:equipment.chain_mail",
        "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
        "source_ids": [
          "srd-equipment-state"
        ],
        "automatic": true
      }
    ],
    "advantage_state": "normal",
    "dice_notation": "1d20",
    "dice_faces": [
      6
    ],
    "selected_die": 6,
    "modifier": 2,
    "total": 8,
    "outcome": "failure",
    "resolver_version": "check-save-resolution-1.0.0",
    "rng_version": "system-random-1.0.0",
    "created_at": "2026-09-01T22:33:49.986025+12:00"
  }
  Response headers
  content-length: 2987
  content-type: application/json
  date: Tue,01 Sep 2026 10:33:48 GMT
  server: uvicorn

Action6.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "command_id": "a11287d8-d78a-449c-a25c-1d6fa0adfd77",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "resolution_type": "ability_check",
    "ability": "strength",
    "skill": "stealth",
    "difficulty_class": 13,
    "advantage_reasons": [],
    "disadvantage_reasons": []
  }'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code  201
  Response body
  {
    "id": "7c0752ce-7856-4f12-b68b-0c9550f68d12",
    "command_id": "a11287d8-d78a-449c-a25c-1d6fa0adfd77",
    "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "dice_roll_id": "27d69dd0-0089-4561-9955-c0024dea6d5c",
    "character_revision": 1,
    "state_revision": 1,
    "resolution_type": "ability_check",
    "ability": "strength",
    "skill": "stealth",
    "difficulty_class": 13,
    "rule_definition_keys": [
      "srd-5.2.1:rule.d20_test",
      "srd-5.2.1:rule.ability_check",
      "srd-5.2.1:rule.difficulty_class"
    ],
    "source_ids": [
      "srd-check-save-resolution"
    ],
    "command": {
      "command_id": "a11287d8-d78a-449c-a25c-1d6fa0adfd77",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "ability_check",
      "ability": "strength",
      "skill": "stealth",
      "difficulty_class": 13,
      "advantage_reasons": [],
      "disadvantage_reasons": []
    },
    "modifier_formula": "Strength modifier + Proficiency Bonus when proficient in Stealth",
    "modifier_components": [
      {
        "kind": "ability",
        "label": "Strength modifier",
        "value": 3,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "floor((ability score - 10) / 2)",
          "definition_keys": [
            "srd-5.2.1:rule.ability_modifier",
            "srd-5.2.1:ability.strength",
            "srd-5.2.1:ability_method.standard_array",
            "srd-5.2.1:background.soldier"
          ],
          "source_ids": [
            "srd-character-details",
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
      {
        "kind": "proficiency",
        "label": "Stealth proficiency",
        "value": 0,
        "applied": false,
        "multiplier": 0,
        "provenance": {
          "formula": "Proficiency Bonus applies once when proficient in the selected skill",
          "definition_keys": [
            "srd-5.2.1:rule.skill_modifier",
            "srd-5.2.1:skill.stealth",
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
      }
    ],
    "advantage_sources": [],
    "disadvantage_sources": [],
    "advantage_state": "normal",
    "dice_notation": "1d20",
    "dice_faces": [
      20
    ],
    "selected_die": 20,
    "modifier": 3,
    "total": 23,
    "outcome": "success",
    "resolver_version": "check-save-resolution-1.0.0",
    "rng_version": "system-random-1.0.0",
    "created_at": "2026-09-01T23:25:31.573183+12:00"
  }
  Response headers
  content-length: 2707
  content-type: application/json
  date: Tue,01 Sep 2026 11:25:31 GMT
  server: uvicorn

Action7.1.
  Curl
  curl -X 'GET' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
    -H 'accept: application/json'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
  Server response
  Code	200
  Response body
  [
    {
      "id": "4f65fe28-63cb-4f89-8cdc-e0c47d8f3ada",
      "command_id": "86316713-3663-45de-a955-580b7becfc59",
      "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
      "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "dice_roll_id": "7a134fe4-8f58-47d2-8fb9-dbec1a9be08a",
      "character_revision": 1,
      "state_revision": 2,
      "resolution_type": "saving_throw",
      "ability": "strength",
      "skill": null,
      "difficulty_class": 13,
      "rule_definition_keys": [
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.saving_throw",
        "srd-5.2.1:rule.difficulty_class"
      ],
      "source_ids": [
        "srd-check-save-resolution"
      ],
      "command": {
        "command_id": "86316713-3663-45de-a955-580b7becfc59",
        "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": "saving_throw",
        "ability": "strength",
        "skill": null,
        "difficulty_class": 13,
        "advantage_reasons": [],
        "disadvantage_reasons": []
      },
      "modifier_formula": "ability modifier + Proficiency Bonus when save-proficient",
      "modifier_components": [
        {
          "kind": "ability",
          "label": "Strength modifier",
          "value": 3,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "floor((ability score - 10) / 2)",
            "definition_keys": [
              "srd-5.2.1:rule.ability_modifier",
              "srd-5.2.1:ability.strength",
              "srd-5.2.1:ability_method.standard_array",
              "srd-5.2.1:background.soldier"
            ],
            "source_ids": [
              "srd-character-details",
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
        {
          "kind": "proficiency",
          "label": "Strength saving throw proficiency",
          "value": 2,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "Proficiency Bonus applies once when proficient in the selected saving throw",
            "definition_keys": [
              "srd-5.2.1:rule.proficiency_bonus",
              "srd-5.2.1:class.fighter",
              "srd-5.2.1:rule.saving_throw_modifier",
              "srd-5.2.1:ability.strength"
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
        }
      ],
      "advantage_sources": [],
      "disadvantage_sources": [],
      "advantage_state": "normal",
      "dice_notation": "1d20",
      "dice_faces": [
        11
      ],
      "selected_die": 11,
      "modifier": 5,
      "total": 16,
      "outcome": "success",
      "resolver_version": "check-save-resolution-1.0.0",
      "rng_version": "system-random-1.0.0",
      "created_at": "2026-09-01T22:07:19.507785+12:00"
    },
    {
      "id": "71eb03a0-3af0-472f-b7cf-02fc7cf3472f",
      "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
      "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "dice_roll_id": "14c53724-65f5-4fc8-b3be-b51013dc0369",
      "character_revision": 1,
      "state_revision": 1,
      "resolution_type": "ability_check",
      "ability": "dexterity",
      "skill": "stealth",
      "difficulty_class": 13,
      "rule_definition_keys": [
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.ability_check",
        "srd-5.2.1:rule.difficulty_class",
        "srd-5.2.1:rule.disadvantage"
      ],
      "source_ids": [
        "srd-check-save-resolution"
      ],
      "command": {
        "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": "ability_check",
        "ability": "dexterity",
        "skill": "stealth",
        "difficulty_class": 13,
        "advantage_reasons": [],
        "disadvantage_reasons": []
      },
      "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
      "modifier_components": [
        {
          "kind": "ability",
          "label": "Dexterity modifier",
          "value": 2,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "floor((ability score - 10) / 2)",
            "definition_keys": [
              "srd-5.2.1:rule.ability_modifier",
              "srd-5.2.1:ability.dexterity",
              "srd-5.2.1:ability_method.standard_array"
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
          "kind": "proficiency",
          "label": "Stealth proficiency",
          "value": 0,
          "applied": false,
          "multiplier": 0,
          "provenance": {
            "formula": "Proficiency Bonus applies once when proficient in the selected skill",
            "definition_keys": [
              "srd-5.2.1:rule.skill_modifier",
              "srd-5.2.1:skill.stealth",
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
        }
      ],
      "advantage_sources": [],
      "disadvantage_sources": [
        {
          "definition_key": "srd-5.2.1:equipment.chain_mail",
          "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
          "source_ids": [
            "srd-equipment-state"
          ],
          "automatic": true
        }
      ],
      "advantage_state": "disadvantage",
      "dice_notation": "2d20",
      "dice_faces": [
        17,
        8
      ],
      "selected_die": 8,
      "modifier": 2,
      "total": 10,
      "outcome": "failure",
      "resolver_version": "check-save-resolution-1.0.0",
      "rng_version": "system-random-1.0.0",
      "created_at": "2026-09-01T22:28:11.737959+12:00"
    },
    {
      "id": "86ac3310-0f24-42c1-9c42-ad3dfe75c9d6",
      "command_id": "4a88bb4a-4502-4d7a-bd62-10273168876f",
      "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "dice_roll_id": "56dca024-dda5-4b0b-9f11-efd19a2ca1e8",
      "character_revision": 1,
      "state_revision": 1,
      "resolution_type": "ability_check",
      "ability": "dexterity",
      "skill": "stealth",
      "difficulty_class": 13,
      "rule_definition_keys": [
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.ability_check",
        "srd-5.2.1:rule.difficulty_class",
        "srd-5.2.1:rule.advantage",
        "srd-5.2.1:rule.disadvantage"
      ],
      "source_ids": [
        "srd-check-save-resolution"
      ],
      "command": {
        "command_id": "4a88bb4a-4502-4d7a-bd62-10273168876f",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": "ability_check",
        "ability": "dexterity",
        "skill": "stealth",
        "difficulty_class": 13,
        "advantage_reasons": [
          "ally_help"
        ],
        "disadvantage_reasons": []
      },
      "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
      "modifier_components": [
        {
          "kind": "ability",
          "label": "Dexterity modifier",
          "value": 2,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "floor((ability score - 10) / 2)",
            "definition_keys": [
              "srd-5.2.1:rule.ability_modifier",
              "srd-5.2.1:ability.dexterity",
              "srd-5.2.1:ability_method.standard_array"
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
          "kind": "proficiency",
          "label": "Stealth proficiency",
          "value": 0,
          "applied": false,
          "multiplier": 0,
          "provenance": {
            "formula": "Proficiency Bonus applies once when proficient in the selected skill",
            "definition_keys": [
              "srd-5.2.1:rule.skill_modifier",
              "srd-5.2.1:skill.stealth",
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
        }
      ],
      "advantage_sources": [
        {
          "definition_key": "srd-5.2.1:rule.advantage",
          "reason": "ally_help",
          "source_ids": [
            "srd-check-save-resolution"
          ],
          "automatic": false
        }
      ],
      "disadvantage_sources": [
        {
          "definition_key": "srd-5.2.1:equipment.chain_mail",
          "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
          "source_ids": [
            "srd-equipment-state"
          ],
          "automatic": true
        }
      ],
      "advantage_state": "normal",
      "dice_notation": "1d20",
      "dice_faces": [
        6
      ],
      "selected_die": 6,
      "modifier": 2,
      "total": 8,
      "outcome": "failure",
      "resolver_version": "check-save-resolution-1.0.0",
      "rng_version": "system-random-1.0.0",
      "created_at": "2026-09-01T22:33:49.986025+12:00"
    },
    {
      "id": "7c0752ce-7856-4f12-b68b-0c9550f68d12",
      "command_id": "a11287d8-d78a-449c-a25c-1d6fa0adfd77",
      "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "dice_roll_id": "27d69dd0-0089-4561-9955-c0024dea6d5c",
      "character_revision": 1,
      "state_revision": 1,
      "resolution_type": "ability_check",
      "ability": "strength",
      "skill": "stealth",
      "difficulty_class": 13,
      "rule_definition_keys": [
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.ability_check",
        "srd-5.2.1:rule.difficulty_class"
      ],
      "source_ids": [
        "srd-check-save-resolution"
      ],
      "command": {
        "command_id": "a11287d8-d78a-449c-a25c-1d6fa0adfd77",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": "ability_check",
        "ability": "strength",
        "skill": "stealth",
        "difficulty_class": 13,
        "advantage_reasons": [],
        "disadvantage_reasons": []
      },
      "modifier_formula": "Strength modifier + Proficiency Bonus when proficient in Stealth",
      "modifier_components": [
        {
          "kind": "ability",
          "label": "Strength modifier",
          "value": 3,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "floor((ability score - 10) / 2)",
            "definition_keys": [
              "srd-5.2.1:rule.ability_modifier",
              "srd-5.2.1:ability.strength",
              "srd-5.2.1:ability_method.standard_array",
              "srd-5.2.1:background.soldier"
            ],
            "source_ids": [
              "srd-character-details",
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
        {
          "kind": "proficiency",
          "label": "Stealth proficiency",
          "value": 0,
          "applied": false,
          "multiplier": 0,
          "provenance": {
            "formula": "Proficiency Bonus applies once when proficient in the selected skill",
            "definition_keys": [
              "srd-5.2.1:rule.skill_modifier",
              "srd-5.2.1:skill.stealth",
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
        }
      ],
      "advantage_sources": [],
      "disadvantage_sources": [],
      "advantage_state": "normal",
      "dice_notation": "1d20",
      "dice_faces": [
        20
      ],
      "selected_die": 20,
      "modifier": 3,
      "total": 23,
      "outcome": "success",
      "resolver_version": "check-save-resolution-1.0.0",
      "rng_version": "system-random-1.0.0",
      "created_at": "2026-09-01T23:25:31.573183+12:00"
    }
  ]
  Response headers
  content-length: 11248
  content-type: application/json
  date: Tue,01 Sep 2026 11:32:50 GMT
  server: uvicorn

Action7.2.
  Curl
  curl -X 'GET' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions/71eb03a0-3af0-472f-b7cf-02fc7cf3472f' \
    -H 'accept: application/json'
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions/71eb03a0-3af0-472f-b7cf-02fc7cf3472f
  Server response
  Code  200
  Response body
  {
    "id": "71eb03a0-3af0-472f-b7cf-02fc7cf3472f",
    "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
    "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
    "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
    "ruleset_release_id": "srd-5.2.1",
    "character_state_catalog_id": "srd-5.2.1-party-state-v1",
    "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
    "dice_roll_id": "14c53724-65f5-4fc8-b3be-b51013dc0369",
    "character_revision": 1,
    "state_revision": 1,
    "resolution_type": "ability_check",
    "ability": "dexterity",
    "skill": "stealth",
    "difficulty_class": 13,
    "rule_definition_keys": [
      "srd-5.2.1:rule.d20_test",
      "srd-5.2.1:rule.ability_check",
      "srd-5.2.1:rule.difficulty_class",
      "srd-5.2.1:rule.disadvantage"
    ],
    "source_ids": [
      "srd-check-save-resolution"
    ],
    "command": {
      "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "ability_check",
      "ability": "dexterity",
      "skill": "stealth",
      "difficulty_class": 13,
      "advantage_reasons": [],
      "disadvantage_reasons": []
    },
    "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
    "modifier_components": [
      {
        "kind": "ability",
        "label": "Dexterity modifier",
        "value": 2,
        "applied": true,
        "multiplier": 1,
        "provenance": {
          "formula": "floor((ability score - 10) / 2)",
          "definition_keys": [
            "srd-5.2.1:rule.ability_modifier",
            "srd-5.2.1:ability.dexterity",
            "srd-5.2.1:ability_method.standard_array"
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
        "kind": "proficiency",
        "label": "Stealth proficiency",
        "value": 0,
        "applied": false,
        "multiplier": 0,
        "provenance": {
          "formula": "Proficiency Bonus applies once when proficient in the selected skill",
          "definition_keys": [
            "srd-5.2.1:rule.skill_modifier",
            "srd-5.2.1:skill.stealth",
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
      }
    ],
    "advantage_sources": [],
    "disadvantage_sources": [
      {
        "definition_key": "srd-5.2.1:equipment.chain_mail",
        "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
        "source_ids": [
          "srd-equipment-state"
        ],
        "automatic": true
      }
    ],
    "advantage_state": "disadvantage",
    "dice_notation": "2d20",
    "dice_faces": [
      17,
      8
    ],
    "selected_die": 8,
    "modifier": 2,
    "total": 10,
    "outcome": "failure",
    "resolver_version": "check-save-resolution-1.0.0",
    "rng_version": "system-random-1.0.0",
    "created_at": "2026-09-01T22:28:11.737959+12:00"
  }
  Response headers
  content-length: 2832
  content-type: application/json
  date: Tue,01 Sep 2026 11:30:30 GMT
  server: uvicorn

Action7.3.
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
    },
    {
      "id": "27eae79c-73db-4965-952f-1975318ac3b8",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
      "sequence": 9,
      "event_type": "rule_resolved",
      "visibility": "player",
      "payload": {
        "command_id": "86316713-3663-45de-a955-580b7becfc59",
        "resolution": {
          "skill": null,
          "total": 16,
          "ability": "strength",
          "outcome": "success",
          "modifier": 5,
          "dice_faces": [
            11
          ],
          "source_ids": [
            "srd-check-save-resolution"
          ],
          "selected_die": 11,
          "dice_notation": "1d20",
          "state_revision": 2,
          "advantage_state": "normal",
          "resolution_type": "saving_throw",
          "difficulty_class": 13,
          "modifier_formula": "ability modifier + Proficiency Bonus when save-proficient",
          "resolver_version": "check-save-resolution-1.0.0",
          "advantage_sources": [],
          "character_revision": 1,
          "modifier_components": [
            {
              "kind": "ability",
              "label": "Strength modifier",
              "value": 3,
              "applied": true,
              "multiplier": 1,
              "provenance": {
                "formula": "floor((ability score - 10) / 2)",
                "source_ids": [
                  "srd-character-details",
                  "srd-character-creation",
                  "srd-soldier",
                  "srd-feats",
                  "srd-core-d20",
                  "srd-equipment"
                ],
                "state_revision": 2,
                "definition_keys": [
                  "srd-5.2.1:rule.ability_modifier",
                  "srd-5.2.1:ability.strength",
                  "srd-5.2.1:ability_method.standard_array",
                  "srd-5.2.1:background.soldier"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
                ]
              }
            },
            {
              "kind": "proficiency",
              "label": "Strength saving throw proficiency",
              "value": 2,
              "applied": true,
              "multiplier": 1,
              "provenance": {
                "formula": "Proficiency Bonus applies once when proficient in the selected saving throw",
                "source_ids": [
                  "srd-d20",
                  "srd-character-details",
                  "srd-fighter",
                  "srd-character-creation",
                  "srd-core-d20"
                ],
                "state_revision": 2,
                "definition_keys": [
                  "srd-5.2.1:rule.proficiency_bonus",
                  "srd-5.2.1:class.fighter",
                  "srd-5.2.1:rule.saving_throw_modifier",
                  "srd-5.2.1:ability.strength"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
                ]
              }
            }
          ],
          "disadvantage_sources": [],
          "rule_definition_keys": [
            "srd-5.2.1:rule.d20_test",
            "srd-5.2.1:rule.saving_throw",
            "srd-5.2.1:rule.difficulty_class"
          ]
        },
        "rng_version": "system-random-1.0.0",
        "dice_roll_id": "7a134fe4-8f58-47d2-8fb9-dbec1a9be08a",
        "resolution_id": "4f65fe28-63cb-4f89-8cdc-e0c47d8f3ada",
        "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1"
      },
      "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "created_at": "2026-09-01T22:07:19.507785+12:00"
    },
    {
      "id": "d4affd62-a854-4270-9cab-a1ace0e7b144",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
      "sequence": 10,
      "event_type": "rule_resolved",
      "visibility": "player",
      "payload": {
        "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
        "resolution": {
          "skill": "stealth",
          "total": 10,
          "ability": "dexterity",
          "outcome": "failure",
          "modifier": 2,
          "dice_faces": [
            17,
            8
          ],
          "source_ids": [
            "srd-check-save-resolution"
          ],
          "selected_die": 8,
          "dice_notation": "2d20",
          "state_revision": 1,
          "advantage_state": "disadvantage",
          "resolution_type": "ability_check",
          "difficulty_class": 13,
          "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
          "resolver_version": "check-save-resolution-1.0.0",
          "advantage_sources": [],
          "character_revision": 1,
          "modifier_components": [
            {
              "kind": "ability",
              "label": "Dexterity modifier",
              "value": 2,
              "applied": true,
              "multiplier": 1,
              "provenance": {
                "formula": "floor((ability score - 10) / 2)",
                "source_ids": [
                  "srd-character-details",
                  "srd-character-creation"
                ],
                "state_revision": 1,
                "definition_keys": [
                  "srd-5.2.1:rule.ability_modifier",
                  "srd-5.2.1:ability.dexterity",
                  "srd-5.2.1:ability_method.standard_array"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "fe2b2c1e-9757-4f32-a650-db1ba5211619"
                ]
              }
            },
            {
              "kind": "proficiency",
              "label": "Stealth proficiency",
              "value": 0,
              "applied": false,
              "multiplier": 0,
              "provenance": {
                "formula": "Proficiency Bonus applies once when proficient in the selected skill",
                "source_ids": [
                  "srd-d20",
                  "srd-character-details",
                  "srd-fighter",
                  "srd-character-creation",
                  "srd-core-d20"
                ],
                "state_revision": 1,
                "definition_keys": [
                  "srd-5.2.1:rule.skill_modifier",
                  "srd-5.2.1:skill.stealth",
                  "srd-5.2.1:rule.proficiency_bonus",
                  "srd-5.2.1:class.fighter"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "fe2b2c1e-9757-4f32-a650-db1ba5211619"
                ]
              }
            }
          ],
          "disadvantage_sources": [
            {
              "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
              "automatic": true,
              "source_ids": [
                "srd-equipment-state"
              ],
              "definition_key": "srd-5.2.1:equipment.chain_mail"
            }
          ],
          "rule_definition_keys": [
            "srd-5.2.1:rule.d20_test",
            "srd-5.2.1:rule.ability_check",
            "srd-5.2.1:rule.difficulty_class",
            "srd-5.2.1:rule.disadvantage"
          ]
        },
        "rng_version": "system-random-1.0.0",
        "dice_roll_id": "14c53724-65f5-4fc8-b3be-b51013dc0369",
        "resolution_id": "71eb03a0-3af0-472f-b7cf-02fc7cf3472f",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1"
      },
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "created_at": "2026-09-01T22:28:11.737959+12:00"
    },
    {
      "id": "74cebe61-5fe9-460d-9a3f-fe2f444d8d0b",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
      "sequence": 11,
      "event_type": "rule_resolved",
      "visibility": "player",
      "payload": {
        "command_id": "4a88bb4a-4502-4d7a-bd62-10273168876f",
        "resolution": {
          "skill": "stealth",
          "total": 8,
          "ability": "dexterity",
          "outcome": "failure",
          "modifier": 2,
          "dice_faces": [
            6
          ],
          "source_ids": [
            "srd-check-save-resolution"
          ],
          "selected_die": 6,
          "dice_notation": "1d20",
          "state_revision": 1,
          "advantage_state": "normal",
          "resolution_type": "ability_check",
          "difficulty_class": 13,
          "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
          "resolver_version": "check-save-resolution-1.0.0",
          "advantage_sources": [
            {
              "reason": "ally_help",
              "automatic": false,
              "source_ids": [
                "srd-check-save-resolution"
              ],
              "definition_key": "srd-5.2.1:rule.advantage"
            }
          ],
          "character_revision": 1,
          "modifier_components": [
            {
              "kind": "ability",
              "label": "Dexterity modifier",
              "value": 2,
              "applied": true,
              "multiplier": 1,
              "provenance": {
                "formula": "floor((ability score - 10) / 2)",
                "source_ids": [
                  "srd-character-details",
                  "srd-character-creation"
                ],
                "state_revision": 1,
                "definition_keys": [
                  "srd-5.2.1:rule.ability_modifier",
                  "srd-5.2.1:ability.dexterity",
                  "srd-5.2.1:ability_method.standard_array"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "fe2b2c1e-9757-4f32-a650-db1ba5211619"
                ]
              }
            },
            {
              "kind": "proficiency",
              "label": "Stealth proficiency",
              "value": 0,
              "applied": false,
              "multiplier": 0,
              "provenance": {
                "formula": "Proficiency Bonus applies once when proficient in the selected skill",
                "source_ids": [
                  "srd-d20",
                  "srd-character-details",
                  "srd-fighter",
                  "srd-character-creation",
                  "srd-core-d20"
                ],
                "state_revision": 1,
                "definition_keys": [
                  "srd-5.2.1:rule.skill_modifier",
                  "srd-5.2.1:skill.stealth",
                  "srd-5.2.1:rule.proficiency_bonus",
                  "srd-5.2.1:class.fighter"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "fe2b2c1e-9757-4f32-a650-db1ba5211619"
                ]
              }
            }
          ],
          "disadvantage_sources": [
            {
              "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
              "automatic": true,
              "source_ids": [
                "srd-equipment-state"
              ],
              "definition_key": "srd-5.2.1:equipment.chain_mail"
            }
          ],
          "rule_definition_keys": [
            "srd-5.2.1:rule.d20_test",
            "srd-5.2.1:rule.ability_check",
            "srd-5.2.1:rule.difficulty_class",
            "srd-5.2.1:rule.advantage",
            "srd-5.2.1:rule.disadvantage"
          ]
        },
        "rng_version": "system-random-1.0.0",
        "dice_roll_id": "56dca024-dda5-4b0b-9f11-efd19a2ca1e8",
        "resolution_id": "86ac3310-0f24-42c1-9c42-ad3dfe75c9d6",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1"
      },
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "created_at": "2026-09-01T22:33:49.986025+12:00"
    },
    {
      "id": "c203d771-de48-46e4-90cc-e411a12f4143",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
      "sequence": 12,
      "event_type": "rule_resolved",
      "visibility": "player",
      "payload": {
        "command_id": "a11287d8-d78a-449c-a25c-1d6fa0adfd77",
        "resolution": {
          "skill": "stealth",
          "total": 23,
          "ability": "strength",
          "outcome": "success",
          "modifier": 3,
          "dice_faces": [
            20
          ],
          "source_ids": [
            "srd-check-save-resolution"
          ],
          "selected_die": 20,
          "dice_notation": "1d20",
          "state_revision": 1,
          "advantage_state": "normal",
          "resolution_type": "ability_check",
          "difficulty_class": 13,
          "modifier_formula": "Strength modifier + Proficiency Bonus when proficient in Stealth",
          "resolver_version": "check-save-resolution-1.0.0",
          "advantage_sources": [],
          "character_revision": 1,
          "modifier_components": [
            {
              "kind": "ability",
              "label": "Strength modifier",
              "value": 3,
              "applied": true,
              "multiplier": 1,
              "provenance": {
                "formula": "floor((ability score - 10) / 2)",
                "source_ids": [
                  "srd-character-details",
                  "srd-character-creation",
                  "srd-soldier",
                  "srd-feats",
                  "srd-core-d20",
                  "srd-equipment"
                ],
                "state_revision": 1,
                "definition_keys": [
                  "srd-5.2.1:rule.ability_modifier",
                  "srd-5.2.1:ability.strength",
                  "srd-5.2.1:ability_method.standard_array",
                  "srd-5.2.1:background.soldier"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "fe2b2c1e-9757-4f32-a650-db1ba5211619"
                ]
              }
            },
            {
              "kind": "proficiency",
              "label": "Stealth proficiency",
              "value": 0,
              "applied": false,
              "multiplier": 0,
              "provenance": {
                "formula": "Proficiency Bonus applies once when proficient in the selected skill",
                "source_ids": [
                  "srd-d20",
                  "srd-character-details",
                  "srd-fighter",
                  "srd-character-creation",
                  "srd-core-d20"
                ],
                "state_revision": 1,
                "definition_keys": [
                  "srd-5.2.1:rule.skill_modifier",
                  "srd-5.2.1:skill.stealth",
                  "srd-5.2.1:rule.proficiency_bonus",
                  "srd-5.2.1:class.fighter"
                ],
                "resolver_version": "character-state-1.0.0",
                "character_revision": 1,
                "acquisition_event_ids": [
                  "fe2b2c1e-9757-4f32-a650-db1ba5211619"
                ]
              }
            }
          ],
          "disadvantage_sources": [],
          "rule_definition_keys": [
            "srd-5.2.1:rule.d20_test",
            "srd-5.2.1:rule.ability_check",
            "srd-5.2.1:rule.difficulty_class"
          ]
        },
        "rng_version": "system-random-1.0.0",
        "dice_roll_id": "27d69dd0-0089-4561-9955-c0024dea6d5c",
        "resolution_id": "7c0752ce-7856-4f12-b68b-0c9550f68d12",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1"
      },
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "created_at": "2026-09-01T23:25:31.573183+12:00"
    }
  ]
  Response headers
  content-length: 20345
  content-type: application/json
  date: Tue,01 Sep 2026 11:34:25 GMT
  server: uvicorn

Action8.
  Curl
  curl -X 'POST' \
    'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions/71eb03a0-3af0-472f-b7cf-02fc7cf3472f/replay' \
    -H 'accept: application/json' \
    -d ''
  Request URL
  http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions/71eb03a0-3af0-472f-b7cf-02fc7cf3472f/replay
  Server response
  Code	200
  Response body
  {
    "resolution_id": "71eb03a0-3af0-472f-b7cf-02fc7cf3472f",
    "equivalent": true,
    "replayed": {
      "id": "71eb03a0-3af0-472f-b7cf-02fc7cf3472f",
      "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
      "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "dice_roll_id": "14c53724-65f5-4fc8-b3be-b51013dc0369",
      "character_revision": 1,
      "state_revision": 1,
      "resolution_type": "ability_check",
      "ability": "dexterity",
      "skill": "stealth",
      "difficulty_class": 13,
      "rule_definition_keys": [
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.ability_check",
        "srd-5.2.1:rule.difficulty_class",
        "srd-5.2.1:rule.disadvantage"
      ],
      "source_ids": [
        "srd-check-save-resolution"
      ],
      "command": {
        "command_id": "e3f9a1cf-d6e8-4273-9462-ff17316f5187",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": "ability_check",
        "ability": "dexterity",
        "skill": "stealth",
        "difficulty_class": 13,
        "advantage_reasons": [],
        "disadvantage_reasons": []
      },
      "modifier_formula": "Dexterity modifier + Proficiency Bonus when proficient in Stealth",
      "modifier_components": [
        {
          "kind": "ability",
          "label": "Dexterity modifier",
          "value": 2,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "floor((ability score - 10) / 2)",
            "definition_keys": [
              "srd-5.2.1:rule.ability_modifier",
              "srd-5.2.1:ability.dexterity",
              "srd-5.2.1:ability_method.standard_array"
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
          "kind": "proficiency",
          "label": "Stealth proficiency",
          "value": 0,
          "applied": false,
          "multiplier": 0,
          "provenance": {
            "formula": "Proficiency Bonus applies once when proficient in the selected skill",
            "definition_keys": [
              "srd-5.2.1:rule.skill_modifier",
              "srd-5.2.1:skill.stealth",
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
        }
      ],
      "advantage_sources": [],
      "disadvantage_sources": [
        {
          "definition_key": "srd-5.2.1:equipment.chain_mail",
          "reason": "Worn Chain Mail imposes Disadvantage on Stealth checks",
          "source_ids": [
            "srd-equipment-state"
          ],
          "automatic": true
        }
      ],
      "advantage_state": "disadvantage",
      "dice_notation": "2d20",
      "dice_faces": [
        17,
        8
      ],
      "selected_die": 8,
      "modifier": 2,
      "total": 10,
      "outcome": "failure",
      "resolver_version": "check-save-resolution-1.0.0",
      "rng_version": "system-random-1.0.0",
      "created_at": "2026-09-01T22:28:11.737959+12:00"
    }
  }
  Response headers
  content-length: 2918
  content-type: application/json
  date: Tue,01 Sep 2026 11:37:13 GMT
  server: uvicorn

Action9.
  Character1:
    Curl
    curl -X 'POST' \
      'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "command_id": "1564274f-a183-46ba-90be-f369d9668c20",
      "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "saving_throw",
      "ability": "strength",
      "skill": null,
      "difficulty_class": 13,
      "advantage_reasons": [],
      "disadvantage_reasons": []
    }'
    Request URL
    http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
    Server response
    Code	201
    Response body
    {
      "id": "bbfc6df0-40a0-4c35-bdb9-2ee4c561eef9",
      "command_id": "1564274f-a183-46ba-90be-f369d9668c20",
      "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
      "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "dice_roll_id": "eb5c9e3f-76e5-4325-86c5-17df183e04ec",
      "character_revision": 1,
      "state_revision": 2,
      "resolution_type": "saving_throw",
      "ability": "strength",
      "skill": null,
      "difficulty_class": 13,
      "rule_definition_keys": [
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.saving_throw",
        "srd-5.2.1:rule.difficulty_class"
      ],
      "source_ids": [
        "srd-check-save-resolution"
      ],
      "command": {
        "command_id": "1564274f-a183-46ba-90be-f369d9668c20",
        "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": "saving_throw",
        "ability": "strength",
        "skill": null,
        "difficulty_class": 13,
        "advantage_reasons": [],
        "disadvantage_reasons": []
      },
      "modifier_formula": "ability modifier + Proficiency Bonus when save-proficient",
      "modifier_components": [
        {
          "kind": "ability",
          "label": "Strength modifier",
          "value": 3,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "floor((ability score - 10) / 2)",
            "definition_keys": [
              "srd-5.2.1:rule.ability_modifier",
              "srd-5.2.1:ability.strength",
              "srd-5.2.1:ability_method.standard_array",
              "srd-5.2.1:background.soldier"
            ],
            "source_ids": [
              "srd-character-details",
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
        {
          "kind": "proficiency",
          "label": "Strength saving throw proficiency",
          "value": 2,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "Proficiency Bonus applies once when proficient in the selected saving throw",
            "definition_keys": [
              "srd-5.2.1:rule.proficiency_bonus",
              "srd-5.2.1:class.fighter",
              "srd-5.2.1:rule.saving_throw_modifier",
              "srd-5.2.1:ability.strength"
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
        }
      ],
      "advantage_sources": [],
      "disadvantage_sources": [],
      "advantage_state": "normal",
      "dice_notation": "1d20",
      "dice_faces": [
        15
      ],
      "selected_die": 15,
      "modifier": 5,
      "total": 20,
      "outcome": "success",
      "resolver_version": "check-save-resolution-1.0.0",
      "rng_version": "system-random-1.0.0",
      "created_at": "2026-09-01T23:44:17.062242+12:00"
    }
    Response headers
    content-length: 2717
    content-type: application/json
    date: Tue,01 Sep 2026 11:44:16 GMT
    server: uvicorn

  Character2:
    Curl
    curl -X 'POST' \
      'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "command_id": "44ece6d3-1b47-43f0-9079-9a4e13dfbb4c",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "resolution_type": "saving_throw",
      "ability": "strength",
      "skill": null,
      "difficulty_class": 13,
      "advantage_reasons": [],
      "disadvantage_reasons": []
    }'
    Request URL
    http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/resolutions
    Server response
    Code	201
    Response body
    {
      "id": "73c55e10-ca97-4c12-a382-a912da753495",
      "command_id": "44ece6d3-1b47-43f0-9079-9a4e13dfbb4c",
      "campaign_id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
      "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "character_state_catalog_id": "srd-5.2.1-party-state-v1",
      "ruleset_data_catalog_id": "srd-5.2.1-check-save-resolution-v1",
      "dice_roll_id": "c54858ee-33fd-490f-bbcb-0d9ff43f8b63",
      "character_revision": 1,
      "state_revision": 1,
      "resolution_type": "saving_throw",
      "ability": "strength",
      "skill": null,
      "difficulty_class": 13,
      "rule_definition_keys": [
        "srd-5.2.1:rule.d20_test",
        "srd-5.2.1:rule.saving_throw",
        "srd-5.2.1:rule.difficulty_class"
      ],
      "source_ids": [
        "srd-check-save-resolution"
      ],
      "command": {
        "command_id": "44ece6d3-1b47-43f0-9079-9a4e13dfbb4c",
        "actor_character_id": "75f50456-a002-4445-8c65-35d38d188a20",
        "ruleset_release_id": "srd-5.2.1",
        "character_state_catalog_id": "srd-5.2.1-party-state-v1",
        "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
        "resolution_type": "saving_throw",
        "ability": "strength",
        "skill": null,
        "difficulty_class": 13,
        "advantage_reasons": [],
        "disadvantage_reasons": []
      },
      "modifier_formula": "ability modifier + Proficiency Bonus when save-proficient",
      "modifier_components": [
        {
          "kind": "ability",
          "label": "Strength modifier",
          "value": 3,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "floor((ability score - 10) / 2)",
            "definition_keys": [
              "srd-5.2.1:rule.ability_modifier",
              "srd-5.2.1:ability.strength",
              "srd-5.2.1:ability_method.standard_array",
              "srd-5.2.1:background.soldier"
            ],
            "source_ids": [
              "srd-character-details",
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
        {
          "kind": "proficiency",
          "label": "Strength saving throw proficiency",
          "value": 2,
          "applied": true,
          "multiplier": 1,
          "provenance": {
            "formula": "Proficiency Bonus applies once when proficient in the selected saving throw",
            "definition_keys": [
              "srd-5.2.1:rule.proficiency_bonus",
              "srd-5.2.1:class.fighter",
              "srd-5.2.1:rule.saving_throw_modifier",
              "srd-5.2.1:ability.strength"
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
        }
      ],
      "advantage_sources": [],
      "disadvantage_sources": [],
      "advantage_state": "normal",
      "dice_notation": "1d20",
      "dice_faces": [
        15
      ],
      "selected_die": 15,
      "modifier": 5,
      "total": 20,
      "outcome": "success",
      "resolver_version": "check-save-resolution-1.0.0",
      "rng_version": "system-random-1.0.0",
      "created_at": "2026-09-01T23:47:01.763498+12:00"
    }
    Response headers
    content-length: 2717
    content-type: application/json
    date: Tue,01 Sep 2026 11:47:00 GMT
    server: uvicorn
