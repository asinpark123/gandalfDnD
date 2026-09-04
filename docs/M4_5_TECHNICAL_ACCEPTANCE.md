# M4.5 Technical Acceptance Evidence

- **State:** Technical gate passed; owner relevance review pending
- **Date:** 2026-09-04
- **External model calls:** 0
- **Live OpenClaw evaluation:** Not run; still requires separate authorization and a call cap
- **Automated scenario:** `tests/test_m4_memory_acceptance.py`
- **Owner fixture:** `scripts/run_m4_5_owner_fixture.py`
- **Owner checklist:** [`player/M4_5_ACCEPTANCE_CHECKLIST.md`](player/M4_5_ACCEPTANCE_CHECKLIST.md)

## Outcome

M4.5's deterministic technical gate passed. The composed lifecycle test now proves that memory
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

This is a technical pass, not yet the M4 owner sign-off. The owner should now judge whether the
returned memories feel relevant, correctly attributed, sufficiently non-repetitive, and continuous
after restart. Those judgments deliberately remain separate from vector metrics.

## Measured local fixture

| Measure | Required | Result |
| --- | ---: | ---: |
| Active corpus | at least 500 | 500 |
| Golden queries | at least 20 | 20 |
| Critical early queries | at least 5 | 5 |
| Critical Recall@8 | 1.00 | 1.00 |
| Overall Recall@8 | at least 0.90 | 1.00 |
| Mean reciprocal rank | at least 0.65 | 1.00 |
| End-to-end exact hybrid retrieval p95 | at most 250 ms | 116 ms |
| Local query embedding p95 | at most 1.5 s | 16.613 ms (retained M4.2 benchmark) |
| Context bound | at most 8 items / 6,000 source characters | enforced; owner samples used 3 items and 291–346 characters |
| Restart stability | identical selected IDs | passed for all 5 owner queries |

Plain-language definitions:

- **Recall@8:** whether the expected memory appeared anywhere in the first eight results.
- **Mean reciprocal rank (MRR):** how close expected memories were to rank 1; `1.00` means every
  expected memory was first.
- **p95 latency:** 95% of measured retrievals completed within this time; a small number may take
  longer.
- **Active corpus:** the number of eligible memories actually available to the tested index.

The owner fixture's quality activation used the same
`hybrid-rrf-entity-recency-1.0.0` policy and fixed thresholds as M4.3. No threshold was weakened.
The recorded retrieval timer includes local query embedding, database ranking, bounded selection,
and audit persistence; its 116 ms result therefore conservatively bounds the database-search
portion below the 250 ms database requirement.

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

The focused M4 run completed with:

```text
26 passed, 1 known TestClient deprecation warning in 62.77s
```

The complete repository regression run completed with:

```text
153 passed, 2 opt-in live OpenClaw tests skipped,
1 known TestClient deprecation warning in 270.40s
```

The dedicated composed test completed with:

```text
2 passed, 1 known TestClient deprecation warning in 9.19s
```

The local owner fixture created only two new isolated development campaigns:

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

## Owner-review samples

The complete questions and all rank 1–3 results are reproduced in the standalone
[`player/M4_5_ACCEPTANCE_CHECKLIST.md`](player/M4_5_ACCEPTANCE_CHECKLIST.md). Each natural-language
query returned its intended early clue at rank 1 after roughly 500 later records:

1. Mira's promise: meet at the Old Tower with the brass astrolabe after three moon bells.
2. Blue door: hum the Rainward Verse beneath the Lantern Archive.
3. Safe channel: find three white stones beside the broken willow at Ashen Quay.
4. Peaceful passage: place a silver feather on the Glasswood north cairn.
5. Western gate: ring the Old Tower bell twice before admitting the rescued patrol.

Ranks 2–3 were generally recent quest/location chronicles. Their exact text is included in the
checklist so the owner can decide whether it is useful context or repetitive noise.

## Remaining gate

M4 stays in **Verification** until the completed owner checklist is preserved and analysed. If the
owner accepts the five samples, M4 can close without an external model call. A live OpenClaw memory
coherence run is optional supplemental evidence and must be separately authorized with an explicit
maximum call count.
