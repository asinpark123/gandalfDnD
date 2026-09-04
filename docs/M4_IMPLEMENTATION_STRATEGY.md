# M4 Long-Term Memory and Retrieval Implementation Strategy

- **Status:** Done (accepted 2026-09-05)
- **Prepared:** 2026-09-04
- **Depends on:** M3 persistent world (Done, including live OpenClaw supplement)
- **Infrastructure audit:** [`M4_POSTGRES_PGVECTOR_AUDIT.md`](M4_POSTGRES_PGVECTOR_AUDIT.md)
- **Database longevity strategy:** [`POSTGRESQL_18_MIGRATION_STRATEGY.md`](POSTGRESQL_18_MIGRATION_STRATEGY.md)
- **PG18.0 evidence:** [`POSTGRESQL_18_READINESS_AUDIT.md`](POSTGRESQL_18_READINESS_AUDIT.md)
- **PG18 execution evidence:**
  [`POSTGRESQL_18_FOUNDATION_EXECUTION.md`](POSTGRESQL_18_FOUNDATION_EXECUTION.md)
- **PG18 development evidence:**
  [`POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md`](POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md)
- **PG18 cutover evidence:** [`POSTGRESQL_18_CUTOVER_EXECUTION.md`](POSTGRESQL_18_CUTOVER_EXECUTION.md)
- **M4.1 evidence:** [`M4_1_MEMORY_FOUNDATION.md`](M4_1_MEMORY_FOUNDATION.md)
- **M4.2 evidence:** [`M4_2_SOURCE_INDEXING.md`](M4_2_SOURCE_INDEXING.md)
- **M4.3 evidence:** [`M4_3_HYBRID_RETRIEVAL.md`](M4_3_HYBRID_RETRIEVAL.md)
- **M4.4 evidence:**
  [`M4_4_SUMMARIES_PROVIDER_INTEGRATION.md`](M4_4_SUMMARIES_PROVIDER_INTEGRATION.md)
- **M4.5 technical evidence:**
  [`M4_5_TECHNICAL_ACCEPTANCE.md`](M4_5_TECHNICAL_ACCEPTANCE.md)
- **Supplemental live evidence:**
  [`M4_OPENCLAW_EVALUATION.md`](M4_OPENCLAW_EVALUATION.md)
- **Owner input required next:** None for M4
- **Owner checkpoint:** Completed 2026-09-05

## 1. Objective

M4 will let a long-running campaign recall relevant earlier conversations and narrative events
without sending full history to a model. It adds rebuildable, versioned narrative memory beside the
exact relational world established in M3.

M4 does not make vector search authoritative. Current HP, inventory, location, NPC presence, facts,
quests, decisions, factions, time, rules, and dice continue to come from their canonical tables.
Retrieved prose may inform interpretation and narration, but cannot establish a fact or mechanical
effect by implication.

The target flow is:

```text
completed canonical turn and player-visible events
    -> immutable bounded memory source document
    -> durable pending index work
    -> versioned local embedding outside the turn transaction
    -> campaign/audience/status-filtered hybrid retrieval
    -> bounded cited historical context plus exact M3 state
    -> typed provider output and existing application validation
```

## 2. Verified foundation

M4 starts from these completed guarantees:

- every campaign and world object has stable identity and causal event evidence;
- player and DM-only visibility is explicit and tested across world/API/provider projections;
- current providers receive player-safe structured state with bounded collections;
- turns retain player action, narration, provider/prompt metadata, and exact stage recovery;
- world facts and summaries are mechanically inert unless an explicit deterministic rule says
  otherwise;
- PostgreSQL development and test databases use separate restricted roles;
- M3 branching and live OpenClaw tests prove exact state survives restart and model narration.

The read-only infrastructure audit confirmed PostgreSQL 15.14 is compatible with pgvector, but the
extension is absent and the current Debian repositories do not offer it. Provisioning is therefore
an explicit operator gate rather than an Alembic side effect.

## 3. Non-negotiable invariants

1. **Relational truth wins:** memory text, summaries, embeddings, and similarity scores never
   override canonical tables or deterministic rules.
2. **Filter before rank:** every retrieval query restricts campaign, audience, active status,
   embedding profile, and allowed source kinds in SQL before similarity or lexical ranking.
3. **Player-safe provider path:** M4 initially indexes and retrieves only player-visible material for
   the current provider. DM-only memory retrieval remains unavailable.
