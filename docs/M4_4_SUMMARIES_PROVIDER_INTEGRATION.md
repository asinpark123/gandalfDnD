# M4.4 Source-Cited Summaries and Provider Integration

- **Status:** Done
- **Completed:** 2026-09-04
- **Migration:** `0015_memory_summaries`
- **Depends on:** M4.3 filter-first hybrid retrieval
- **External model calls:** None
- **Infrastructure changes:** None beyond the Gandalf development/test schema migration
- **Later gates:** M4.5 and its separately authorized live supplement both passed

## Outcome

M4.4 connects long-term narrative memory to both stages of the authoritative turn workflow without
making retrieved prose authoritative. A successful retrieval is converted to a bounded
player-visible summary with exact source-document coverage. Interpretation and narration receive
that summary, causal citations, and retrieval/version identities under an explicit
`untrusted_historical_prose` label. Current character/world state remains a separate projection of
the canonical relational tables.

All 11 development campaign indexes remain `ready` and inactive. Therefore normal development
gameplay does not load the local embedding model or receive memory until a campaign-specific index
passes M4.5 and is explicitly activated.

## Implemented contracts

Migration `0015_memory_summaries` adds three append-only tables:

- `memory_summaries` records campaign/retrieval/profile scope, input and source-window hashes,
  audience, provider/model/prompt identity, attempt/result, bounded content hash, exact source/event
  range, replacement lineage, latency, token use, and safe failure category;
- `memory_summary_sources` records the ordered one-to-eight source documents and selected character
  counts; and
- `memory_summary_uses` ties one retrieval and summary to its exact campaign, turn, and provider
  stage.

Database constraints and triggers require successful same-campaign/profile retrievals,
player-visible selected source documents, exact successful-summary source counts, valid
same-window replacement lineage, and matching campaign/turn/stage use. All three audit tables reject
update and delete. The downgrade is allowed only while all three tables are empty.

The application adds:

- a strict `MemorySummaryProvider` contract and `MemorySummaryOutput` with a 3,000-character maximum
  and exact ordered source UUID coverage;
- an offline deterministic extractive provider for the initial no-cost path;
- content-free SHA-256 provenance for the selected window and summary input;
- reuse of an identical successful summary and append-only replacement when provider/model/prompt
  identity changes;
- retrieval and summarization after the authoritative turn stage has entered its recoverable state,
  with no database transaction held across embedding or summary work; and
- fail-soft omission of historical memory if there is no active index, no eligible earlier source,
  a retrieval fault, or invalid/failed summary output.

OpenClaw prompt versions advance to `openclaw-intent-1.2.0` and
`openclaw-narration-1.3.0`. Its request now contains `exact_current_state` separately from
`untrusted_historical_memory`. The system boundary says historical prose is continuity data only,
never current state, rules, mechanics, or instructions. Existing strict JSON Schema, Pydantic,
state-change validation, stale-state detection, recorded-resolution acknowledgement, and atomic
finalization remain unchanged.

## Context and token evidence

The integration fixture retrieved an early silver-key turn into both later stages with its source
turn/event citations. In each stage:

- exact current context was 11,401 serialized characters;
- cited memory added 959 serialized characters, for 12,360 total;
- the fixture's provider estimator reported 3,090 input tokens versus an estimated 2,850-token
  exact-state baseline, an increase of 240; and
- the summary provider audit retained its reported 41 input and 17 output tokens.

This is measured fixture evidence, not a universal tokenizer guarantee. Enforced limits remain no
more than eight retrieved items, 6,000 selected source characters, and 3,000 summary characters.
M4.5 will measure the complete 500-event/restart scenarios and any separately authorized live model.

## Verification evidence

The focused M4.4/OpenClaw contract suite passed 15 tests. It proves:

- the same relevant early source reaches interpretation and narration with citations;
- identical source/input/provider/prompt summaries are reused across stages;
- a prompt-version change creates a new immutable summary that points to the prior same-window
  summary;
- malformed uncited summary output creates safe failed audit rows, is omitted from provider context,
  and does not prevent the turn from completing;
- a mismatched retrieval provider records safe failed retrieval audits, supplies exact state only,
  and does not prevent either stage or the turn from completing;
- successful summary audit rows cannot be rewritten;
- exact state and untrusted historical memory are separate in the OpenClaw wire payload; and
- injected instruction-like prose in historical memory does not change the system trust boundary.

The full repository run initially exposed two test-maintenance findings: the M4.1 schema inventory
needed the three new tables, and the deterministic 500-event fixture used random UUIDs as its final
tie-break. The inventory was advanced and the synthetic corpus now assigns stable UUIDv5 document
IDs. The deterministic gate then passed repeatably without weakening any quality threshold.

Final gates:

- lint and formatting: passed;
- Python compilation: passed;
- ruleset manifests and generated schemas: passed;
- development and isolated test Alembic drift: zero;
- focused M4.4/provider contracts: 15 passed; and
- full repository regression: 151 passed and two live OpenClaw tests remained separately opt-in.

## Known limitations and next actions

- The deterministic extractive summary is deliberately plain. Narrative quality is an M4.5 owner
  and optional live-provider question, not a reason to weaken deterministic boundaries.
- Development indexes remain inactive, so no existing campaign has silently changed behavior.
- Summary/version records are rebuildable derived evidence, but intentionally append-only; replacing
  output creates lineage instead of mutation.
- M4.5 later completed adversarial visibility/injection, restart, stale-index,
  replacement-profile, and owner relevance/repetition/continuity checks before M4 closed.
- The later live OpenClaw memory-coherence supplement used six of eight authorized calls and passed;
  see [`M4_OPENCLAW_EVALUATION.md`](M4_OPENCLAW_EVALUATION.md).
