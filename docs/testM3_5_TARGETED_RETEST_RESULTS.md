# Raw inputs and outputs
❯ python -m scripts.run_m3_5_owner_fixture --guided | tee /tmp/gandalf-m3-5-targeted-retest.txt
/Users/ahshin/Git/gandalfDnD/.venv/lib/python3.11/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa

[campaign_one] promise made
{
  "campaign_id": "55348fa1-fccf-4938-a4ad-c71ee7ba7881",
  "world_revision": 3,
  "location": "Lantern Hall",
  "narrative_time_minutes": 0,
  "present_npcs": [
    {
      "id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "name": "Mira",
      "description": "A watchful innkeeper."
    },
    {
      "id": "ac4808b7-171e-4ef7-a037-16ad63854ef0",
      "name": "Mira",
      "description": "A weary caravan guard."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "npc_attitude",
      "value": "friendly"
    }
  ],
  "quests": [],
  "selected_decisions": []
}

[campaign_one] quest offer
Decision opened: accept_lantern_patrol

[campaign_one] Will the party search for the missing Lantern Watch patrol?
  accept: Accept the search
  decline: Decline the search
Choose an option key: accept

[campaign_one] quest accepted
{
  "campaign_id": "55348fa1-fccf-4938-a4ad-c71ee7ba7881",
  "world_revision": 8,
  "location": "Lantern Hall",
  "narrative_time_minutes": 0,
  "present_npcs": [
    {
      "id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "name": "Mira",
      "description": "A watchful innkeeper."
    },
    {
      "id": "ac4808b7-171e-4ef7-a037-16ad63854ef0",
      "name": "Mira",
      "description": "A weary caravan guard."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "npc_attitude",
      "value": "friendly"
    }
  ],
  "quests": [
    {
      "title": "The Missing Lantern Patrol",
      "status": "active",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "active"
        }
      ]
    }
  ],
  "selected_decisions": [
    {
      "key": "accept_lantern_patrol",
      "option": "accept"
    }
  ]
}

[campaign_one] promise keeper returns
{
  "campaign_id": "55348fa1-fccf-4938-a4ad-c71ee7ba7881",
  "world_revision": 12,
  "location": "Old Tower",
  "narrative_time_minutes": 0,
  "present_npcs": [
    {
      "id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "name": "Mira",
      "description": "A watchful innkeeper."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "npc_attitude",
      "value": "friendly"
    }
  ],
  "quests": [
    {
      "title": "The Missing Lantern Patrol",
      "status": "active",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "active"
        }
      ]
    }
  ],
  "selected_decisions": [
    {
      "key": "accept_lantern_patrol",
      "option": "accept"
    }
  ],
  "absent_target_error": {
    "detail": "Target NPC is not present in the current scene",
    "code": "world_target_not_present",
    "recovery": "Choose an NPC present in the current scene or act without a target."
  }
}

[campaign_one] route choice
Decision opened: tower_route

[campaign_one] Which route will the party use to reach the patrol?
  signal_bridge: Cross the signal bridge
  flooded_tunnel: Enter the flooded tunnel
Choose an option key: flooded_tunnel

[campaign_one] final world after restart
{
  "campaign_id": "55348fa1-fccf-4938-a4ad-c71ee7ba7881",
  "world_revision": 20,
  "location": "Old Tower",
  "narrative_time_minutes": 90,
  "present_npcs": [
    {
      "id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "name": "Mira",
      "description": "A watchful innkeeper."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "type": "npc_attitude",
      "value": "friendly"
    },
    {
      "subject_npc_id": null,
      "type": "discovery",
      "value": "The flooded tunnel collapsed before the patrol was found."
    }
  ],
  "quests": [
    {
      "title": "The Missing Lantern Patrol",
      "status": "active",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "failed"
        }
      ]
    }
  ],
  "selected_decisions": [
    {
      "key": "accept_lantern_patrol",
      "option": "accept"
    },
    {
      "key": "tower_route",
      "option": "flooded_tunnel"
    }
  ],
  "selected_route": "flooded_tunnel"
}

