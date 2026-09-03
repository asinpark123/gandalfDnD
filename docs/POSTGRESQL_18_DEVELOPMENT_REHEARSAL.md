# PostgreSQL 18 Development Restore and Cutover Rehearsal

- **Status:** Complete; active cutover requires explicit owner authorization
- **Execution date:** 2026-09-04
- **Host:** `postgresvm`
- **Authorized boundary:** Fresh development snapshot, PostgreSQL 18 development identity/database,
  restore, integrity comparison, role isolation, temporary runtime acceptance, and cutover planning
- **Foundation evidence:**
  [`POSTGRESQL_18_FOUNDATION_EXECUTION.md`](POSTGRESQL_18_FOUNDATION_EXECUTION.md)
- **Migration strategy:** [`POSTGRESQL_18_MIGRATION_STRATEGY.md`](POSTGRESQL_18_MIGRATION_STRATEGY.md)

## 1. Outcome

The development restore and cutover rehearsal passed. PostgreSQL 18 now contains both
`gandalfdnd_dev` and `gandalfdnd_test`, each owned by its matching login-only role. Neither role is
a superuser or has database-creation, role-creation, or replication authority. `PUBLIC CONNECT` is
revoked from both databases. Positive matching-database access and negative cross-Gandalf and
`postgres` database tests passed.

The active MacBook tunnel still maps local port 5433 to PostgreSQL 15 remote port 5432, and the
ordinary Gandalf API remains healthy on PostgreSQL 15. PostgreSQL 18 was tested through temporary
local port 5434, and the temporary API on port 8001 was removed after acceptance. No connection
cutover, old-role disablement, deletion, pgvector extension enablement, Clawvis change, or unrelated
service change occurred.

## 2. Fresh development recovery boundary

The local development API was briefly paused as one process group. An idle connection created by a
pre-pause health check was identified and closed only after confirming no non-idle Gandalf
development session existed. A PostgreSQL 18.6 `pg_dump` then captured PostgreSQL 15
`gandalfdnd_dev` in custom format with no application session connected. The API was immediately
resumed and returned HTTP 200 from `/health`.

The owner-only recovery directory is outside Git at:

`~/Backups/GandalfDnD/pg18-dev-restore-ac21aec`

It contains the 267 KiB custom-format dump, its 22 KiB contents manifest, and passing SHA-256
checksums. Files are mode 600 and the directory is mode 700. The earlier foundation recovery bundle
also remains at `~/Backups/GandalfDnD/pg18-preflight-7f04efc`.

## 3. Restore and integrity comparison

The fresh archive restored without error into the new PostgreSQL 18 development database. The
source and restore both report Alembic head `0011_factions_time`, 23 public tables, 8 public
functions, 8 enabled non-internal triggers, no sequences, and no installed `vector` extension.

Every public table row count matched at the initial and final comparisons:

| Table group | Matching evidence |
| --- | --- |
| Campaign core | 11 campaigns, 22 characters, 836 character grants, 21 locations |
| Turn/rules audit | 116 turns, 229 provider calls, 6 dice rolls, 6 rule resolutions |
| Persistent world | 668 events, 21 scenes, 30 NPCs, 39 presences, 39 world facts |
| Branching/factions | 19 decisions, 38 options, 19 selections, 10 quests, 10 objectives, 10 factions, 18 relationships |
| Rules catalogs | 1 ruleset release and 4 data catalogs |

Both versions expose 289 public-table columns, 90 check constraints, 78 foreign keys, 23 primary
keys, 21 unique constraints, and 107 valid/ready indexes. No constraint is unvalidated, no index is
invalid, no application trigger is disabled, and no table or function has an unexpected owner.
PostgreSQL 18 additionally represents 226 `NOT NULL` constraints as `pg_constraint` type `n`; this
is an expected PostgreSQL 18 catalog representation difference rather than schema drift. Both
databases give the development owner `USAGE` and `CREATE` on `public` while denying database
`CONNECT` to `PUBLIC`.

Alembic `current` and `check` against the PostgreSQL 18 development restore reported head `0011`
and no new upgrade operations.

## 4. Runtime and regression acceptance

A temporary second Gandalf API connected to PostgreSQL 18 through local port 5434 while the
existing port-8000 API continued to use PostgreSQL 15. Both APIs reported healthy database
connections and identical OpenAPI schemas. Across all 11 restored campaigns, the following six
read-only routes were compared for every campaign:

- characters;
- canonical character/campaign state;
- player-visible world state;
- events;
- turn executions;
- rule resolutions.

All 66 response pairs matched exactly. The PostgreSQL 18 API was stopped, restarted from a fresh
process, and the complete 66-response comparison passed again. This proves restored state,
projection behavior, serialized output, and runtime reconnection without mutating either copy.

The final repository gate ran against the separate PostgreSQL 18 test database:

- Alembic current: `0011_factions_time (head)`;
- ruleset/catalog integrity: passed;
- Ruff lint: passed;
- Ruff formatting: passed for 86 files;
- Pytest: 126 passed, 2 intentionally opt-in live OpenClaw tests skipped, and the existing
  TestClient deprecation warning; elapsed time 274.58 seconds.

Both PG15/PG18 HBA parsers finished with zero errors. PG15 own-database access and cross/unrelated
denials passed after rehearsal. PostgreSQL 15, PostgreSQL 18, and Bluebuild remained active;
Bluebuild returned HTTP 200 for `/`, `/docs`, and `/openapi.json`.

## 5. Harmless stopped diagnostics

Four diagnostics failed closed and are retained so later operators do not repeat them:

- PostgreSQL `pg_dump` rejected the psql-only `-X` option before producing a snapshot; the API
  safety trap resumed it immediately and no database changed.
- A second snapshot attempt found one idle pooled API connection and stopped rather than assuming a
  clean boundary. The final attempt verified no non-idle sessions, drained that idle connection,
  and succeeded.
- PostgreSQL 18 `pg_restore -l` treats a literal `-` as a filename. The already completed dump was
  validated by omitting the filename and reading standard input; no repeat snapshot was needed.
- The first temporary API used a diagnostic environment label outside the application enum and
  returned HTTP 500. It was stopped, restarted as `development`, then passed every comparison twice.

None of these events affected PostgreSQL 15 data, the accepted PostgreSQL 18 restore, Bluebuild,
Clawvis, or unrelated databases.

## 6. Active-cutover authorization gate

Stop here for owner review. A separately authorized active cutover should:

1. recheck both clusters, disk, HBA, Bluebuild, the local API/tunnel identity, and source/restore
   fingerprints;
2. briefly pause the local Gandalf API and drain only its idle development connection;
3. take and verify a final PostgreSQL 15 development dump; stop if its fingerprint differs from the
   accepted PostgreSQL 18 copy rather than overwriting the accepted restore implicitly;
4. change the PostgreSQL 18 cluster startup policy from manual to automatic;
5. replace only the MacBook's local 5433 SSH forwarding target from remote PG15 port 5432 to remote
   PG18 port 5433, restart only the local Gandalf API, and prove its server version, health, all
   read-only projections, and a rollback-safe transactional write check;
6. return immediately to the preserved PG15 tunnel if any acceptance check fails before user writes
   resume.

Successful cutover still must retain the PostgreSQL 15 databases and roles through stabilization.
It does not authorize disabling old logins, deleting either database copy, retiring PostgreSQL 15,
enabling pgvector in a database, or changing unrelated services.
