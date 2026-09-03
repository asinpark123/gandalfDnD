# M4.2 Player-Safe Source Indexing and Local Embeddings

- **Status:** Complete
- **Execution date:** 2026-09-04
- **Migration head:** `0013_memory_lifecycle`
- **Source projection:** `completed-source-1.0.0`
- **Deterministic profile:** `deterministic-hash-v1`
- **Local profile:** `local-bge-small-en-v1.5-q-v1`
- **Runtime:** `fastembed==0.8.0`, ONNX CPU execution only
- **Strategy:** [`M4_IMPLEMENTATION_STRATEGY.md`](M4_IMPLEMENTATION_STRATEGY.md)
- **Foundation:** [`M4_1_MEMORY_FOUNDATION.md`](M4_1_MEMORY_FOUNDATION.md)

## 1. Outcome

M4.2 passed. Every newly completed turn is now offered to a separate fail-soft projection
transaction after canonical gameplay has committed. The durable scanner can recover anything that
the best-effort hook misses. Failed, cancelled, incomplete, and eventless turns are ineligible.

One immutable player-visible document contains bounded player action plus final GM narration. It
cites the exact visible event range and records canonical character, NPC, location, quest, decision,
faction, world-revision, and narrative-time tags where the completed source establishes them.
DM-only events, hidden dice, provider errors, credentials, raw provider payloads, and mechanical JSON
dumps are never copied into document text. Documents are capped at 6,000 characters and hashed;
targeted re-projection is a no-op for the same hash and fails closed on drift.

Durable jobs now move through pending, claimed-with-lease, complete, or safely classified failed
states. Local inference occurs with no database transaction open. Expired claims recover after a
restart, retries upsert one document/profile vector, and profile progress becomes ready only when
every active eligible document has a matching current hash. A replacement profile builds beside the
old profile; the tested activation transaction refuses incomplete work, retires the previous active
index atomically, and retains its embeddings for rollback. The operational CLI intentionally does
not expose activation until M4.3 implements the real retrieval-quality gate.

Memory still does not enter interpretation or narration. That remains M4.4 work.

## 2. Local model decision

The measured comparison selected `BAAI/bge-small-en-v1.5` through Qdrant's quantized ONNX artifact
and FastEmbed. It was clearly preferable inside the accepted M4.2 bounds, so no owner choice was
needed:

| Candidate | Dimensions / maximum input | Artifact size | License | Decision |
| --- | --- | ---: | --- | --- |
| BGE small English v1.5 | 384 / 512 tokens | 0.067 GB | MIT upstream | Selected: smallest candidate, retrieval-oriented, current FastEmbed default |
| all-MiniLM-L6-v2 | 384 / 256 tokens | 0.090 GB | Apache-2.0 | Rejected: larger and shorter input limit |
| E5 small v2 | 384 / 512 tokens | about 0.133 GB ONNX | MIT | Rejected: roughly twice the selected artifact size and not in FastEmbed's current small-model list |