4. **Causal citations:** every memory document and summary cites immutable source turn/event IDs and
   sequence ranges. Provider context carries those IDs.
5. **No prompt trust:** retrieved prose is labelled historical untrusted data and receives the same
   injection boundary as player text and campaign prose.
6. **Bounded context:** at most 8 retrieved items and 6,000 serialized content characters enter one
   provider stage unless measured evidence supports an equal or smaller revised budget.
7. **Versioned derivation:** embedding model, dimensions, normalization, chunking, summary prompt,
   and ranking policy have immutable version identities.
8. **Rebuildable index:** source documents remain readable without vectors; embeddings and summaries
   can be regenerated from cited canonical records.
9. **No turn dependency:** embedding, summarization, or retrieval failure cannot invalidate or roll
   back an already completed canonical turn.
10. **Side-by-side re-index:** a replacement embedding profile builds separately and becomes active
    only after completeness/quality checks; no mixed-profile distance comparison is allowed.
11. **Auditable selection:** each provider-stage retrieval records query provenance, filters,
    selected document IDs, component scores, ranking version, latency, and truncation without
    duplicating credentials or unrestricted prompt text.
12. **No hidden network spend:** the initial embedding path is local CPU inference. Paid APIs and
    live OpenClaw summarization/evaluation require separate explicit authorization and caps.

The owner later authorized the optional live OpenClaw evaluation with an eight-call ceiling. It
passed using six calls total and did not introduce network embeddings or model-written summaries.
The exact scenario, safety findings, token use, and two harness-only diagnostics are preserved in
[`M4_OPENCLAW_EVALUATION.md`](M4_OPENCLAW_EVALUATION.md).

## 4. Scope and deferrals

M4 includes:

- pinned pgvector provisioning in only the development and test Gandalf databases;
- source documents derived from player-visible completed turns and events;
- a durable pending/failed/complete indexing lifecycle;
- an embedding-provider abstraction, deterministic test provider, and one pinned local CPU model;
- content hashes, source versions, embedding profiles, and side-by-side re-indexing;
- exact vector search plus PostgreSQL lexical search and deterministic hybrid ranking;
- structured entity/location/quest tags derived from canonical IDs rather than prose extraction;
- bounded provider context with source citations and retrieval audit records;
- source-bound hierarchical summaries for older player-visible history;
- restart, failure, visibility, injection, quality, latency, and 500-event evidence.

M4 does not include:

- using retrieved text as current HP, inventory, location, presence, quest, decision, or rules state;
- DM-only planning context or secret-aware narration;
- the separate spoiler-safe Guide service (M6);
- approximate HNSW/IVFFlat indexes before exact-search evidence shows they are necessary;
- Qdrant, Pinecone, Elasticsearch, a graph database, Redis, Celery, Kafka, Docker, or another worker
  framework;
- model-written mechanical consequences, autonomous retconning, or deletion of event history;
- embedding the full SRD or research archive as campaign memory;
- a frontend memory journal or player controls (M7).

## 5. Data model direction

M4.1 validated these names and boundaries in migration `0012_memory_foundation` and focused tests.

### 5.1 `memory_documents`

One immutable bounded text unit derived from a completed canonical source:

- UUID, campaign ID, source kind, source turn/event ID, and event sequence range;
- player visibility only in the initial implementation;
- bounded content, SHA-256, chunker version, and active/superseded status;
- optional canonical location, NPC, character, quest, decision, and faction UUID tags;
- source world revision/time where available;
- unique source/version/chunk identity for idempotent extraction.

A completed turn should normally become one document containing the bounded player action and final
narration, with its player-visible events represented as citations/tags rather than duplicate prose.
Standalone non-turn player events may become their own document. Provider errors, audits,
credentials, raw hidden payloads, and mechanically redundant JSON dumps are not memory content.

### 5.2 `memory_embedding_profiles` and `memory_embeddings`

An immutable profile records provider kind, exact model/revision, artifact checksum/license,
dimensions, normalization/distance policy, and application adapter version. Embeddings reference a
document and profile, retain the document hash they were computed from, and store a PostgreSQL
`vector` plus timestamps/status.

Use the unconstrained `vector` type initially so a new profile with different dimensions can be
built side by side. Retrieval must filter one profile before applying cosine distance. At the
500-event scale, use exact scans; add an approximate index only after measured need and a new ADR.

### 5.3 `campaign_memory_indexes`

