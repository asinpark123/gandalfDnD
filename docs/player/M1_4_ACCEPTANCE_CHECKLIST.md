# M1.4 Deterministic Resolution Owner Acceptance Checklist

- **Milestone state:** Done (accepted 2026-09-02)
- **Automated gate:** Passed on 2026-09-01
- **Owner gate:** All nine actions passed; API restart before replay confirmed on 2026-09-02
- **Purpose:** Confirm authoritative ability checks and saving throws use the selected character's
  canonical state, reject supplied modifiers, preserve provenance, and replay after restart.

This is a backend correctness checkpoint. Visual clarity and ordinary-player error guidance remain
part of the M7 interface acceptance work.

## Setup

Keep the PostgreSQL tunnel open, then start Gandalf from `~/Git/gandalfDnD`:

```bash
source .venv/bin/activate
alembic upgrade head
uvicorn app.api:app --reload
```

Open `http://127.0.0.1:8000/docs`. Use an existing ready two-character Party Commander campaign or
complete the M1.3 creation checklist first. Save the campaign ID and both finalized character IDs.
These actions affect only Gandalf's development database and do not use Clawvis or make a paid model
call.

## Actions and expected results

1. Choose one finalized character and call `POST /campaigns/{campaign_id}/resolutions` with:

```json
{
  "command_id": "<new UUID>",
  "actor_character_id": "<character UUID>",
  "ruleset_release_id": "srd-5.2.1",
  "character_state_catalog_id": "srd-5.2.1-party-state-v1",
  "resolution_catalog_id": "srd-5.2.1-check-save-resolution-v1",
  "resolution_type": "saving_throw",
  "ability": "strength",
  "skill": null,
  "difficulty_class": 13,
  "advantage_reasons": [],
  "disadvantage_reasons": []
}
```

   Expect HTTP 201. Confirm the response identifies the chosen actor; contains the character/state
   revisions and both catalog IDs; derives a Strength ability component and Fighter saving-throw
   proficiency component; records the exact d20 face, selected die, total, DC, and `success` or
   `failure`; and includes rule IDs, source references, resolver version, and RNG version. Production
   dice are intentionally random, so either outcome is valid when its arithmetic is correct.
2. Send the identical request again, including the same `command_id`. Expect HTTP 201 and the same
   resolution ID, dice, total, and outcome. Change the DC while retaining that command ID and expect
   HTTP 409 because an idempotency key cannot represent two different commands.
3. Send a new resolution command but add `"modifier": 99`. Expect HTTP 422 with the field rejected
   as an extra input. This proves an API client or model cannot override the canonical modifier.
4. For a character currently wearing Chain Mail, submit an `ability_check` with `ability` set to
   `dexterity`, `skill` set to `stealth`, DC 13, and empty reason lists. Expect
   `advantage_state: "disadvantage"`, two recorded d20 faces, the lower face selected, and a
   canonical Stealth proficiency component when the character is proficient.
5. Repeat step 4 with a new command ID and one already-adjudicated advantage reason, for example
   `"advantage_reasons": ["ally_help"]`. Expect the advantage and Chain Mail disadvantage to
   cancel: `advantage_state: "normal"`, exactly one d20 face, and that face selected.
6. Submit a Strength (Stealth) ability check for the same armored character by changing only
   `ability` to `strength` and using a new command ID. Confirm Chain Mail does not automatically add
   disadvantage: its rule applies specifically to Dexterity (Stealth), while the contextual ability
   still uses the character's Stealth proficiency if present.
7. Call `GET /campaigns/{campaign_id}/resolutions`, then read one result with
   `GET /campaigns/{campaign_id}/resolutions/{resolution_id}`. Confirm the records retain the exact
   actor, inputs, components, dice, outcome, and provenance. In
   `GET /campaigns/{campaign_id}/events`, confirm a `rule_resolved` event identifies the same actor
   and resolution.
8. Restart the API, then call
   `POST /campaigns/{campaign_id}/resolutions/{resolution_id}/replay`. Expect HTTP 200,
   `equivalent: true`, and identical recomputed advantage state, modifier, selected die, total, and
   outcome. Replay does not reroll the dice; it verifies the stored mechanical evidence.
9. Submit otherwise valid commands for the second character and compare the modifier components.
   Confirm each resolution uses only its selected actor's ability and proficiency state and neither
   character's record or event is attributed to the other.

## Results to record

For each step, record the HTTP status and whether the returned structured values match the expected
rules and arithmetic. Classify any discrepancy as:

- pass;
- defect, with the request and relevant response copied without credentials;
- rules/ruling question;
- documentation clarification; or
- accepted limitation.

The automated suite uses fixed dice to prove deterministic natural-1, natural-20, normal,
Advantage, Disadvantage, cancellation, actor-isolation, rejection, persistence, and replay cases.
This owner test confirms those contracts are understandable and work in the running development
environment; it does not need to force a particular random face.

Save the results in `docs/` and notify Codex. The outcome will be incorporated into
[`../PROJECT_PLAN.md`](../PROJECT_PLAN.md) before M1.4 is marked Done.

## Final outcome

The complete result is preserved in
[`../testM1_4_ACCEPTANCE_CHECKLIST_RESULTS.md`](../testM1_4_ACCEPTANCE_CHECKLIST_RESULTS.md). All nine
actions passed with correct arithmetic, idempotency, modifier rejection, automatic and cancelling
Advantage/Disadvantage, contextual ability use, persistence, event attribution, actor isolation, and
post-restart replay. The owner confirmed the API restart occurred before action 8. No defect,
targeted retest, workaround, or new ruling was required.

Both owner-test characters had the same relevant Strength/save build and therefore correctly
produced equal modifiers. Their actor IDs, acquisition-event provenance, and state revisions were
distinct; the automated contrasting-ability fixture separately proves unequal canonical actor
state produces unequal modifiers. M1.4 is Done.

## Known limitations

- M1.4 covers ability checks and saving throws, not attacks, damage, combat, conditions, tools,
  Heroic Inspiration expenditure/rerolls, or narrative consequences.
- Advantage and Disadvantage reason lists are already-adjudicated application/GM context. Automatic
  sources currently cover the supported Chain Mail Dexterity (Stealth) rule.
- The legacy Phase 0 turn endpoint still accepts its older non-authoritative dice-request modifier;
  M2 will route live turns through this authoritative resolution service before narration.
