# M1.3 Party Commander Owner Acceptance Checklist

- **Milestone state:** Done (accepted 2026-09-01)
- **Automated gate:** Passed on 2026-08-31
- **Purpose:** Preserve the owner acceptance workflow and evidence for Party Commander backend
  correctness. Player-interface usability is intentionally reassessed in M7.

## Setup

Keep the PostgreSQL tunnel open, then start Gandalf from `~/Git/gandalfDnD`:

```bash
source .venv/bin/activate
alembic upgrade head
uvicorn app.api:app --reload
```

Open `http://127.0.0.1:8000/docs`. The default deterministic provider makes no paid or external
model call. This checklist creates only a new Gandalf development campaign; it does not touch other
databases or Clawvis.

## Actions and expected results

1. Call `POST /campaigns` with a memorable test name. Confirm the response says
   `play_mode: party_commander`, `party_min_active: 2`, `party_max_active: 4`, and catalog
   `srd-5.2.1-party-state-v1`.
2. Call `POST /campaigns/{campaign_id}/characters` twice with different names. Save both character
   IDs. Confirm their `party_position` values are 1 and 2 and both are `draft`.
3. Call `GET /campaigns/{campaign_id}/state`. Confirm `party_ready` is false and both drafts are
   shown in party order.
4. In `GET /rulesets/srd-5.2.1/character-creation/options`, confirm the supported creation catalog
   is `srd-5.2.1-character-creation-v1` and the party description says two to four characters.
5. Finalize character 1 with
   `POST /campaigns/{campaign_id}/characters/{character_id}/finalize`, using this supported fixture:

```json
{
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
}
```

6. Confirm character 1 shows HP 12; Strength save +5; Constitution save +4; initiative +4; passive
   Perception 12; Speed 30; worn Chain Mail plus Defense AC 17; two Second Wind uses; one d10 Hit
   Die; and one Heroic Inspiration. Open a few `provenance` objects and confirm the formula and
   source/acquisition IDs are understandable. Confirm every equipment row—including `Dice Set` and
   `GP`—has non-empty `provenance_definition_keys`, `source_ids`, and `acquisition_event_ids`.
   Party readiness should still be false.
7. Finalize character 2 with the same fixture. Confirm `party_ready` becomes true and both character
   sheets remain independently addressable.
8. Change only character 1's loadout with
   `PUT /campaigns/{campaign_id}/characters/{character_1_id}/loadout`:

```json
{"worn_armor_item_id": null, "held_item_ids": ["greatsword"]}
```

   Confirm character 1 becomes AC 12 and state revision 2, while character 2 remains AC 17 with
   Chain Mail. Confirm the Greatsword is `held` and other owned equipment remains `carried`.
9. Try a turn without `actor_character_id`; remove the property from the JSON entirely rather than
   sending an empty string. Expect HTTP 409. Repeat with character 1's ID; expect HTTP 201 and the
   same actor ID on the turn. In `GET /campaigns/{campaign_id}/events`, confirm the player action and
   response identify character 1.
10. Restart the API, read campaign state again, and confirm the party order, both sheets, character
    1's AC/loadout revision, and character 2's unchanged state survived.

## Feedback to record

- Were the two-character party and selected actor obvious?
- Were the calculated values and their explanations readable without D&D expertise?
- Did any value look wrong, surprising, or too technical?
- Did character 1's loadout change leave character 2 clearly unchanged?
- Did any API error fail to explain how to correct the request?

Record the result as pass, defect, documentation clarification, or accepted limitation in
[`../PROJECT_PLAN.md`](../PROJECT_PLAN.md) before closing M1.3.

## Targeted retest after the first owner run

The first owner run passed the party, sheet, loadout, actor-attributed turn, and restart checks. It
exposed missing projected provenance for the dynamically selected Dice Set and aggregated GP; it
also sent an empty UUID rather than omitting the actor property and did not record the events read.
After updating to the correction commit, only these checks need repeating:

1. Restart/reload the API and call `GET /campaigns/{campaign_id}/state` for the existing campaign.
   Under both characters' `mechanical_state.equipment`, confirm `Dice Set` and `GP` now have non-empty
   `provenance_definition_keys`, `source_ids`, and `acquisition_event_ids`.
2. Call `POST /campaigns/{campaign_id}/turns` with exactly this body and expect HTTP 409 with
   `Party Commander turns require actor_character_id`:

```json
{"action": "Someone scouts ahead."}
```

3. Call `GET /campaigns/{campaign_id}/events`. Confirm the successful turn's `player_action` and
   `dm_response` events both identify character 1 in `actor_character_id`.

Then answer the five subjective feedback questions above. No other M1.3 action needs repeating.

## Final outcome

The targeted retest passed all technical checks. The owner accepted questions 1–4 as frontend
concerns because direct JSON testing can establish structured-value correctness but cannot establish
visual clarity or discoverability. The owner considered the tested API error adequate for developer
diagnosis, while requiring the future frontend to add contextual, actionable player guidance.

M1.3 is Done. The deferred interface requirements are tracked as `UX-001` under M7 in
[`../PROJECT_PLAN.md`](../PROJECT_PLAN.md); no additional M1.3 API rerun is required.
