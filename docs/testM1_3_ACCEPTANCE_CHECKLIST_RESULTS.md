
Actions and results:
Action1.
Curl
curl -X 'POST' \
  '[http://127.0.0.1:8000/campaigns](http://127.0.0.1:8000/campaigns)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "hello world",
  "ruleset_release_id": "srd-5.2.1",
  "starting_location": "Roadside Inn"
}'
Request URL
[http://127.0.0.1:8000/campaigns](http://127.0.0.1:8000/campaigns)
Server response: 201 
Response body

{
  "id": "85c0cd9f-c515-4821-b4c0-5542f08e95e5",
  "name": "hello world",
  "ruleset_release_id": "srd-5.2.1",
  "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
  "status": "active",
  "play_mode": "party_commander",
  "party_min_active": 2,
  "party_max_active": 4,
  "created_at": "2026-08-31T22:37:43.654285+12:00"
}
Response headers
 content-length: 290 
 content-type: application/json 
 date: Mon,31 Aug 2026 10:37:42 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action2.1.
Curl
curl -X 'POST' \
  '[http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters](http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "SugarHigh"
}'
Request URL
[http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters](http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters)
Server response
Code 201	
Response body
{
  "id": "2039690f-15ca-4154-8822-1fbd4190daf1",
  "ruleset_release_id": "srd-5.2.1",
  "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
  "name": "SugarHigh",
  "creation_status": "draft",
  "revision": 0,
  "hp": null,
  "max_hp": null,
  "inventory": {},
  "character_sheet": null,
  "finalized_at": null,
  "party_position": 1,
  "control_mode": "player",
  "party_status": "active",
  "state_revision": 0,
  "equipped_items": {
    "worn_armor_item_id": null,
    "held_item_ids": []
  },
  "resources": {},
  "mechanical_state": null
}
Response headers
 content-length: 460 
 content-type: application/json 
 date: Mon,31 Aug 2026 10:43:49 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action2.2.
Curl
curl -X 'POST' \
  '[http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters](http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "LooneyHigh"
}'
Request URL
[http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters](http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters)
Server response
Code	201	
Response body
{
  "id": "75f50456-a002-4445-8c65-35d38d188a20",
  "ruleset_release_id": "srd-5.2.1",
  "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
  "name": "LooneyHigh",
  "creation_status": "draft",
  "revision": 0,
  "hp": null,
  "max_hp": null,
  "inventory": {},
  "character_sheet": null,
  "finalized_at": null,
  "party_position": 2,
  "control_mode": "player",
  "party_status": "active",
  "state_revision": 0,
  "equipped_items": {
    "worn_armor_item_id": null,
    "held_item_ids": []
  },
  "resources": {},
  "mechanical_state": null
}
Response headers
 content-length: 461 
 content-type: application/json 
 date: Mon,31 Aug 2026 10:45:45 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 
Action3.
Curl
curl -X 'GET' \
  '[http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/state](http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/state)' \
  -H 'accept: application/json'
Request URL
[http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/state](http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/state)
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
      "creation_status": "draft",
      "revision": 0,
      "hp": null,
      "max_hp": null,
      "inventory": {},
      "character_sheet": null,
      "finalized_at": null,
      "party_position": 1,
      "control_mode": "player",
      "party_status": "active",
      "state_revision": 0,
      "equipped_items": {
        "worn_armor_item_id": null,
        "held_item_ids": []
      },
      "resources": {},
      "mechanical_state": null
    },
    {
      "id": "75f50456-a002-4445-8c65-35d38d188a20",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
      "name": "LooneyHigh",
      "creation_status": "draft",
      "revision": 0,
      "hp": null,
      "max_hp": null,
      "inventory": {},
      "character_sheet": null,
      "finalized_at": null,
      "party_position": 2,
      "control_mode": "player",
      "party_status": "active",
      "state_revision": 0,
      "equipped_items": {
        "worn_armor_item_id": null,
        "held_item_ids": []
      },
      "resources": {},
      "mechanical_state": null
    }
  ],
  "party_ready": false,
  "location": {
    "id": "4a872d66-ad82-4c09-ba17-9385e552c5da",
    "name": "Roadside Inn",
    "description": "The campaign's starting point."
  },
  "turn_count": 0
}
Response headers
 content-length: 1419 
 content-type: application/json 
 date: Mon,31 Aug 2026 10:47:52 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action4.
Curl
curl -X 'GET' \
  'http://127.0.0.1:8000/rulesets/srd-5.2.1/character-creation/options' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/rulesets/srd-5.2.1/character-creation/options
