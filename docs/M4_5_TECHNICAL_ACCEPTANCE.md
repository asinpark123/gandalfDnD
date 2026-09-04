# M4.5 Technical Acceptance Evidence

- **State:** Accepted; M4 closed
- **Date:** 2026-09-05
- **External model calls:** 0
- **Live OpenClaw evaluation:** Not run; still requires separate authorization and a call cap
- **Automated scenario:** `tests/test_m4_memory_acceptance.py`
- **Owner fixture:** `scripts/run_m4_5_owner_fixture.py`
- **Owner checklist:** [`player/M4_5_ACCEPTANCE_CHECKLIST.md`](player/M4_5_ACCEPTANCE_CHECKLIST.md)
- **Targeted retest:** [`player/M4_5_TARGETED_RETEST.md`](player/M4_5_TARGETED_RETEST.md)
- **Accepted owner results:**
  [`testM4_5_TARGETED_RETEST_RESULTS.md`](testM4_5_TARGETED_RETEST_RESULTS.md)

## Outcome

M4.5's original deterministic technical gate passed. The composed lifecycle test proves that memory
retrieval remains safe when a player-visible source contains instruction-like hostile prose, a
DM-only event contains a stronger prompt injection, the application recreates its database
connection pool, the active index is temporarily stale, and a replacement profile with a different
vector dimension builds beside it. The old profile stays usable until the replacement is complete,
early activation is rejected, and
the final switch retires the old profile and activates the replacement atomically.

The pinned local BGE model also passed a fresh, isolated development fixture containing 500 active
documents, 20 golden paraphrase queries, five early critical clues, five locations, three quests,
two decision branches, same-name NPCs with different identities, a superseded source, a near-copy
in another campaign, and a DM-only prompt-injection event.

The owner's first review accepted all five primary results but rejected generic, repetitive ranks
2–3 and correctly identified that the fixture did not show an active interaction with its second
NPC named Mira. M4 therefore entered focused rework under ISSUE-016 rather than closing from vector
metrics alone.

Ranking policy `hybrid-rrf-entity-recency-1.1.0` now treats the requested result count as a ceiling.
It retains the primary result and admits supporting results only when they clear a relative-score
floor, query-term evidence threshold, source-range deduplication, and content-diversity threshold.
The original rank-fusion weights, candidate filters, eight-item/6,000-character safety limits, and
quality thresholds did not change. Policy `1.0.0` remains supported for replay of existing audits.

Fixture `m4.5-owner-relevance-v2` adds meaningful supporting candidates plus a separate active
Glasswood interaction for the other Mira. The pinned local model returned only the relevant primary
memory for each of six owner questions because no lower candidate cleared every support check. It
still placed all 20 golden sources first, passed the 500-memory quality gate, excluded every unsafe
source, and reproduced the same six selections after reconnecting. Targeted owner review is the
final gate; the owner completed it on 2026-09-05 and accepted every judgment.

The deterministic fixture independently verifies the complementary behavior: at least one
meaningful support item survives the new gates, while no generic `Chronicle` item enters any owner
sample. The policy therefore does not hard-code a single-result outcome.

## Measured local fixture

| Measure | Required | Initial v1 | Rework v2 |
| --- | ---: | ---: | ---: |
| Active corpus | at least 500 | 500 | 500 |
| Golden queries | at least 20 | 20 | 20 |
| Critical early queries | at least 5 | 5 | 5 |
| Critical Recall@8 | 1.00 | 1.00 | 1.00 |
| Overall Recall@8 | at least 0.90 | 1.00 | 1.00 |
| Mean reciprocal rank | at least 0.65 | 1.00 | 1.00 |
| End-to-end exact hybrid retrieval p95 | at most 250 ms | 116 ms | 214 ms |
| Local query embedding p95 | at most 1.5 s | 16.613 ms | 16.613 ms (retained M4.2 benchmark) |
| Context bound | at most 8 items / 6,000 source characters | 3 items, 291–346 characters | 1 item, 113–172 characters |
| Restart stability | identical selected IDs | all 5 questions | all 6 questions |

Plain-language definitions:

- **Recall@8:** whether the expected memory appeared anywhere in the first eight results.
- **Mean reciprocal rank (MRR):** how close expected memories were to rank 1; `1.00` means every
  expected memory was first.
- **p95 latency:** 95% of measured retrievals completed within this time; a small number may take
  longer.
- **Active corpus:** the number of eligible memories actually available to the tested index.

The first fixture used `hybrid-rrf-entity-recency-1.0.0`; the corrected fixture used version `1.1.0`
with unchanged rank-fusion and quality thresholds. The recorded retrieval timer includes local
query embedding, database ranking, bounded selection, and audit persistence; both runs therefore
conservatively bound the database-search portion below the 250 ms database requirement.

## Adversarial and lifecycle matrix