[campaign_two] promise made
{
  "campaign_id": "2106e1da-1d5c-4190-8b22-8cb956d56413",
  "world_revision": 3,
  "location": "Lantern Hall",
  "narrative_time_minutes": 0,
  "present_npcs": [
    {
      "id": "5b736feb-61fe-4a42-bb3d-88e2f3266799",
      "name": "Mira",
      "description": "A weary caravan guard."
    },
    {
      "id": "5e983218-af72-4069-9a96-38a27baee304",
      "name": "Mira",
      "description": "A watchful innkeeper."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "npc_attitude",
      "value": "friendly"
    }
  ],
  "quests": [],
  "selected_decisions": []
}

[campaign_two] quest offer
Decision opened: accept_lantern_patrol

[campaign_two] Will the party search for the missing Lantern Watch patrol?
  accept: Accept the search
  decline: Decline the search
Choose an option key: accept
^[[D^[[C
[campaign_two] quest accepted
{
  "campaign_id": "2106e1da-1d5c-4190-8b22-8cb956d56413",
  "world_revision": 8,
  "location": "Lantern Hall",
  "narrative_time_minutes": 0,
  "present_npcs": [
    {
      "id": "5b736feb-61fe-4a42-bb3d-88e2f3266799",
      "name": "Mira",
      "description": "A weary caravan guard."
    },
    {
      "id": "5e983218-af72-4069-9a96-38a27baee304",
      "name": "Mira",
      "description": "A watchful innkeeper."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "npc_attitude",
      "value": "friendly"
    }
  ],
  "quests": [
    {
      "title": "The Missing Lantern Patrol",
      "status": "active",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "active"
        }
      ]
    }
  ],
  "selected_decisions": [
    {
      "key": "accept_lantern_patrol",
      "option": "accept"
    }
  ]
}

[campaign_two] promise keeper returns
{
  "campaign_id": "2106e1da-1d5c-4190-8b22-8cb956d56413",
  "world_revision": 12,
  "location": "Old Tower",
  "narrative_time_minutes": 0,
  "present_npcs": [
    {
      "id": "5e983218-af72-4069-9a96-38a27baee304",
      "name": "Mira",
      "description": "A watchful innkeeper."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "npc_attitude",
      "value": "friendly"
    }
  ],
  "quests": [
    {
      "title": "The Missing Lantern Patrol",
      "status": "active",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "active"
        }
      ]
    }
  ],
  "selected_decisions": [
    {
      "key": "accept_lantern_patrol",
      "option": "accept"
    }
  ],
  "absent_target_error": {
    "detail": "Target NPC is not present in the current scene",
    "code": "world_target_not_present",
    "recovery": "Choose an NPC present in the current scene or act without a target."
  }
}

[campaign_two] route choice
Decision opened: tower_route

[campaign_two] Which route will the party use to reach the patrol?
  signal_bridge: Cross the signal bridge
  flooded_tunnel: Enter the flooded tunnel
Choose an option key: signal_bridge
Choose one of: flooded_tunnel, signal_bridge
Choose an option key: signal_bridge