Track each campaign/profile build independently:

- building, ready, active, failed, or retired status;
- indexed-through source event sequence and source count;
- last error category and safe retry metadata;
- quality-gate result and activation timestamp.

Only one profile is active for a campaign. Activation is atomic after every eligible source through
the chosen checkpoint is embedded and the golden retrieval gate passes.

### 5.4 `memory_index_jobs`

Durable idempotent jobs identify document/profile work as pending, claimed with a short lease,
complete, or failed. This reuses the proven M2 lease principles without adding a distributed queue.
A bounded service/CLI drains jobs outside canonical turn transactions. Expired claims can be
recovered; repeated work upserts the same document/profile identity.

### 5.5 `memory_summaries`

Summaries are derived, mechanically inert documents with:

- campaign, audience, source sequence range, and cited source document IDs;
- summary/prompt/provider/model versions and content hash;
- active/superseded status and replacement provenance;
- a maximum input range and output length.

M4 initially creates player-visible summaries only from player-visible inputs. A summary can make
history cheaper to recall but cannot replace its source citations or become a world fact.

### 5.6 `memory_retrievals` and selected items

One audit row per retrieval records campaign, turn/provider-call stage, active embedding profile,
ranking policy, safe query-source hash, filters, requested/returned counts, latency, and context
budget. Child rows preserve ranked document/summary IDs plus semantic, lexical, recency/entity, and
combined scores.

The original player action already exists on the turn, so the audit should reference it rather than
copy unrestricted query text. This keeps reconstruction possible without creating another prompt
log.

## 6. Source extraction and indexing lifecycle

1. A canonical turn completes and commits without waiting on an embedding service.
2. After that commit, a separate idempotent projection transaction records pending work keyed to the
   source. A checkpoint scanner/backfill detects any completed source missed by that best-effort call;
   the canonical transaction never depends on the memory tables.
3. After commit, a bounded local indexing call reads the player-safe source projection, creates the
   immutable document and tags, and computes the embedding with no database transaction held open.
4. A short transaction checks the document hash/profile, stores the vector, completes the job, and
   advances the campaign/profile checkpoint.
5. Failure leaves the turn valid and the job retryable with a stable safe category. It never inserts
   a partial vector or activates an incomplete profile.
6. The local development runtime may drain a small number of pending jobs after a response or before
   the next turn. A CLI supports explicit backfill and recovery. No in-memory-only queue is the
   source of truth.

Deletion is not the ordinary correction mechanism. If canonical visibility or source eligibility
changes, a projection job supersedes the derived document and removes it from active retrieval while
retaining audit provenance. Re-indexing regenerates from eligible canonical sources.

## 7. Embedding strategy

The application receives an `EmbeddingProvider` abstraction with batch document embedding and
single-query embedding methods. Tests use a deterministic fixed-vector provider and never download
a model or call a network service.

The first real provider will run locally on the MacBook CPU so routine indexing/querying creates no
API charges and does not depend on Clawvis. Before selecting it, M4.2 will benchmark a small,
English-focused 384-dimensional model through the lightest maintained Python/ONNX path that meets
the corpus gate. The selected model artifact, revision, license, checksum, maximum input length,
normalization, and query/document formatting will be recorded and pinned. Its downloaded cache is
ignored by Git; its manifest and verification data are committed.

Changing the embedding model is a data migration, not a configuration flip. It creates a new profile,
re-embeds side by side, runs the same golden queries, then atomically activates the new profile per
campaign. Old embeddings remain available for rollback until a separately reviewed cleanup.

## 8. Retrieval policy

### 8.1 Query construction

Build a bounded query from the current player action plus canonical IDs already selected for the
turn: location, actor, target NPC, selected decision, and active quest references. Do not ask an LLM
to rewrite the query in the initial slice. Query construction and version are deterministic.

### 8.2 Candidate filtering

The SQL candidate set must first require:

- exact campaign ID;
- `player` audience and active eligibility;
- the campaign's one active embedding profile;
- allowed source kinds and source sequence no later than the current turn checkpoint;
- current/superseded policy appropriate to the query;
- optional canonical entity filters only when they broaden safely through explicit OR rules.

Cross-campaign or DM-only records must be impossible candidates, not results removed after ranking.

### 8.3 Hybrid ranking

