# M4.5 Memory Relevance and Continuity Owner Checklist

- **Milestone state:** Completed initial review — focused rework required
- **External model use:** None
- **Outcome:** Primary recall passed; unclear generic supporting results and an inconclusive
  same-name sample triggered ISSUE-016
- **Next review:** [`M4_5_TARGETED_RETEST.md`](M4_5_TARGETED_RETEST.md)
- **Your task:** Read the five retrieval samples below and answer the five review questions
- **Estimated review time:** 10–15 minutes
- **Results form:** [`../testM4_5_ACCEPTANCE_CHECKLIST_RESULTS.md`](../testM4_5_ACCEPTANCE_CHECKLIST_RESULTS.md)
- **Supporting evidence:** [`../M4_5_TECHNICAL_ACCEPTANCE.md`](../M4_5_TECHNICAL_ACCEPTANCE.md)

## What you need to do

You do **not** need to run a command, restart PostgreSQL, use the API, or create another test
campaign. Everything required for this review is displayed below.

1. Read each question and its three returned memory items.
2. Decide whether rank 1 answers the question accurately.
3. Decide whether ranks 2–3 add useful context or are generic/repetitive noise.
4. Record your five answers in the prepared results form.

This is a content-quality review. Automated tests have already proved campaign isolation, hidden
information exclusion, citations, context limits, stale-index behavior, and atomic re-indexing.

## How to read the samples

- **Rank 1** is the memory considered most relevant.
- **Ranks 2–3** are additional supporting memories.
- Labels such as `aurora00` are synthetic test identifiers. They help automated testing and are not
  proposed player-facing story text.
- “Branch” values are deterministic fixture data showing that memories can retain different earlier
  decisions. They are not prose intended for the final game interface.

The fixture retrieved three total memory items for each question: one primary result and two
supporting results. The provider may internally receive up to eight items when necessary, but no
frontend display default has been implemented yet.

## Retrieval samples

### Sample 1 — Mira's promise

**Question:** What did Mira the lantern keeper promise about the brass astrolabe and Old Tower?

1. **Rank 1:** “Clue aurora00. At the Sunken Observatory, Mira the lantern keeper promised to meet
   the party at the Old Tower with the brass astrolabe after three moon bells.”
2. **Rank 2:** “Chronicle 279: in Old Tower, patrol 13 advanced quest Recover the Astrolabe after
   branch mira.”
3. **Rank 3:** “Chronicle 039: in Old Tower, patrol 01 advanced quest Recover the Astrolabe after
   branch mira.”

The fixture also contained another NPC named Mira—a Glasswood glassblower with a different UUID—and
a superseded misleading record about her. Neither displaced the lantern keeper's promise.

### Sample 2 — The blue door

**Question:** Which verse opens the blue door beneath the Lantern Archive?

1. **Rank 1:** “Clue aurora01. Archivist Orin taught the party that humming the Rainward Verse opens
   the blue door beneath the Lantern Archive.”
2. **Rank 2:** “Chronicle 115: in Lantern Archive, patrol 01 advanced quest Open the Blue Door after
   branch mira.”
3. **Rank 3:** “Chronicle 400: in Lantern Archive, patrol 01 advanced quest Open the Blue Door after
   branch ridge.”

### Sample 3 — The safe channel

**Question:** How can the party recognize Sela's safe channel at Ashen Quay?

1. **Rank 1:** “Clue aurora02. Ferryman Sela marked the safe Ashen Quay channel with three white
   stones beside the broken willow.”
2. **Rank 2:** “Chronicle 347: in Ashen Quay, patrol 05 advanced quest Find the Patrol after branch
   mira.”
3. **Rank 3:** “Chronicle 077: in Ashen Quay, patrol 01 advanced quest Find the Patrol after branch
   mira.”

### Sample 4 — Peaceful passage

**Question:** What sign requests peaceful passage from the Glasswood scouts?

1. **Rank 1:** “Clue aurora03. The Glasswood scouts agreed that a silver feather laid on the north
   cairn requests peaceful passage.”
2. **Rank 2:** “Chronicle 248: in Glasswood, patrol 01 advanced quest Find the Patrol after branch
   ridge.”
3. **Rank 3:** “Chronicle 038: in Glasswood, patrol 00 advanced quest Find the Patrol after branch
   ridge.”

### Sample 5 — The western gate

**Question:** What must happen before the rescued patrol can enter the Old Tower's western gate?

1. **Rank 1:** “Clue aurora04. Captain Ilyra revealed that the Old Tower bell must ring twice before
   the western gate will admit the rescued patrol.”
2. **Rank 2:** “Chronicle 094: in Old Tower, patrol 18 advanced quest Open the Blue Door after branch
   ridge.”
3. **Rank 3:** “Chronicle 484: in Old Tower, patrol 09 advanced quest Open the Blue Door after branch
   ridge.”

## Continuity evidence already established

The application discarded its database connections and established a fresh connection pool, then
ran all five questions again. Each question returned the same source document IDs in the same
order. This was an **application database-connection restart simulation**, not a PostgreSQL server
restart or VM reboot.

The evidence establishes that the engine does not lose or silently replace selected memories when
the application reconnects. Your role is to decide whether that is the continuity behavior you
expect from persistent campaign memory; you do not need to reproduce the restart.

## Questions to answer

Use the prepared [results form](../testM4_5_ACCEPTANCE_CHECKLIST_RESULTS.md):

1. Were all five rank-1 memories relevant, specific, and accurate enough to support the next scene?
2. Looking at the actual ranks 2–3 above, should they remain as supporting context, or should the
   engine more aggressively suppress generic same-location/same-quest chronicles?
3. Was Mira the lantern keeper and her promise unambiguous despite the same-name NPC distractor?
4. Does returning the same cited sources after a fresh application database connection meet your
   expectation for persistent memory continuity?
5. For a future player-facing memory view, would you initially display all three retrieved items,
   only the primary result, or the primary result plus selected supporting context? This does not
   change the internal safety maximum of eight.

There are no predetermined “correct” answers to Questions 2 and 5. If supporting results feel
generic or repetitive, say so; that is exactly what this review is intended to detect.

## Optional full fixture reproduction

This is **not required** for acceptance. Only use it if you deliberately want another complete
technical run. It takes roughly 20–60 seconds on the development MacBook and creates two additional
isolated development campaigns rather than reusing or deleting existing campaigns.

Keep the PostgreSQL tunnel open and run from `~/Git/gandalfDnD`:

```bash
source .venv/bin/activate
python -m scripts.run_m4_5_owner_fixture --confirm-create \
  | tee /tmp/gandalf-m4-5-owner-fixture.txt
```

A successful run reports `"passed": true`, five `"expected_source_recalled": true` values,
`"restart_results_identical": true`, and all security checks as `true`. The command refuses any
database whose name does not begin with `gandalfdnd_dev`, uses the pinned local CPU embedding model,
and makes zero OpenClaw or paid-provider calls.
