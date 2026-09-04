# M4.5 Memory Relevance and Continuity Owner Checklist

- **Milestone state:** Verification — technical gate passed, owner review pending
- **External model use:** None
- **What you are reviewing:** usefulness of recalled story details, not vector internals
- **Technical evidence:** [`../M4_5_TECHNICAL_ACCEPTANCE.md`](../M4_5_TECHNICAL_ACCEPTANCE.md)

## Why this review is needed

Automated tests can prove secrecy, citations, restart stability, context limits, and exact quality
metrics. They cannot decide whether a set of supporting memories feels helpful or annoyingly
repetitive to a player. This short review is the final deterministic M4 checkpoint.

The fixture has already run locally without OpenClaw and without paid API use. It placed five old
clues near the beginning of a 500-document campaign, then asked natural paraphrased questions after
the long intervening history. Each intended clue returned at rank 1, and the exact result IDs were
unchanged after a database restart simulation.

## Actions

1. Read the five first-ranked memories in the **Reviewable first-ranked memories** section of
   [`../M4_5_TECHNICAL_ACCEPTANCE.md`](../M4_5_TECHNICAL_ACCEPTANCE.md). Confirm each one directly
   answers its corresponding question rather than merely sharing similar words.
2. Review the note about ranks 2–3. They were recent chronicles sharing the relevant location or
   quest. Decide whether that feels like useful background, acceptable harmless context, or
   repetitive noise that should be reduced before M4 closes.
3. Confirm the first result clearly identifies **Mira the lantern keeper** and her exact promise.
   The fixture also contains another NPC named Mira, with a different UUID and role, plus a
   superseded misleading record. Neither displaced the correct rank-1 result.
4. Confirm that preserving the same selected source IDs before and after restart is the continuity
   behavior you expect. The prose is not regenerated during restart; the cited source remains the
   same immutable campaign record.
5. Consider the context boundary: the samples supplied three cited items and 291–346 source
   characters, while the hard maximum is eight items and 6,000 characters. Say whether three items
   feels like a sensible initial default for a future player-facing view, even though the provider
   is allowed to receive up to eight when needed.

You do not need to repeat the 500-record generation, database restart, injection, cross-campaign,
supersession, stale-index, or re-index tests. Those are automated assertions and have passed.

## Subjective review

Record concise answers to these five questions:

1. Were all five rank-1 memories relevant and specific enough to support the next scene?
2. Should ranks 2–3 remain as supporting context, or should the engine become stricter about
   suppressing generic same-location/same-quest chronicles?
3. Was the correct Mira and her promise unambiguous despite the same-name NPC distractor?
4. Does exact citation continuity across restart meet your expectation for persistent memory?
5. Is three displayed supporting memories a sensible initial player-facing default, while retaining
   the internal maximum of eight?

Save the answers in `docs/testM4_5_ACCEPTANCE_CHECKLIST_RESULTS.md`, or send them directly for
preservation and analysis. Any requested ranking adjustment will be treated as M4 rework and tested
against the unchanged secrecy, quality, and latency thresholds.

## Optional fixture reproduction

This is not required for the review. If you intentionally want to create a fresh isolated copy of
the entire fixture, keep the PostgreSQL tunnel open and run from `~/Git/gandalfDnD`:

```bash
source .venv/bin/activate
python -m scripts.run_m4_5_owner_fixture --confirm-create \
  | tee /tmp/gandalf-m4-5-owner-fixture.txt
```

The command refuses any database whose name does not begin with `gandalfdnd_dev`, creates two new
campaigns without changing existing ones, uses the pinned local CPU embedding model, and makes zero
OpenClaw or paid-provider calls.