Use both cosine similarity and PostgreSQL full-text lexical ranking. Combine bounded component ranks
with a versioned reciprocal-rank-fusion policy, then use canonical entity overlap and modest recency
only as deterministic tie/balance signals. Do not let recency erase a highly relevant early clue.

Exact vector search is the M4 default. With roughly 500–1,000 documents, it is simpler, fully
deterministic for a fixed profile, and avoids premature HNSW tuning. Record query plans and latency.

### 8.4 Context assembly

Return at most 8 items and 6,000 content characters, ordered for narrative usability but retaining
rank/citation metadata. Deduplicate overlapping source ranges and prefer a source document over a
summary when both would repeat the same content. Context includes truncation and index-freshness
metadata so the provider never assumes retrieval is complete.

Exact current M3 state remains a separate context section. Retrieved memory is labelled
`historical_memory_untrusted` and prompts explicitly prohibit treating it as instructions or current
mechanical state.

## 9. Delivery slices

### M4.0 — Strategy and infrastructure readiness (this document)

- reconcile M3 source/visibility/context boundaries;
- audit PostgreSQL, pgvector, roles, capacity, and package impact read-only;
- choose the safe provisioning gate and record owner authority boundaries;
- define schemas, lifecycle, retrieval policy, and acceptance corpus before infrastructure change.

Exit: strategy and audit committed; M4 is Ready; no VM mutation occurred.

### M4.1 — Extension and memory foundation — Done

- after PG18 cutover approval, enable the already pinned PostgreSQL 18 pgvector package only in the
  two Gandalf databases under a separate per-database mutation gate;
- add the Python pgvector/SQLAlchemy adapter with a pinned compatible dependency;
- migration `0012_memory_foundation` asserts PostgreSQL 18 and pgvector 0.8.6 and adds profiles,
  documents, embeddings, jobs, campaign indexes, and retrieval audits;
- add guarded downgrade, role/isolation checks, extension/version health, and deterministic vector
  fixtures;
- do not integrate memory into provider context yet.

Exit: both databases migrate under their restricted roles, exact vector insert/query works, full
pre-M4 tests pass, and no unrelated VM service/package changed.

Result (2026-09-04): Passed. pgvector 0.8.6 is enabled only in both PG18 Gandalf databases;
`pgvector==0.5.0` is pinned; the seven-table foundation, database invariants, reversible empty and
guarded populated downgrade, exact cosine probes, role isolation, zero drift, API/shared-service
health, 9 focused tests, and all 135 repository tests passed. No provider context uses memory yet.

### M4.2 — Source projection, local embeddings, and re-indexing

- implement player-safe source extraction and canonical tags;
- implement deterministic and pinned local embedding providers;
- add leased idempotent indexing plus bounded CLI/backfill paths;
- support failure/retry, content-hash no-op, engine restart, and side-by-side profile builds;
- commit the local model manifest/license/checksum policy, not model weights.

Exit: eligible sources index exactly once, hidden/error sources never index, failure does not affect
turns, and a new profile can build without altering the active profile.

Result (2026-09-04): Passed. Completed-turn projection, canonical tags, content hashes, deterministic
and checksum-verified local providers, leased jobs, bounded backfill/recovery, failure safety,
restart recovery, and side-by-side activation guards pass. BGE small English v1.5 was selected at
an immutable quantized ONNX revision; its 64 MiB local artifact produced 384-dimensional vectors at
16.613 ms warm p95 on the MacBook. Development backfill created and embedded exactly 115 documents
across 11 ready, inactive builds. Migration `0013_memory_lifecycle` repaired the M4.1 shared-trigger
record-shape defect. Memory remains outside provider context.

### M4.3 — Hybrid retrieval and audit

- implement filter-before-rank SQL, lexical plus cosine candidates, versioned rank fusion, and
  entity/recency signals;
- enforce top-count/character budgets and source-range deduplication;
- store reconstructable retrieval selections/scores without duplicating raw prompts;
- expose an internal/test retrieval service; do not yet let results affect provider calls.

Exit: golden queries meet quality/security/latency thresholds on a 500-event corpus, and retrieval
audits replay to the same candidate policy for a fixed profile.

Result (2026-09-04): Passed. Migration `0014_memory_retrieval` adds the English GIN lexical index;
the internal `hybrid-rrf-entity-recency-1.0.0` service filters campaign, audience, active status,
profile, current hash, and indexed event cutoff before exact cosine and lexical ranking. It enforces
8-item/6,000-character and overlapping-source bounds, stores raw-query-free immutable score audits,
and replays IDs and scores. Both deterministic and pinned local BGE gates passed a 500-record,
20-paraphrase corpus with five early critical clues. Local BGE achieved 1.00 critical/overall
Recall@8, 1.00 MRR, and 168 ms p95. Development's 11 ready indexes remain inactive; no memory
reaches a provider.

