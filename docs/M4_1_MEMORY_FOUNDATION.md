# M4.1 pgvector and Memory Foundation Execution Record

- **Status:** Complete
- **Execution date:** 2026-09-04
- **Database platform:** PostgreSQL 18.6 on `postgresvm`
- **Migration:** `0012_memory_foundation`
- **Current successor head:** `0013_memory_lifecycle` repairs the shared lifecycle trigger exposed
  during M4.2; see [`M4_2_SOURCE_INDEXING.md`](M4_2_SOURCE_INDEXING.md)
- **Server extension:** pgvector `0.8.6`
- **Python adapter:** `pgvector==0.5.0`
- **Strategy:** [`M4_IMPLEMENTATION_STRATEGY.md`](M4_IMPLEMENTATION_STRATEGY.md)
- **Infrastructure audit:** [`M4_POSTGRES_PGVECTOR_AUDIT.md`](M4_POSTGRES_PGVECTOR_AUDIT.md)

## 1. Outcome

M4.1 passed. The database administrator enabled the already installed `vector` extension at exact
version `0.8.6` in `gandalfdnd_dev` and `gandalfdnd_test` only. The `postgres` database does not
have the extension. No package installation, package upgrade, service configuration change,
PostgreSQL 15 change, unrelated database change, or Clawvis change occurred in this slice.

Both Gandalf databases are at Alembic head `0012_memory_foundation` with zero model drift. Their
restricted application roles can create and query exact vectors in their own database and remain
denied from the other Gandalf database and `postgres`.

The memory tables are a mechanically inert foundation. No canonical turn writes memory yet, no
retrieval reaches either LLM stage, no embedding model was downloaded, and no network embedding or
paid provider call occurred.

## 2. Recovery boundary

Before extension enablement, fresh PostgreSQL 18 custom-format dumps of both Gandalf databases were
captured in the owner-only directory:

`~/Backups/GandalfDnD/m4.1-pgvector-pre-eb13ff7`

The directory is mode 700; both dumps and `SHA256SUMS` are mode 600; checksum verification passed.
The preserved PostgreSQL 15 rollback databases/roles and all earlier PostgreSQL 18 recovery bundles
remain unchanged.

Migration downgrade removes only an empty M4.1 schema. Once any memory profile, document, index,
job, or retrieval is recorded, it fails closed rather than discarding the history. Downgrade does
not drop the database extension; extension removal is an administrator operation outside ordinary
Alembic rollback and remains unauthorized.

## 3. Implemented schema

Migration `0012_memory_foundation` first asserts PostgreSQL 18+ and exact extension version `0.8.6`,
then creates seven tables:

| Table | Foundation responsibility |
| --- | --- |
| `memory_embedding_profiles` | Immutable provider/model/revision, artifact hash, license, dimensions, normalization, distance policy, and adapter version |
| `memory_documents` | Bounded player-visible turn/event-derived text, source/version/chunk identity, hashes, sequence range, canonical entity tags, and explicit supersession |
| `memory_embeddings` | Immutable document/profile vector with copied source hash and database-validated dimensions |
| `campaign_memory_indexes` | Per-campaign/profile build state, checkpoint, source count, quality result, failure category, and atomic active-profile boundary |
| `memory_index_jobs` | Durable pending/claimed/complete/failed work with attempts, leases, retry time, and safe error fields |
| `memory_retrievals` | Immutable retrieval audit with query-source hash, filters, profile/ranking version, counts, latency, budget, truncation, and outcome—never raw query text |
| `memory_retrieval_items` | Immutable ranked document citations and component/combined scores |

Database constraints and triggers enforce:

- player-only source documents in the first memory implementation;
- exactly one turn or event source, bounded non-empty content, SHA-256 form, sequence ranges, and
  idempotent source/version/chunk identities;
- same-campaign source and canonical tag ownership;
- immutable profile metadata, document source/content, embeddings, retrievals, and ranked items;
- mutable job/index lifecycle state without mutable campaign/document/profile identity;
- matching document hashes, matching profile dimensions, and finite vector values;
- one active embedding profile per campaign;
- state-shaped job leases, index activation/failure records, and retrieval outcomes;
- same-campaign player-visible documents in retrieval selections.

The embedding column intentionally uses unconstrained `vector`, because different immutable
profiles may have different dimensions during side-by-side re-indexing. The database trigger checks
each stored vector against its selected profile before accepting it. M4 continues to use exact
cosine search; no HNSW or IVFFlat index was added.

## 4. Dependency decision

The official pgvector Python adapter is pinned to `0.5.0`, the maintained release verified during
implementation. It supports Python 3.11, SQLAlchemy 2, Psycopg 3, and unconstrained `VECTOR()`
columns. The adapter has no runtime dependency of its own and does not download model weights.

Primary references:

- [pgvector Python repository](https://github.com/pgvector/pgvector-python)
- [pgvector 0.5.0 package record](https://pypi.org/project/pgvector/0.5.0/)

## 5. Acceptance evidence

Focused M4.1 acceptance: 9 tests passed. They prove:

- extension/database/role/head identity and absence of raw query storage;
- two-document exact cosine ordering through the SQLAlchemy adapter;
- hash mismatch, wrong dimensions, and non-finite vector rejection;
- cross-campaign source, job, and retrieval-item rejection;
- immutable profile, document content, index identity, and job identity;
- only one active profile per campaign;
- empty downgrade/upgrade replay while retaining `vector`;
- guarded downgrade after memory data exists.

The final isolated repository gate passed:

- ruleset/catalog validation: passed;
- Ruff lint: passed;
- Ruff formatting: 91 files passed;
- Pytest: 135 passed, 2 separately opt-in live OpenClaw tests skipped;
- known warning: the existing Starlette/httpx TestClient deprecation warning;
- elapsed test time: 197.77 seconds;
- development and test Alembic heads: `0012_memory_foundation`;
- development and test extension versions: `0.8.6`;
- development and test model drift: none.

An exact-vector temporary-table probe also passed through the active development role and was rolled
back. Application `/health` returned HTTP 200. PostgreSQL 15, PostgreSQL 18, and Bluebuild remained
active; Bluebuild returned HTTP 200 for `/`, `/docs`, and `/openapi.json`.

## 6. Resolved test assumption

The first full run reported 129 passing tests and six failures. No application or migration guard
failed. Six older downgrade tests still expected the former latest revision `0011_factions_time`.
Alembic correctly rolled their multi-revision downgrade attempts back atomically to the new head
`0012_memory_foundation`. The tests now capture the pre-attempt head and assert it remains unchanged,
and the fixture restores the repository head before cleanup if a future migration test intentionally
stops at an older revision.
The focused 15-test migration set and the final 135-test repository run then passed.

## 7. Next gate

M4.2 will implement player-safe source projection, deterministic embedding fixtures, a pinned local
CPU embedding provider, durable leased indexing, backfill/recovery, and side-by-side re-indexing.
Before downloading a real model, compare candidate size, license, artifact/revision pinning, CPU
latency, maximum input, and retrieval quality, then present the evidence to the owner if the choice
is material. A model download or a paid/network embedding service is not authorized by M4.1.
