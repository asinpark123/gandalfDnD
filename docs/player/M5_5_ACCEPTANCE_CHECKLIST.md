# M5.5 Health and Combat Outcome Owner Checklist

- **Milestone state:** Implemented — owner acceptance pending
- **External model use:** None
- **Estimated time:** 10–15 minutes
- **Result form:**
  [`../testM5_5_ACCEPTANCE_CHECKLIST_RESULTS.md`](../testM5_5_ACCEPTANCE_CHECKLIST_RESULTS.md)
- **Technical evidence:**
  [`../M5_5_HEALTH_RECOVERY_OUTCOMES.md`](../M5_5_HEALTH_RECOVERY_OUTCOMES.md)

## What this review is for

This is the first required owner combat review. It asks whether the backend outcomes are
understandable and reasonable before any model is allowed to propose or narrate combat in M5.6.
You are reviewing the meaning and correctness of the printed values, not frontend presentation.

The runner creates nine new, isolated development campaigns. It does not modify or delete earlier
campaigns, call OpenClaw, spend API credits, or change PostgreSQL/Clawvis infrastructure. A few
scenarios deliberately prepare an injured or unconscious character directly so you can review the
health boundary without playing many setup rounds; the actual Second Wind, death-save, attack,
knockout, defeat, recovery, event, and restart transitions still pass through the real API.

## Setup and one required command

Keep the usual PostgreSQL tunnel open. You do not need to run the API separately. From
`~/Git/gandalfDnD`, run:

```bash
source .venv/bin/activate
alembic upgrade head
python -m scripts.run_m5_5_owner_fixture --confirm-create \
  | tee /tmp/gandalf-m5-5-owner-fixture.json
```

The runner refuses to operate unless the configured database name begins with `gandalfdnd_dev`.
If it reports a failure, stop and paste the complete error into the result form; do not rerun it
repeatedly.

## Check the printed results

The command prints one JSON document. Confirm these six sections:

1. **`difficulty_samples`** contains exactly four two-character examples:
   - 1 Goblin Warrior: 50 XP, `favorable`;
   - 2 Goblin Warriors: 100 XP, `low`;
   - 3 Goblin Warriors: 150 XP, `moderate`;
   - 4 Goblin Warriors: 200 XP, `high`.

   Every example should show party budgets of Low 100, Moderate 150, and High 200. These labels are
   published XP inputs only—not a promise of survival or subjective balance.

2. **`second_wind_and_restart`** starts at 5 HP, rolls 6, and ends at 12 HP (`6 + level 1`, capped
   by the character maximum). It should show 1 use remaining, no Bonus Action remaining, and
   `restart_state_matches: true`.

3. **`natural_twenty_death_save`** should show die 20, outcome `revived`, 1 HP, and state `active`.

4. **`explicit_knockout_victory`** should show an 11-damage melee hit deliberately converted into
   an unconscious target at 1 HP, with encounter outcome `victory`. Its summary should identify
   both party members and the enemy's final state.

5. **`party_defeat`** should show outcome `defeat`. One party member should be `stable` at 0 HP and
   the other `unconscious` at 0 HP; neither can continue fighting. The summary should retain those
   distinct states rather than reporting both as dead. It should also show
   `new_combat_rejected: true`, proving they were not silently reactivated without recovery.

6. **`javelin_recovery`** should show outcome `agreement`, one recovered Javelin tied to its owner,
   and `completion_event_count: 1`.

Automated tests already cover natural 1, three death-save successes/failures, failed first aid,
damage while down, massive death, Temporary HP ordering, ranged-knockout rejection, stale requests,
idempotency, cross-campaign isolation, and database guards. You do not need to reproduce those
mechanical edge cases manually.

## Questions to answer

Record answers in the linked result form:

1. Are the four difficulty labels understandable as warnings rather than guarantees, and is that
   distinction acceptable?
2. Does the Second Wind result make its die, level bonus, HP cap, spent Bonus Action, and remaining
   use clear enough for a future frontend to explain?
3. Do the natural-20 revival and the separate stable/unconscious defeat states match your expected
   understanding of D&D character danger?
4. Is requiring an explicit melee knockout choice before the attack an acceptable player decision
   boundary?
5. Does the bounded completion summary contain the essential result without overwhelming detail?
6. Is automatic recovery of a thrown Javelin after victory/agreement/enemy surrender—but not after
   defeat or party flight/surrender—an acceptable initial policy?
7. Did anything feel unfair, unclear, missing, or surprising enough that M5.5 should be changed
   before provider integration?

Save the completed form and tell Codex when it is ready. M5.5 remains acceptance-pending until the
answers are analyzed.