### M4.4 — Summaries and provider integration

- create source-cited player-visible summary windows with immutable prompt/provider versions;
- validate summary input audience, output bounds, source coverage, replacement, and failure safety;
- insert bounded retrieved memories into interpretation and narration as untrusted historical data;
- preserve M2/M3 transaction, stale-state, prompt-injection, structured-output, and atomicity rules;
- measure context size and provider token use against the pre-M4 baseline.

Exit: a relevant early event reaches both stages with citations, exact current state stays separate,
and malformed/failed retrieval or summary work safely falls back to exact state.

Result (2026-09-04): Passed. Migration `0015_memory_summaries` adds immutable summary, ordered
source, and stage-use evidence with database-enforced audience, retrieval/profile/campaign,
coverage, replacement, and append-only constraints. A strict deterministic provider produces or
reuses source-complete summaries; failures are audited and omitted without failing gameplay. Both
provider stages receive a labelled cited memory envelope beside separate exact state. OpenClaw
prompt versions `openclaw-intent-1.2.0` and `openclaw-narration-1.3.0` additionally separate the
wire fields and reject historical prose as instructions/current state. The fixture added 959
serialized characters and an estimated 240 provider input tokens per stage over its pre-memory
exact-state baseline. The focused 15-test gate passed without an external model call; all 11
development indexes remain inactive. All 151 normal regression tests passed; the two prior live
OpenClaw evaluations remained separately opt-in.

### M4.5 — Re-index, 500-event, owner, and optional live gates

- complete the full synthetic campaign, adversarial visibility/injection, restart, and re-index
  matrix;
- prove a replacement embedding profile cannot activate early or mix dimensions;
- provide an owner checklist focused on relevance, repetition, and continuity rather than raw vector
  internals;
- request separate authorization and a call cap before any live OpenClaw memory evaluation.

Exit: all M4 technical thresholds pass, owner feedback is recorded, and any authorized live
supplement is classified separately from deterministic correctness.

Result (2026-09-04): Technical gate passed; owner review pending. The composed lifecycle fixture
proves hidden and player-visible injection boundaries, restart replay, stale-index behavior, and
atomic side-by-side replacement across different vector dimensions. A fresh pinned-local-BGE
development corpus passed 20/20 golden queries with 1.00 critical and overall Recall@8, 1.00 MRR,
116 ms end-to-end retrieval p95, zero hidden/cross-campaign/superseded leakage, and identical five-query results
after restart. The focused M4 suite reports 26 passed and the complete suite reports 153 passed plus
two intentionally skipped live OpenClaw tests, without an external model call. The isolated
review campaign is the only active development memory index; the 11 pre-existing indexes remain
ready and inactive. See [`M4_5_TECHNICAL_ACCEPTANCE.md`](M4_5_TECHNICAL_ACCEPTANCE.md) and
[`player/M4_5_ACCEPTANCE_CHECKLIST.md`](player/M4_5_ACCEPTANCE_CHECKLIST.md).

Rework result (2026-09-05): the owner accepted all primary memories but rejected repetitive,
unclear supporting chronicles and could not assess the second same-name NPC from fixture v1.
Ranking policy `hybrid-rrf-entity-recency-1.1.0` makes requested count a ceiling and requires every
supporting candidate to clear relative-score, query-term-evidence, and content-diversity checks.
Existing `1.0.0` audits remain replayable. Fixture v2 adds a separate active Glasswood interaction
for the second Mira. Its pinned-local-BGE run kept 1.00 critical/overall Recall@8 and 1.00 MRR,
passed at 214 ms p95, excluded all unsafe sources, and returned six identical relevant-only results
after reconnection. The completed review is preserved in
[`player/M4_5_TARGETED_RETEST.md`](player/M4_5_TARGETED_RETEST.md).

Owner closure (2026-09-05): Accepted. Primary recall remained accurate, relevant-only selection was
clearer, the two Miras were unambiguous, and `primary plus only qualifying support` was approved.
The owner also required M7 to present useful supporting memories when available. ISSUE-016 is
closed, no further M4 retest is required, and any live OpenClaw run is supplemental rather than an
exit gate.

