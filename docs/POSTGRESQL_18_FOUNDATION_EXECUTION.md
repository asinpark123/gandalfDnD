# PostgreSQL 18 Foundation and Test-Restore Record

- **Status:** Complete; development rehearsal and active cutover subsequently passed
- **Execution date:** 2026-09-04
- **Host:** `postgresvm`
- **Authorized boundary:** Recovery evidence, signed/pinned packages, targeted PostgreSQL 15 HBA
  isolation, a parallel PostgreSQL 18 cluster, and test-database restore/verification only
- **Readiness audit:** [`POSTGRESQL_18_READINESS_AUDIT.md`](POSTGRESQL_18_READINESS_AUDIT.md)
- **Migration strategy:** [`POSTGRESQL_18_MIGRATION_STRATEGY.md`](POSTGRESQL_18_MIGRATION_STRATEGY.md)
- **Development rehearsal:**
  [`POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md`](POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md)
- **Active cutover:** [`POSTGRESQL_18_CUTOVER_EXECUTION.md`](POSTGRESQL_18_CUTOVER_EXECUTION.md)

## 1. Outcome

The authorized foundation passed. PostgreSQL 18.6 was established as the separate `18/gandalf`
cluster on remote port 5433. It listens only on `127.0.0.1`, uses SCRAM-SHA-256, has data checksums
enabled, and uses conservative settings. Its manual foundation-stage startup policy changed to
automatic only at the later accepted cutover. PostgreSQL 15 `15/main` remains online on port 5432.
Bluebuild remained active and returned HTTP 200 for `/`, `/docs`, and `/openapi.json` before and
after the shared-package transaction and after test acceptance.

Only `gandalfdnd_test_user` and `gandalfdnd_test` exist in the PostgreSQL 18 cluster. The test role
is login-only and is not a superuser and has no database-creation, role-creation, or replication
authority. `PUBLIC CONNECT` is revoked from the test database. The PostgreSQL 18 development role
and database do not yet exist. Gandalf's active development connection has not been cut over.

The pgvector 0.8.6 server package is installed for PostgreSQL 18 and appears in
`pg_available_extensions`; the `vector` extension is intentionally not enabled in a database yet.
That database mutation belongs to the later M4.1 gate.

## 2. Recovery evidence

The credential-free recovery bundle is stored outside Git at:

`~/Backups/GandalfDnD/pg18-preflight-7f04efc`

The directory is owner-only. Its database dumps and supporting files are mode 600. `SHA256SUMS`
passed for all artifacts. The bundle contains:

- PostgreSQL 15 emergency custom-format dumps and contents listings for development and test;
- PostgreSQL 18-client migration dumps and contents listings for development and test;
- PostgreSQL/APT configuration archive and pre-change package inventory;
- post-install package inventory;
- cached rollback `.deb` files for the three shared packages changed by the transaction.

No hypervisor checkpoint was confirmed, so this verified bundle is the explicitly documented
equivalent recovery evidence for the bounded operation. It does not authorize an improvised shared-
package downgrade; restoration or rollback must be reviewed against the exact failure state.

## 3. Signed and pinned package transaction

The official PostgreSQL signing key was installed with verified fingerprint
`B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8`. The Debian 12 PGDG source uses `Signed-By`, and a
restrictive preference gives the PGDG origin negative priority except for the exact reviewed
packages. A fresh signed simulation matched the approved boundary: three upgrades, four installs,
no removals, no PostgreSQL 15 server/client change, and no unrelated pending upgrade.

Applied versions:

| Package | Applied version |
| --- | --- |
| `postgresql-18`, `postgresql-client-18` | `18.6-1.pgdg12+2` |
| `postgresql-18-pgvector` | `0.8.6-1.pgdg12+1` |
| `postgresql-common`, `postgresql-client-common` | `293.pgdg12+1` |
| `libpq5` | `18.6-1.pgdg12+2` |
| `liburing2` | `2.3-3` |
| `postgresql-15`, `postgresql-client-15` | unchanged at `15.14-0+deb12u1` |

Automatic `18/main` creation was disabled before installation. The control fragment remains in
place, and no unintended cluster was created.

## 4. Access isolation

PostgreSQL 15 received ordered, Gandalf-role-specific loopback rules: each Gandalf role can reach
only its own database and is rejected from every other database over IPv4 and IPv6. The original
HBA file was preserved on the VM. Syntax validation and reload passed. Positive own-database tests,
cross-Gandalf denial tests, and unrelated-database denial tests passed after the change and after all
later work. No unrelated database ACL was modified.

PostgreSQL 18 was restrictive from first successful start: local administration uses peer
authentication; the matching Gandalf role/database path uses SCRAM over loopback; all other TCP
access is rejected. The HBA parser reports zero errors. A tunneled positive test reached
`gandalfdnd_test` as `gandalfdnd_test_user` on PostgreSQL 18, and that same role was rejected from
the `postgres` database.

## 5. Restore and compatibility evidence

The PostgreSQL 18-client test dump restored without error. Before the automated suite changed test
fixtures, exact comparison with the PostgreSQL 15 source showed:

- matching Alembic head: `0011_factions_time`;
- identical row counts for every public table;
- 23 public tables, 8 public functions, and 8 non-internal public triggers on each copy;
- no installed `vector` extension in either database.

The repository then ran entirely against the PostgreSQL 18 test database through a temporary SSH
tunnel:

- Alembic current: `0011_factions_time (head)`;
- ruleset/catalog integrity validation: passed;
- Ruff lint: passed;
- Ruff formatting check: 85 files formatted;
- Pytest: 126 passed, 2 intentionally opt-in live OpenClaw tests skipped, 1 existing TestClient
  deprecation warning; elapsed time 279.62 seconds.

The suite exercises migration upgrades/downgrades, UUID/JSONB persistence, constraints, triggers,
transactions, deterministic resolution, restart behavior, and the complete M3 Lantern scenario.
No live provider call was required for database compatibility. The existing warning remains tracked
as `WARN-001` and is not a PostgreSQL 18 regression.

## 6. Harmless execution corrections

The following stopped before causing an uncontrolled change and were corrected within scope:

- the first signing-key fingerprint check had shell quoting that prevented the check from running;
  it was corrected before the signed source was installed;
- the first package command found that the intended `createcluster.d` directory did not yet exist;
  the directory and disable-auto-cluster fragment were then created and verified before APT ran;
- the first PostgreSQL 18 starts failed because the configuration helper serialized the numeric
  loopback address first without quotes and then with doubled quotes. The cluster never became
  reachable in either attempt. The exact valid `listen_addresses = '127.0.0.1'` line was installed,
  parsed independently, and the cluster then started loopback-only;
- an initial Bluebuild `/health` probe returned 404 because that service does not define that route;
  its actual `/`, `/docs`, and `/openapi.json` surfaces all returned 200.

These events did not interrupt PostgreSQL 15, Bluebuild, or unrelated databases. They are retained
here so later operators do not repeat the same diagnostics.

## 7. Follow-up status

The separately authorized development restore and cutover rehearsal subsequently passed; see
`POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md`. Both PostgreSQL 18 Gandalf databases now exist and have
accepted relational/runtime evidence. The active application subsequently cut over successfully to
PostgreSQL 18. PostgreSQL 15 copies and roles remain intact for stabilization/rollback, and pgvector
is still not enabled in either database.
