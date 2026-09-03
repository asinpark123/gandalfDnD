# PostgreSQL 18 Active Cutover Record

- **Status:** Cutover complete; stabilization monitoring active
- **Execution date:** 2026-09-04
- **Host:** `postgresvm`
- **Authorized boundary:** Final development recovery point, automatic PostgreSQL 18 startup,
  Gandalf-only local tunnel/API switch, acceptance, and automatic PostgreSQL 15 rollback on failure
- **Development rehearsal:**
  [`POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md`](POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md)
- **Migration strategy:** [`POSTGRESQL_18_MIGRATION_STRATEGY.md`](POSTGRESQL_18_MIGRATION_STRATEGY.md)
- **Subsequent M4.1 evidence:** [`M4_1_MEMORY_FOUNDATION.md`](M4_1_MEMORY_FOUNDATION.md)

## 1. Outcome

GandalfDnD's active MacBook development connection now uses PostgreSQL 18.6. Local port 5433
forwards to loopback-only remote port 5433 on the `18/gandalf` cluster. The local API was restarted
after the switch and returns HTTP 200 from `/health`. A direct application-role check proves the
active connection reaches `gandalfdnd_dev` as `gandalfdnd_dev_user` on PostgreSQL 18 with Alembic
head `0011_factions_time`.

The PostgreSQL 18 cluster startup policy changed from manual to automatic. The host's aggregate
PostgreSQL service is enabled. PostgreSQL 15 `15/main` remains online on remote port 5432 with its
two Gandalf database copies and roles intact as the rollback source; it has zero active Gandalf
development sessions after cutover.

No PostgreSQL 15 role was disabled, no database was deleted, no package was removed, no `vector`
extension was enabled, and no unrelated database, Bluebuild setting, or Clawvis VM was changed.

## 2. Final recovery and unchanged-data gate

Before the connection switch, the active API was paused, every remaining idle PG15 development
session was drained, and a final PostgreSQL 18-client custom-format dump was taken. The verified
owner-only recovery directory is:

`~/Backups/GandalfDnD/pg18-active-cutover-6b3b58c`

It contains a 267 KiB development dump, 22 KiB contents manifest, and passing SHA-256 checksums.
Files are mode 600 and the directory is mode 700. The earlier preflight and development-rehearsal
recovery bundles also remain intact.

The paused PG15 source and accepted PG18 target then matched exactly at:

- Alembic head `0011_factions_time`;
- every row count across 23 public tables;
- 8 public functions and 8 non-internal triggers;
- no installed `vector` extension.

The key nonzero counts remained 11 campaigns, 22 characters, 836 character grants, 668 events, 116
turns, 229 provider calls, 30 NPCs, 39 presences, 39 world facts, 19 decisions, 10 quests, and 10
factions. Any mismatch would have stopped before the tunnel change; none occurred.

## 3. Rollback-protected switch

The cutover ran under one script with an exit trap prepared to restore all of the following on any
failure:

- PostgreSQL 18 startup policy from automatic back to manual;
- local port 5433 forwarding from PostgreSQL 18 back to PostgreSQL 15;
- a fresh local API process on the restored PostgreSQL 15 path.

The script first verified the final dump and source/target fingerprints, then changed startup
policy, gracefully stopped the old API, replaced only the SSH forwarding target, proved the direct
PostgreSQL 18 identity and a transactional write/rollback, and started the new API. Every acceptance
check passed, so rollback was not invoked.

The transactional write probe created and populated a temporary table inside an explicit
transaction and rolled it back. It proved write capability without changing persistent campaign or
schema state.

## 4. API and regression acceptance

Before cutover, SHA-256 fingerprints were captured for health, OpenAPI, and six read-only routes for
each of all 11 campaigns. After the API restart on PostgreSQL 18, all 68 response fingerprints
matched. They passed once more after the full test run.

Active-development Alembic checks reported `0011_factions_time (head)` and no model drift. The full
post-cutover repository gate used an explicit runner that first asserted the isolated
`gandalfdnd_test_user`/`gandalfdnd_test` identity, preventing any test mutation of active
development data:

- ruleset/catalog integrity: passed;
- Ruff lint: passed;
- Ruff formatting: passed for 87 files;
- Pytest: 126 passed, 2 intentionally opt-in live OpenClaw tests skipped, and the existing
  TestClient deprecation warning; elapsed time 175.29 seconds.

An initial generic test command was rejected before execution because its target was not explicit
enough for the safety gate. The isolated runner was then used; no test touched development data.

## 5. Access and shared-service acceptance

Through the active tunnel:

- the development role reaches only `gandalfdnd_dev` and is rejected from `gandalfdnd_test` and
  `postgres`;
- the test role reaches only `gandalfdnd_test` and is rejected from `postgres`;
- at cutover acceptance, both databases were at head `0011` with `vector` absent.

Both PG15 and PG18 HBA parsers report zero errors. PG18 remains bound only to `127.0.0.1:5433`.
PostgreSQL 15, PostgreSQL 18, and Bluebuild are active. Bluebuild returns HTTP 200 for `/`, `/docs`,
and `/openapi.json`.

## 6. Stabilization and completed next gate

Keep the PostgreSQL 15 Gandalf databases, roles, HBA rollback path, and all three recovery bundles
unchanged during stabilization. Monitor API/database errors, connection placement, disk, migration
behavior, and restart behavior as development continues. Any unexplained PG18 regression should
pause writes and use the preserved rollback procedure rather than modifying both copies.

The owner subsequently authorized M4.1. Exact pgvector 0.8.6 enablement in the two PostgreSQL 18
Gandalf databases, the pinned Python adapter, and guarded `0012_memory_foundation` migration passed;
see `M4_1_MEMORY_FOUNDATION.md`. PostgreSQL 15 role disablement, copy deletion, and cluster
retirement remain later destructive decisions and were not part of M4.1.