[campaign_two] final world after restart
{
  "campaign_id": "2106e1da-1d5c-4190-8b22-8cb956d56413",
  "world_revision": 20,
  "location": "Old Tower",
  "narrative_time_minutes": 90,
  "present_npcs": [
    {
      "id": "5e983218-af72-4069-9a96-38a27baee304",
      "name": "Mira",
      "description": "A watchful innkeeper."
    }
  ],
  "continuity_facts": [
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "promise",
      "value": "Mira will guide the party to the Old Tower."
    },
    {
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "type": "npc_attitude",
      "value": "friendly"
    },
    {
      "subject_npc_id": null,
      "type": "discovery",
      "value": "The party rescued the patrol across the signal bridge."
    }
  ],
  "quests": [
    {
      "title": "The Missing Lantern Patrol",
      "status": "active",
      "objectives": [
        {
          "title": "Find the missing patrol",
          "status": "completed"
        }
      ]
    }
  ],
  "selected_decisions": [
    {
      "key": "accept_lantern_patrol",
      "option": "accept"
    },
    {
      "key": "tower_route",
      "option": "signal_bridge"
    }
  ],
  "selected_route": "signal_bridge"
}
{
  "database": "gandalfdnd_dev",
  "external_provider_calls": 0,
  "fixture": "m3.5-guided-owner-retest-v2",
  "selected_routes": [
    "flooded_tunnel",
    "signal_bridge"
  ],
  "campaign_one": {
    "campaign_id": "55348fa1-fccf-4938-a4ad-c71ee7ba7881",
    "character_ids": [
      "ff700be3-c728-452a-ab36-de85698c7472",
      "991eaf05-fa35-4967-88e4-115b3a93053a"
    ],
    "starting_npc_ids": [
      "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "ac4808b7-171e-4ef7-a037-16ad63854ef0"
    ],
    "guide_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
    "absent_npc_id": "ac4808b7-171e-4ef7-a037-16ad63854ef0",
    "world": {
      "campaign_id": "55348fa1-fccf-4938-a4ad-c71ee7ba7881",
      "world_revision": 20,
      "narrative_time_minutes": 90,
      "location": {
        "id": "d77a6d3f-a69e-4d3c-afc1-e95edc2037ab",
        "name": "Old Tower",
        "description": "A ruined watchtower above the flooded road."
      },
      "scene": {
        "id": "19aaefc3-d752-4dc4-b20b-2ded7b3152bd",
        "sequence": 2,
        "title": "Old Tower",
        "summary": "A ruined watchtower above the flooded road.",
        "status": "active",
        "revision": 0,
        "created_at": "2026-09-04T00:07:11.427427+12:00"
      },
      "present_npcs": [
        {
          "id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
          "name": "Mira",
          "public_description": "A watchful innkeeper.",
          "status": "active",
          "revision": 0,
          "created_at": "2026-09-04T00:05:38.458368+12:00"
        }
      ],
      "facts": [
        {
          "id": "74e62742-4728-4d8d-8a3c-0f6fadf35700",
          "subject_npc_id": null,
          "fact_type": "clue",
          "value": "The Lantern Watch bell bears a concealed tunnel map.",
          "status": "current",
          "revision": 1,
          "created_at": "2026-09-04T00:05:39.852610+12:00"
        },
        {
          "id": "022a5e83-60c6-4022-b4be-3fddbffbe420",
          "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
          "fact_type": "promise",
          "value": "Mira will guide the party to the Old Tower.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-04T00:05:41.021886+12:00"
        },
        {
          "id": "bd109ce8-a048-427e-b21e-615f43bb1fd6",
          "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
          "fact_type": "npc_attitude",
          "value": "friendly",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-04T00:05:41.021886+12:00"
        },
        {
          "id": "77d5c8c9-5c42-4db4-8a3a-47d30e82c95b",
          "subject_npc_id": null,
          "fact_type": "discovery",
          "value": "The flooded tunnel collapsed before the patrol was found.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-04T00:07:57.796601+12:00"
        }
      ],
      "quests": [
        {
          "id": "ddb63635-3ecf-4c2b-9589-f74352f507c1",
          "quest_key": "missing_lantern_patrol",
          "title": "The Missing Lantern Patrol",
          "summary": "Find the patrol beyond the Old Tower.",
          "status": "active",
          "revision": 0,
          "objectives": [
            {
              "id": "81d5aa8e-86e4-49b4-86c7-c89ff2435059",
              "objective_key": "find_patrol",
              "title": "Find the missing patrol",
              "description": null,
              "status": "failed",
              "position": 1,
              "revision": 2,
              "created_at": "2026-09-04T00:05:42.518903+12:00"
            }
          ],
          "created_at": "2026-09-04T00:05:42.518903+12:00"
        }
      ],
      "decisions": [
        {
          "id": "a17d42b4-33d2-492f-a5ac-17be4b648aff",
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
          "created_at": "2026-09-04T00:05:43.915377+12:00"
        },
        {
          "id": "c1b8989e-0fce-4f5c-8296-43ea5ca89bcb",
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
          "created_at": "2026-09-04T00:07:20.326718+12:00"
        }
      ],
      "factions": [
        {
          "id": "115532be-8992-4833-b7ad-2237a338e338",
          "faction_key": "lantern_watch",
          "name": "Lantern Watch",
          "description": "Wardens of the northern road.",
          "status": "active",
          "revision": 0,
          "relationships": [
            {
              "id": "bdc24a62-dd89-4be7-9a23-124be7897b1c",
              "relation_type": "attitude",
              "character_id": null,
              "npc_id": null,
              "value": "friendly",
              "revision": 0,
              "created_at": "2026-09-04T00:07:18.973411+12:00"
            },
            {
              "id": "e7d1d0c8-3ea6-4cb2-a6cc-8de48531af39",
              "relation_type": "membership",
              "character_id": "ff700be3-c728-452a-ab36-de85698c7472",
              "npc_id": null,
              "value": "associate",
              "revision": 0,
              "created_at": "2026-09-04T00:07:18.973411+12:00"
            }
          ],
          "created_at": "2026-09-04T00:05:42.518903+12:00"
        }
      ]
    }
  },
  "campaign_two": {
    "campaign_id": "2106e1da-1d5c-4190-8b22-8cb956d56413",
    "character_ids": [
      "a75abb58-ee3d-4067-b36e-43193deaa4b5",
      "c7eda494-cb4c-4917-9a0e-cf33a2435415"
    ],
    "starting_npc_ids": [
      "5b736feb-61fe-4a42-bb3d-88e2f3266799",
      "5e983218-af72-4069-9a96-38a27baee304"
    ],
    "guide_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
    "absent_npc_id": "5b736feb-61fe-4a42-bb3d-88e2f3266799",
    "world": {
      "campaign_id": "2106e1da-1d5c-4190-8b22-8cb956d56413",
      "world_revision": 20,
      "narrative_time_minutes": 90,
      "location": {
        "id": "a0e75303-499d-44bd-8100-4e7fefe5c8f3",
        "name": "Old Tower",
        "description": "A ruined watchtower above the flooded road."
      },
      "scene": {
        "id": "b4181232-0738-4852-9e80-e6280c3a1ac3",
        "sequence": 2,
        "title": "Old Tower",
        "summary": "A ruined watchtower above the flooded road.",
        "status": "active",
        "revision": 0,
        "created_at": "2026-09-04T00:08:11.628169+12:00"
      },
      "present_npcs": [
        {
          "id": "5e983218-af72-4069-9a96-38a27baee304",
          "name": "Mira",
          "public_description": "A watchful innkeeper.",
          "status": "active",
          "revision": 0,
          "created_at": "2026-09-04T00:07:58.867011+12:00"
        }
      ],
      "facts": [
        {
          "id": "d85ff269-0670-4ccb-b1ca-624039bf3634",
          "subject_npc_id": null,
          "fact_type": "clue",
          "value": "The Lantern Watch bell bears a concealed tunnel map.",
          "status": "current",
          "revision": 1,
          "created_at": "2026-09-04T00:08:00.022842+12:00"
        },
        {
          "id": "4db8f91f-27de-467b-afc2-f06ebd6de117",
          "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
          "fact_type": "promise",
          "value": "Mira will guide the party to the Old Tower.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-04T00:08:01.106520+12:00"
        },
        {
          "id": "a7d050f5-9d49-46aa-a52b-7c6f598c3d39",
          "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
          "fact_type": "npc_attitude",
          "value": "friendly",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-04T00:08:01.106520+12:00"
        },
        {
          "id": "e8e23e62-79e3-40aa-9e22-00490288e9eb",
          "subject_npc_id": null,
          "fact_type": "discovery",
          "value": "The party rescued the patrol across the signal bridge.",
          "status": "current",
          "revision": 0,
          "created_at": "2026-09-04T00:08:34.515121+12:00"
        }
      ],
      "quests": [
        {
          "id": "38e70920-1a74-4e65-9ea3-b15d9a4b0655",
          "quest_key": "missing_lantern_patrol",
          "title": "The Missing Lantern Patrol",
          "summary": "Find the patrol beyond the Old Tower.",
          "status": "active",
          "revision": 0,
          "objectives": [
            {
              "id": "d6952bf5-ee01-46ac-ab9a-78682d0dc0e2",
              "objective_key": "find_patrol",
              "title": "Find the missing patrol",
              "description": null,
              "status": "completed",
              "position": 1,
              "revision": 2,
              "created_at": "2026-09-04T00:08:02.565904+12:00"
            }
          ],
          "created_at": "2026-09-04T00:08:02.565904+12:00"
        }
      ],
      "decisions": [
        {
          "id": "c4a4e87c-1eb4-4002-8d75-0ca89fabf774",
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
          "created_at": "2026-09-04T00:08:03.866963+12:00"
        },
        {
          "id": "2f378909-9937-4d0d-8b23-caea605103d7",
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
          "created_at": "2026-09-04T00:08:20.414687+12:00"
        }
      ],
      "factions": [
        {
          "id": "4b731ff7-f76b-4b33-97ef-ddcebec44d71",
          "faction_key": "lantern_watch",
          "name": "Lantern Watch",
          "description": "Wardens of the northern road.",
          "status": "active",
          "revision": 0,
          "relationships": [
            {
              "id": "127f83e7-f760-4f78-bd68-e8f3f8a94516",
              "relation_type": "attitude",
              "character_id": null,
              "npc_id": null,
              "value": "friendly",
              "revision": 0,
              "created_at": "2026-09-04T00:08:19.017562+12:00"
            },
            {
              "id": "124e84d5-7c35-4ce0-a4b6-f1cf91fad3bf",
              "relation_type": "membership",
              "character_id": "a75abb58-ee3d-4067-b36e-43193deaa4b5",
              "npc_id": null,
              "value": "associate",
              "revision": 0,
              "created_at": "2026-09-04T00:08:19.017562+12:00"
            }
          ],
          "created_at": "2026-09-04T00:08:02.565904+12:00"
        }
      ]
    }
  }
}

