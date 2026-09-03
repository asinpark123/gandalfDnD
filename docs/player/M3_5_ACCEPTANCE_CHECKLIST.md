# M3.5 Persistent World Owner Acceptance Checklist

- **Milestone state:** Verification — deterministic gate passed; owner review required
- **Automated gate:** Two-branch scenario passed locally
- **External model use:** None; the fixture uses only the deterministic in-process provider
- **Purpose:** Confirm that NPC continuity, quest acceptance, explicit choices, faction state,
  revealed knowledge, and time form an understandable persistent campaign history.

This is a backend coherence checkpoint. Exact identity, revisions, visibility, rollback, event
causality, context limits, and restart equality are enforced by automated tests. Frontend
presentation and ordinary-player guidance remain M7 work.

## Setup

Keep the PostgreSQL tunnel open. Stop the development API if it is already running, then prepare two
isolated review campaigns from `~/Git/gandalfDnD`:

```bash
source .venv/bin/activate
alembic upgrade head
python -m scripts.run_m3_5_owner_fixture | tee /tmp/gandalf-m3-5-owner-fixture.json
uvicorn app.api:app --reload
```

The runner refuses any database whose name does not begin with `gandalfdnd_dev`. It creates new
campaign rows without altering prior campaigns, uses no Clawvis/OpenClaw route, makes no paid call,
and prints both campaign, character, and starting-NPC IDs plus their final world projections. Keep
the JSON file open and open `http://127.0.0.1:8000/docs`.

## Actions and expected results

1. In the fixture JSON, confirm `fixture` is `m3.5-branching-lantern-v1`,
   `external_provider_calls` is `0`, and the two campaign IDs differ. Both worlds should report
   `world_revision: 20`, `narrative_time_minutes: 90`, and `Old Tower` as the current location.
2. Call `GET /campaigns/{campaign_id}/world` for both campaign IDs. Confirm each response exactly
   matches its saved fixture projection after allowing for JSON object-key ordering. Restart the
   API, repeat both calls, and confirm neither world changed.
3. In each world, confirm only the caravan-guard Mira is currently present. Seren and the
   innkeeper Mira should not be present after their recorded departures. The two same-name Miras
   retain distinct IDs, and the present Mira's ID matches the second `starting_npc_ids` value.
4. Confirm both worlds contain the current friendly attitude and Mira's promise to guide the party,
   plus the revealed clue about the Lantern Watch bell. No numeric reputation, automatic modifier,
   rest, healing, resource recovery, condition, reward, XP, or level change should appear.
5. Confirm `The Missing Lantern Patrol` is active and its `find_patrol` objective differs by branch:
   `completed` for `signal_bridge` and `failed` for `flooded_tunnel`. In both campaigns the
   `accept_lantern_patrol` decision should be `selected` with `accept` recorded.
6. Confirm the second decision records exactly the player's branch: `signal_bridge` in one campaign
   and `flooded_tunnel` in the other. The matching discovery should say either that the patrol was
   rescued across the bridge or that the tunnel collapsed before the patrol was found. The other
   branch's discovery must be absent.
7. Confirm the Lantern Watch faction persists in both worlds with a `friendly` party attitude and
   an `associate` membership for Arin's character ID. Both relationship rows should remain
   narrative labels and should not change either character's HP, resources, inventory, or derived
   rules state.
8. Call `GET /campaigns/{campaign_id}/events` for each campaign. Confirm sequences are strictly
   increasing and the history visibly explains NPC arrivals/departures, scene closure/opening, quest
   creation and acceptance, clue reveal, faction changes, time advancement, decision selection,
   objective outcome, and branch discovery. The hidden clue-creation event itself must not appear;
   only its later player-visible reveal may contain the clue value.
9. For either final campaign, use its first `starting_npc_ids` value as `target_npc_id` in
   `POST /campaigns/{campaign_id}/turn-executions` with a new UUID, an action such as
   `Ask the absent innkeeper Mira for help`, and either finalized character ID. Expect HTTP 409 with
   `Target NPC is not present in the current scene`. No provider call or canonical event is created.

## Subjective review

Record concise answers after the nine actions:

1. Does Mira's promise and attitude feel continuous after travel and restart?
2. Is it clear that accepting the quest and choosing the route are separate player decisions?
3. Do the two outcomes feel meaningfully different and consistent with their selected route?
4. Does the event history contain enough structured information to explain how the final world was
   reached, even though a future frontend will present it more clearly?
5. Is the absent-target error sufficient for a future frontend to tell a player why the action is
   unavailable and what they should do next? If not, describe the missing guidance.

## Results to record

For every action, record the HTTP status where applicable, the relevant returned values, and one of:

- pass;
- defect, with the request and credential-free response;
- coherence or product-design concern;
- documentation clarification; or
- accepted limitation.

Copy this checklist to `docs/testM3_5_ACCEPTANCE_CHECKLIST_RESULTS.md`, append the observed evidence
and subjective answers, and notify Codex. M3 remains in Verification until the result is analyzed
and any defect is fixed. The optional capped live OpenClaw run is a separate supplemental gate and
still requires explicit authorization.
