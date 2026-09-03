# PostgreSQL 18 Readiness Audit

- **Status:** PG18.0 complete; conditionally ready for an explicitly authorized parallel migration
- **Audit date:** 2026-09-04
- **Host:** `postgresvm`
- **Scope:** Read-only package, cluster, access, recovery, and Gandalf compatibility assessment
- **Strategy:** [`POSTGRESQL_18_MIGRATION_STRATEGY.md`](POSTGRESQL_18_MIGRATION_STRATEGY.md)

## 1. Outcome and sequencing decision

A parallel PostgreSQL 18 Gandalf cluster is feasible on `postgresvm`. The recommended sequence is
to migrate GandalfDnD to PostgreSQL 18 **before M4.1**, then install/enable pgvector for PostgreSQL
18 only. This avoids building M4 on PostgreSQL 15 and repeating its extension work after migration.

The result is **conditional readiness**, not permission to install. PostgreSQL 18 can coexist with
the current PostgreSQL 15 server and the exact narrowed transaction removes no package and does not
upgrade the PostgreSQL 15 server/client. However, it must upgrade three shared packages used to
manage or access PostgreSQL installations. The host also runs an unrelated active application
against PostgreSQL 15, so a recovery point, maintenance boundary, package pin, and post-change
service verification are mandatory.

No configured repository, package, database, role, service, firewall, authentication file, or
application setting changed during PG18.0. Temporary APT simulation directories were removed after
each run. The documentation/GitHub push preceding the audit did not alter the VM.

## 2. Verified host and cluster baseline

| Area | Read-only finding | Migration implication |
| --- | --- | --- |
| Operating system | Debian 12/bookworm, amd64, 64-bit | Supported by the official PostgreSQL APT repository |
| Current cluster | PostgreSQL 15.14, `15/main`, online on port 5432 | Preserve unchanged during parallel work |
| Current minor status | Debian security candidate is PostgreSQL 15.19 | Do not combine that server update with PG18 provisioning |
| Shared use | Three unrelated application databases exist; Bluebuild had an active connection | Shared-package changes require a quiet window and explicit health checks |
| Resources | 2 CPUs, 3.8 GiB RAM, about 2.5 GiB available, 32 GiB disk free | Adequate for two small clusters with conservative defaults and exact M4 search |
| Current PG15 footprint | About 121 MiB data directory; Gandalf databases are 12 MiB and 13 MiB | Logical dump/restore is simpler than whole-cluster `pg_upgrade` |
| Locale | `en_NZ.utf8` is installed; Gandalf databases use `en_NZ.UTF-8` | A matching PG18 Gandalf cluster can be initialized |
| Checksums/WAL | PG15 checksums off; `archive_mode` off; `wal_level=replica` | PG18's checksum default is safe with logical restore; no existing PITR safety net exists |
| Backups | No pgBackRest, Barman, WAL-G, or database-backup timer was found | Fresh verified Gandalf dumps and a shared-package recovery point are prerequisites |
| Extensions | Only `plpgsql` in both Gandalf databases | No extension migration conflict; enable `vector` only after restore |
| Alembic | Both Gandalf databases are at `0011_factions_time` | Empty-chain and populated-restore testing have one known head |
| Roles | Separate non-superuser Gandalf owners; passwords are SCRAM-SHA-256 | Compatible with a SCRAM-only PostgreSQL 18 HBA policy |
| Network | PostgreSQL 15 listens on all interfaces at 5432; 5433 is free remotely | Bind PG18 to loopback on remote port 5433; test through a separate SSH tunnel |

The recurring `could not change directory to /home/ahshin` text was emitted when read-only commands
changed to the `postgres` account while retaining the SSH user's inaccessible working directory. It
did not affect any query.

## 3. Exact package evidence

The official PGDG Debian 12/amd64 index offered these audited versions:

- `postgresql-18` and `postgresql-client-18`: `18.6-1.pgdg12+2`;
- `postgresql-18-pgvector`: `0.8.6-1.pgdg12+1`;
- `postgresql-common` and `postgresql-client-common`: `293.pgdg12+1`;
- `libpq5`: `18.6-1.pgdg12+2`.

The PostgreSQL project documents Debian 12/amd64 support and the version-specific server/client
packages through its [official Debian repository](https://www.postgresql.org/download/linux/debian/).
pgvector likewise documents the matching PostgreSQL APT package as a supported installation route
in its [official repository](https://github.com/pgvector/pgvector).

An unrestricted simulation also tried to move the generic `postgresql` meta-package from 15 to
18. A stricter simulation assigned the PGDG origin a negative default priority, allowed only the
reviewed required package names, pinned the meta-package to its installed Debian version, requested
the exact versions above, and disabled recommended packages. Its complete transaction was:

| Action | Packages |
| --- | --- |
| Upgrade (3) | `postgresql-common` 248→293, `postgresql-client-common` 248→293, `libpq5` 15.14→18.6 |
| Install (4) | `liburing2`, `postgresql-client-18`, `postgresql-18`, `postgresql-18-pgvector` |
| Remove | None |
| PostgreSQL 15 server/client change | None |
| Unrelated pending upgrades included | None; 259 remained untouched |

`postgresql-common >=275` and `libpq5 >=18.6` are hard PostgreSQL 18 dependencies, so those three
upgrades cannot be eliminated while using the supported PGDG binary package. `libpq` retains its
version-5 client ABI and the only running processes observed mapping it were two administrator
`psql` sessions, not the unrelated FastAPI service. Nevertheless, the shared package change is an
operator-visible risk and must be verified, not assumed harmless.

The temporary simulation source used HTTPS with `trusted=yes` because the PGDG signing key is not
installed on the VM; APT correctly reported the missing key. Real provisioning must install the
official key, use `Signed-By`, verify the signed index, and re-run the exact simulation. The audit's
temporary trust override must never become the persisted source configuration.

Recommended packages, including PostgreSQL 18 JIT, were intentionally excluded. M4's small exact
search workload does not justify adding LLVM/JIT before measurements show a need.

## 4. Cluster-coexistence finding

The installed `postgresql-common` configuration retains its default `create_main_cluster=true`.
Installing a new server major would therefore automatically initialize a default `18/main` cluster,
normally using the next free port. That is insufficiently controlled for this shared host.

The approved execution plan should instead:

1. preserve the current PostgreSQL configuration and package inventory;
2. deliberately set `create_main_cluster=false` before installing the server package;
3. complete the exact signed and pinned package transaction with `--no-install-recommends`;
4. manually create a named `18/gandalf` cluster on remote port 5433 with matching locale, loopback
   listening only, checksums enabled, conservative memory, and a restrictive HBA file;
5. initially keep the new cluster under explicit test control, then change its startup policy only
   at the cutover gate;
6. leave `15/main` on port 5432 and verify its active application before and after every shared
   package change.

During parallel testing, use a different MacBook local port, such as local 5434 forwarded to remote
5433. At cutover, the existing application-local port 5433 can forward to remote 5433, allowing the
database URL shape to remain stable while changing only the tunnel target.

## 5. Application compatibility assessment

The local environment currently uses:

- Python 3.11.4;
- psycopg 3.3.4 with its binary implementation and bundled libpq 18.0;
- SQLAlchemy 2.0.52;
- Alembic 1.19.1.

The installed application driver already connects successfully to PostgreSQL 15 while using its
bundled libpq 18 client, which is positive cross-version evidence. Static review found conventional
PostgreSQL UUID, JSONB, foreign-key, check-constraint, partial-index, transaction, trigger, and
PL/pgSQL usage. It found no use of the migration-sensitive PostgreSQL 16–18 features identified in
the reviewed release notes, including `NULLS NOT DISTINCT` primary keys, `old_snapshot_threshold`,
custom-function expression indexes, or changed interval `ago` syntax.

This is not a substitute for execution. PG18.3 must still prove:

- the full migration chain into an empty database;
- a populated PostgreSQL 15→18 logical dump/restore using PostgreSQL 18 `pg_dump`;
- grants, triggers, indexes, sequences, constraints, JSONB/UUID behavior, and Alembic head;
- the complete automated suite, deterministic Lantern replay, API health, restart, and isolation;
- pgvector insert/query and later M4 migrations under the restricted roles.

PostgreSQL officially recommends concurrent old/new installations for cautious application testing
and recommends using the newer `pg_dump` for a cross-major logical migration. See
[Upgrading a PostgreSQL cluster](https://www.postgresql.org/docs/18/upgrading.html), the
[PostgreSQL 16 migration notes](https://www.postgresql.org/docs/16/release-16.html),
[PostgreSQL 17 migration notes](https://www.postgresql.org/docs/17/release-17.html), and
[PostgreSQL 18 migration notes](https://www.postgresql.org/docs/18/release-18.html).

## 6. Access-isolation finding

PG18.0 found a pre-existing least-privilege gap:

- the two Gandalf roles are mutually denied `CONNECT` to each other's Gandalf database as intended;
- the unrelated databases retain PostgreSQL's default `PUBLIC CONNECT` privilege;
- the shared PG15 HBA rules broadly allow authenticated users to request any database from
  loopback, the LAN, and one private address;
- consequently, both Gandalf roles can authenticate to several unrelated databases;
- metadata-only checks found no `CREATE`, `SELECT`, or write privileges for Gandalf roles on the
  unrelated application tables inspected, so no unrelated table-data access was observed.

This is narrower than a data exposure but does not meet the project's desired database isolation.
Do not revoke `PUBLIC CONNECT` from unrelated databases, because that could disrupt their owners.
The preferred correction is ordered HBA rules that allow each Gandalf role to reach only its own
database through the loopback SSH-tunnel path and reject that role for every other database. Apply
and test this as an explicitly approved PG15 reload-only hardening step. Build the PostgreSQL 18 HBA
correctly from the start. After accepted cutover, disable the old PG15 Gandalf logins while retaining
a documented rollback method.

## 7. Recovery and authorization gate

Before any VM mutation, obtain explicit approval for one bounded operation that includes:

1. a hypervisor/VM recovery point or equivalent recovery evidence for the shared package change;
2. fresh checksummed emergency dumps of only the two Gandalf databases using the installed PG15
   tools before the package change, followed by PostgreSQL 18 migration dumps after its client is
   installed and before any restore;
3. copies/checksums of the PG15 package inventory and PostgreSQL configuration;
4. the official signed PGDG source plus restrictive exact-version package preferences;
5. the exact three-upgrade/four-install transaction above, re-simulated immediately before use;
6. prevention of automatic `18/main` creation and manual creation of loopback-only `18/gandalf`;
7. the targeted PG15 Gandalf-role HBA restriction and configuration reload;
8. PG15/Bluebuild health verification before and after package changes;
9. test-database restore and acceptance before any development-database copy;
10. no cutover, old-role disablement, package downgrade, database deletion, or PG15 retirement.

Any changed package set, service restart requirement, signature problem, new removal, PG15 server
upgrade, failed unrelated-service health check, or insufficient recovery point stops the operation.
Package rollback should use the reviewed VM recovery point rather than an improvised downgrade of
shared cluster-management packages.

## 8. PG18.0 conclusion

**Go, with the authorization and recovery prerequisites above.** Migrate before M4.1. The database
sizes, available resources, compatible driver, standard schema features, exact binary packages,
free parallel port, and logical-restore strategy make this a favourable point in development to
establish the long-lived platform. The migration must remain staged: package/cluster foundation,
test restore, development restore, acceptance, and final cutover are separate gates.

PostgreSQL 15.14 remains active after this audit. Its update to 15.19 for unrelated remaining users
is advisable but outside Gandalf's migration scope and must not be bundled into this operation.