Server response
Code	200	
Response body
{
  "selected_ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
  "character_creation": {
    "$schema": "../schema/character-creation.schema.json",
    "schema_version": "1.0.0",
    "id": "srd-5.2.1-character-creation-v1",
    "ruleset_release_id": "srd-5.2.1",
    "resolver_version": "character-creation-1.0.0",
    "sources": [
      {
        "id": "srd-core-d20",
        "title": "System Reference Document 5.2.1",
        "section": "Playing the Game: Proficiency and Skills",
        "printed_pages": [
          8,
          9
        ],
        "url": "https://www.dndbeyond.com/srd"
      },
      {
        "id": "srd-character-creation",
        "title": "System Reference Document 5.2.1",
        "section": "Character Creation",
        "printed_pages": [
          19,
          20,
          21,
          22,
          23
        ],
        "url": "https://www.dndbeyond.com/srd"
      },
      {
        "id": "srd-fighter",
        "title": "System Reference Document 5.2.1",
        "section": "Classes: Fighter",
        "printed_pages": [
          47,
          48
        ],
        "url": "https://www.dndbeyond.com/srd"
      },
      {
        "id": "srd-soldier",
        "title": "System Reference Document 5.2.1",
        "section": "Character Origins: Soldier",
        "printed_pages": [
          83
        ],
        "url": "https://www.dndbeyond.com/srd"
      },
      {
        "id": "srd-human",
        "title": "System Reference Document 5.2.1",
        "section": "Character Origins: Human",
        "printed_pages": [
          86
        ],
        "url": "https://www.dndbeyond.com/srd"
      },
      {
        "id": "srd-feats",
        "title": "System Reference Document 5.2.1",
        "section": "Feats: Origin and Fighting Style Feats",
        "printed_pages": [
          87,
          88
        ],
        "url": "https://www.dndbeyond.com/srd"
      },
      {
        "id": "srd-equipment",
        "title": "System Reference Document 5.2.1",
        "section": "Equipment: Weapons, Armor, Tools, and Adventuring Gear",
        "printed_pages": [
          91,
          92,
          94,
          95,
          97
        ],
        "url": "https://www.dndbeyond.com/srd"
      }
    ],
    "abilities": [
      {
        "id": "strength",
        "definition_key": "srd-5.2.1:ability.strength",
        "name": "Strength",
        "beginner_description": "Physical power and athletic force.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "dexterity",
        "definition_key": "srd-5.2.1:ability.dexterity",
        "name": "Dexterity",
        "beginner_description": "Agility, reflexes, and precise movement.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "constitution",
        "definition_key": "srd-5.2.1:ability.constitution",
        "name": "Constitution",
        "beginner_description": "Health, endurance, and resilience.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "intelligence",
        "definition_key": "srd-5.2.1:ability.intelligence",
        "name": "Intelligence",
        "beginner_description": "Reasoning, recall, and analysis.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "wisdom",
        "definition_key": "srd-5.2.1:ability.wisdom",
        "name": "Wisdom",
        "beginner_description": "Awareness, intuition, and judgment.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "charisma",
        "definition_key": "srd-5.2.1:ability.charisma",
        "name": "Charisma",
        "beginner_description": "Confidence, presence, and influence.",
        "source_ids": [
          "srd-character-creation"
        ]
      }
    ],
    "alignments": [
      {
        "id": "lg",
        "definition_key": "srd-5.2.1:alignment.lawful_good",
        "name": "Lawful Good",
        "beginner_description": "Do what is right while respecting order and duty.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "ng",
        "definition_key": "srd-5.2.1:alignment.neutral_good",
        "name": "Neutral Good",
        "beginner_description": "Help others without being strongly bound to order or rebellion.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "cg",
        "definition_key": "srd-5.2.1:alignment.chaotic_good",
        "name": "Chaotic Good",
        "beginner_description": "Follow conscience and personal freedom while helping others.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "ln",
        "definition_key": "srd-5.2.1:alignment.lawful_neutral",
        "name": "Lawful Neutral",
        "beginner_description": "Follow law, tradition, or a personal code.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "n",
        "definition_key": "srd-5.2.1:alignment.neutral",
        "name": "Neutral",
        "beginner_description": "Choose what seems best without a strong moral or orderly extreme.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "cn",
        "definition_key": "srd-5.2.1:alignment.chaotic_neutral",
        "name": "Chaotic Neutral",
        "beginner_description": "Value personal freedom and follow changing impulses.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "le",
        "definition_key": "srd-5.2.1:alignment.lawful_evil",
        "name": "Lawful Evil",
        "beginner_description": "Pursue selfish ends within a code or hierarchy.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "ne",
        "definition_key": "srd-5.2.1:alignment.neutral_evil",
        "name": "Neutral Evil",
        "beginner_description": "Pursue selfish ends without loyalty to order or freedom.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "ce",
        "definition_key": "srd-5.2.1:alignment.chaotic_evil",
        "name": "Chaotic Evil",
        "beginner_description": "Act with destructive selfishness and little restraint.",
        "source_ids": [
          "srd-character-creation"
        ]
      }
    ],
    "skills": [
      {
        "id": "acrobatics",
        "definition_key": "srd-5.2.1:skill.acrobatics",
        "name": "Acrobatics",
        "beginner_description": "Balance and acrobatic movement.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "dexterity"
      },
      {
        "id": "animal_handling",
        "definition_key": "srd-5.2.1:skill.animal_handling",
        "name": "Animal Handling",
        "beginner_description": "Calm, train, or direct animals.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "wisdom"
      },
      {
        "id": "arcana",
        "definition_key": "srd-5.2.1:skill.arcana",
        "name": "Arcana",
        "beginner_description": "Recall lore about magic and the planes.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "intelligence"
      },
      {
        "id": "athletics",
        "definition_key": "srd-5.2.1:skill.athletics",
        "name": "Athletics",
        "beginner_description": "Climb, jump, swim, and exert force.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "strength"
      },
      {
        "id": "deception",
        "definition_key": "srd-5.2.1:skill.deception",
        "name": "Deception",
        "beginner_description": "Mislead others convincingly.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "charisma"
      },
      {
        "id": "history",
        "definition_key": "srd-5.2.1:skill.history",
        "name": "History",
        "beginner_description": "Recall historical people, places, and events.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "intelligence"
      },
      {
        "id": "insight",
        "definition_key": "srd-5.2.1:skill.insight",
        "name": "Insight",
        "beginner_description": "Read moods, motives, and intentions.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "wisdom"
      },
      {
        "id": "intimidation",
        "definition_key": "srd-5.2.1:skill.intimidation",
        "name": "Intimidation",
        "beginner_description": "Influence through threats or force of presence.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "charisma"
      },
      {
        "id": "investigation",
        "definition_key": "srd-5.2.1:skill.investigation",
        "name": "Investigation",
        "beginner_description": "Find information and deduce how things work.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "intelligence"
      },
      {
        "id": "medicine",
        "definition_key": "srd-5.2.1:skill.medicine",
        "name": "Medicine",
        "beginner_description": "Diagnose illness or determine causes of injury and death.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "wisdom"
      },
      {
        "id": "nature",
        "definition_key": "srd-5.2.1:skill.nature",
        "name": "Nature",
        "beginner_description": "Recall lore about terrain, plants, animals, and weather.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "intelligence"
      },
      {
        "id": "perception",
        "definition_key": "srd-5.2.1:skill.perception",
        "name": "Perception",
        "beginner_description": "Notice details using your senses.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "wisdom"
      },
      {
        "id": "performance",
        "definition_key": "srd-5.2.1:skill.performance",
        "name": "Performance",
        "beginner_description": "Act, tell stories, make music, or dance.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "charisma"
      },
      {
        "id": "persuasion",
        "definition_key": "srd-5.2.1:skill.persuasion",
        "name": "Persuasion",
        "beginner_description": "Convince others honestly and graciously.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "charisma"
      },
      {
        "id": "religion",
        "definition_key": "srd-5.2.1:skill.religion",
        "name": "Religion",
        "beginner_description": "Recall lore about gods, rituals, and holy symbols.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "intelligence"
      },
      {
        "id": "sleight_of_hand",
        "definition_key": "srd-5.2.1:skill.sleight_of_hand",
        "name": "Sleight of Hand",
        "beginner_description": "Pick pockets, conceal objects, and perform legerdemain.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "dexterity"
      },
      {
        "id": "stealth",
        "definition_key": "srd-5.2.1:skill.stealth",
        "name": "Stealth",
        "beginner_description": "Move quietly and avoid notice.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "dexterity"
      },
      {
        "id": "survival",
        "definition_key": "srd-5.2.1:skill.survival",
        "name": "Survival",
        "beginner_description": "Track, forage, navigate, and avoid natural hazards.",
        "source_ids": [
          "srd-core-d20"
        ],
        "typical_ability": "wisdom"
      }
    ],
    "languages": [
      {
        "id": "common",
        "definition_key": "srd-5.2.1:language.common",
        "name": "Common",
        "beginner_description": "Every player character knows Common automatically.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "common_sign",
        "definition_key": "srd-5.2.1:language.common_sign",
        "name": "Common Sign Language",
        "beginner_description": "A widespread signed language.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "draconic",
        "definition_key": "srd-5.2.1:language.draconic",
        "name": "Draconic",
        "beginner_description": "A standard language associated with dragons and dragonborn.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "dwarvish",
        "definition_key": "srd-5.2.1:language.dwarvish",
        "name": "Dwarvish",
        "beginner_description": "A standard language associated with dwarves.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "elvish",
        "definition_key": "srd-5.2.1:language.elvish",
        "name": "Elvish",
        "beginner_description": "A standard language associated with elves.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "giant",
        "definition_key": "srd-5.2.1:language.giant",
        "name": "Giant",
        "beginner_description": "A standard language associated with giants.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "gnomish",
        "definition_key": "srd-5.2.1:language.gnomish",
        "name": "Gnomish",
        "beginner_description": "A standard language associated with gnomes.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "goblin",
        "definition_key": "srd-5.2.1:language.goblin",
        "name": "Goblin",
        "beginner_description": "A widespread standard language.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "halfling",
        "definition_key": "srd-5.2.1:language.halfling",
        "name": "Halfling",
        "beginner_description": "A standard language associated with halflings.",
        "source_ids": [
          "srd-character-creation"
        ]
      },
      {
        "id": "orc",
        "definition_key": "srd-5.2.1:language.orc",
        "name": "Orc",
        "beginner_description": "A standard language associated with orcs.",
        "source_ids": [
          "srd-character-creation"
        ]
      }
    ],
    "gaming_sets": [
      {
        "id": "dice",
        "definition_key": "srd-5.2.1:tool.gaming_set.dice",
        "name": "Dice Set",
        "beginner_description": "A compact set of gaming dice.",
        "source_ids": [
          "srd-equipment"
        ]
      },
      {
        "id": "dragonchess",
        "definition_key": "srd-5.2.1:tool.gaming_set.dragonchess",
        "name": "Dragonchess Set",
        "beginner_description": "A strategy gaming set.",
        "source_ids": [
          "srd-equipment"
        ]
      },
      {
        "id": "playing_cards",
        "definition_key": "srd-5.2.1:tool.gaming_set.playing_cards",
        "name": "Playing Card Set",
        "beginner_description": "A deck used for many games.",
        "source_ids": [
          "srd-equipment"
        ]
      },
      {
        "id": "three_dragon_ante",
        "definition_key": "srd-5.2.1:tool.gaming_set.three_dragon_ante",
        "name": "Three-Dragon Ante Set",
        "beginner_description": "A card-based gaming set.",
        "source_ids": [
          "srd-equipment"
        ]
      }
    ],
    "standard_array": {
      "id": "standard_array",
      "definition_key": "srd-5.2.1:ability_method.standard_array",
      "name": "Standard Array",
      "beginner_description": "Assign 15, 14, 13, 12, 10, and 8 once each among the six abilities.",
      "source_ids": [
        "srd-character-creation"
      ],
      "scores": [
        15,
        14,
        13,
        12,
        10,
        8
      ]
    },
    "background": {
      "id": "soldier",
      "definition_key": "srd-5.2.1:background.soldier",
      "name": "Soldier",
      "beginner_description": "A martial background granting physical ability increases, combat-oriented skills, Savage Attacker, and one gaming-set proficiency.",
      "source_ids": [
        "srd-soldier"
      ],
      "ability_score_options": [
        "strength",
        "dexterity",
        "constitution"
      ],
      "granted_feat_definition_key": "srd-5.2.1:feat.origin.savage_attacker",
      "skill_proficiencies": [
        "athletics",
        "intimidation"
      ],
      "gaming_set_choice_count": 1,
      "equipment_package_definition_key": "srd-5.2.1:equipment_package.soldier.a"
    },
    "species": {
      "id": "human",
      "definition_key": "srd-5.2.1:species.human",
      "name": "Human",
      "beginner_description": "A versatile Humanoid with Resourceful, Skillful, and Versatile traits.",
      "source_ids": [
        "srd-human"
      ],
      "creature_type": "humanoid",
      "sizes": [
        "small",
        "medium"
      ],
      "speed_feet": 30,
      "skill_choice_count": 1,
      "origin_feat_choice_count": 1,
      "origin_feat_options": [
        "srd-5.2.1:feat.origin.alert",
        "srd-5.2.1:feat.origin.skilled"
      ],
      "feature_definition_keys": [
        "srd-5.2.1:species_feature.human.resourceful",
        "srd-5.2.1:species_feature.human.skillful",
        "srd-5.2.1:species_feature.human.versatile"
      ]
    },
    "character_class": {
      "id": "fighter",
      "definition_key": "srd-5.2.1:class.fighter",
      "name": "Fighter",
      "beginner_description": "A level-one martial class trained with all standard armor and weapons.",
      "source_ids": [
        "srd-fighter"
      ],
      "level": 1,
      "hit_die": 10,
      "proficiency_bonus": 2,
      "saving_throw_proficiencies": [
        "strength",
        "constitution"
      ],
      "skill_choice_count": 2,
      "skill_options": [
        "acrobatics",
        "animal_handling",
        "athletics",
        "history",
        "insight",
        "intimidation",
        "persuasion",
        "perception",
        "survival"
      ],
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
      "fighting_style_choice_count": 1,
      "fighting_style_options": [
        "srd-5.2.1:feat.fighting_style.archery",
        "srd-5.2.1:feat.fighting_style.defense",
        "srd-5.2.1:feat.fighting_style.great_weapon_fighting",
        "srd-5.2.1:feat.fighting_style.two_weapon_fighting"
      ],
      "weapon_mastery_choice_count": 3,
      "weapon_mastery_options": [
        "srd-5.2.1:weapon.javelin",
        "srd-5.2.1:weapon.flail",
        "srd-5.2.1:weapon.greatsword"
      ],
      "feature_definition_keys": [
        "srd-5.2.1:class_feature.fighter.fighting_style",
        "srd-5.2.1:class_feature.fighter.second_wind",
        "srd-5.2.1:class_feature.fighter.weapon_mastery"
      ],
      "second_wind_uses": 2,
      "equipment_package_definition_key": "srd-5.2.1:equipment_package.fighter.a"
    },
    "features": [
      {
        "id": "human_resourceful",
        "definition_key": "srd-5.2.1:species_feature.human.resourceful",
        "name": "Resourceful",
        "beginner_description": "Gain Heroic Inspiration after finishing a Long Rest.",
        "source_ids": [
          "srd-human"
        ]
      },
      {
        "id": "human_skillful",
        "definition_key": "srd-5.2.1:species_feature.human.skillful",
        "name": "Skillful",
        "beginner_description": "Gain proficiency in one chosen skill.",
        "source_ids": [
          "srd-human"
        ]
      },
      {
        "id": "human_versatile",
        "definition_key": "srd-5.2.1:species_feature.human.versatile",
        "name": "Versatile",
        "beginner_description": "Gain one chosen Origin feat.",
        "source_ids": [
          "srd-human"
        ]
      },
      {
        "id": "fighter_fighting_style",
        "definition_key": "srd-5.2.1:class_feature.fighter.fighting_style",
        "name": "Fighting Style",
        "beginner_description": "Choose one supported Fighting Style feat.",
        "source_ids": [
          "srd-fighter"
        ]
      },
      {
        "id": "fighter_second_wind",
        "definition_key": "srd-5.2.1:class_feature.fighter.second_wind",
        "name": "Second Wind",
        "beginner_description": "Two uses at level one; a use can restore 1d10 plus Fighter level Hit Points.",
        "source_ids": [
          "srd-fighter"
        ]
      },
      {
        "id": "fighter_weapon_mastery",
        "definition_key": "srd-5.2.1:class_feature.fighter.weapon_mastery",
        "name": "Weapon Mastery",
        "beginner_description": "Use the mastery properties of three selected Simple or Martial weapon kinds.",
        "source_ids": [
          "srd-fighter"
        ]
      }
    ],
    "origin_feats": [
      {
        "id": "savage_attacker",
        "definition_key": "srd-5.2.1:feat.origin.savage_attacker",
        "name": "Savage Attacker",
        "beginner_description": "Once per turn, roll weapon damage dice twice and use either roll.",
        "source_ids": [
          "srd-feats"
        ],
        "additional_skill_choice_count": 0
      },
      {
        "id": "alert",
        "definition_key": "srd-5.2.1:feat.origin.alert",
        "name": "Alert",
        "beginner_description": "Add Proficiency Bonus to Initiative and potentially swap Initiative with a willing ally.",
        "source_ids": [
          "srd-feats"
        ],
        "additional_skill_choice_count": 0
      },
      {
        "id": "skilled",
        "definition_key": "srd-5.2.1:feat.origin.skilled",
        "name": "Skilled",
        "beginner_description": "Gain three additional supported skill proficiencies in this initial slice.",
        "source_ids": [
          "srd-feats"
        ],
        "additional_skill_choice_count": 3
      }
    ],
    "fighting_styles": [
      {
        "id": "archery",
        "definition_key": "srd-5.2.1:feat.fighting_style.archery",
        "name": "Archery",
        "beginner_description": "Improve attack rolls made with ranged weapons.",
        "source_ids": [
          "srd-feats"
        ],
        "effect_summary": "+2 to attack rolls with Ranged weapons"
      },
      {
        "id": "defense",
        "definition_key": "srd-5.2.1:feat.fighting_style.defense",
        "name": "Defense",
        "beginner_description": "Improve Armor Class while wearing armor.",
        "source_ids": [
          "srd-feats"
        ],
        "effect_summary": "+1 Armor Class while wearing Light, Medium, or Heavy armor"
      },
      {
        "id": "great_weapon_fighting",
        "definition_key": "srd-5.2.1:feat.fighting_style.great_weapon_fighting",
        "name": "Great Weapon Fighting",
        "beginner_description": "Raise very low damage-die results with eligible two-handed melee weapons.",
        "source_ids": [
          "srd-feats"
        ],
        "effect_summary": "Treat eligible weapon damage-die results of 1 or 2 as 3"
      },
      {
        "id": "two_weapon_fighting",
        "definition_key": "srd-5.2.1:feat.fighting_style.two_weapon_fighting",
        "name": "Two-Weapon Fighting",
        "beginner_description": "Add the ability modifier to eligible extra Light-weapon attack damage.",
        "source_ids": [
          "srd-feats"
        ],
        "effect_summary": "Add the ability modifier to eligible Light-weapon extra-attack damage"
      }
    ],
    "weapons": [
      {
        "id": "javelin",
        "definition_key": "srd-5.2.1:weapon.javelin",
        "name": "Javelin",
        "beginner_description": "A Simple melee weapon that can be thrown.",
        "source_ids": [
          "srd-equipment"
        ],
        "category": "simple",
        "mastery": "slow"
      },
      {
        "id": "flail",
        "definition_key": "srd-5.2.1:weapon.flail",
        "name": "Flail",
        "beginner_description": "A one-handed Martial melee weapon.",
        "source_ids": [
          "srd-equipment"
        ],
        "category": "martial",
        "mastery": "sap"
      },
      {
        "id": "greatsword",
        "definition_key": "srd-5.2.1:weapon.greatsword",
        "name": "Greatsword",
        "beginner_description": "A heavy, two-handed Martial melee weapon.",
        "source_ids": [
          "srd-equipment"
        ],
        "category": "martial",
        "mastery": "graze"
      }
    ],
    "equipment_packages": [
      {
        "id": "soldier_a",
        "definition_key": "srd-5.2.1:equipment_package.soldier.a",
        "name": "Soldier Equipment A",
        "beginner_description": "The supported Soldier equipment package.",
        "source_ids": [
          "srd-soldier",
          "srd-equipment"
        ],
        "items": [
          {
            "item_id": "spear",
            "name": "Spear",
            "quantity": 1
          },
          {
            "item_id": "shortbow",
            "name": "Shortbow",
            "quantity": 1
          },
          {
            "item_id": "arrow",
            "name": "Arrow",
            "quantity": 20
          },
          {
            "item_id": "chosen_gaming_set",
            "name": "Chosen Gaming Set",
            "quantity": 1
          },
          {
            "item_id": "healers_kit",
            "name": "Healer's Kit",
            "quantity": 1
          },
          {
            "item_id": "quiver",
            "name": "Quiver",
            "quantity": 1
          },
          {
            "item_id": "travelers_clothes",
            "name": "Traveler's Clothes",
            "quantity": 1
          }
        ],
        "gold_pieces": 14
      },
      {
        "id": "fighter_a",
        "definition_key": "srd-5.2.1:equipment_package.fighter.a",
        "name": "Fighter Equipment A",
        "beginner_description": "The supported Strength-focused Fighter equipment package.",
        "source_ids": [
          "srd-fighter",
          "srd-equipment"
        ],
        "items": [
          {
            "item_id": "chain_mail",
            "name": "Chain Mail",
            "quantity": 1
          },
          {
            "item_id": "greatsword",
            "name": "Greatsword",
            "quantity": 1
          },
          {
            "item_id": "flail",
            "name": "Flail",
            "quantity": 1
          },
          {
            "item_id": "javelin",
            "name": "Javelin",
            "quantity": 8
          },
          {
            "item_id": "dungeoneers_pack",
            "name": "Dungeoneer's Pack",
            "quantity": 1
          }
        ],
        "gold_pieces": 4
      }
    ],
    "supported_profile": {
      "species_definition_key": "srd-5.2.1:species.human",
      "background_definition_key": "srd-5.2.1:background.soldier",
      "class_definition_key": "srd-5.2.1:class.fighter",
      "ability_method_definition_key": "srd-5.2.1:ability_method.standard_array",
      "equipment_route_id": "soldier-a+fighter-a"
    }
  },
  "party": {
    "mode": "party_commander",
    "minimum_active_characters": 2,
    "maximum_active_characters": 4,
    "control_mode": "player"
  }
}
Response headers
 content-length: 19224 
 content-type: application/json 
 date: Mon,31 Aug 2026 10:50:17 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action5&6
 Curl