Action6.1.
Curl
curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/55348fa1-fccf-4938-a4ad-c71ee7ba7881/world' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/55348fa1-fccf-4938-a4ad-c71ee7ba7881/world
Server response
Code	200	
Response body
{
  "campaign_id": "55348fa1-fccf-4938-a4ad-c71ee7ba7881",
  "world_revision": 20,
  "narrative_time_minutes": 90,
  "location": {
    "id": "d77a6d3f-a69e-4d3c-afc1-e95edc2037ab",
    "name": "Old Tower",
    "description": "A ruined watchtower above the flooded road."
  },
  "scene": {
    "id": "19aaefc3-d752-4dc4-b20b-2ded7b3152bd",
    "sequence": 2,
    "title": "Old Tower",
    "summary": "A ruined watchtower above the flooded road.",
    "status": "active",
    "revision": 0,
    "created_at": "2026-09-04T00:07:11.427427+12:00"
  },
  "present_npcs": [
    {
      "id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "name": "Mira",
      "public_description": "A watchful innkeeper.",
      "status": "active",
      "revision": 0,
      "created_at": "2026-09-04T00:05:38.458368+12:00"
    }
  ],
  "facts": [
    {
      "id": "74e62742-4728-4d8d-8a3c-0f6fadf35700",
      "subject_npc_id": null,
      "fact_type": "clue",
      "value": "The Lantern Watch bell bears a concealed tunnel map.",
      "status": "current",
      "revision": 1,
      "created_at": "2026-09-04T00:05:39.852610+12:00"
    },
    {
      "id": "022a5e83-60c6-4022-b4be-3fddbffbe420",
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "fact_type": "promise",
      "value": "Mira will guide the party to the Old Tower.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-04T00:05:41.021886+12:00"
    },
    {
      "id": "bd109ce8-a048-427e-b21e-615f43bb1fd6",
      "subject_npc_id": "32fdc583-52ac-40a4-91fc-3cb341b7ea9f",
      "fact_type": "npc_attitude",
      "value": "friendly",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-04T00:05:41.021886+12:00"
    },
    {
      "id": "77d5c8c9-5c42-4db4-8a3a-47d30e82c95b",
      "subject_npc_id": null,
      "fact_type": "discovery",
      "value": "The flooded tunnel collapsed before the patrol was found.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-04T00:07:57.796601+12:00"
    }
  ],
  "quests": [
    {
      "id": "ddb63635-3ecf-4c2b-9589-f74352f507c1",
      "quest_key": "missing_lantern_patrol",
      "title": "The Missing Lantern Patrol",
      "summary": "Find the patrol beyond the Old Tower.",
      "status": "active",
      "revision": 0,
      "objectives": [
        {
          "id": "81d5aa8e-86e4-49b4-86c7-c89ff2435059",
          "objective_key": "find_patrol",
          "title": "Find the missing patrol",
          "description": null,
          "status": "failed",
          "position": 1,
          "revision": 2,
          "created_at": "2026-09-04T00:05:42.518903+12:00"
        }
      ],
      "created_at": "2026-09-04T00:05:42.518903+12:00"
    }
  ],
  "decisions": [
    {
      "id": "a17d42b4-33d2-492f-a5ac-17be4b648aff",
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
      "created_at": "2026-09-04T00:05:43.915377+12:00"
    },
    {
      "id": "c1b8989e-0fce-4f5c-8296-43ea5ca89bcb",
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
      "created_at": "2026-09-04T00:07:20.326718+12:00"
    }
  ],
  "factions": [
    {
      "id": "115532be-8992-4833-b7ad-2237a338e338",
      "faction_key": "lantern_watch",
      "name": "Lantern Watch",
      "description": "Wardens of the northern road.",
      "status": "active",
      "revision": 0,
      "relationships": [
        {
          "id": "bdc24a62-dd89-4be7-9a23-124be7897b1c",
          "relation_type": "attitude",
          "character_id": null,
          "npc_id": null,
          "value": "friendly",
          "revision": 0,
          "created_at": "2026-09-04T00:07:18.973411+12:00"
        },
        {
          "id": "e7d1d0c8-3ea6-4cb2-a6cc-8de48531af39",
          "relation_type": "membership",
          "character_id": "ff700be3-c728-452a-ab36-de85698c7472",
          "npc_id": null,
          "value": "associate",
          "revision": 0,
          "created_at": "2026-09-04T00:07:18.973411+12:00"
        }
      ],
      "created_at": "2026-09-04T00:05:42.518903+12:00"
    }
  ]
}

