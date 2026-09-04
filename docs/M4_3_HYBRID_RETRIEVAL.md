# M4.3 Hybrid Retrieval and Immutable Audit

- **Status:** Complete
- **Execution date:** 2026-09-04
- **Migration head:** `0014_memory_retrieval`
- **Ranking policy:** `hybrid-rrf-entity-recency-1.0.0`
- **Strategy:** [`M4_IMPLEMENTATION_STRATEGY.md`](M4_IMPLEMENTATION_STRATEGY.md)
- **Indexing foundation:** [`M4_2_SOURCE_INDEXING.md`](M4_2_SOURCE_INDEXING.md)

> Historical policy note: M4.5 owner evidence later introduced
> `hybrid-rrf-entity-recency-1.1.0`, which preserves this rank fusion but gates supporting results
> after rank 1. Existing `1.0.0` audits remain replayable. See
> [`M4_5_TECHNICAL_ACCEPTANCE.md`](M4_5_TECHNICAL_ACCEPTANCE.md).

## 1. Outcome

M4.3 passed. GandalfDnD now has an internal hybrid retrieval service that combines exact pgvector
cosine candidates with PostgreSQL English lexical candidates. It does not expose a player API and
does not supply memory to interpretation, narration, OpenClaw, or any other LLM. M4.4 owns that
integration boundary.

Every query filters by campaign, player audience, active document status, immutable embedding
profile, current document hash, and the lower of the requested event cutoff and indexed checkpoint
before ranking. A ready profile can be queried only through an explicit evaluation-profile path;
normal retrieval refuses it until the complete quality gate atomically activates the index.

## 2. Versioned ranking and bounds

The committed `hybrid-rrf-entity-recency-1.0.0` policy uses:

1. at most 50 exact-cosine candidates and 50 PostgreSQL full-text candidates;
2. deterministic reciprocal-rank fusion weighted 0.65 semantic and 0.25 lexical;
3. bounded 0.07 entity and 0.03 chronology signals;
4. deterministic score, sequence, and document-identity tie breaking;
5. rejection of overlapping selected source ranges; and
6. a hard maximum of 8 results and 6,000 selected content characters.

Migration `0014_memory_retrieval` adds a GIN expression index over the English search vector. Exact
vector search remains profile-filtered and deliberately has no approximate index at this corpus
size.

Selected results retain canonical document, turn/event source, and event-range citations. Exact
relational state remains authoritative and is not inferred from retrieved prose.

## 3. Audit and replay

Each successful retrieval stores its fixed ranking-policy version, SHA-256 of canonicalized query
text, complete non-secret filter/cutoff/profile evidence, count and character budgets, latency,
truncation state, selected document IDs, ranks, component scores, final scores, and selected
character counts. The raw query or provider prompt is not stored.

Replay requires the caller-held query text to match the audit hash and the embedding provider to
match the immutable audited profile. It recomputes the fixed candidate policy and verifies IDs,
ranks, component/final scores, and selected character counts. Provider/profile mismatch and query
hash mismatch fail closed.

After an index has been resolved, a retrieval/provider failure creates a safe failed audit with no
selected items or raw query. Canonical gameplay state is not involved in this service.

## 4. Quality and security evidence

The acceptance corpus contains 500 ordered player-visible records, 20 paraphrased golden queries,
five critical clues more than 400 records before the query cutoff, 480 distractors, and a tempting
near-duplicate in another campaign. The full gate ran once with deterministic embeddings and once
with the selected, checksum-verified local BGE model.

The real local BGE run measured:

- critical Recall@8: **1.00** (required 1.00);
- overall golden-source Recall@8: **1.00** (required at least 0.90);
- mean reciprocal rank: **1.00** (required at least 0.65); and
- retrieval p95: **168 ms** (required at most 250 ms).

The test first ran only 19 queries and proved the ready index remained inactive. The complete
20-query gate then activated it atomically in the isolated test database. Separate adversarial
coverage proves cross-campaign, future-sequence, superseded, overlapping-range, and wrong-profile
records cannot enter results; M4.2's source-projection tests continue to prove DM-only content never
becomes an eligible memory document.

The synthetic test data is cleared by the isolated test workflow. Development data remains exactly
115 documents and 115 embeddings across 11 ready, intentionally inactive indexes, with zero
retrieval audits. No development index was activated without campaign-specific golden evidence.

## 5. Defect found and corrected

The finalized local-model test first completed all assertions but the Python process then exited 134
because ONNX Runtime attempted to destroy a native recursive mutex during interpreter teardown.
This was a test/runtime lifecycle defect rather than a retrieval-result failure, but a non-zero
process exit is not acceptable evidence. `LocalFastEmbedProvider.close()` now releases the native
session explicitly while the interpreter is healthy, and the complete deterministic/local gate
subsequently exited zero. This is tracked as resolved `ISSUE-014`.

## 6. Verification

- 4 M4.3 cases passed, including deterministic and real-local-model parameterizations;
- all 21 M4.1–M4.3 tests passed;
- the complete suite passed: 147 passed, 2 opt-in live OpenClaw tests skipped;
- the only warning remains the previously recorded Starlette TestClient/httpx deprecation;
- lint, formatting, compilation, migration upgrade/downgrade isolation, and model/schema drift
  checks passed;
- both development and test databases are at `0014_memory_retrieval` with zero Alembic drift; and
- Clawvis, PostgreSQL 15 rollback assets, unrelated databases, and shared services were untouched.

## 7. Next boundary

M4.4 may add bounded, source-cited player-visible summaries and pass retrieved history to both
provider stages as explicitly untrusted historical prose. It must preserve exact M3 state as a
separate authoritative input and fall back safely when retrieval or summary work fails. M4.5 still
owns the broader stale-index/re-index/restart/adversarial matrix, owner relevance review, and any
separately authorized live OpenClaw memory evaluation.