Primary references: [FastEmbed supported models](https://qdrant.github.io/fastembed/examples/Supported_Models/),
[FastEmbed repository](https://github.com/qdrant/fastembed),
[BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5), and
[pinned Qdrant ONNX artifact](https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q/tree/c32e6154d1bb7a0e47c5e745fd895e7700f44385).

The repository manifest at
`resources/embedding_models/bge-small-en-v1.5.json` pins the complete 40-character revision, all
seven required file sizes and SHA-256 values, 384 dimensions, 512-token limit, normalization,
query/document methods, license, CPU provider, and adapter version. The ONNX model hash is
`51f1bd0addd6e859e42c2c8021a5e5461385bb676a649f4b269aa445449f2431`.

The model download is 67,411,945 bytes (64 MiB on disk) and remains under
`.cache/embedding_models/`, excluded from Git. The download helper requests only the seven listed
files from the exact revision; the runtime uses `local_files_only=True` and verifies every file
before loading. FastEmbed's alternative archive-download path is not used.

MacBook ARM64 evidence, two ONNX threads:

- cold provider load: 0.067 seconds;
- warm one-query median across 20 queries: 14.868 ms;
- warm one-query p95: 16.613 ms;
- maximum observed: 16.635 ms;
- output: finite, L2-normalized, 384-dimensional vectors.

This is comfortably below the M4 activation ceiling of 1.5 seconds. Corpus retrieval quality is not
claimed yet; M4.3 and M4.5 own the golden-query and 500-event gates.

## 3. Operations and deployment

For a fresh deployment, install the pinned project dependencies, then make the one explicit model
download:

```bash
python scripts/fetch_embedding_model.py
```

The helper verifies the cache before returning. There is no API key, model service, GPU, OpenClaw,
or recurring network charge. A deployment may choose another cache path with `--destination` and
the matching `GANDALF_EMBEDDING_MODEL_DIR` setting.

Backfill and build are separate, bounded actions:

```bash
python -m app.memory_cli backfill --limit 1000
python -m app.memory_cli build CAMPAIGN_UUID
python -m app.memory_cli drain --limit 1000
python -m app.memory_cli recover
```

`backfill` and `recover` do not load the model. `build` verifies the selected local model and creates
durable work for one campaign. `drain` claims a bounded batch and can be repeated safely. For offline
lifecycle diagnostics only, place `--provider deterministic` before the subcommand.

Do not manually change index status or activate the ready local profile. M4.3 will connect activation
to measured completeness and retrieval-quality evidence.

## 4. Development data evidence

The development database migrated from `0012_memory_foundation` to
`0013_memory_lifecycle`. Its 115 completed turns across 11 campaigns produced exactly 115 bounded
documents and 115 local embeddings. All jobs completed, all 11 campaign/profile builds are ready,
and zero builds are active. No existing turn, event, world state, provider call, or relational rule
record changed.

The test database also reached `0013_memory_lifecycle`. PostgreSQL 15 rollback copies, PG18 service
configuration, extensions, roles, unrelated databases, Bluebuild, and Clawvis were untouched.

## 5. Defect found and corrected

The first lifecycle run exposed `ISSUE-013` in the M4.1 shared identity trigger. Its function served
both `campaign_memory_indexes` and `memory_index_jobs`, but referenced `OLD.document_id` in a branch
for jobs. PostgreSQL resolves the record field for an index-row update even when the table-name
predicate is false, so a legitimate index progress update failed with `record OLD has no field
document_id`.

Migration `0013_memory_lifecycle` splits the trigger into one table-specific function per record
shape. The fresh-install definition in `0012` is corrected too, while `0013` repairs already-migrated
databases. Both index and job identity remain immutable; lifecycle fields now update normally.

The new post-commit source projection also caused two older M3 downgrade tests to encounter the M4
data guard first. Those tests now disable only the new best-effort projection while constructing
their lower-layer fixture, preserving independent evidence for the M3.3 and M3.4 guards. M4's own
populated downgrade guard remains separately tested.

## 6. Acceptance evidence

Eight new M4.2 tests prove:

- deterministic vectors are stable, normalized, dimensioned, and query-compatible;
- the pinned local model verifies all artifacts and performs offline CPU inference;
- completed-turn documents are bounded, player-only, source-cited, tagged, and idempotent;
- failed turns and hidden event content never become memory text;
- jobs embed exactly once across engine restart;
- provider failure leaves the completed turn intact, stores only a safe category, and retries;
- expired leases recover without duplicate embeddings;
- source drift fails closed and side-by-side profiles cannot activate early or mix dimensions.

Focused M4.1+M4.2 and lower-migration isolation gates pass. The final full suite reports 143 passed,
2 optional live OpenClaw tests skipped, and the one previously recorded TestClient deprecation
warning. Lint, format, compilation, ruleset/schema integrity, dependency consistency, migration
upgrade/downgrade, dual-database head/drift, API health, and service isolation also pass.

## 7. Next boundary

M4.3 may now implement filter-before-rank exact cosine plus PostgreSQL lexical retrieval,
deterministic hybrid fusion, count/character budgets, canonical citations, and immutable retrieval
audits. It may activate a profile only after measured completeness and retrieval-quality evidence.
It still must not send memory to an LLM; provider integration remains M4.4.