Action6.2.
Curl

curl -X 'GET' \
  'http://127.0.0.1:8000/campaigns/2106e1da-1d5c-4190-8b22-8cb956d56413/world' \
  -H 'accept: application/json'
Request URL
http://127.0.0.1:8000/campaigns/2106e1da-1d5c-4190-8b22-8cb956d56413/world
Server response
Code	Details
200	
Response body
Download
{
  "campaign_id": "2106e1da-1d5c-4190-8b22-8cb956d56413",
  "world_revision": 20,
  "narrative_time_minutes": 90,
  "location": {
    "id": "a0e75303-499d-44bd-8100-4e7fefe5c8f3",
    "name": "Old Tower",
    "description": "A ruined watchtower above the flooded road."
  },
  "scene": {
    "id": "b4181232-0738-4852-9e80-e6280c3a1ac3",
    "sequence": 2,
    "title": "Old Tower",
    "summary": "A ruined watchtower above the flooded road.",
    "status": "active",
    "revision": 0,
    "created_at": "2026-09-04T00:08:11.628169+12:00"
  },
  "present_npcs": [
    {
      "id": "5e983218-af72-4069-9a96-38a27baee304",
      "name": "Mira",
      "public_description": "A watchful innkeeper.",
      "status": "active",
      "revision": 0,
      "created_at": "2026-09-04T00:07:58.867011+12:00"
    }
  ],
  "facts": [
    {
      "id": "d85ff269-0670-4ccb-b1ca-624039bf3634",
      "subject_npc_id": null,
      "fact_type": "clue",
      "value": "The Lantern Watch bell bears a concealed tunnel map.",
      "status": "current",
      "revision": 1,
      "created_at": "2026-09-04T00:08:00.022842+12:00"
    },
    {
      "id": "4db8f91f-27de-467b-afc2-f06ebd6de117",
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "fact_type": "promise",
      "value": "Mira will guide the party to the Old Tower.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-04T00:08:01.106520+12:00"
    },
    {
      "id": "a7d050f5-9d49-46aa-a52b-7c6f598c3d39",
      "subject_npc_id": "5e983218-af72-4069-9a96-38a27baee304",
      "fact_type": "npc_attitude",
      "value": "friendly",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-04T00:08:01.106520+12:00"
    },
    {
      "id": "e8e23e62-79e3-40aa-9e22-00490288e9eb",
      "subject_npc_id": null,
      "fact_type": "discovery",
      "value": "The party rescued the patrol across the signal bridge.",
      "status": "current",
      "revision": 0,
      "created_at": "2026-09-04T00:08:34.515121+12:00"
    }
  ],
  "quests": [
    {
      "id": "38e70920-1a74-4e65-9ea3-b15d9a4b0655",
      "quest_key": "missing_lantern_patrol",
      "title": "The Missing Lantern Patrol",
      "summary": "Find the patrol beyond the Old Tower.",
      "status": "active",
      "revision": 0,
      "objectives": [
        {
          "id": "d6952bf5-ee01-46ac-ab9a-78682d0dc0e2",
          "objective_key": "find_patrol",
          "title": "Find the missing patrol",
          "description": null,
          "status": "completed",
          "position": 1,
          "revision": 2,
          "created_at": "2026-09-04T00:08:02.565904+12:00"
        }
      ],
      "created_at": "2026-09-04T00:08:02.565904+12:00"
    }
  ],
  "decisions": [
    {
      "id": "c4a4e87c-1eb4-4002-8d75-0ca89fabf774",
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
      "created_at": "2026-09-04T00:08:03.866963+12:00"
    },
    {
      "id": "2f378909-9937-4d0d-8b23-caea605103d7",
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
      "created_at": "2026-09-04T00:08:20.414687+12:00"
    }
  ],
  "factions": [
    {
      "id": "4b731ff7-f76b-4b33-97ef-ddcebec44d71",
      "faction_key": "lantern_watch",
      "name": "Lantern Watch",
      "description": "Wardens of the northern road.",
      "status": "active",
      "revision": 0,
      "relationships": [
        {
          "id": "127f83e7-f760-4f78-bd68-e8f3f8a94516",
          "relation_type": "attitude",
          "character_id": null,
          "npc_id": null,
          "value": "friendly",
          "revision": 0,
          "created_at": "2026-09-04T00:08:19.017562+12:00"
        },
        {
          "id": "124e84d5-7c35-4ce0-a4b6-f1cf91fad3bf",
          "relation_type": "membership",
          "character_id": "a75abb58-ee3d-4067-b36e-43193deaa4b5",
          "npc_id": null,
          "value": "associate",
          "revision": 0,
          "created_at": "2026-09-04T00:08:19.017562+12:00"
        }
      ],
      "created_at": "2026-09-04T00:08:02.565904+12:00"
    }
  ]
}

