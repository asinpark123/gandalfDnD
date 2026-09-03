# PostgreSQL 18 Migration Strategy

- **Status:** Proposed; read-only readiness assessment is next
- **Decision date:** 2026-09-04
- **Current Gandalf database platform:** PostgreSQL 15.14 on Debian 12
- **Target:** PostgreSQL 18, subject to compatibility evidence and an explicit mutation gate
- **Scope:** `gandalfdnd_dev` and `gandalfdnd_test`; unrelated databases and services are excluded

## 1. Decision and purpose

GandalfDnD should move from PostgreSQL 15 to PostgreSQL 18 to establish a longer-supported database
foundation before the project becomes difficult to migrate. PostgreSQL 15 remains supported until
2027-11-11, while PostgreSQL 18 is supported until 2030-11-14. PostgreSQL also recommends running
the current minor release of a supported major version. See the official
[PostgreSQL versioning policy](https://www.postgresql.org/support/versioning/).

This is a separately gated infrastructure track, not an incidental part of installing pgvector.
The approved direction authorizes planning and read-only assessment. It does **not** authorize
package/repository changes, a PostgreSQL restart, creating a new cluster, copying data, changing the
application connection, or removing PostgreSQL 15.

## 2. Migration principles

1. **Parallel, not in-place:** create and validate a PostgreSQL 18 cluster alongside PostgreSQL 15.
2. **Gandalf-only scope:** inventory shared-host dependencies without reading or changing unrelated
   database content. Migrate only the two Gandalf databases and their restricted roles.
3. **Restore rather than transform in place:** because the Gandalf databases are small, prefer
   logical dump/restore into the parallel cluster. Preserve PostgreSQL 15 as the rollback source.
4. **Application evidence before cutover:** run the complete migration chain, tests, schema-drift
   checks, API health, deterministic scenarios, and pgvector checks against PostgreSQL 18.
5. **One change boundary at a time:** do not hide PostgreSQL, libc, pgvector, application-schema,
   or unrelated-service upgrades inside one unreviewed package transaction.
6. **Reversible cutover:** changing Gandalf's connection target is the cutover. Do not delete the
   PostgreSQL 15 copies during the stabilization period.
7. **No automatic retirement:** an old shared cluster can be retired only after every owner and
   service using it has independently migrated and explicitly authorized removal.

## 3. Relationship to M4 and pgvector

The PostgreSQL 18 readiness assessment occurs before M4.1 changes the VM. Its outcome selects one
of two documented sequences:

- **Preferred when readily achievable:** migrate the Gandalf databases to PostgreSQL 18, install
  the matching pinned `postgresql-18-pgvector` package under the same clean-simulation gate, enable
  `vector` only in the two PostgreSQL 18 Gandalf databases, then implement M4.1.
- **Supported interim path:** if PostgreSQL 18 needs broader shared-host coordination, keep Gandalf
  on supported PostgreSQL 15, safely install the pinned PostgreSQL 15 pgvector package, implement
  M4, and perform a later tested PostgreSQL 18 migration. This avoids blocking product development
  without weakening the 2027 retirement deadline.

The decision will be based on evidence rather than elapsed time alone. M4 must not provision both
packages or clusters speculatively.

## 4. Delivery stages and gates

### PG18.0 — Read-only readiness assessment

- record OS architecture, PostgreSQL packages, cluster layout, ports, configuration boundaries,
  disk headroom, service health, and active sessions;
- identify database names, owners, extensions, encodings/locales, and connection consumers without
  reading unrelated application tables or records;
- inspect Gandalf-specific roles, grants, database sizes, migrations, extension requirements, and
  backup capability;
- inspect official PostgreSQL 18 package availability and simulate the proposed transaction;
- identify whether PostgreSQL 15 and 18 can coexist without port, service, disk, or package
  conflicts;
- record the exact proposed package changes and stop if the transaction would remove or replace the
  PostgreSQL 15 cluster or alter unrelated services.

Exit: a credential-free report states whether parallel PostgreSQL 18 is feasible, what it would
change, how M4 should be sequenced, and which later actions require approval. No mutation occurs.

### PG18.1 — Recovery and compatibility rehearsal

- take fresh logical backups of only `gandalfdnd_dev` and `gandalfdnd_test` after approval;
- verify backup checksums and perform a disposable restore rehearsal;
- reproduce only the Gandalf roles and least-privilege grants rather than importing all cluster
  globals;
- run Alembic from an empty PostgreSQL 18 Gandalf database and restore a populated copy;
- run all automated tests, migration upgrades/downgrades allowed by project policy, schema-drift
  checks, deterministic scenarios, and API health checks;
- verify driver, SQLAlchemy, Alembic, SQL syntax, UUID/JSONB behavior, transactions, constraints,
  time handling, and extension compatibility.

Exit: both clean-build and populated-restore paths pass with recorded timing and no access to
unrelated database content.

### PG18.2 — Parallel cluster provisioning

- require explicit owner approval for the reviewed package transaction;
- install pinned PostgreSQL 18 packages without removing PostgreSQL 15;
- create a separately addressed cluster with documented port, storage, locale, authentication, and
  service ownership;
- apply conservative access controls and create only the two Gandalf databases/roles;
- keep Clawvis and unrelated services untouched.

Exit: PostgreSQL 15 remains healthy and unchanged at its existing endpoint; PostgreSQL 18 is healthy
at a separate endpoint and accepts only the intended Gandalf access.

### PG18.3 — Gandalf restore and acceptance

- restore fresh Gandalf-only backups to PostgreSQL 18;
- reconcile sequences, ownership, grants, Alembic heads, row counts, constraints, and application
  invariants;
- install/enable pgvector only when the chosen M4 sequence reaches its separately approved gate;
- run the full repository, dual-database, restart, deterministic replay, role-isolation, and M4
  extension tests;
- compare runtime behavior and record any compatibility defect or workaround.

Exit: development and test copies pass every applicable gate on PostgreSQL 18 without changing the
active PostgreSQL 15 Gandalf connection.

### PG18.4 — Controlled cutover and rollback window

- stop new Gandalf writes for a bounded maintenance window;
- take and verify final Gandalf-only backups, restore the final delta/database copies, and repeat
  integrity checks;
- update only Gandalf connection configuration and restart only Gandalf application processes;
- verify health, migrations, representative reads/writes, deterministic state, and event ordering;
- if any exit check fails, point Gandalf back to the preserved PostgreSQL 15 databases before writes
  diverge, or use the reviewed forward/reconciliation procedure if writes already occurred.

Exit: Gandalf runs on PostgreSQL 18 with documented recovery points and a tested rollback boundary.

### PG18.5 — Stabilization and retirement decision

- monitor errors, connections, storage, backups, migrations, and performance through the agreed
  stabilization period;
- update developer/operator setup, package inventory, recovery instructions, and project evidence;
- retain the PostgreSQL 15 Gandalf copies until acceptance and explicit deletion approval;
- do not stop or remove a shared PostgreSQL 15 cluster merely because Gandalf no longer uses it.

Exit: the owner accepts the PostgreSQL 18 migration. Any removal of old data, packages, or clusters
is a separate destructive action with exact targets, dependency confirmation, verified backups, and
explicit authorization.

## 5. Acceptance criteria

The migration is complete only when:

- PostgreSQL 18 runs a pinned, supported minor release and its package source/pinning is recorded;
- both Gandalf databases have the expected owners, grants, extensions, Alembic head, schema, and
  integrity counts;
- cross-database and unrelated-database access remains denied to Gandalf roles;
- the full test suite and applicable live/runtime checks pass against PostgreSQL 18;
- a fresh backup can be restored and used by the application;
- PostgreSQL 15 and unrelated services remain healthy throughout the parallel and cutover stages;
- cutover and rollback evidence contains no credentials or private database content;
- M4's selected pgvector version and extension upgrade path are recorded when applicable;
- the living project plan, README, operations guidance, and issue/risk register match reality.

## 6. Failure and rollback boundaries

- A package simulation proposing removal/replacement of PostgreSQL 15, libc changes, or unrelated
  service changes stops the operation for review.
- A failed PostgreSQL 18 test never justifies changing PostgreSQL 15 data to make the test pass.
- Do not use destructive cluster recreation, data-directory deletion, `DROP ... CASCADE`, or an
  unrestricted globals restore as a shortcut.
- Do not permit simultaneous application writes to the PostgreSQL 15 and 18 Gandalf copies without
  an explicitly designed replication/reconciliation mechanism; none is currently planned.
- After cutover writes begin, rollback requires a deliberate data-divergence decision. The safest
  default is to pause writes, diagnose, and either repair forward or restore the verified final
  backup to the selected authoritative cluster.

## 7. Immediate next decision

Complete PG18.0 read-only assessment first. Then choose and record whether PostgreSQL 18 migration
precedes M4.1 or whether M4 temporarily proceeds on supported PostgreSQL 15. No VM mutation should
occur until the resulting exact transaction and rollback plan receive explicit owner approval.
