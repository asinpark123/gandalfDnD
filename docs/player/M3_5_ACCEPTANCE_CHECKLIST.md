# M3.5 Persistent World Targeted Owner Retest

- **Milestone state:** Done — targeted owner retest passed 2026-09-04
- **Automated gate:** Corrected two-branch scenario and full regression gate pass locally
- **External model use:** None; this uses only the deterministic in-process provider
- **Purpose:** Confirm through staged interaction that the same NPC keeps her promise, the owner
  makes both types of decisions, the branches diverge coherently, and an unavailable action gives
  frontend-ready recovery information.

The completed evidence is preserved in
[`../testM3_5_TARGETED_RETEST_RESULTS.md`](../testM3_5_TARGETED_RETEST_RESULTS.md). All six actions
and all four subjective questions passed; this checklist is retained as the reproducible procedure.

The original owner run is preserved unchanged in
[`../testM3_5_ACCEPTANCE_CHECKLIST_RESULTS.md`](../testM3_5_ACCEPTANCE_CHECKLIST_RESULTS.md). It
confirmed persistence, event causality, restart behavior, visibility, and mechanically inert world
state, but it could not establish the subjective continuity/choice gate: the runner had already
made every choice, and an unstable test-fixture lookup returned a different same-name Mira instead
of the promise-bearing guide. This targeted retest replaces only the inconclusive portion.

## Setup

Keep the PostgreSQL tunnel open. Stop the development API if it is already running, then run from
`~/Git/gandalfDnD`:

```bash
source .venv/bin/activate
alembic upgrade head
python -m scripts.run_m3_5_owner_fixture --guided | tee /tmp/gandalf-m3-5-targeted-retest.txt
```

The runner refuses any database whose name does not begin with `gandalfdnd_dev`. It creates new
campaign rows without changing earlier campaigns, makes no OpenClaw or paid-provider call, and
pauses for your choices. It prints concise checkpoints as the story progresses and a complete final
record for both campaigns.

## Actions and expected results

1. For both campaigns, enter `accept` when asked whether the party will search for the patrol. The
   next checkpoint should show the quest objective changing from `pending` to `active`.
2. At `promise made`, note the guide's ID and the promise/attitude `subject_npc_id`. At
   `promise keeper returns`, confirm the present watchful innkeeper has that same ID and both facts
   still refer to it. The weary caravan guard must be absent.
3. At the route prompt, choose `signal_bridge` for one campaign and `flooded_tunnel` for the other,
   in either order. The runner will require the second choice to differ from the first.
4. At each `final world after restart` checkpoint, confirm the selected route remains recorded.
   The bridge route should complete `Find the missing patrol` and record a rescue; the tunnel route
   should fail it and record a collapse. Both should finish at the Old Tower, revision 20, after 90
   narrative minutes.
5. Confirm the printed `absent_target_error` is HTTP-equivalent error data with all three fields:

   ```json
   {
     "detail": "Target NPC is not present in the current scene",
     "code": "world_target_not_present",
     "recovery": "Choose an NPC present in the current scene or act without a target."
   }
   ```

6. Start the API with `uvicorn app.api:app --reload`, open `http://127.0.0.1:8000/docs`, and call
   `GET /campaigns/{campaign_id}/world` for both final campaign IDs. Confirm the final state matches
   the saved output. Also confirm the documented 409 response for
   `POST /campaigns/{campaign_id}/turn-executions` uses the structured error schema rather than
   appearing as an undocumented response.

Exact identity, revisions, no rejected-turn provider/event writes, hidden-data exclusion, complete
event replay, atomic rollback, and engine-disposal equality remain automated assertions and do not
need manual repetition.

## Subjective review

Record concise answers after the six actions:

1. With the checkpoints shown in order, does the guide's promise and attitude now feel continuous
   through travel and restart?
2. Did personally accepting the quest and later choosing a route feel like two distinct decisions?
3. Did the two selected routes produce meaningfully different, internally consistent outcomes?
4. Is the absent-target error structured well enough for a future frontend to explain the problem
   and offer a corrective action? Visual clarity itself remains an M7 frontend question.

## Recorded result

The complete result and four positive subjective answers are stored in
`docs/testM3_5_TARGETED_RETEST_RESULTS.md`. M3 is Done. The optional capped live OpenClaw run is a
separate supplemental evaluation; it was later authorized, passed after hardening, and is recorded
in `docs/M3_OPENCLAW_EVALUATION.md`.
