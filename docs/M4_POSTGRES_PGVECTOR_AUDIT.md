# M4 PostgreSQL and pgvector Readiness Audit

- **Status:** Read-only audit complete; provisioning not yet authorized or performed
- **Audit date:** 2026-09-04
- **Host:** `postgresvm`
- **Scope:** M4 compatibility, least privilege, capacity, and safe installation planning

## 1. Outcome

`postgresvm` can support pgvector, but pgvector is not currently installed or available through the
configured Debian repositories. No database, package, repository, role, service, or configuration
was changed during this audit.

The preferred next step is a narrowly pinned prebuilt pgvector package from the official PostgreSQL
APT repository, but only if a fresh package simulation proves it will install the extension without
replacing or upgrading PostgreSQL, libc, or unrelated services. If that condition is not met, stop
and return for a separately reviewed maintenance plan. Do not silently fall back to a source build.

The owner subsequently accepted PostgreSQL 18 as Gandalf's long-term database target. Complete the
read-only PG18.0 assessment in [`POSTGRESQL_18_MIGRATION_STRATEGY.md`](POSTGRESQL_18_MIGRATION_STRATEGY.md)
before mutating this VM. That assessment decides whether Gandalf migrates first and uses the matching
PostgreSQL 18 pgvector package, or M4 temporarily follows this PostgreSQL 15 plan. This audit does
not authorize either package path.

## 2. Verified host and cluster state

| Area | Read-only finding | M4 implication |
| --- | --- | --- |
| Operating system | Debian GNU/Linux 12, amd64, Linux 6.1 | Official pgvector supports Linux and PostgreSQL 15 |
| PostgreSQL client/server | 15.14 Debian build | Supported by current pgvector, which supports PostgreSQL 13+ |
| Debian security candidate | PostgreSQL 15.19 was visible to package simulation | Extension work must not cause an unplanned server upgrade/restart |
| Installed extensions | `plpgsql` only in the cluster and both Gandalf databases | `vector` must be installed at OS level and enabled per Gandalf database |
| Available extensions | No `vector` row | `CREATE EXTENSION vector` would currently fail |
| Shared preload libraries | Empty | pgvector does not require a preload setting or planned server restart |
| Gandalf databases | `gandalfdnd_dev` 12 MB; `gandalfdnd_test` 13 MB | Small enough for exact vector scans and quick Gandalf-scoped backups |
| Application roles | Separate `*_user` logins; not superuser, `CREATEDB`, or `CREATEROLE` | A database administrator must enable the extension; normal app roles remain restricted |
| Database ownership | Each app role owns only its corresponding Gandalf database and can create there | Alembic may create M4 tables after the administrator enables the extension |
| Connectivity isolation | Each Gandalf role is denied connection to the other database; `public` is denied both | Extension enablement and migrations remain independently scoped to development/test |
| Compute | 2 CPUs, 3.8 GiB RAM, about 2.5 GiB available during audit | Suitable for the initial 500-event test; avoid memory-heavy index builds |
| Storage | About 32 GiB free on the PostgreSQL filesystem | Ample for the bounded M4 corpus and side-by-side re-index test |
| Build tools | GNU Make 4.3, GCC 12.2, `build-essential` installed | A source build is technically possible but is not the preferred change path |
| PostgreSQL headers | `postgresql-server-dev-15` not installed | Direct source compilation is not currently ready |

The harmless `could not change directory to /home/ahshin` message came from running read-only
PostgreSQL commands as the database administrator while the SSH working directory remained the
login user's home. It did not affect any query or permission result.

## 3. Dependency-impact finding

A no-change package simulation for `postgresql-server-dev-15` proposed:

- 14 package upgrades, including PostgreSQL server/client 15.14 to 15.19, libc, libpq, curl, and
  libxml2;
- 26 new packages, including Clang/LLVM development packages and PostgreSQL headers.

That is too broad to treat as an incidental pgvector installation on a VM that may host other
services or databases. The source-build path therefore requires a separate maintenance decision,
explicit backup/restart planning, and a new simulation. It is not authorized by ordinary M4
application development.

## 4. Upstream compatibility and version pin

The official [pgvector repository](https://github.com/pgvector/pgvector) documents PostgreSQL 13+
support, per-database `CREATE EXTENSION vector`, exact and approximate search, and both source and
PostgreSQL APT installation paths. The upstream `v0.8.6` tag was independently resolved during this
audit to commit `8ee86c96f0fd72390f890aa8a336fda6d3ab4c6c`.

M4 should pin a reviewed pgvector release and record its package version, upstream tag/commit, and
installed database extension version. It must not track an unpinned branch or accept an implicit
`latest` version. Re-check upstream and package state immediately before provisioning because both
are external, changing inputs.

## 5. Recommended provisioning gate

This is a plan, not an authorization to execute it.

1. Confirm current backups and take fresh logical backups of only `gandalfdnd_dev` and
   `gandalfdnd_test`; do not read, dump, or change unrelated databases.
2. Record the current PostgreSQL package versions, cluster health, active connections, available
   extensions, and Alembic heads.
3. Configure the official PostgreSQL APT source and signing key with package preferences restricted
   to the required PostgreSQL-15 pgvector package.
4. Run a fresh simulated install for the exact pgvector package/version.
5. Continue only if the simulation adds the expected pgvector package and does not upgrade,
   downgrade, remove, or replace PostgreSQL, libc, or unrelated packages. Otherwise stop.
6. Install the pinned prebuilt extension package without changing PostgreSQL configuration.
7. As the database administrator, enable the exact extension version only in `gandalfdnd_dev` and
   `gandalfdnd_test`. Do not enable it in `postgres`, templates, or any unrelated database.
8. Verify extension version, cluster health, both existing Gandalf schemas, application-role access,
   and pre-M4 runtime/tests before creating M4 tables.
9. Apply the M4 Alembic migration as each existing restricted Gandalf role. The migration should
   assert that `vector` exists and fail clearly rather than attempting privilege escalation.
10. Record every actual package/database change, verification result, and recovery point in this
    document and the living project plan.

The official APT path is preferred over copying unmanaged extension files into PostgreSQL system
directories. If no safe pinned binary transaction is available, the fallback is not Docker or an
automatic source compile. Return for approval of a controlled source-build/host-maintenance plan.

## 6. Rollback and failure boundaries

- Before M4 tables exist, a failed package activation can be reversed according to the approved
  package plan after verifying the two Gandalf databases remain unchanged.
- Once a migration stores `vector` values, do not drop the extension or package as an ad hoc
  rollback. Restore the Gandalf-scoped backups or apply a reviewed forward repair.
- Never use `DROP EXTENSION ... CASCADE`, delete PostgreSQL data directories, recreate the cluster,
  or change unrelated database ownership as part of M4 recovery.
- A failed embedding or retrieval operation must not roll back a completed game turn or canonical
  world state. Memory indexing is a rebuildable derived subsystem.

## 7. Authorization boundary

The following still require explicit owner approval because they change shared VM state:

- adding the official PostgreSQL APT signing key/source and package pin;
- installing a pgvector OS package;
- enabling `vector` in the two Gandalf databases;
- any PostgreSQL package upgrade, service restart, or source-build dependency installation.

Repository-only M4 code and deterministic tests may proceed after the extension foundation exists.
No OpenClaw calls, paid API calls, embedding-model download, or unrelated VM work are authorized by
this audit alone.
