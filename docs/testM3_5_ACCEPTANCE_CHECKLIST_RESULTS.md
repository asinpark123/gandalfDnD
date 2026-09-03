# In Setup stage

❯ python -m scripts.run_m3_5_owner_fixture | tee /tmp/gandalf-m3-5-owner-fixture.json
/Users/ahshin/Git/gandalfDnD/.venv/lib/python3.11/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa
{
  "fixture": "m3.5-branching-lantern-v1",
  "database": "gandalfdnd_dev",
  "external_provider_calls": 0,
  "signal_bridge": {
    "campaign_id": "9e08e898-0a9c-456b-9e4a-e59708dd8447",
    "character_ids": [
      "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
    ],
    "starting_npc_ids": [
      "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "9a172bfa-1de2-427d-bb7c-34caf7aa2444"
    ],
    "world": {
      "campaign_id": "9e08e898-0a9c-456b-9e4a-e59708dd8447",
      "world_revision": 20,
      "narrative_time_minutes": 90,
      "location": {
        "id": "aa96a085-ac59-49dd-ad9a-9d59d172c0c1",
        "name": "Old Tower",
        "description": "A ruined watchtower above the flooded road."
      },
      "scene": {
        "id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
        "sequence": 2,
        "title": "Old Tower",
        "summary": "A ruined watchtower above the flooded road.",
        "status": "active",
        "revision": 0,
        "created_at": "2026-09-03T22:28:09.060028+12:00"
      },
      "present_npcs": [
        {
          "id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
          "name": "Mira",
          "public_description": "A weary caravan guard.",
          "status": "active",
          "revision": 0,
          "created_at": "2026-09-03T22:28:01.078906+12:00"
        }
      ],
      "facts": [
        {
          "id": "a7699cd5-36fd-420f-88ae-f4a91d98eef3",
          "subject_npc_id": null,
          "fact_type": "clue",
          "value": "The Lantern Watch bell bears a concealed tunnel map.",
          "status": "current",
          "revision": 1,
          "created_at": "2026-09-03T22:28:02.259877+12:00"
        },
        {
          "id": "3df4e990-b388-4ccd-8abc-f3f4c1b1f0b0",
          "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
          "fact_type": "promise",
          "value": "Mira will guide the party to the Old Tower.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-03T22:28:03.429182+12:00"
        },
        {
          "id": "77ca9ff4-e4f5-4e0d-8766-9e9be7517917",
          "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
          "fact_type": "npc_attitude",
          "value": "friendly",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-03T22:28:03.429182+12:00"
        },
        {
          "id": "c9ec5740-a2a3-4dc9-8581-53270602cd5d",
          "subject_npc_id": null,
          "fact_type": "discovery",
          "value": "The party rescued the patrol across the signal bridge.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-03T22:28:19.650538+12:00"
        }
      ],
      "quests": [
        {
          "id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
          "quest_key": "missing_lantern_patrol",
          "title": "The Missing Lantern Patrol",
          "summary": "Find the patrol beyond the Old Tower.",
          "status": "active",
          "revision": 0,
          "objectives": [
            {
              "id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
              "objective_key": "find_patrol",
              "title": "Find the missing patrol",
              "description": null,
              "status": "completed",
              "position": 1,
              "revision": 2,
              "created_at": "2026-09-03T22:28:04.846992+12:00"
            }
          ],
          "created_at": "2026-09-03T22:28:04.846992+12:00"
        }
      ],
      "decisions": [
        {
          "id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
          "decision_key": "accept_lantern_patrol",
          "prompt": "Will the party search for the missing Lantern Watch patrol?",
          "status": "selected",
          "selected_option_key": "accept",
          "revision": 1,
          "options": [
            {
              "option_key": "accept",
              "label": "Accept the search",
              "description": null,
              "position": 1
            },
            {
              "option_key": "decline",
              "label": "Decline the search",
              "description": null,
              "position": 2
            }
          ],
          "created_at": "2026-09-03T22:28:06.162361+12:00"
        },
        {
          "id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
          "decision_key": "tower_route",
          "prompt": "Which route will the party use to reach the patrol?",
          "status": "selected",
          "selected_option_key": "signal_bridge",
          "revision": 1,
          "options": [
            {
              "option_key": "signal_bridge",
              "label": "Cross the signal bridge",
              "description": null,
              "position": 1
            },
            {
              "option_key": "flooded_tunnel",
              "label": "Enter the flooded tunnel",
              "description": null,
              "position": 2
            }
          ],
          "created_at": "2026-09-03T22:28:18.126792+12:00"
        }
      ],
      "factions": [
        {
          "id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
          "faction_key": "lantern_watch",
          "name": "Lantern Watch",
          "description": "Wardens of the northern road.",
          "status": "active",
          "revision": 0,
          "relationships": [
            {
              "id": "c965bf70-d493-480b-ab1d-b85175cfbd45",
              "relation_type": "attitude",
              "character_id": null,
              "npc_id": null,
              "value": "friendly",
              "revision": 0,
              "created_at": "2026-09-03T22:28:16.810867+12:00"
            },
            {
              "id": "354343dd-a483-48a7-8be2-9ff0f012bbe2",
              "relation_type": "membership",
              "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
              "npc_id": null,
              "value": "associate",
              "revision": 0,
              "created_at": "2026-09-03T22:28:16.810867+12:00"
            }
          ],
          "created_at": "2026-09-03T22:28:04.846992+12:00"
        }
      ]
    }
  },
  "flooded_tunnel": {
    "campaign_id": "ed97507a-b535-48b7-b874-75ceb402f29d",
    "character_ids": [
      "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec"
    ],
    "starting_npc_ids": [
      "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5"
    ],
    "world": {
      "campaign_id": "ed97507a-b535-48b7-b874-75ceb402f29d",
      "world_revision": 20,
      "narrative_time_minutes": 90,
      "location": {
        "id": "42fcd68a-21e9-4c21-a018-865dcb7bfd2e",
        "name": "Old Tower",
        "description": "A ruined watchtower above the flooded road."
      },
      "scene": {
        "id": "d6908560-9ac4-4ea1-95f5-5a28b20d7c6d",
        "sequence": 2,
        "title": "Old Tower",
        "summary": "A ruined watchtower above the flooded road.",
        "status": "active",
        "revision": 0,
        "created_at": "2026-09-03T22:28:29.095025+12:00"
      },
      "present_npcs": [
        {
          "id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
          "name": "Mira",
          "public_description": "A watchful innkeeper.",
          "status": "active",
          "revision": 0,
          "created_at": "2026-09-03T22:28:20.806270+12:00"
        }
      ],
      "facts": [
        {
          "id": "ab79d729-2a25-4e5b-a609-13947a025ab8",
          "subject_npc_id": null,
          "fact_type": "clue",
          "value": "The Lantern Watch bell bears a concealed tunnel map.",
          "status": "current",
          "revision": 1,
          "created_at": "2026-09-03T22:28:22.113377+12:00"
        },
        {
          "id": "188d91e0-574d-4789-a3ac-ab37c6a4f78e",
          "subject_npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
          "fact_type": "promise",
          "value": "Mira will guide the party to the Old Tower.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-03T22:28:23.319236+12:00"
        },
        {
          "id": "aa5275fe-aea6-4103-82cf-66f8fa317687",
          "subject_npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
          "fact_type": "npc_attitude",
          "value": "friendly",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-03T22:28:23.319236+12:00"
        },
        {
          "id": "0f4bf7dd-6fd5-4d0c-854a-2bd9a725ac11",
          "subject_npc_id": null,
          "fact_type": "discovery",
          "value": "The flooded tunnel collapsed before the patrol was found.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-03T22:28:39.938852+12:00"
        }
      ],
      "quests": [
        {
          "id": "0f7c4f7e-8029-458d-a6b4-4c6f05c301ad",
          "quest_key": "missing_lantern_patrol",
          "title": "The Missing Lantern Patrol",
          "summary": "Find the patrol beyond the Old Tower.",
          "status": "active",
          "revision": 0,
          "objectives": [
            {
              "id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
              "objective_key": "find_patrol",
              "title": "Find the missing patrol",
              "description": null,
              "status": "failed",
              "position": 1,
              "revision": 2,
              "created_at": "2026-09-03T22:28:24.760712+12:00"
            }
          ],
          "created_at": "2026-09-03T22:28:24.760712+12:00"
        }
      ],
      "decisions": [
        {
          "id": "1074e7a0-7482-4751-b68a-eb5b864ed451",
          "decision_key": "accept_lantern_patrol",
          "prompt": "Will the party search for the missing Lantern Watch patrol?",
          "status": "selected",
          "selected_option_key": "accept",
          "revision": 1,
          "options": [
            {
              "option_key": "accept",
              "label": "Accept the search",
              "description": null,
              "position": 1
            },
            {
              "option_key": "decline",
              "label": "Decline the search",
              "description": null,
              "position": 2
            }
          ],
          "created_at": "2026-09-03T22:28:26.243304+12:00"
        },
        {
          "id": "688bf454-fae0-4011-941e-63a928fb8b07",
          "decision_key": "tower_route",
          "prompt": "Which route will the party use to reach the patrol?",
          "status": "selected",
          "selected_option_key": "flooded_tunnel",
          "revision": 1,
          "options": [
            {
              "option_key": "signal_bridge",
              "label": "Cross the signal bridge",
              "description": null,
              "position": 1
            },
            {
              "option_key": "flooded_tunnel",
              "label": "Enter the flooded tunnel",
              "description": null,
              "position": 2
            }
          ],
          "created_at": "2026-09-03T22:28:38.320887+12:00"
        }
      ],
      "factions": [
        {
          "id": "4379fa95-bee9-4393-9668-9866226d3f83",
          "faction_key": "lantern_watch",
          "name": "Lantern Watch",
          "description": "Wardens of the northern road.",
          "status": "active",
          "revision": 0,
          "relationships": [
            {
              "id": "8bc88e94-8cd2-43b9-94aa-e13c69559669",
              "relation_type": "attitude",
              "character_id": null,
              "npc_id": null,
              "value": "friendly",
              "revision": 0,
              "created_at": "2026-09-03T22:28:36.836253+12:00"
            },
            {
              "id": "88a50085-01d2-45a7-93a3-9810b4fc6fda",
              "relation_type": "membership",
              "character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
              "npc_id": null,
              "value": "associate",
              "revision": 0,
              "created_at": "2026-09-03T22:28:36.836253+12:00"
            }
          ],
          "created_at": "2026-09-03T22:28:24.760712+12:00"
        }
      ]
    }
  }
}

> uvicorn app.api:app --reload
returned 'Application startup complete'

# Raw inputs and outputs of Actions

Action1.
Confirmed 
- "fixture": "m3.5-branching-lantern-v1"
- "external_provider_calls": 0
-  Both worlds show "world_revision": 20 and "narrative_time_minutes": 90 and "location": {... "name": "Old Tower", ....}