| Risk | Evidence | Result |
| --- | --- | --- |
| DM-only prompt injection | Hidden event has no memory document and never appears in selected text | Passed |
| Player-visible instruction-like prose | Remains quoted, cited `untrusted_historical_prose`; the offline OpenClaw-adapter boundary test keeps it separate from exact state | Passed |
| Cross-campaign near-copy | Candidate is excluded in SQL before ranking | Passed |
| Superseded source | Old same-name-Mira record is excluded; its active correction remains eligible | Passed |
| Repeated names / different identities | Two `Mira` NPCs have distinct UUIDs and canonical tags | Passed |
| Future/stale source | A newly projected source stays unavailable until the active profile catches up | Passed |
| Application reconnection | Stored retrieval IDs and component scores replay identically after engine disposal and fresh connections | Passed |
| Failed embedding batch | Existing retry test preserves the completed turn and records a safe category | Passed |
| Expired lease | Existing recovery test completes once without a duplicate embedding | Passed |
| Early replacement activation | Rejected while any replacement job is incomplete | Passed |
| Mixed dimensions | 72- and 104-dimension profiles coexist but are never compared; wrong-provider requests fail safely | Passed |
| Atomic re-index | Old active profile remains usable while building; one transaction retires old and activates new | Passed |
| Citation and audit coverage | Every selected item retains a canonical source; every successful selection has an immutable audit item | Passed |

## Reproducible commands and results

The corrected focused M4 run completed with:

```text
27 passed, 1 known TestClient deprecation warning in 88.24s
```

The corrected complete repository regression run completed with:

```text
154 passed, 2 opt-in live OpenClaw tests skipped,
1 known TestClient deprecation warning in 368.96s
```

The dedicated composed test completed with:

```text
2 passed, 1 known TestClient deprecation warning in 9.19s
```

Static analysis, formatting, compilation, ruleset integrity, generated-schema freshness, and
Alembic drift checks also passed. The corrected run adds one support-selection regression to the
initial 153-test baseline; it does not replace or weaken the composed lifecycle scenario.

The initial local owner fixture created only two isolated development campaigns:

- review campaign `89d7a7be-21fb-425e-abc4-47335a05bb7c`;
- adversarial neighbour `d03fdb98-a8a6-43c7-be74-b18d37db148a`.

Only the review campaign's local-BGE index became active, and only after its 20-query gate passed.
The 11 earlier development campaign indexes remain ready and inactive. The resulting development
inventory is 13 campaigns, 617 documents, 617 embeddings, 30 retrieval audits, one active review
index, and 11 ready indexes. Migration `0015_memory_summaries` remains at head with zero detected
schema drift.

The fixture is additive and refuses non-development databases. It creates no paid or network model
call. Re-running it with `--confirm-create` deliberately creates another isolated pair rather than
changing or deleting prior campaigns.

The rework fixture likewise created only two isolated development campaigns:

- review campaign `ea98c2bc-001a-462c-be30-6efc7f18e8d2`;
- adversarial neighbour `f2f1e9f4-fb13-4bb8-ba3f-60dc940db736`.

Only the new review campaign's v2 index became active after its unchanged quality gate passed. The
run made zero external-provider calls and did not modify the initial fixture campaigns.
The post-run development inventory is 15 campaigns, 1,119 documents, 1,119 embeddings, 62
retrieval audits, two active isolated review indexes, and 11 ready indexes. These are additive
development fixtures, not production campaigns.

## Owner-review samples

The complete questions and all rank 1–3 results are reproduced in the standalone
[`player/M4_5_ACCEPTANCE_CHECKLIST.md`](player/M4_5_ACCEPTANCE_CHECKLIST.md). Each natural-language
query returned its intended early clue at rank 1 after roughly 500 later records:

1. Mira's promise: meet at the Old Tower with the brass astrolabe after three moon bells.
2. Blue door: hum the Rainward Verse beneath the Lantern Archive.
3. Safe channel: find three white stones beside the broken willow at Ashen Quay.
4. Peaceful passage: place a silver feather on the Glasswood north cairn.
5. Western gate: ring the Old Tower bell twice before admitting the rescued patrol.

The first review accepted all five rank-1 results and found the generally recent quest/location
chronicles at ranks 2–3 repetitive and unclear. The exact initial evidence and answers remain in
the original checklist/results pair.

The targeted retest contains those five primary facts without filler plus an active, separately
identified Glasswood glassblower interaction. It asks only whether the correction resolves the two
owner findings; it does not repeat already established continuity or security work.

## Owner acceptance and closure

The targeted owner retest passed on 2026-09-05:

- the original five primary memories remained accurate and sufficient;
- omitting non-useful ranks 2–3 was clearer than quota-filling generic chronicles;
- the lantern keeper and Glasswood glassblower named Mira were unambiguous through role and
  narrative;
- `primary plus only qualifying support` was accepted, with direct player presentation deferred to
  M7.

No further deterministic, database, restart, security, or owner test is required for M4. A live
OpenClaw memory-coherence run remains an optional supplement, not an M4 closure requirement, and
still requires separate authorization with an explicit maximum call count.