Action6.3
Curl

curl -X 'POST' \
  'http://127.0.0.1:8000/campaigns/55348fa1-fccf-4938-a4ad-c71ee7ba7881/turn-executions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "command_id": "c9366022-27d6-4945-89b4-6f85c330f2ad",
  "action": "Ask the absent caravan guard Mira for what she sees.",
  "actor_character_id": "ff700be3-c728-452a-ab36-de85698c7472",
  "target_npc_id": "ac4808b7-171e-4ef7-a037-16ad63854ef0"
}'
Request URL
http://127.0.0.1:8000/campaigns/55348fa1-fccf-4938-a4ad-c71ee7ba7881/turn-executions
Server response
Code	Details
409	
Error: Conflict

Response body
Download
{
  "detail": "Target NPC is not present in the current scene",
  "code": "world_target_not_present",
  "recovery": "Choose an NPC present in the current scene or act without a target."
}

# Subjective review
1. With the checkpoints shown in order, does the guide's promise and attitude now feel continuous
   through travel and restart?
    - yes
2. Did personally accepting the quest and later choosing a route feel like two distinct decisions?
    - yes
3. Did the two selected routes produce meaningfully different, internally consistent outcomes?
    - yes
4. Is the absent-target error structured well enough for a future frontend to explain the problem
   and offer a corrective action? Visual clarity itself remains an M7 frontend question.
    - yes