Action2.1.
Curl
curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/world' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/world
Server response
Code	200	
Response body
{
  "campaign_id": "9e08e898-0a9c-456b-9e4a-e59708dd8447",
  "world_revision": 20,
  "narrative_time_minutes": 90,
  "location": {
    "id": "aa96a085-ac59-49dd-ad9a-9d59d172c0c1",
    "name": "Old Tower",
    "description": "A ruined watchtower above the flooded road."
  },
  "scene": {
    "id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
    "sequence": 2,
    "title": "Old Tower",
    "summary": "A ruined watchtower above the flooded road.",
    "status": "active",
    "revision": 0,
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  "present_npcs": [
    {
      "id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "name": "Mira",
      "public_description": "A weary caravan guard.",
      "status": "active",
      "revision": 0,
      "created_at": "2026-09-03T22:28:01.078906+12:00"
    }
  ],
  "facts": [
    {
      "id": "a7699cd5-36fd-420f-88ae-f4a91d98eef3",
      "subject_npc_id": null,
      "fact_type": "clue",
      "value": "The Lantern Watch bell bears a concealed tunnel map.",
      "status": "current",
      "revision": 1,
      "created_at": "2026-09-03T22:28:02.259877+12:00"
    },
    {
      "id": "3df4e990-b388-4ccd-8abc-f3f4c1b1f0b0",
      "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "fact_type": "promise",
      "value": "Mira will guide the party to the Old Tower.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-03T22:28:03.429182+12:00"
    },
    {
      "id": "77ca9ff4-e4f5-4e0d-8766-9e9be7517917",
      "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "fact_type": "npc_attitude",
      "value": "friendly",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-03T22:28:03.429182+12:00"
    },
    {
      "id": "c9ec5740-a2a3-4dc9-8581-53270602cd5d",
      "subject_npc_id": null,
      "fact_type": "discovery",
      "value": "The party rescued the patrol across the signal bridge.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-03T22:28:19.650538+12:00"
    }
  ],
  "quests": [
    {
      "id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
      "quest_key": "missing_lantern_patrol",
      "title": "The Missing Lantern Patrol",
      "summary": "Find the patrol beyond the Old Tower.",
      "status": "active",
      "revision": 0,
      "objectives": [
        {
          "id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
          "objective_key": "find_patrol",
          "title": "Find the missing patrol",
          "description": null,
          "status": "completed",
          "position": 1,
          "revision": 2,
          "created_at": "2026-09-03T22:28:04.846992+12:00"
        }
      ],
      "created_at": "2026-09-03T22:28:04.846992+12:00"
    }
  ],
  "decisions": [
    {
      "id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
      "decision_key": "accept_lantern_patrol",
      "prompt": "Will the party search for the missing Lantern Watch patrol?",
      "status": "selected",
      "selected_option_key": "accept",
      "revision": 1,
      "options": [
        {
          "option_key": "accept",
          "label": "Accept the search",
          "description": null,
          "position": 1
        },
        {
          "option_key": "decline",
          "label": "Decline the search",
          "description": null,
          "position": 2
        }
      ],
      "created_at": "2026-09-03T22:28:06.162361+12:00"
    },
    {
      "id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
      "decision_key": "tower_route",
      "prompt": "Which route will the party use to reach the patrol?",
      "status": "selected",
      "selected_option_key": "signal_bridge",
      "revision": 1,
      "options": [
        {
          "option_key": "signal_bridge",
          "label": "Cross the signal bridge",
          "description": null,
          "position": 1
        },
        {
          "option_key": "flooded_tunnel",
          "label": "Enter the flooded tunnel",
          "description": null,
          "position": 2
        }
      ],
      "created_at": "2026-09-03T22:28:18.126792+12:00"
    }
  ],
  "factions": [
    {
      "id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
      "faction_key": "lantern_watch",
      "name": "Lantern Watch",
      "description": "Wardens of the northern road.",
      "status": "active",
      "revision": 0,
      "relationships": [
        {
          "id": "c965bf70-d493-480b-ab1d-b85175cfbd45",
          "relation_type": "attitude",
          "character_id": null,
          "npc_id": null,
          "value": "friendly",
          "revision": 0,
          "created_at": "2026-09-03T22:28:16.810867+12:00"
        },
        {
          "id": "354343dd-a483-48a7-8be2-9ff0f012bbe2",
          "relation_type": "membership",
          "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
          "npc_id": null,
          "value": "associate",
          "revision": 0,
          "created_at": "2026-09-03T22:28:16.810867+12:00"
        }
      ],
      "created_at": "2026-09-03T22:28:04.846992+12:00"
    }
  ]
}

Action2.2.
Curl
curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/ed97507a-b535-48b7-b874-75ceb402f29d/world' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/ed97507a-b535-48b7-b874-75ceb402f29d/world
Server response
Code	200	
Response body
{
  "campaign_id": "ed97507a-b535-48b7-b874-75ceb402f29d",
  "world_revision": 20,
  "narrative_time_minutes": 90,
  "location": {
    "id": "42fcd68a-21e9-4c21-a018-865dcb7bfd2e",
    "name": "Old Tower",
    "description": "A ruined watchtower above the flooded road."
  },
  "scene": {
    "id": "d6908560-9ac4-4ea1-95f5-5a28b20d7c6d",
    "sequence": 2,
    "title": "Old Tower",
    "summary": "A ruined watchtower above the flooded road.",
    "status": "active",
    "revision": 0,
    "created_at": "2026-09-03T22:28:29.095025+12:00"
  },
  "present_npcs": [
    {
      "id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "name": "Mira",
      "public_description": "A watchful innkeeper.",
      "status": "active",
      "revision": 0,
      "created_at": "2026-09-03T22:28:20.806270+12:00"
    }
  ],
  "facts": [
    {
      "id": "ab79d729-2a25-4e5b-a609-13947a025ab8",
      "subject_npc_id": null,
      "fact_type": "clue",
      "value": "The Lantern Watch bell bears a concealed tunnel map.",
      "status": "current",
      "revision": 1,
      "created_at": "2026-09-03T22:28:22.113377+12:00"
    },
    {
      "id": "188d91e0-574d-4789-a3ac-ab37c6a4f78e",
      "subject_npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "fact_type": "promise",
      "value": "Mira will guide the party to the Old Tower.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-03T22:28:23.319236+12:00"
    },
    {
      "id": "aa5275fe-aea6-4103-82cf-66f8fa317687",
      "subject_npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "fact_type": "npc_attitude",
      "value": "friendly",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-03T22:28:23.319236+12:00"
    },
    {
      "id": "0f4bf7dd-6fd5-4d0c-854a-2bd9a725ac11",
      "subject_npc_id": null,
      "fact_type": "discovery",
      "value": "The flooded tunnel collapsed before the patrol was found.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-03T22:28:39.938852+12:00"
    }
  ],
  "quests": [
    {
      "id": "0f7c4f7e-8029-458d-a6b4-4c6f05c301ad",
      "quest_key": "missing_lantern_patrol",
      "title": "The Missing Lantern Patrol",
      "summary": "Find the patrol beyond the Old Tower.",
      "status": "active",
      "revision": 0,
      "objectives": [
        {
          "id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
          "objective_key": "find_patrol",
          "title": "Find the missing patrol",
          "description": null,
          "status": "failed",
          "position": 1,
          "revision": 2,
          "created_at": "2026-09-03T22:28:24.760712+12:00"
        }
      ],
      "created_at": "2026-09-03T22:28:24.760712+12:00"
    }
  ],
  "decisions": [
    {
      "id": "1074e7a0-7482-4751-b68a-eb5b864ed451",
      "decision_key": "accept_lantern_patrol",
      "prompt": "Will the party search for the missing Lantern Watch patrol?",
      "status": "selected",
      "selected_option_key": "accept",
      "revision": 1,
      "options": [
        {
          "option_key": "accept",
          "label": "Accept the search",
          "description": null,
          "position": 1
        },
        {
          "option_key": "decline",
          "label": "Decline the search",
          "description": null,
          "position": 2
        }
      ],
      "created_at": "2026-09-03T22:28:26.243304+12:00"
    },
    {
      "id": "688bf454-fae0-4011-941e-63a928fb8b07",
      "decision_key": "tower_route",
      "prompt": "Which route will the party use to reach the patrol?",
      "status": "selected",
      "selected_option_key": "flooded_tunnel",
      "revision": 1,
      "options": [
        {
          "option_key": "signal_bridge",
          "label": "Cross the signal bridge",
          "description": null,
          "position": 1
        },
        {
          "option_key": "flooded_tunnel",
          "label": "Enter the flooded tunnel",
          "description": null,
          "position": 2
        }
      ],
      "created_at": "2026-09-03T22:28:38.320887+12:00"
    }
  ],
  "factions": [
    {
      "id": "4379fa95-bee9-4393-9668-9866226d3f83",
      "faction_key": "lantern_watch",
      "name": "Lantern Watch",
      "description": "Wardens of the northern road.",
      "status": "active",
      "revision": 0,
      "relationships": [
        {
          "id": "8bc88e94-8cd2-43b9-94aa-e13c69559669",
          "relation_type": "attitude",
          "character_id": null,
          "npc_id": null,
          "value": "friendly",
          "revision": 0,
          "created_at": "2026-09-03T22:28:36.836253+12:00"
        },
        {
          "id": "88a50085-01d2-45a7-93a3-9810b4fc6fda",
          "relation_type": "membership",
          "character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
          "npc_id": null,
          "value": "associate",
          "revision": 0,
          "created_at": "2026-09-03T22:28:36.836253+12:00"
        }
      ],
      "created_at": "2026-09-03T22:28:24.760712+12:00"
    }
  ]
}

Action3.
All confirmed true as results show above

Action4.
All confirmed true as results show above

Action5.
All confirmed true as results show above

Action6.
All confirmed true as results show above

Action6.
All confirmed true as results show above

Action7.
All confirmed true as results show above

Action8.1.
Curl

curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/events' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/events
Server response
Code	200	
Response body
[
  {
    "id": "5dd8b65d-b94e-4a7a-9e90-5181fb99c7e2",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 1,
    "event_type": "campaign_created",
    "visibility": "player",
    "payload": {
      "name": "M3 World Presence",
      "play_mode": "party_commander",
      "party_size": {
        "maximum": 4,
        "minimum": 2
      },
      "starting_location": "Lantern Hall",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "57f37eee-2bb0-48c1-9622-3a7b4ef66983",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 2,
    "event_type": "scene_opened",
    "visibility": "player",
    "payload": {
      "title": "A Rainy Arrival",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "location_id": "1c7c3c61-a415-4244-aeec-f20a6f8947d4",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "724fc2e5-9677-4405-b6cb-be55f1cb8bae",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 3,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Mira",
      "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "world_revision": 0,
      "public_description": "A watchful innkeeper."
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "d809dff3-6d24-48e3-b30e-0fbbf7065d0e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 4,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "49de7155-0a1f-4c6c-9207-e223b17626d0",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 5,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Mira",
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "world_revision": 0,
      "public_description": "A weary caravan guard."
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "6ba8476c-de4f-4751-b2b7-377a12bd26cf",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 6,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "c23934a1-cd85-494c-865c-78adc8042e79",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 7,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "Arin",
      "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "control_mode": "player",
      "party_position": 1,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.400195+12:00"
  },
  {
    "id": "125b8a5e-6a4e-446b-9c4d-36f5d49d4d11",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 8,
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
      "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "party_position": 1
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:01.596025+12:00"
  },
  {
    "id": "c6676a91-b40d-44ba-a3a9-741b9e268e53",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 9,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "Bryn",
      "character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "control_mode": "player",
      "party_position": 2,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.784154+12:00"
  },
  {
    "id": "a095382a-46fa-4931-8dfc-42a1031a5215",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 10,
    "event_type": "character_finalized",
    "visibility": "player",
    "payload": {
      "sheet": {
        "size": "medium",
        "level": 1,
        "max_hp": 12,
        "abilities": {
          "wisdom": {
            "base": 12,
            "final": 12,
            "modifier": 1,
            "background_increase": 0
          },
          "charisma": {
            "base": 15,
            "final": 15,
            "modifier": 2,
            "background_increase": 0
          },
          "strength": {
            "base": 8,
            "final": 10,
            "modifier": 0,
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
            "base": 10,
            "final": 10,
            "modifier": 0,
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
          "wisdom": 12,
          "charisma": 15,
          "strength": 8,
          "dexterity": 14,
          "constitution": 13,
          "intelligence": 10
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
      "character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "party_position": 2
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:01.854041+12:00"
  },
  {
    "id": "e9081c4f-cbff-4951-ad0d-bcc8a138d965",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 12,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin asks Mira about the missing lantern patrol.",
      "command_id": "22fc9ebe-3d16-46ca-a4c7-a53ab9dc23c8",
      "decision_id": null,
      "target_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:02.631423+12:00"
  },
  {
    "id": "a9754ceb-4d77-4b88-bbae-f7cd36652d20",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 13,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "000da80a-26c6-4fdc-8a09-8ecc44aa7be5",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 14,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "friendly",
      "fact_id": "77ca9ff4-e4f5-4e0d-8766-9e9be7517917",
      "fact_type": "npc_attitude",
      "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "world_revision": 2,
      "supersedes_fact_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "1723f9a5-313a-4f7b-a355-e1b46438e0be",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 15,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "Mira will guide the party to the Old Tower.",
      "fact_id": "3df4e990-b388-4ccd-8abc-f3f4c1b1f0b0",
      "fact_type": "promise",
      "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "world_revision": 3,
      "supersedes_fact_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "5247566f-c961-4fe0-ade9-fb759c30f3bb",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 16,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_attitude_set",
          "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
          "attitude": "friendly"
        },
        {
          "type": "promise_record",
          "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
          "promise": "Mira will guide the party to the Old Tower."
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "0432551a-3e2f-4962-9a33-c5b08b926f21",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 17,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Bryn listens to the Watch's request.",
      "command_id": "f7aecbe9-b66d-4d46-bc6e-316ca61d6c1e",
      "decision_id": null,
      "target_npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:03.954719+12:00"
  },
  {
    "id": "8911249e-acd8-4520-8cd0-bef08256df05",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 18,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "73249c49-77aa-40e0-af85-d79027379e59",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 19,
    "event_type": "quest_created",
    "visibility": "player",
    "payload": {
      "title": "The Missing Lantern Patrol",
      "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
      "quest_key": "missing_lantern_patrol",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "pending",
          "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
          "objective_key": "find_patrol"
        }
      ],
      "world_revision": 4
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "0ecb1f93-b958-4e3e-bf0e-0b50e80cf663",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 20,
    "event_type": "faction_created",
    "visibility": "player",
    "payload": {
      "name": "Lantern Watch",
      "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
      "description": "Wardens of the northern road.",
      "faction_key": "lantern_watch",
      "world_revision": 5
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "a2078e32-c08b-43d9-9669-fa9495ad57eb",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 21,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "quest_create",
          "title": "The Missing Lantern Patrol",
          "summary": "Find the patrol beyond the Old Tower.",
          "quest_key": "missing_lantern_patrol",
          "objectives": [
            {
              "title": "Find the missing patrol",
              "status": "pending",
              "description": null,
              "objective_key": "find_patrol"
            }
          ]
        },
        {
          "name": "Lantern Watch",
          "type": "faction_create",
          "description": "Wardens of the northern road.",
          "faction_key": "lantern_watch"
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "8aba1701-1abe-4bed-9e26-df5e0eb22847",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 22,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party considers the Watch's request.",
      "command_id": "31b79edf-2da6-44d9-b983-4bdaf9e800bb",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:05.428934+12:00"
  },
  {
    "id": "5547e919-9127-4e6b-91bf-4dd4731e7529",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 23,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.162361+12:00"
  },
  {
    "id": "195b5aa6-5855-4640-833f-8167d31c1fe3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 24,
    "event_type": "decision_opened",
    "visibility": "player",
    "payload": {
      "prompt": "Will the party search for the missing Lantern Watch patrol?",
      "options": [
        {
          "label": "Accept the search",
          "option_id": "8435b205-cf15-40e6-8e7a-48d41c505bc7",
          "option_key": "accept",
          "description": null
        },
        {
          "label": "Decline the search",
          "option_id": "a0c45d92-ae46-48e3-a632-1b3e64d5d02f",
          "option_key": "decline",
          "description": null
        }
      ],
      "decision_id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
      "decision_key": "accept_lantern_patrol",
      "world_revision": 6
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.162361+12:00"
  },
  {
    "id": "3c3ae957-d0ca-4789-98c4-f1850e11e679",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 25,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "decision_open",
          "prompt": "Will the party search for the missing Lantern Watch patrol?",
          "options": [
            {
              "label": "Accept the search",
              "option_key": "accept",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "active",
                  "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
                  "expected_revision": 0
                }
              ]
            },
            {
              "label": "Decline the search",
              "option_key": "decline",
              "description": null,
              "consequences": [
                {
                  "type": "transition_quest",
                  "status": "abandoned",
                  "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
                  "expected_revision": 0
                }
              ]
            }
          ],
          "decision_key": "accept_lantern_patrol"
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.162361+12:00"
  },
  {
    "id": "3c87dfca-31e3-4ccb-b789-58ce5c33d29a",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 26,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party accepts the Lantern Watch mission.",
      "command_id": "9d16328d-6665-42aa-b4cb-3b2432721b46",
      "decision_id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": "accept"
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.847667+12:00"
  },
  {
    "id": "021e397c-7baa-47c8-ae66-8e59abbcd3b6",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 27,
    "event_type": "decision_selected",
    "visibility": "player",
    "payload": {
      "option_id": "8435b205-cf15-40e6-8e7a-48d41c505bc7",
      "option_key": "accept",
      "decision_id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
      "decision_key": "accept_lantern_patrol",
      "world_revision": 7
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:07.756608+12:00"
  },
  {
    "id": "ceec02b0-37f3-4c98-a696-d5323b6e03bc",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 28,
    "event_type": "quest_objective_status_changed",
    "visibility": "player",
    "payload": {
      "status": "active",
      "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
      "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
      "objective_key": "find_patrol",
      "world_revision": 8,
      "previous_status": "pending",
      "objective_revision": 1
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:07.756608+12:00"
  },
  {
    "id": "969bc62a-1da0-4af6-8726-d5af5de6da57",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 29,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:07.756608+12:00"
  },
  {
    "id": "9574cf20-4ebb-4070-86e9-bc2e9250828d",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 30,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Bryn leads the party to the Old Tower.",
      "command_id": "7f6d6e2a-ed6a-495f-b16b-fd5ba7477453",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:08.185671+12:00"
  },
  {
    "id": "f3a2ffbd-02bd-4cdd-bdd0-758b938ba666",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 31,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "08c4de45-a601-4715-96f8-07324e57db1c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 32,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "e7cdb2bb-4099-4cf4-9d53-3dea9c7cbec2",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 33,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "a868f4ee-7f9a-4947-ab0d-286bf33bbb95",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 34,
    "event_type": "scene_closed",
    "visibility": "player",
    "payload": {
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "location_id": "1c7c3c61-a415-4244-aeec-f20a6f8947d4",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "56b624a8-0aff-4ae5-8016-3e55a43bbb1b",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 35,
    "event_type": "scene_opened",
    "visibility": "player",
    "payload": {
      "title": "Old Tower",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "location_id": "aa96a085-ac59-49dd-ad9a-9d59d172c0c1",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "e798f78e-2eae-4853-a032-d30d596b6f28",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 36,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "move_location",
          "description": "A ruined watchtower above the flooded road.",
          "location_name": "Old Tower"
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "fa0c156e-5081-4ff3-a8f6-0052317d1efb",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 37,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin finds a stranded Watch scout.",
      "command_id": "d70d2485-cb0d-4e79-927e-f7fa727fe68e",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.030907+12:00"
  },
  {
    "id": "a847c01d-bee5-4891-839d-425bfc0d0421",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 38,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "2ccf3629-32df-4ca9-880c-8a4428033b97",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 39,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Seren",
      "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "world_revision": 10,
      "public_description": "A Lantern Watch scout sheltering in the tower."
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "1ed96a7f-e056-4f78-bae5-d0c1e9a041dc",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 40,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "world_revision": 10
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "57660c5a-b11c-471d-b0cd-2e27cb940032",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 41,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "name": "Seren",
          "type": "npc_introduce",
          "public_description": "A Lantern Watch scout sheltering in the tower."
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "6a3f9b40-fd78-4ed4-954f-47fafa25e14f",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 42,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Seren leaves to warn the road patrol.",
      "command_id": "3d4c5b04-2e72-4cb5-a5c0-3fd2964e81fd",
      "decision_id": null,
      "target_npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:11.418289+12:00"
  },
  {
    "id": "77d0a8da-482c-4921-a37a-55ccf68d1ba0",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 43,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:12.414854+12:00"
  },
  {
    "id": "ce231e2b-63d8-4a81-963d-9c1e5f7d55b3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 44,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "world_revision": 11
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:12.414854+12:00"
  },
  {
    "id": "ffaf4ff6-c145-4b10-80ac-fb27726f5cfa",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 45,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_depart",
          "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9"
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:12.414854+12:00"
  },
  {
    "id": "7e972b16-7c0c-49ea-abe8-016ff60414cf",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 46,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The caravan guard Mira catches up at the Old Tower.",
      "command_id": "223500e5-cd54-4045-9997-3097974d1403",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:12.877942+12:00"
  },
  {
    "id": "41247052-0e17-4322-9f21-6328c2a951a7",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 47,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:13.844923+12:00"
  },
  {
    "id": "59454869-e745-49db-b75f-9a736c8a5f79",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 48,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "world_revision": 12
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:13.844923+12:00"
  },
  {
    "id": "f1d9f8c2-e212-45dc-8b58-8a8e259185b7",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 49,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_arrive",
          "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444"
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:13.844923+12:00"
  },
  {
    "id": "ccd900e1-7505-4862-9f38-7ec74dccc140",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 50,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin deciphers the concealed map on the bell.",
      "command_id": "3ac72c08-0493-46bb-9956-49dbc98772f0",
      "decision_id": null,
      "target_npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:14.396078+12:00"
  },
  {
    "id": "b9fbaee6-55ad-4226-bed6-767098d1f24c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 51,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:15.321159+12:00"
  },
  {
    "id": "70b601ba-f73b-4c1b-b4a0-d88e392aaaaf",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 52,
    "event_type": "world_fact_revealed",
    "visibility": "player",
    "payload": {
      "value": "The Lantern Watch bell bears a concealed tunnel map.",
      "fact_id": "a7699cd5-36fd-420f-88ae-f4a91d98eef3",
      "fact_type": "clue",
      "subject_npc_id": null,
      "world_revision": 13
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:15.321159+12:00"
  },
  {
    "id": "8fa5dc2a-c12b-4d46-ba02-cd060f86525e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 53,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "world_fact_reveal",
          "fact_id": "a7699cd5-36fd-420f-88ae-f4a91d98eef3",
          "expected_revision": 0
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:15.321159+12:00"
  },
  {
    "id": "fb5e1f37-e80b-4a7c-9fc8-ca14799713dd",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 54,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The Watch recognizes the party's help as the search continues.",
      "command_id": "d8437275-f0bf-410f-9ad9-91144a0bcf00",
      "decision_id": null,
      "target_npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:15.845497+12:00"
  },
  {
    "id": "26798a45-0a1a-43ec-97ce-357ce41eec2c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 55,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "1a58e106-fe82-48a5-ae78-3a4e30f9b360",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 56,
    "event_type": "faction_attitude_set",
    "visibility": "player",
    "payload": {
      "value": "friendly",
      "npc_id": null,
      "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
      "faction_key": "lantern_watch",
      "character_id": null,
      "relation_type": "attitude",
      "previous_value": null,
      "world_revision": 14,
      "relationship_id": "c965bf70-d493-480b-ab1d-b85175cfbd45",
      "relationship_revision": 0
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "3f303249-296b-4aed-9717-2be88d053cfe",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 57,
    "event_type": "faction_membership_set",
    "visibility": "player",
    "payload": {
      "value": "associate",
      "npc_id": null,
      "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
      "faction_key": "lantern_watch",
      "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "relation_type": "membership",
      "previous_value": null,
      "world_revision": 15,
      "relationship_id": "354343dd-a483-48a7-8be2-9ff0f012bbe2",
      "relationship_revision": 0
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "e784b29e-8168-4942-9ef3-02d02b30f639",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 58,
    "event_type": "narrative_time_advanced",
    "visibility": "player",
    "payload": {
      "reason": "The party follows the map through the flooded tower cellars.",
      "minutes": 90,
      "world_revision": 16,
      "previous_time_minutes": 0,
      "narrative_time_minutes": 90
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "9e8ef933-e625-4e81-9dd5-a5d9e277b2d3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 59,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "faction_attitude_set",
          "attitude": "friendly",
          "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
          "expected_revision": null
        },
        {
          "type": "faction_membership_set",
          "member_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
          "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
          "membership": "associate",
          "member_type": "character",
          "expected_revision": null
        },
        {
          "type": "narrative_time_advance",
          "reason": "The party follows the map through the flooded tower cellars.",
          "minutes": 90
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "f7bdcd75-4aad-4760-8209-f6c18c87a6ec",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 60,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party reaches two possible routes beneath the tower.",
      "command_id": "942d312d-4baf-4218-9030-b6dd45a87855",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:17.328846+12:00"
  },
  {
    "id": "13276359-fb8e-443e-bf78-df0040ffbcae",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 61,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.126792+12:00"
  },
  {
    "id": "3387f061-3c46-4f53-8c08-69816ae28f52",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 62,
    "event_type": "decision_opened",
    "visibility": "player",
    "payload": {
      "prompt": "Which route will the party use to reach the patrol?",
      "options": [
        {
          "label": "Cross the signal bridge",
          "option_id": "f2491eb1-cb43-491e-8539-6528f525393e",
          "option_key": "signal_bridge",
          "description": null
        },
        {
          "label": "Enter the flooded tunnel",
          "option_id": "c20f33f9-ccbb-4d50-b79f-3ecbb64c7fdf",
          "option_key": "flooded_tunnel",
          "description": null
        }
      ],
      "decision_id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
      "decision_key": "tower_route",
      "world_revision": 17
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.126792+12:00"
  },
  {
    "id": "429535e2-9d4d-4250-8088-4344f0da1760",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 63,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "decision_open",
          "prompt": "Which route will the party use to reach the patrol?",
          "options": [
            {
              "label": "Cross the signal bridge",
              "option_key": "signal_bridge",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "completed",
                  "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
                  "expected_revision": 1
                },
                {
                  "type": "record_fact",
                  "value": "The party rescued the patrol across the signal bridge.",
                  "fact_type": "discovery",
                  "subject_npc_id": null
                }
              ]
            },
            {
              "label": "Enter the flooded tunnel",
              "option_key": "flooded_tunnel",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "failed",
                  "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
                  "expected_revision": 1
                },
                {
                  "type": "record_fact",
                  "value": "The flooded tunnel collapsed before the patrol was found.",
                  "fact_type": "discovery",
                  "subject_npc_id": null
                }
              ]
            }
          ],
          "decision_key": "tower_route"
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.126792+12:00"
  },
  {
    "id": "25f88291-677e-4a92-9cbc-38c15ceea2af",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 64,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party chooses signal_bridge.",
      "command_id": "8ee2abe2-a1c3-49a8-997a-84263059a831",
      "decision_id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": "signal_bridge"
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.644714+12:00"
  },
  {
    "id": "43f30e28-01cf-448d-a0ec-7155a73397cd",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 65,
    "event_type": "decision_selected",
    "visibility": "player",
    "payload": {
      "option_id": "f2491eb1-cb43-491e-8539-6528f525393e",
      "option_key": "signal_bridge",
      "decision_id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
      "decision_key": "tower_route",
      "world_revision": 18
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  },
  {
    "id": "feeed207-7d51-4b9d-8142-8b8a5ab9684e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 66,
    "event_type": "quest_objective_status_changed",
    "visibility": "player",
    "payload": {
      "status": "completed",
      "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
      "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
      "objective_key": "find_patrol",
      "world_revision": 19,
      "previous_status": "active",
      "objective_revision": 2
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  },
  {
    "id": "db0cb682-ee15-43d7-9258-cd6c1dcd8526",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 67,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "The party rescued the patrol across the signal bridge.",
      "fact_id": "c9ec5740-a2a3-4dc9-8581-53270602cd5d",
      "fact_type": "discovery",
      "subject_npc_id": null,
      "world_revision": 20,
      "supersedes_fact_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  },
  {
    "id": "16be2313-6d39-4b26-932a-512ef30d2d2f",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 68,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  }
]

Action8.2.
Curl

curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/ed97507a-b535-48b7-b874-75ceb402f29d/events' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/ed97507a-b535-48b7-b874-75ceb402f29d/events
Server response
Code	200	
Response body
[
  {
    "id": "d5b6d7af-e049-4e8e-aca4-3ee459d675b0",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 1,
    "event_type": "campaign_created",
    "visibility": "player",
    "payload": {
      "name": "M3 World Presence",
      "play_mode": "party_commander",
      "party_size": {
        "maximum": 4,
        "minimum": 2
      },
      "starting_location": "Lantern Hall",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:20.806270+12:00"
  },
  {
    "id": "ded4862e-7dcf-4f3d-a612-552335fb81fe",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 2,
    "event_type": "scene_opened",
    "visibility": "player",
    "payload": {
      "title": "A Rainy Arrival",
      "scene_id": "dc25820d-7cdb-4511-98c0-b7588cedc938",
      "location_id": "a5a5c273-0c5f-43ff-8613-6ee154eb99d4",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:20.806270+12:00"
  },
  {
    "id": "af972901-1178-49bd-a335-fd8e2450f600",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 3,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Mira",
      "npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "world_revision": 0,
      "public_description": "A watchful innkeeper."
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:20.806270+12:00"
  },
  {
    "id": "e66e2037-75bb-4858-aa70-529469f47484",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 4,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "scene_id": "dc25820d-7cdb-4511-98c0-b7588cedc938",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:20.806270+12:00"
  },
  {
    "id": "b1e23a17-b1f7-4ad6-9200-7b8f673a2cc2",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 5,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Mira",
      "npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "world_revision": 0,
      "public_description": "A weary caravan guard."
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:20.806270+12:00"
  },
  {
    "id": "6bd74d87-d6d4-4691-9088-6d320d591a13",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 6,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "scene_id": "dc25820d-7cdb-4511-98c0-b7588cedc938",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:20.806270+12:00"
  },
  {
    "id": "050baa7e-01d2-43c5-83f0-4188fda2e3f5",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 7,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "Arin",
      "character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "control_mode": "player",
      "party_position": 1,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:21.166668+12:00"
  },
  {
    "id": "4f252666-84e4-4a70-a105-040afa9a4035",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 8,
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
      "character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "party_position": 1
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:21.242105+12:00"
  },
  {
    "id": "7f904f83-0e58-47f8-bb4d-0b241fa0268f",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 9,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "Bryn",
      "character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
      "control_mode": "player",
      "party_position": 2,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:21.546277+12:00"
  },
  {
    "id": "a80d6946-c5a5-43b4-80a4-f18336ed695c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 10,
    "event_type": "character_finalized",
    "visibility": "player",
    "payload": {
      "sheet": {
        "size": "medium",
        "level": 1,
        "max_hp": 12,
        "abilities": {
          "wisdom": {
            "base": 12,
            "final": 12,
            "modifier": 1,
            "background_increase": 0
          },
          "charisma": {
            "base": 15,
            "final": 15,
            "modifier": 2,
            "background_increase": 0
          },
          "strength": {
            "base": 8,
            "final": 10,
            "modifier": 0,
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
            "base": 10,
            "final": 10,
            "modifier": 0,
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
          "wisdom": 12,
          "charisma": 15,
          "strength": 8,
          "dexterity": 14,
          "constitution": 13,
          "intelligence": 10
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
      "character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
      "party_position": 2
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:21.641237+12:00"
  },
  {
    "id": "e7763e1b-99c0-4ba8-b411-9f0dfeb6f6fe",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 12,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin asks Mira about the missing lantern patrol.",
      "command_id": "78f612f9-11ad-468b-acd8-50f2e383811a",
      "decision_id": null,
      "target_npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:22.401110+12:00"
  },
  {
    "id": "c37a9384-60d8-4c72-ab54-46af6bbef3d3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 13,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:23.319236+12:00"
  },
  {
    "id": "0f30e4af-390a-4e3c-ba7c-121ae34c7e8e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 14,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "friendly",
      "fact_id": "aa5275fe-aea6-4103-82cf-66f8fa317687",
      "fact_type": "npc_attitude",
      "subject_npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "world_revision": 2,
      "supersedes_fact_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:23.319236+12:00"
  },
  {
    "id": "b088aaf5-e6ae-488e-9b6d-aae9764498f7",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 15,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "Mira will guide the party to the Old Tower.",
      "fact_id": "188d91e0-574d-4789-a3ac-ab37c6a4f78e",
      "fact_type": "promise",
      "subject_npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "world_revision": 3,
      "supersedes_fact_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:23.319236+12:00"
  },
  {
    "id": "b35fc6e0-d540-42d9-9591-447298aa018c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 16,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_attitude_set",
          "npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
          "attitude": "friendly"
        },
        {
          "type": "promise_record",
          "npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
          "promise": "Mira will guide the party to the Old Tower."
        }
      ],
      "affected_character_ids": [
        "b81ffaab-d451-4e1c-81a1-621dfad4e0d4"
      ]
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:23.319236+12:00"
  },
  {
    "id": "11851415-a9e8-46e1-ac53-9d6e08fa49ef",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 17,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Bryn listens to the Watch's request.",
      "command_id": "0842fa26-0745-4f72-9caf-abdb4dc9d3b0",
      "decision_id": null,
      "target_npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
      "decision_option_key": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:23.793676+12:00"
  },
  {
    "id": "6938dfc1-3afa-4ff7-9aaf-e91576557230",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 18,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:24.760712+12:00"
  },
  {
    "id": "4dc03ea0-af24-4372-ae7d-e97622685f59",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 19,
    "event_type": "quest_created",
    "visibility": "player",
    "payload": {
      "title": "The Missing Lantern Patrol",
      "quest_id": "0f7c4f7e-8029-458d-a6b4-4c6f05c301ad",
      "quest_key": "missing_lantern_patrol",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "pending",
          "objective_id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
          "objective_key": "find_patrol"
        }
      ],
      "world_revision": 4
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:24.760712+12:00"
  },
  {
    "id": "81d1efdc-fb5c-4fa7-b594-b5a848670901",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 20,
    "event_type": "faction_created",
    "visibility": "player",
    "payload": {
      "name": "Lantern Watch",
      "faction_id": "4379fa95-bee9-4393-9668-9866226d3f83",
      "description": "Wardens of the northern road.",
      "faction_key": "lantern_watch",
      "world_revision": 5
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:24.760712+12:00"
  },
  {
    "id": "ded6a225-ee98-4ac1-b308-e5d62396225a",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 21,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "quest_create",
          "title": "The Missing Lantern Patrol",
          "summary": "Find the patrol beyond the Old Tower.",
          "quest_key": "missing_lantern_patrol",
          "objectives": [
            {
              "title": "Find the missing patrol",
              "status": "pending",
              "description": null,
              "objective_key": "find_patrol"
            }
          ]
        },
        {
          "name": "Lantern Watch",
          "type": "faction_create",
          "description": "Wardens of the northern road.",
          "faction_key": "lantern_watch"
        }
      ],
      "affected_character_ids": [
        "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec"
      ]
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:24.760712+12:00"
  },
  {
    "id": "176b3068-2616-4a96-bfe8-398f8e2ff2a9",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 22,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party considers the Watch's request.",
      "command_id": "54195dd5-11b7-41bc-ab2b-76c8db9ee84c",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:25.314612+12:00"
  },
  {
    "id": "af2f90d9-62ec-4ad3-89cc-4117d7c7b8cc",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 23,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:26.243304+12:00"
  },
  {
    "id": "23d64238-2f36-40e9-8a92-e3d8f413b501",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 24,
    "event_type": "decision_opened",
    "visibility": "player",
    "payload": {
      "prompt": "Will the party search for the missing Lantern Watch patrol?",
      "options": [
        {
          "label": "Accept the search",
          "option_id": "7aac7ed4-0e11-4cb2-81d5-3332032181b0",
          "option_key": "accept",
          "description": null
        },
        {
          "label": "Decline the search",
          "option_id": "ed3a3985-3eb5-46f4-90fb-174512919e4e",
          "option_key": "decline",
          "description": null
        }
      ],
      "decision_id": "1074e7a0-7482-4751-b68a-eb5b864ed451",
      "decision_key": "accept_lantern_patrol",
      "world_revision": 6
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:26.243304+12:00"
  },
  {
    "id": "1e63fbc6-ea36-405f-98dc-ac0ecdfc1ffd",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 25,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "decision_open",
          "prompt": "Will the party search for the missing Lantern Watch patrol?",
          "options": [
            {
              "label": "Accept the search",
              "option_key": "accept",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "active",
                  "objective_id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
                  "expected_revision": 0
                }
              ]
            },
            {
              "label": "Decline the search",
              "option_key": "decline",
              "description": null,
              "consequences": [
                {
                  "type": "transition_quest",
                  "status": "abandoned",
                  "quest_id": "0f7c4f7e-8029-458d-a6b4-4c6f05c301ad",
                  "expected_revision": 0
                }
              ]
            }
          ],
          "decision_key": "accept_lantern_patrol"
        }
      ],
      "affected_character_ids": [
        "b81ffaab-d451-4e1c-81a1-621dfad4e0d4"
      ]
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:26.243304+12:00"
  },
  {
    "id": "c7b41573-edfc-442e-ba34-ce572642e4fd",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 26,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party accepts the Lantern Watch mission.",
      "command_id": "0cd364e6-66b7-4601-b73b-8ff71237a520",
      "decision_id": "1074e7a0-7482-4751-b68a-eb5b864ed451",
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": "accept"
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:26.767782+12:00"
  },
  {
    "id": "2436e4c0-9679-4a34-8c12-b4c437514ce0",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 27,
    "event_type": "decision_selected",
    "visibility": "player",
    "payload": {
      "option_id": "7aac7ed4-0e11-4cb2-81d5-3332032181b0",
      "option_key": "accept",
      "decision_id": "1074e7a0-7482-4751-b68a-eb5b864ed451",
      "decision_key": "accept_lantern_patrol",
      "world_revision": 7
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:27.813268+12:00"
  },
  {
    "id": "6e09c949-230e-49a1-b980-5e58383618b7",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 28,
    "event_type": "quest_objective_status_changed",
    "visibility": "player",
    "payload": {
      "status": "active",
      "quest_id": "0f7c4f7e-8029-458d-a6b4-4c6f05c301ad",
      "objective_id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
      "objective_key": "find_patrol",
      "world_revision": 8,
      "previous_status": "pending",
      "objective_revision": 1
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:27.813268+12:00"
  },
  {
    "id": "66e04940-e5b5-4a4b-b996-9217d91ce1be",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 29,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:27.813268+12:00"
  },
  {
    "id": "99ac196a-2202-40e7-91a6-a92e1e561eda",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 30,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Bryn leads the party to the Old Tower.",
      "command_id": "8271eade-61aa-4884-a045-2e284ec1d200",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
      "decision_option_key": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:28.141797+12:00"
  },
  {
    "id": "08b8ae89-58f5-4ce8-a9cf-7de7e7e8bae4",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 31,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:29.095025+12:00"
  },
  {
    "id": "67e07eda-b84d-4ccf-a291-7d9ac2950d50",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 32,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "2b761f5c-e7cf-4ad2-8151-96300a8d15b6",
      "scene_id": "dc25820d-7cdb-4511-98c0-b7588cedc938",
      "world_revision": 9
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:29.095025+12:00"
  },
  {
    "id": "a980407b-6cfa-43fa-87bb-6027cf7d63f8",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 33,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "scene_id": "dc25820d-7cdb-4511-98c0-b7588cedc938",
      "world_revision": 9
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:29.095025+12:00"
  },
  {
    "id": "32e4a512-3902-43e7-a680-3088acabc773",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 34,
    "event_type": "scene_closed",
    "visibility": "player",
    "payload": {
      "scene_id": "dc25820d-7cdb-4511-98c0-b7588cedc938",
      "location_id": "a5a5c273-0c5f-43ff-8613-6ee154eb99d4",
      "world_revision": 9
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:29.095025+12:00"
  },
  {
    "id": "5e3408f0-a1bf-46f2-a459-54069ead2ac4",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 35,
    "event_type": "scene_opened",
    "visibility": "player",
    "payload": {
      "title": "Old Tower",
      "scene_id": "d6908560-9ac4-4ea1-95f5-5a28b20d7c6d",
      "location_id": "42fcd68a-21e9-4c21-a018-865dcb7bfd2e",
      "world_revision": 9
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:29.095025+12:00"
  },
  {
    "id": "3b2ab500-d9de-4d5c-ba0a-670921dd2b87",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 36,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "move_location",
          "description": "A ruined watchtower above the flooded road.",
          "location_name": "Old Tower"
        }
      ],
      "affected_character_ids": [
        "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec"
      ]
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:29.095025+12:00"
  },
  {
    "id": "a649f087-68b4-42d5-8e0a-c38142b68e68",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 37,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin finds a stranded Watch scout.",
      "command_id": "2c9eac67-86f7-42b5-8149-efef42c15b0e",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:30.092170+12:00"
  },
  {
    "id": "6daa1e4d-4261-4f63-9c9f-d02cb527b14f",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 38,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:31.067698+12:00"
  },
  {
    "id": "71b3842d-9b45-423c-aa94-f771c464f7c9",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 39,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Seren",
      "npc_id": "0fadc97a-4801-4354-a78f-081f5cc007ec",
      "world_revision": 10,
      "public_description": "A Lantern Watch scout sheltering in the tower."
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:31.067698+12:00"
  },
  {
    "id": "7c592e63-7b64-4dff-ae00-19a029efbec6",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 40,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "0fadc97a-4801-4354-a78f-081f5cc007ec",
      "scene_id": "d6908560-9ac4-4ea1-95f5-5a28b20d7c6d",
      "world_revision": 10
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:31.067698+12:00"
  },
  {
    "id": "1a1e80c1-18e2-425d-9796-f641121a88ef",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 41,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "name": "Seren",
          "type": "npc_introduce",
          "public_description": "A Lantern Watch scout sheltering in the tower."
        }
      ],
      "affected_character_ids": [
        "b81ffaab-d451-4e1c-81a1-621dfad4e0d4"
      ]
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:31.067698+12:00"
  },
  {
    "id": "238fcba9-ed89-4c48-86eb-3405e684b1bc",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 42,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Seren leaves to warn the road patrol.",
      "command_id": "83e65040-829d-4dc2-8e81-6ad8a0f58969",
      "decision_id": null,
      "target_npc_id": "0fadc97a-4801-4354-a78f-081f5cc007ec",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
      "decision_option_key": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:31.644626+12:00"
  },
  {
    "id": "89307e61-0dd8-4611-ab85-9800f4d6f658",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 43,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:32.591085+12:00"
  },
  {
    "id": "756b9b38-61f4-44dc-bd68-05b00292e5b5",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 44,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "0fadc97a-4801-4354-a78f-081f5cc007ec",
      "scene_id": "d6908560-9ac4-4ea1-95f5-5a28b20d7c6d",
      "world_revision": 11
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:32.591085+12:00"
  },
  {
    "id": "ec944206-93b0-4d42-8a23-41c328608571",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 45,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_depart",
          "npc_id": "0fadc97a-4801-4354-a78f-081f5cc007ec"
        }
      ],
      "affected_character_ids": [
        "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec"
      ]
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:32.591085+12:00"
  },
  {
    "id": "c164e787-12ab-4c16-84f1-9c1c52ea5a70",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 46,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The caravan guard Mira catches up at the Old Tower.",
      "command_id": "1aa7a923-987b-4b29-a1ae-a4d13651dddb",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:32.920344+12:00"
  },
  {
    "id": "20af93a7-8865-4be2-85ba-4afa37514ef6",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 47,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:33.842898+12:00"
  },
  {
    "id": "17e49d16-051d-42f6-84b1-665257019284",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 48,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "scene_id": "d6908560-9ac4-4ea1-95f5-5a28b20d7c6d",
      "world_revision": 12
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:33.842898+12:00"
  },
  {
    "id": "d71f9244-0922-45cb-9416-f670b6b6a40e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 49,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_arrive",
          "npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5"
        }
      ],
      "affected_character_ids": [
        "b81ffaab-d451-4e1c-81a1-621dfad4e0d4"
      ]
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:33.842898+12:00"
  },
  {
    "id": "4019df15-f62b-4484-8da3-4aca30e1bd8d",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 50,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin deciphers the concealed map on the bell.",
      "command_id": "5fa47a2b-f604-4c94-aab4-081e7cb1dc8f",
      "decision_id": null,
      "target_npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:34.388563+12:00"
  },
  {
    "id": "56c6d4af-c7f6-4623-99aa-2786053fc2ad",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 51,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:35.336087+12:00"
  },
  {
    "id": "855a7b3e-4b45-4974-bc01-e17d8df32d8e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 52,
    "event_type": "world_fact_revealed",
    "visibility": "player",
    "payload": {
      "value": "The Lantern Watch bell bears a concealed tunnel map.",
      "fact_id": "ab79d729-2a25-4e5b-a609-13947a025ab8",
      "fact_type": "clue",
      "subject_npc_id": null,
      "world_revision": 13
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:35.336087+12:00"
  },
  {
    "id": "1a153fb9-14f7-4638-9347-89948b2e8c3b",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 53,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "world_fact_reveal",
          "fact_id": "ab79d729-2a25-4e5b-a609-13947a025ab8",
          "expected_revision": 0
        }
      ],
      "affected_character_ids": [
        "b81ffaab-d451-4e1c-81a1-621dfad4e0d4"
      ]
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:35.336087+12:00"
  },
  {
    "id": "25c74e42-9342-4c53-b383-66fc042c30de",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 54,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The Watch recognizes the party's help as the search continues.",
      "command_id": "f7f901ba-9813-4b66-a114-56f3b9cb647c",
      "decision_id": null,
      "target_npc_id": "7e5ea4d7-59c6-4786-9fbf-6718f92d99b5",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
      "decision_option_key": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:35.915412+12:00"
  },
  {
    "id": "8836c8b3-7833-41dd-98af-22c63a4b17f7",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 55,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:36.836253+12:00"
  },
  {
    "id": "cd6a29dc-a8f8-4a83-9492-0e57e7ea9b8b",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 56,
    "event_type": "faction_attitude_set",
    "visibility": "player",
    "payload": {
      "value": "friendly",
      "npc_id": null,
      "faction_id": "4379fa95-bee9-4393-9668-9866226d3f83",
      "faction_key": "lantern_watch",
      "character_id": null,
      "relation_type": "attitude",
      "previous_value": null,
      "world_revision": 14,
      "relationship_id": "8bc88e94-8cd2-43b9-94aa-e13c69559669",
      "relationship_revision": 0
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:36.836253+12:00"
  },
  {
    "id": "3546aa1d-259f-41d6-b5f6-870fe61c147b",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 57,
    "event_type": "faction_membership_set",
    "visibility": "player",
    "payload": {
      "value": "associate",
      "npc_id": null,
      "faction_id": "4379fa95-bee9-4393-9668-9866226d3f83",
      "faction_key": "lantern_watch",
      "character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "relation_type": "membership",
      "previous_value": null,
      "world_revision": 15,
      "relationship_id": "88a50085-01d2-45a7-93a3-9810b4fc6fda",
      "relationship_revision": 0
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:36.836253+12:00"
  },
  {
    "id": "d30346e9-9e67-4704-80e7-ce7ca9ee80ac",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 58,
    "event_type": "narrative_time_advanced",
    "visibility": "player",
    "payload": {
      "reason": "The party follows the map through the flooded tower cellars.",
      "minutes": 90,
      "world_revision": 16,
      "previous_time_minutes": 0,
      "narrative_time_minutes": 90
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:36.836253+12:00"
  },
  {
    "id": "12f94b1a-456d-46d1-995b-1121557b7bbe",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 59,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "faction_attitude_set",
          "attitude": "friendly",
          "faction_id": "4379fa95-bee9-4393-9668-9866226d3f83",
          "expected_revision": null
        },
        {
          "type": "faction_membership_set",
          "member_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
          "faction_id": "4379fa95-bee9-4393-9668-9866226d3f83",
          "membership": "associate",
          "member_type": "character",
          "expected_revision": null
        },
        {
          "type": "narrative_time_advance",
          "reason": "The party follows the map through the flooded tower cellars.",
          "minutes": 90
        }
      ],
      "affected_character_ids": [
        "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec"
      ]
    },
    "actor_character_id": "482ff648-67cd-4c9f-8bd3-32e5b4bbe8ec",
    "created_at": "2026-09-03T22:28:36.836253+12:00"
  },
  {
    "id": "e5c86656-d3da-4b39-bafe-1bc07f173955",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 60,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party reaches two possible routes beneath the tower.",
      "command_id": "fc1ffe66-a9d5-4327-ba8b-b2f6ed5ea8bc",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:37.385873+12:00"
  },
  {
    "id": "fdb6ed24-39ca-4040-87c1-d8aa012201f9",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 61,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:38.320887+12:00"
  },
  {
    "id": "5fb5cc3e-88a2-4082-b674-2d81149284b6",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 62,
    "event_type": "decision_opened",
    "visibility": "player",
    "payload": {
      "prompt": "Which route will the party use to reach the patrol?",
      "options": [
        {
          "label": "Cross the signal bridge",
          "option_id": "4ee1cb77-fc8f-4ce0-897a-a2f5c3a39812",
          "option_key": "signal_bridge",
          "description": null
        },
        {
          "label": "Enter the flooded tunnel",
          "option_id": "14030676-7d81-432a-b980-9905b891e630",
          "option_key": "flooded_tunnel",
          "description": null
        }
      ],
      "decision_id": "688bf454-fae0-4011-941e-63a928fb8b07",
      "decision_key": "tower_route",
      "world_revision": 17
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:38.320887+12:00"
  },
  {
    "id": "868cf086-508d-4e38-8fd7-1c6bd7e1e1e6",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 63,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "decision_open",
          "prompt": "Which route will the party use to reach the patrol?",
          "options": [
            {
              "label": "Cross the signal bridge",
              "option_key": "signal_bridge",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "completed",
                  "objective_id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
                  "expected_revision": 1
                },
                {
                  "type": "record_fact",
                  "value": "The party rescued the patrol across the signal bridge.",
                  "fact_type": "discovery",
                  "subject_npc_id": null
                }
              ]
            },
            {
              "label": "Enter the flooded tunnel",
              "option_key": "flooded_tunnel",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "failed",
                  "objective_id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
                  "expected_revision": 1
                },
                {
                  "type": "record_fact",
                  "value": "The flooded tunnel collapsed before the patrol was found.",
                  "fact_type": "discovery",
                  "subject_npc_id": null
                }
              ]
            }
          ],
          "decision_key": "tower_route"
        }
      ],
      "affected_character_ids": [
        "b81ffaab-d451-4e1c-81a1-621dfad4e0d4"
      ]
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:38.320887+12:00"
  },
  {
    "id": "165f41e3-3695-4ce0-87f0-2b11d2ce2886",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 64,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party chooses flooded_tunnel.",
      "command_id": "929166b4-7232-4ad3-bbfa-a4d56928bffd",
      "decision_id": "688bf454-fae0-4011-941e-63a928fb8b07",
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
      "decision_option_key": "flooded_tunnel"
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:38.886238+12:00"
  },
  {
    "id": "f0b55e09-e7d0-4e12-baf9-15d0093ac3a3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 65,
    "event_type": "decision_selected",
    "visibility": "player",
    "payload": {
      "option_id": "14030676-7d81-432a-b980-9905b891e630",
      "option_key": "flooded_tunnel",
      "decision_id": "688bf454-fae0-4011-941e-63a928fb8b07",
      "decision_key": "tower_route",
      "world_revision": 18
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:39.938852+12:00"
  },
  {
    "id": "f91896d4-3c8d-4c07-b382-94d316d0db5c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 66,
    "event_type": "quest_objective_status_changed",
    "visibility": "player",
    "payload": {
      "status": "failed",
      "quest_id": "0f7c4f7e-8029-458d-a6b4-4c6f05c301ad",
      "objective_id": "2065ba8d-dd04-4d70-b552-0e5d7c87e550",
      "objective_key": "find_patrol",
      "world_revision": 19,
      "previous_status": "active",
      "objective_revision": 2
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:39.938852+12:00"
  },
  {
    "id": "567e90de-87c7-41cc-96a7-3963ce83944f",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 67,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "The flooded tunnel collapsed before the patrol was found.",
      "fact_id": "0f4bf7dd-6fd5-4d0c-854a-2bd9a725ac11",
      "fact_type": "discovery",
      "subject_npc_id": null,
      "world_revision": 20,
      "supersedes_fact_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:39.938852+12:00"
  },
  {
    "id": "6e5be658-c9b8-457f-9c37-20ec42ecc3f6",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 68,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "b81ffaab-d451-4e1c-81a1-621dfad4e0d4",
    "created_at": "2026-09-03T22:28:39.938852+12:00"
  }
]

Action9.1.
Curl
curl -X 'POST' \
  'http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/turn-executions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "command_id": "6a701e20-84ae-4a8f-9e72-7254608c2db5",
  "action": "Ask the absent innkeeper Mira for help",
  "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
  "target_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
  "decision_id": null,
  "decision_option_key": null
}'
Request URL
http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/turn-executions
Server response
Code	409
Undocumented
Error: Conflict

Response body
{
  "detail": "Target NPC is not present in the current scene"
}

Action9.2.
Curl

curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/events' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/9e08e898-0a9c-456b-9e4a-e59708dd8447/events
Server response
Code	Details
200	
Response body
Download
[
  {
    "id": "5dd8b65d-b94e-4a7a-9e90-5181fb99c7e2",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 1,
    "event_type": "campaign_created",
    "visibility": "player",
    "payload": {
      "name": "M3 World Presence",
      "play_mode": "party_commander",
      "party_size": {
        "maximum": 4,
        "minimum": 2
      },
      "starting_location": "Lantern Hall",
      "ruleset_release_id": "srd-5.2.1",
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "57f37eee-2bb0-48c1-9622-3a7b4ef66983",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 2,
    "event_type": "scene_opened",
    "visibility": "player",
    "payload": {
      "title": "A Rainy Arrival",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "location_id": "1c7c3c61-a415-4244-aeec-f20a6f8947d4",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "724fc2e5-9677-4405-b6cb-be55f1cb8bae",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 3,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Mira",
      "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "world_revision": 0,
      "public_description": "A watchful innkeeper."
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "d809dff3-6d24-48e3-b30e-0fbbf7065d0e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 4,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "49de7155-0a1f-4c6c-9207-e223b17626d0",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 5,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Mira",
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "world_revision": 0,
      "public_description": "A weary caravan guard."
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "6ba8476c-de4f-4751-b2b7-377a12bd26cf",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 6,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 0
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.078906+12:00"
  },
  {
    "id": "c23934a1-cd85-494c-865c-78adc8042e79",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 7,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "Arin",
      "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "control_mode": "player",
      "party_position": 1,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.400195+12:00"
  },
  {
    "id": "125b8a5e-6a4e-446b-9c4d-36f5d49d4d11",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 8,
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
      "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "party_position": 1
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:01.596025+12:00"
  },
  {
    "id": "c6676a91-b40d-44ba-a3a9-741b9e268e53",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 9,
    "event_type": "character_draft_created",
    "visibility": "player",
    "payload": {
      "name": "Bryn",
      "character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "control_mode": "player",
      "party_position": 2,
      "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1"
    },
    "actor_character_id": null,
    "created_at": "2026-09-03T22:28:01.784154+12:00"
  },
  {
    "id": "a095382a-46fa-4931-8dfc-42a1031a5215",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 10,
    "event_type": "character_finalized",
    "visibility": "player",
    "payload": {
      "sheet": {
        "size": "medium",
        "level": 1,
        "max_hp": 12,
        "abilities": {
          "wisdom": {
            "base": 12,
            "final": 12,
            "modifier": 1,
            "background_increase": 0
          },
          "charisma": {
            "base": 15,
            "final": 15,
            "modifier": 2,
            "background_increase": 0
          },
          "strength": {
            "base": 8,
            "final": 10,
            "modifier": 0,
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
            "base": 10,
            "final": 10,
            "modifier": 0,
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
          "wisdom": 12,
          "charisma": 15,
          "strength": 8,
          "dexterity": 14,
          "constitution": 13,
          "intelligence": 10
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
      "character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "party_position": 2
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:01.854041+12:00"
  },
  {
    "id": "e9081c4f-cbff-4951-ad0d-bcc8a138d965",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 12,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin asks Mira about the missing lantern patrol.",
      "command_id": "22fc9ebe-3d16-46ca-a4c7-a53ab9dc23c8",
      "decision_id": null,
      "target_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:02.631423+12:00"
  },
  {
    "id": "a9754ceb-4d77-4b88-bbae-f7cd36652d20",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 13,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "000da80a-26c6-4fdc-8a09-8ecc44aa7be5",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 14,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "friendly",
      "fact_id": "77ca9ff4-e4f5-4e0d-8766-9e9be7517917",
      "fact_type": "npc_attitude",
      "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "world_revision": 2,
      "supersedes_fact_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "1723f9a5-313a-4f7b-a355-e1b46438e0be",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 15,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "Mira will guide the party to the Old Tower.",
      "fact_id": "3df4e990-b388-4ccd-8abc-f3f4c1b1f0b0",
      "fact_type": "promise",
      "subject_npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "world_revision": 3,
      "supersedes_fact_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "5247566f-c961-4fe0-ade9-fb759c30f3bb",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 16,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_attitude_set",
          "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
          "attitude": "friendly"
        },
        {
          "type": "promise_record",
          "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
          "promise": "Mira will guide the party to the Old Tower."
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:03.429182+12:00"
  },
  {
    "id": "0432551a-3e2f-4962-9a33-c5b08b926f21",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 17,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Bryn listens to the Watch's request.",
      "command_id": "f7aecbe9-b66d-4d46-bc6e-316ca61d6c1e",
      "decision_id": null,
      "target_npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:03.954719+12:00"
  },
  {
    "id": "8911249e-acd8-4520-8cd0-bef08256df05",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 18,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "73249c49-77aa-40e0-af85-d79027379e59",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 19,
    "event_type": "quest_created",
    "visibility": "player",
    "payload": {
      "title": "The Missing Lantern Patrol",
      "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
      "quest_key": "missing_lantern_patrol",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "pending",
          "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
          "objective_key": "find_patrol"
        }
      ],
      "world_revision": 4
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "0ecb1f93-b958-4e3e-bf0e-0b50e80cf663",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 20,
    "event_type": "faction_created",
    "visibility": "player",
    "payload": {
      "name": "Lantern Watch",
      "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
      "description": "Wardens of the northern road.",
      "faction_key": "lantern_watch",
      "world_revision": 5
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "a2078e32-c08b-43d9-9669-fa9495ad57eb",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 21,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "quest_create",
          "title": "The Missing Lantern Patrol",
          "summary": "Find the patrol beyond the Old Tower.",
          "quest_key": "missing_lantern_patrol",
          "objectives": [
            {
              "title": "Find the missing patrol",
              "status": "pending",
              "description": null,
              "objective_key": "find_patrol"
            }
          ]
        },
        {
          "name": "Lantern Watch",
          "type": "faction_create",
          "description": "Wardens of the northern road.",
          "faction_key": "lantern_watch"
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:04.846992+12:00"
  },
  {
    "id": "8aba1701-1abe-4bed-9e26-df5e0eb22847",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 22,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party considers the Watch's request.",
      "command_id": "31b79edf-2da6-44d9-b983-4bdaf9e800bb",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:05.428934+12:00"
  },
  {
    "id": "5547e919-9127-4e6b-91bf-4dd4731e7529",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 23,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.162361+12:00"
  },
  {
    "id": "195b5aa6-5855-4640-833f-8167d31c1fe3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 24,
    "event_type": "decision_opened",
    "visibility": "player",
    "payload": {
      "prompt": "Will the party search for the missing Lantern Watch patrol?",
      "options": [
        {
          "label": "Accept the search",
          "option_id": "8435b205-cf15-40e6-8e7a-48d41c505bc7",
          "option_key": "accept",
          "description": null
        },
        {
          "label": "Decline the search",
          "option_id": "a0c45d92-ae46-48e3-a632-1b3e64d5d02f",
          "option_key": "decline",
          "description": null
        }
      ],
      "decision_id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
      "decision_key": "accept_lantern_patrol",
      "world_revision": 6
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.162361+12:00"
  },
  {
    "id": "3c3ae957-d0ca-4789-98c4-f1850e11e679",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 25,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "decision_open",
          "prompt": "Will the party search for the missing Lantern Watch patrol?",
          "options": [
            {
              "label": "Accept the search",
              "option_key": "accept",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "active",
                  "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
                  "expected_revision": 0
                }
              ]
            },
            {
              "label": "Decline the search",
              "option_key": "decline",
              "description": null,
              "consequences": [
                {
                  "type": "transition_quest",
                  "status": "abandoned",
                  "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
                  "expected_revision": 0
                }
              ]
            }
          ],
          "decision_key": "accept_lantern_patrol"
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.162361+12:00"
  },
  {
    "id": "3c87dfca-31e3-4ccb-b789-58ce5c33d29a",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 26,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party accepts the Lantern Watch mission.",
      "command_id": "9d16328d-6665-42aa-b4cb-3b2432721b46",
      "decision_id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": "accept"
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:06.847667+12:00"
  },
  {
    "id": "021e397c-7baa-47c8-ae66-8e59abbcd3b6",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 27,
    "event_type": "decision_selected",
    "visibility": "player",
    "payload": {
      "option_id": "8435b205-cf15-40e6-8e7a-48d41c505bc7",
      "option_key": "accept",
      "decision_id": "9c576e72-07f9-4d23-8dac-d9cb2dd3f315",
      "decision_key": "accept_lantern_patrol",
      "world_revision": 7
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:07.756608+12:00"
  },
  {
    "id": "ceec02b0-37f3-4c98-a696-d5323b6e03bc",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 28,
    "event_type": "quest_objective_status_changed",
    "visibility": "player",
    "payload": {
      "status": "active",
      "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
      "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
      "objective_key": "find_patrol",
      "world_revision": 8,
      "previous_status": "pending",
      "objective_revision": 1
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:07.756608+12:00"
  },
  {
    "id": "969bc62a-1da0-4af6-8726-d5af5de6da57",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 29,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:07.756608+12:00"
  },
  {
    "id": "9574cf20-4ebb-4070-86e9-bc2e9250828d",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 30,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Bryn leads the party to the Old Tower.",
      "command_id": "7f6d6e2a-ed6a-495f-b16b-fd5ba7477453",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:08.185671+12:00"
  },
  {
    "id": "f3a2ffbd-02bd-4cdd-bdd0-758b938ba666",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 31,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "08c4de45-a601-4715-96f8-07324e57db1c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 32,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "0997562f-5226-4cd5-a8dc-a5e69928bae1",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "e7cdb2bb-4099-4cf4-9d53-3dea9c7cbec2",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 33,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "a868f4ee-7f9a-4947-ab0d-286bf33bbb95",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 34,
    "event_type": "scene_closed",
    "visibility": "player",
    "payload": {
      "scene_id": "b6e3ee4a-a91c-46f4-912b-96da057731b2",
      "location_id": "1c7c3c61-a415-4244-aeec-f20a6f8947d4",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "56b624a8-0aff-4ae5-8016-3e55a43bbb1b",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 35,
    "event_type": "scene_opened",
    "visibility": "player",
    "payload": {
      "title": "Old Tower",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "location_id": "aa96a085-ac59-49dd-ad9a-9d59d172c0c1",
      "world_revision": 9
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "e798f78e-2eae-4853-a032-d30d596b6f28",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 36,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "move_location",
          "description": "A ruined watchtower above the flooded road.",
          "location_name": "Old Tower"
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:09.060028+12:00"
  },
  {
    "id": "fa0c156e-5081-4ff3-a8f6-0052317d1efb",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 37,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin finds a stranded Watch scout.",
      "command_id": "d70d2485-cb0d-4e79-927e-f7fa727fe68e",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.030907+12:00"
  },
  {
    "id": "a847c01d-bee5-4891-839d-425bfc0d0421",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 38,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "2ccf3629-32df-4ca9-880c-8a4428033b97",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 39,
    "event_type": "npc_introduced",
    "visibility": "player",
    "payload": {
      "name": "Seren",
      "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "world_revision": 10,
      "public_description": "A Lantern Watch scout sheltering in the tower."
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "1ed96a7f-e056-4f78-bae5-d0c1e9a041dc",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 40,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "world_revision": 10
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "57660c5a-b11c-471d-b0cd-2e27cb940032",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 41,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "name": "Seren",
          "type": "npc_introduce",
          "public_description": "A Lantern Watch scout sheltering in the tower."
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:10.842573+12:00"
  },
  {
    "id": "6a3f9b40-fd78-4ed4-954f-47fafa25e14f",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 42,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Seren leaves to warn the road patrol.",
      "command_id": "3d4c5b04-2e72-4cb5-a5c0-3fd2964e81fd",
      "decision_id": null,
      "target_npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:11.418289+12:00"
  },
  {
    "id": "77d0a8da-482c-4921-a37a-55ccf68d1ba0",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 43,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:12.414854+12:00"
  },
  {
    "id": "ce231e2b-63d8-4a81-963d-9c1e5f7d55b3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 44,
    "event_type": "npc_departed",
    "visibility": "player",
    "payload": {
      "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "world_revision": 11
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:12.414854+12:00"
  },
  {
    "id": "ffaf4ff6-c145-4b10-80ac-fb27726f5cfa",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 45,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_depart",
          "npc_id": "e215638c-58c2-4d9c-acca-c3dbd6488df9"
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:12.414854+12:00"
  },
  {
    "id": "7e972b16-7c0c-49ea-abe8-016ff60414cf",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 46,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The caravan guard Mira catches up at the Old Tower.",
      "command_id": "223500e5-cd54-4045-9997-3097974d1403",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:12.877942+12:00"
  },
  {
    "id": "41247052-0e17-4322-9f21-6328c2a951a7",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 47,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:13.844923+12:00"
  },
  {
    "id": "59454869-e745-49db-b75f-9a736c8a5f79",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 48,
    "event_type": "npc_arrived",
    "visibility": "player",
    "payload": {
      "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "scene_id": "6671a6d8-61bf-4e1a-a1e2-e24451f2cc90",
      "world_revision": 12
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:13.844923+12:00"
  },
  {
    "id": "f1d9f8c2-e212-45dc-8b58-8a8e259185b7",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 49,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "npc_arrive",
          "npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444"
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:13.844923+12:00"
  },
  {
    "id": "ccd900e1-7505-4862-9f38-7ec74dccc140",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 50,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "Arin deciphers the concealed map on the bell.",
      "command_id": "3ac72c08-0493-46bb-9956-49dbc98772f0",
      "decision_id": null,
      "target_npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:14.396078+12:00"
  },
  {
    "id": "b9fbaee6-55ad-4226-bed6-767098d1f24c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 51,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:15.321159+12:00"
  },
  {
    "id": "70b601ba-f73b-4c1b-b4a0-d88e392aaaaf",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 52,
    "event_type": "world_fact_revealed",
    "visibility": "player",
    "payload": {
      "value": "The Lantern Watch bell bears a concealed tunnel map.",
      "fact_id": "a7699cd5-36fd-420f-88ae-f4a91d98eef3",
      "fact_type": "clue",
      "subject_npc_id": null,
      "world_revision": 13
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:15.321159+12:00"
  },
  {
    "id": "8fa5dc2a-c12b-4d46-ba02-cd060f86525e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 53,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "world_fact_reveal",
          "fact_id": "a7699cd5-36fd-420f-88ae-f4a91d98eef3",
          "expected_revision": 0
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:15.321159+12:00"
  },
  {
    "id": "fb5e1f37-e80b-4a7c-9fc8-ca14799713dd",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 54,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The Watch recognizes the party's help as the search continues.",
      "command_id": "d8437275-f0bf-410f-9ad9-91144a0bcf00",
      "decision_id": null,
      "target_npc_id": "9a172bfa-1de2-427d-bb7c-34caf7aa2444",
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
      "decision_option_key": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:15.845497+12:00"
  },
  {
    "id": "26798a45-0a1a-43ec-97ce-357ce41eec2c",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 55,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "1a58e106-fe82-48a5-ae78-3a4e30f9b360",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 56,
    "event_type": "faction_attitude_set",
    "visibility": "player",
    "payload": {
      "value": "friendly",
      "npc_id": null,
      "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
      "faction_key": "lantern_watch",
      "character_id": null,
      "relation_type": "attitude",
      "previous_value": null,
      "world_revision": 14,
      "relationship_id": "c965bf70-d493-480b-ab1d-b85175cfbd45",
      "relationship_revision": 0
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "3f303249-296b-4aed-9717-2be88d053cfe",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 57,
    "event_type": "faction_membership_set",
    "visibility": "player",
    "payload": {
      "value": "associate",
      "npc_id": null,
      "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
      "faction_key": "lantern_watch",
      "character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "relation_type": "membership",
      "previous_value": null,
      "world_revision": 15,
      "relationship_id": "354343dd-a483-48a7-8be2-9ff0f012bbe2",
      "relationship_revision": 0
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "e784b29e-8168-4942-9ef3-02d02b30f639",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 58,
    "event_type": "narrative_time_advanced",
    "visibility": "player",
    "payload": {
      "reason": "The party follows the map through the flooded tower cellars.",
      "minutes": 90,
      "world_revision": 16,
      "previous_time_minutes": 0,
      "narrative_time_minutes": 90
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "9e8ef933-e625-4e81-9dd5-a5d9e277b2d3",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 59,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "faction_attitude_set",
          "attitude": "friendly",
          "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
          "expected_revision": null
        },
        {
          "type": "faction_membership_set",
          "member_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
          "faction_id": "0bce7187-19ea-4cb0-8f9b-2f3081e569d0",
          "membership": "associate",
          "member_type": "character",
          "expected_revision": null
        },
        {
          "type": "narrative_time_advance",
          "reason": "The party follows the map through the flooded tower cellars.",
          "minutes": 90
        }
      ],
      "affected_character_ids": [
        "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3"
      ]
    },
    "actor_character_id": "bacff5a5-afca-485d-bb75-ff4fd6e2ceb3",
    "created_at": "2026-09-03T22:28:16.810867+12:00"
  },
  {
    "id": "f7bdcd75-4aad-4760-8209-f6c18c87a6ec",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 60,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party reaches two possible routes beneath the tower.",
      "command_id": "942d312d-4baf-4218-9030-b6dd45a87855",
      "decision_id": null,
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:17.328846+12:00"
  },
  {
    "id": "13276359-fb8e-443e-bf78-df0040ffbcae",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 61,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.126792+12:00"
  },
  {
    "id": "3387f061-3c46-4f53-8c08-69816ae28f52",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 62,
    "event_type": "decision_opened",
    "visibility": "player",
    "payload": {
      "prompt": "Which route will the party use to reach the patrol?",
      "options": [
        {
          "label": "Cross the signal bridge",
          "option_id": "f2491eb1-cb43-491e-8539-6528f525393e",
          "option_key": "signal_bridge",
          "description": null
        },
        {
          "label": "Enter the flooded tunnel",
          "option_id": "c20f33f9-ccbb-4d50-b79f-3ecbb64c7fdf",
          "option_key": "flooded_tunnel",
          "description": null
        }
      ],
      "decision_id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
      "decision_key": "tower_route",
      "world_revision": 17
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.126792+12:00"
  },
  {
    "id": "429535e2-9d4d-4250-8088-4344f0da1760",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 63,
    "event_type": "state_changed",
    "visibility": "player",
    "payload": {
      "changes": [
        {
          "type": "decision_open",
          "prompt": "Which route will the party use to reach the patrol?",
          "options": [
            {
              "label": "Cross the signal bridge",
              "option_key": "signal_bridge",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "completed",
                  "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
                  "expected_revision": 1
                },
                {
                  "type": "record_fact",
                  "value": "The party rescued the patrol across the signal bridge.",
                  "fact_type": "discovery",
                  "subject_npc_id": null
                }
              ]
            },
            {
              "label": "Enter the flooded tunnel",
              "option_key": "flooded_tunnel",
              "description": null,
              "consequences": [
                {
                  "type": "transition_objective",
                  "status": "failed",
                  "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
                  "expected_revision": 1
                },
                {
                  "type": "record_fact",
                  "value": "The flooded tunnel collapsed before the patrol was found.",
                  "fact_type": "discovery",
                  "subject_npc_id": null
                }
              ]
            }
          ],
          "decision_key": "tower_route"
        }
      ],
      "affected_character_ids": [
        "f570c49a-6075-4347-bf4d-5a5e796bcc1c"
      ]
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.126792+12:00"
  },
  {
    "id": "25f88291-677e-4a92-9cbc-38c15ceea2af",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 64,
    "event_type": "player_action",
    "visibility": "player",
    "payload": {
      "action": "The party chooses signal_bridge.",
      "command_id": "8ee2abe2-a1c3-49a8-997a-84263059a831",
      "decision_id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
      "target_npc_id": null,
      "workflow_version": "two-stage-turn-1.0.0",
      "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
      "decision_option_key": "signal_bridge"
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:18.644714+12:00"
  },
  {
    "id": "43f30e28-01cf-448d-a0ec-7155a73397cd",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 65,
    "event_type": "decision_selected",
    "visibility": "player",
    "payload": {
      "option_id": "f2491eb1-cb43-491e-8539-6528f525393e",
      "option_key": "signal_bridge",
      "decision_id": "4e92bff8-a70e-4544-a418-ed5fd5ba8546",
      "decision_key": "tower_route",
      "world_revision": 18
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  },
  {
    "id": "feeed207-7d51-4b9d-8142-8b8a5ab9684e",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 66,
    "event_type": "quest_objective_status_changed",
    "visibility": "player",
    "payload": {
      "status": "completed",
      "quest_id": "04bc8387-cf50-4046-8d48-d1845b30b2e0",
      "objective_id": "a9ebb1f4-bbaf-4adc-aecc-c4b712f75e53",
      "objective_key": "find_patrol",
      "world_revision": 19,
      "previous_status": "active",
      "objective_revision": 2
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  },
  {
    "id": "db0cb682-ee15-43d7-9258-cd6c1dcd8526",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 67,
    "event_type": "world_fact_recorded",
    "visibility": "player",
    "payload": {
      "value": "The party rescued the patrol across the signal bridge.",
      "fact_id": "c9ec5740-a2a3-4dc9-8581-53270602cd5d",
      "fact_type": "discovery",
      "subject_npc_id": null,
      "world_revision": 20,
      "supersedes_fact_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  },
  {
    "id": "16be2313-6d39-4b26-932a-512ef30d2d2f",
    "ruleset_release_id": "srd-5.2.1",
    "ruleset_data_catalog_id": "srd-5.2.1-party-state-v1",
    "sequence": 68,
    "event_type": "dm_response",
    "visibility": "player",
    "payload": {
      "outcome": null,
      "narration": "The party's declared choice becomes durable campaign history.",
      "resolution_id": null
    },
    "actor_character_id": "f570c49a-6075-4347-bf4d-5a5e796bcc1c",
    "created_at": "2026-09-03T22:28:19.650538+12:00"
  }
]

# Subjective review
1. Does Mira's promise and attitude feel continuous after travel and restart?
- I couldn't quite connect the dots of continuity regarding Mira's promise and attitude because the test involved me outputting what seemed to be predetermined or already progressed set of events, rather than going through the journey.
2. Is it clear that accepting the quest and choosing the route are separate player decisions?
- From the returned result there seem to be a distinction - again, whether I feel that way or not was not accountable since this test didn't seem like a test through a certain play through, but exercise of fetching data and inspecting the result. 
3. Do the two outcomes feel meaningfully different and consistent with their selected route?
- Not quite sure if consistency can be determined by me observing two instances of scenarios. It definitely did seem different from fetched result of event sequences.
4. Does the event history contain enough structured information to explain how the final world was
   reached, even though a future frontend will present it more clearly?
- I was able to gather what sequence of actions happened that lead to the last event of the sequence.
5. Is the absent-target error sufficient for a future frontend to tell a player why the action is
   unavailable and what they should do next? If not, describe the missing guidance.
- this probably cannot be determined from one test, it might be better determined from testing few playthroughs once a functioning and playable frontend has been established