Supplemental live result (2026-09-05): Passed. After separate authorization, six of eight allowed
OpenClaw calls verified cited recall for both role-specific Miras, inert treatment of a hostile
historical quotation, DM-only exclusion, database reconnection, and unchanged canonical state. Two
harness-only diagnostics are counted and documented; neither changed application behavior or
Clawvis. See [`M4_OPENCLAW_EVALUATION.md`](M4_OPENCLAW_EVALUATION.md).

## 10. Synthetic corpus and acceptance metrics

The acceptance fixture must contain at least 500 chronologically ordered player-visible events or
turn-derived documents across several locations, NPCs, quests, and decision branches, plus:

- at least 20 golden paraphrased queries with known cited relevant sources;
- at least 5 important early clues more than 400 source events before the query;
- lexically similar distractors involving different NPC/location/quest UUIDs;
- superseded narrative records and repeated names with different UUIDs;
- a second campaign with tempting near-duplicate content;
- DM-only records containing both likely keywords and prompt-injection text;
- a restart, failed embedding batch, expired job lease, stale index, and side-by-side re-index.

Minimum M4 gate:

- 100% of designated critical clues appear within the top 8;
- overall golden-source Recall@8 is at least 0.90 and mean reciprocal rank at least 0.65;
- zero DM-only, cross-campaign, future-sequence, inactive/superseded-disallowed, or wrong-profile
  results across the adversarial suite;
- provider context contains at most 8 memory items and 6,000 memory-content characters and never
  includes full campaign history;
- warm exact-search database latency p95 is at most 250 ms for the 500-event fixture on the audited
  VM; local query embedding p95 is recorded and must be at most 1.5 seconds on the development
  MacBook before activation;
- re-index activation is atomic and the old profile remains usable until the replacement passes;
- every selected item cites a canonical source and every retrieval has an audit row;
- all M0–M3 tests, ruleset/schema integrity, migrations, and dual-database drift checks remain green.

Quality thresholds may be made stricter from evidence. Weakening them requires an explicit recorded
decision and failure analysis, not tuning against hidden test answers.

## 11. Failure and observability policy

Stable categories should distinguish extension unavailable/version mismatch, embedding model
unavailable, invalid vector dimensions/nonfinite values, index job lease conflict/expiry, source
hash drift, incomplete profile, retrieval timeout, and malformed summary output.

Observability records counts/latency by extraction, embedding, retrieval, and summary stage; pending
and failed job age; indexed-through event lag; context items/characters; ranking version; and local
model/profile. Never log gateway tokens, embedding artifacts, DM-only content on player paths, or
full unrestricted prompts.

Retrieval failure is fail-soft for gameplay: use exact current state and omit historical memory with
a safe internal audit. Extension/schema corruption, visibility-filter failure, mixed-profile search,
or cross-campaign output is fail-closed and blocks the memory path until repaired.

## 12. Owner checkpoints

Owner input is required at three bounded points:

1. **M4.1 complete:** the bounded extension, adapter, migration, recovery, rollback, isolation, and
   regression gate passed. PostgreSQL 15 rollback copies, retirement, deletion, and unrelated
   services remained excluded.
2. **M4.2 model selection (resolved):** BGE small English v1.5 clearly met the recorded size,
   license, input, maintenance, CPU, and no-cost bounds. The exact model/runtime revision and every
   artifact checksum are committed. The M4.3 synthetic corpus gate passed; M4.5 retains the broader
   adversarial/re-index and owner relevance gate.
3. **M4.5 acceptance:** test whether recalled details feel relevant, correctly attributed,
   non-repetitive, and consistent after restart. Live OpenClaw testing remains a separate opt-in
   decision with a maximum-call budget.

No player input is needed for table/index implementation details that remain inside these accepted
boundaries.

## 13. Completion rule

Each slice must update this strategy and the living plan with schema/version identities, evidence,
quality/latency results, defects, workarounds, and next actions. M4 moves to Rework if any later test
shows hidden/cross-campaign retrieval, uncited memory, mixed profiles, canonical-state substitution,
unbounded context, or a completed turn depending on index availability.

M4 is complete. The corrected technical gate and focused owner retest are preserved, and all exit
criteria pass. Paid or network embeddings, live OpenClaw evaluation, PostgreSQL 15 retirement, and
unrelated-service changes remain outside the current authority boundary.