curl -X 'POST' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters/2039690f-15ca-4154-8822-1fbd4190daf1/finalize' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
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
    "charisma": 12
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
    "srd-5.2.1:weapon.greatsword"
  ],
  "equipment_route_id": "soldier-a+fighter-a"
}'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters/2039690f-15ca-4154-8822-1fbd4190daf1/finalize
Server response
Code	200	
Response body
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
    "Spear": 1,
    "Shortbow": 1,
    "Arrow": 20,
    "Dice Set": 1,
    "Healer's Kit": 1,
    "Quiver": 1,
    "Traveler's Clothes": 1,
    "Chain Mail": 1,
    "Greatsword": 1,
    "Flail": 1,
    "Javelin": 8,
    "Dungeoneer's Pack": 1,
    "GP": 18
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
      },
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
      "Spear": 1,
      "Shortbow": 1,
      "Arrow": 20,
      "Dice Set": 1,
      "Healer's Kit": 1,
      "Quiver": 1,
      "Traveler's Clothes": 1,
      "Chain Mail": 1,
      "Greatsword": 1,
      "Flail": 1,
      "Javelin": 8,
      "Dungeoneer's Pack": 1,
      "GP": 18
    },
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
    "resolver_version": "character-creation-1.0.0"
  },
  "finalized_at": "2026-08-31T10:55:22.788199Z",
  "party_position": 1,
  "control_mode": "player",
  "party_status": "active",
  "state_revision": 1,
  "equipped_items": {
    "worn_armor_item_id": "chain_mail",
    "held_item_ids": []
  },
  "resources": {
    "second_wind": 2,
    "heroic_inspiration": 1,
    "hit_dice": 1
  },
  "mechanical_state": {
    "resolver_version": "character-state-1.0.0",
    "character_revision": 1,
    "state_revision": 1,
    "level": 1,
    "abilities": {
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
      },
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
        "state_revision": 1,
        "resolver_version": "character-state-1.0.0"
      }
    },
    "saving_throws": {
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
          ],
          "character_revision": 1,
          "state_revision": 1,
          "resolver_version": "character-state-1.0.0"
        },
        "ability": "intelligence",
        "proficient": false
      },
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
          ],
          "character_revision": 1,
          "state_revision": 1,
          "resolver_version": "character-state-1.0.0"
        },
        "ability": "charisma",
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
          "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
          "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
          "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
          "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
          "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
        "equipped_quantity": 1,
        "position": "worn",
        "definition_key": "srd-5.2.1:equipment.chain_mail",
        "source_ids": [
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
        "definition_key": null,
        "source_ids": [],
        "acquisition_event_ids": []
      },
      {
        "item_id": "dungeoneers_pack",
        "name": "Dungeoneer's Pack",
        "quantity": 1,
        "equipped_quantity": 0,
        "position": "carried",
        "definition_key": null,
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
        "source_ids": [
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
        "source_ids": [],
        "acquisition_event_ids": []
      },
      {
        "item_id": "greatsword",
        "name": "Greatsword",
        "quantity": 1,
        "equipped_quantity": 0,
        "position": "carried",
        "definition_key": "srd-5.2.1:equipment.greatsword.state",
        "source_ids": [
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
        "source_ids": [
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
          ],
          "character_revision": 1,
          "state_revision": 1,
          "resolver_version": "character-state-1.0.0"
        }
      }
    }
  }
}
Response headers
 content-length: 23753 
 content-type: application/json 
 date: Mon,31 Aug 2026 10:55:22 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action7.1.
