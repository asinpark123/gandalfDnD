# M4.5 Targeted Memory-Relevance Retest

- **Milestone state:** Accepted 2026-09-05
- **External model use:** None
- **Required action:** Read six short retrieval results and record four judgments
- **Estimated review time:** 5 minutes
- **Results form:**
  [`../testM4_5_TARGETED_RETEST_RESULTS.md`](../testM4_5_TARGETED_RETEST_RESULTS.md)
- **Why this retest exists:** The first review accepted every rank-1 result but found ranks 2–3
  repetitive and could not assess the two distinct NPCs named Mira
- **Outcome:** All four judgments and the final owner decision passed; no further M4 retest is
  required

## What changed

The retrieval engine still ranks memories with exact-vector, lexical, entity, and recency signals.
Policy `hybrid-rrf-entity-recency-1.1.0` changes only the final supporting-result selection:

1. the strongest eligible memory remains available;
2. the requested count is a maximum, not a quota;
3. an additional memory must be sufficiently strong, contain enough evidence related to the query,
   and differ meaningfully from already selected text;
4. an unclear generic chronicle is omitted rather than used to fill rank 2 or 3.

The engine may still return useful supporting context when it clears those checks. Whether and how
retrieved memories are shown directly to players remains an M7 interface decision.

The revised 500-memory fixture also contains two active, unrelated NPC interactions:

- Mira the lantern keeper arranged an Old Tower astrolabe meeting;
- Mira the Glasswood glassblower arranged a green-lantern repair in her kiln workshop.

They have different canonical UUIDs. The queries include their roles and pass the corresponding
NPC identity to the retrieval service.

## Verified technical result

The pinned local BGE model ran the revised fixture on `gandalfdnd_dev`. All hard gates passed:

- 500 eligible memories and 20 golden queries;
- 1.00 critical Recall@8, 1.00 overall Recall@8, and 1.00 mean reciprocal rank;
- 214 ms p95 against the 250 ms limit;
- no DM-only, cross-campaign, or superseded source leakage;
- identical selected source IDs after recreating the application database connections;
- no OpenClaw or paid-provider calls.

Each request below asked for at most three memories. The engine returned one because none of the
remaining candidates passed all supporting-context checks. This is expected, not a missing result.

## Retrieval samples

### 1 — Mira the lantern keeper

**Question:** What did Mira the lantern keeper promise about the brass astrolabe and Old Tower?

**Returned memory:** “Clue aurora00. At the Sunken Observatory, Mira the lantern keeper promised to
meet the party at the Old Tower with the brass astrolabe after three moon bells.”

### 2 — The blue door

**Question:** Which verse opens the blue door beneath the Lantern Archive?

**Returned memory:** “Clue aurora01. Archivist Orin taught the party that humming the Rainward
Verse opens the blue door beneath the Lantern Archive.”

### 3 — Sela's safe channel

**Question:** How can the party recognize Sela's safe channel at Ashen Quay?

**Returned memory:** “Clue aurora02. Ferryman Sela marked the safe Ashen Quay channel with three
white stones beside the broken willow.”

### 4 — Glasswood passage

**Question:** What sign requests peaceful passage from the Glasswood scouts?

**Returned memory:** “Clue aurora03. The Glasswood scouts agreed that a silver feather laid on the
north cairn requests peaceful passage.”

### 5 — The western gate

**Question:** What must happen before the rescued patrol can enter the Old Tower's western gate?

**Returned memory:** “Clue aurora04. Captain Ilyra revealed that the Old Tower bell must ring twice
before the western gate will admit the rescued patrol.”

### 6 — Mira the Glasswood glassblower

**Question:** What did Mira the Glasswood glassblower agree to repair, and where?

**Returned memory:** “In Glasswood, Mira the glassblower agreed to repair the party's cracked green
lantern at sunrise in her kiln workshop. She did not discuss the Old Tower or brass astrolabe.”

## Questions to answer

Record answers in the prepared results form:

1. Do the first five primary memories remain accurate and sufficient for their questions?
2. Is returning one relevant memory clearer and more useful than filling ranks 2–3 with the generic
   chronicles shown in the first review?
3. Do Samples 1 and 6 make the two NPCs named Mira and their separate interactions unambiguous?
4. Should M4 accept the policy “primary result plus only supporting memories that pass the quality
   checks,” while leaving direct player display design to M7?

No command, API call, database restart, or repeat fixture run is required.