Curl
curl -X 'POST' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters/75f50456-a002-4445-8c65-35d38d188a20/finalize' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
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
    "charisma": 12
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
    "srd-5.2.1:weapon.greatsword"
  ],
  "equipment_route_id": "soldier-a+fighter-a"
}'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters/75f50456-a002-4445-8c65-35d38d188a20/finalize
Server response
Code	200	
Response body
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
    "Spear": 1,
    "Shortbow": 1,
    "Arrow": 20,
    "Dice Set": 1,
    "Healer's Kit": 1,
    "Quiver": 1,
    "Traveler's Clothes": 1,
    "Chain Mail": 1,
    "Greatsword": 1,
    "Flail": 1,
    "Javelin": 8,
    "Dungeoneer's Pack": 1,
    "GP": 18
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
      },
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
      "Spear": 1,
      "Shortbow": 1,
      "Arrow": 20,
      "Dice Set": 1,
      "Healer's Kit": 1,
      "Quiver": 1,
      "Traveler's Clothes": 1,
      "Chain Mail": 1,
      "Greatsword": 1,
      "Flail": 1,
      "Javelin": 8,
      "Dungeoneer's Pack": 1,
      "GP": 18
    },
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-character-creation-v1",
    "resolver_version": "character-creation-1.0.0"
  },
  "finalized_at": "2026-08-31T11:02:55.175375Z",
  "party_position": 2,
  "control_mode": "player",
  "party_status": "active",
  "state_revision": 1,
  "equipped_items": {
    "worn_armor_item_id": "chain_mail",
    "held_item_ids": []
  },
  "resources": {
    "second_wind": 2,
    "heroic_inspiration": 1,
    "hit_dice": 1
  },
  "mechanical_state": {
    "resolver_version": "character-state-1.0.0",
    "character_revision": 1,
    "state_revision": 1,
    "level": 1,
    "abilities": {
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
      },
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
      },
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
        "source_ids": [
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
        "definition_key": null,
        "source_ids": [],
        "acquisition_event_ids": []
      },
      {
        "item_id": "dungeoneers_pack",
        "name": "Dungeoneer's Pack",
        "quantity": 1,
        "equipped_quantity": 0,
        "position": "carried",
        "definition_key": null,
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
        "source_ids": [
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
        "source_ids": [],
        "acquisition_event_ids": []
      },
      {
        "item_id": "greatsword",
        "name": "Greatsword",
        "quantity": 1,
        "equipped_quantity": 0,
        "position": "carried",
        "definition_key": "srd-5.2.1:equipment.greatsword.state",
        "source_ids": [
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
        "source_ids": [
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
Response headers
 content-length: 23754 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:02:54 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action7.2.
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
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
              "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
            "equipped_quantity": 1,
            "position": "worn",
            "definition_key": "srd-5.2.1:equipment.chain_mail",
            "source_ids": [
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
            "definition_key": null,
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "dungeoneers_pack",
            "name": "Dungeoneer's Pack",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
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
            "source_ids": [
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
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "greatsword",
            "name": "Greatsword",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.greatsword.state",
            "source_ids": [
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
            "source_ids": [
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
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
                "7da975fb-7ea4-4ee0-8a09-963294af2d7e"
              ],
              "character_revision": 1,
              "state_revision": 1,
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
            "source_ids": [
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
            "definition_key": null,
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "dungeoneers_pack",
            "name": "Dungeoneer's Pack",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
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
            "source_ids": [
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
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "greatsword",
            "name": "Greatsword",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.greatsword.state",
            "source_ids": [
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
            "source_ids": [
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
  "turn_count": 0
}
Response headers
 content-length: 48014 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:05:09 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action8.
 Curl
curl -X 'PUT' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters/2039690f-15ca-4154-8822-1fbd4190daf1/loadout' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"worn_armor_item_id": null, "held_item_ids": ["greatsword"]}'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/characters/2039690f-15ca-4154-8822-1fbd4190daf1/loadout
Server response
Code	200	
Response body
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
        "source_ids": [
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
        "definition_key": null,
        "source_ids": [],
        "acquisition_event_ids": []
      },
      {
        "item_id": "dungeoneers_pack",
        "name": "Dungeoneer's Pack",
        "quantity": 1,
        "equipped_quantity": 0,
        "position": "carried",
        "definition_key": null,
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
        "source_ids": [
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
        "source_ids": [],
        "acquisition_event_ids": []
      },
      {
        "item_id": "greatsword",
        "name": "Greatsword",
        "quantity": 1,
        "equipped_quantity": 1,
        "position": "held",
        "definition_key": "srd-5.2.1:equipment.greatsword.state",
        "source_ids": [
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
        "source_ids": [
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
}
Response headers
 content-length: 23262 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:09:51 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action9.1.
Curl
curl -X 'POST' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/turns' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "action": "Arin carefully searches the room for anything unusual.",
  "actor_character_id": ""
}'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/turns
Server response
Code	422	
Error: Unprocessable Entity
Response body
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": [
        "body",
        "actor_character_id"
      ],
      "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 0",
      "input": "",
      "ctx": {
        "error": "invalid length: expected length 32 for simple format, found 0"
      }
    }
  ]
}
Response headers
 content-length: 263 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:15:07 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action9.2.
Curl

curl -X 'POST' \
  'http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/turns' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "action": "Arin carefully searches the room for anything unusual.",
  "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1"
}'
Request URL
http://127.0.0.1:8000/campaigns/85c0cd9f-c515-4821-b4c0-5542f08e95e5/turns
Server response
Code	201	
Response body
{
  "id": "f54eba75-c24a-4b0e-810d-dbdf4776a7c9",
  "sequence": 1,
  "player_action": "Arin carefully searches the room for anything unusual.",
  "narration": "At Roadside Inn, the world responds to your choice: Arin carefully searches the room for anything unusual. The next moment is yours to shape.",
  "actor_character_id": "2039690f-15ca-4154-8822-1fbd4190daf1",
  "dice_rolls": [],
  "state": {
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
              "source_ids": [
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
              "definition_key": null,
              "source_ids": [],
              "acquisition_event_ids": []
            },
            {
              "item_id": "dungeoneers_pack",
              "name": "Dungeoneer's Pack",
              "quantity": 1,
              "equipped_quantity": 0,
              "position": "carried",
              "definition_key": null,
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
              "source_ids": [
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
              "source_ids": [],
              "acquisition_event_ids": []
            },
            {
              "item_id": "greatsword",
              "name": "Greatsword",
              "quantity": 1,
              "equipped_quantity": 1,
              "position": "held",
              "definition_key": "srd-5.2.1:equipment.greatsword.state",
              "source_ids": [
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
              "source_ids": [
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
              "source_ids": [
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
              "definition_key": null,
              "source_ids": [],
              "acquisition_event_ids": []
            },
            {
              "item_id": "dungeoneers_pack",
              "name": "Dungeoneer's Pack",
              "quantity": 1,
              "equipped_quantity": 0,
              "position": "carried",
              "definition_key": null,
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
              "source_ids": [
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
              "source_ids": [],
              "acquisition_event_ids": []
            },
            {
              "item_id": "greatsword",
              "name": "Greatsword",
              "quantity": 1,
              "equipped_quantity": 0,
              "position": "carried",
              "definition_key": "srd-5.2.1:equipment.greatsword.state",
              "source_ids": [
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
              "source_ids": [
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
}
Response headers
 content-length: 47890 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:16:22 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 

Action10.
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
            "source_ids": [
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
            "definition_key": null,
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "dungeoneers_pack",
            "name": "Dungeoneer's Pack",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
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
            "source_ids": [
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
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "greatsword",
            "name": "Greatsword",
            "quantity": 1,
            "equipped_quantity": 1,
            "position": "held",
            "definition_key": "srd-5.2.1:equipment.greatsword.state",
            "source_ids": [
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
            "source_ids": [
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
            "source_ids": [
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
            "definition_key": null,
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "dungeoneers_pack",
            "name": "Dungeoneer's Pack",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": null,
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
            "source_ids": [
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
            "source_ids": [],
            "acquisition_event_ids": []
          },
          {
            "item_id": "greatsword",
            "name": "Greatsword",
            "quantity": 1,
            "equipped_quantity": 0,
            "position": "carried",
            "definition_key": "srd-5.2.1:equipment.greatsword.state",
            "source_ids": [
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
            "source_ids": [
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
 content-length: 47518 
 content-type: application/json 
 date: Mon,31 Aug 2026 11:18:43 GMT 
 private-token-client-replay: 241b088d-44ba-49c6-a62f-8c4a45804495 
 server: uvicorn 