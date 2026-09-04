# M5.2 Encounter Persistence and Initiative Evidence

- **Status:** Done
- **Completed:** 2026-09-05
- **Migration:** `0016_combat_encounters`
- **Ruleset:** `srd-5.2.1`
- **Character-state catalog:** `srd-5.2.1-party-state-v1`
- **Combat catalog:** `srd-5.2.1-combat-v1`
- **Combat catalog SHA-256:**
  `423b80e84593738d4cadc5537278d208a51fbebacbb074a2d79531f0ee023204`
- **Resolver:** `combat-resolution-1.0.0`
- **External provider calls:** None
- **Clawvis/infrastructure changes:** None

## 1. Outcome

M5.2 establishes the durable deterministic combat boundary. A complete finalized Party Commander
party and supported Goblin instances can now enter a guarded encounter, receive exact application-
owned initiative rolls, explicitly resolve every equal-total tie, reconnect, and replay the same
order from pinned definitions and recorded faces.

This slice deliberately stops at the start of round one. Movement, actions, reactions, attacks,
damage, and encounter completion remain assigned to M5.3-M5.5.

## 2. Durable records

Migration `0016_combat_encounters` adds:

- `combat_encounters` with campaign/active-scene identity, immutable rules/catalog/hash/resolver
  pins, bounded grid size, revision, status, round, and active-turn position;
- `combatants` with stable encounter identity, exact character or monster origin, fixed source
  snapshot, HP/AC/Speed/initiative projection, starting cell, state, and revision;
- `combat_commands` with campaign-scoped idempotency keys, typed payloads, expected revisions, and
  stable result identities;
- `combat_initiative_ties` with exact participant sets and an explicit decided order;
- append-only `combat_events` with encounter-local sequence numbers;
- nullable combat attribution on the existing `dice_rolls` boundary: encounter, combatant,
  command, and per-command roll index.

Database protections enforce one open encounter per campaign, bounded non-overlapping starting
cells, finalized active party membership in the same campaign, valid command scope, matching combat
dice identities and catalog pins, immutable command/event/source facts, immutable resolved ties,
and downgrade refusal after material combat evidence exists.

## 3. API contract

The following endpoints are available and documented with structured 404/409/422 error responses:

- `POST /campaigns/{campaign_id}/combat-encounters`
- `GET /campaigns/{campaign_id}/combat-encounters/{encounter_id}`
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/start`
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/initiative-ties/{tie_id}`
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/replay`

Clients provide identities, starting cells, catalog identity, and expected revisions. They do not
provide HP, AC, Speed, initiative modifiers, monster stats, dice faces, or inferred tie order.

Encounter creation requires exactly every finalized active party member, a supported immutable
monster definition, the campaign's active scene, the current world revision, and no existing open
encounter. Monster HP uses the catalog's fixed average value.

Initiative validates the encounter, scene, pins, revision, and unchanged character source state
before rolling. Party modifiers come from canonical character mechanics; monster modifiers come
from the pinned combat catalog. Every roll is written once in the same transaction as the command,
state, and events. Equal totals leave all order positions unset until an explicit exact participant
ordering is submitted.

## 4. Replay and recovery

Replay reloads the pinned combat catalog, recomputes each initiative result from the recorded d20
face and stored canonical modifier, reapplies explicit tie decisions, and compares the recomputed
order with the stored order. A connection-pool recreation followed by GET returns the identical
encounter representation.

Repeated command IDs with the same typed payload return the existing encounter without rolling or
emitting another event. Reuse with a different payload returns 409. Stale world or encounter
revisions, unsupported monsters, wrong party membership, inactive scenes, or a second open
encounter fail before dice and roll back atomically.

## 5. Verification

Focused M5.2 coverage proves:

- canonical 12 HP, AC 17, Speed and initiative +4 for both current Fighter fixtures;
- fixed Goblin Warrior 10 HP, AC 15, Speed 30, and initiative +2;
- exact no-tie order, round-one activation, dice attribution, and replay;
- an equal-total player tie remains pending until the submitted exact order is accepted;
- an invalid tie participant set changes no revision or tie state;
- create/start retries do not reroll or duplicate events;
- stale creation/start and unsupported content create no rolls or partial encounter;
- a second open encounter is rejected;
- command and combat-event records reject direct mutation;
- downgrade refuses to discard recorded combat data;
- empty downgrade/re-upgrade remains reversible, including when earlier tests cleared catalog rows.

Commands used for final verification:

```text
.venv/bin/ruff check app tests alembic/versions/0016_combat_encounters.py
.venv/bin/python -m compileall -q app alembic/versions/0016_combat_encounters.py
.venv/bin/pytest -q tests/test_combat_encounters.py tests/test_rulesets.py
.venv/bin/pytest -q
```

The focused encounter/ruleset gate passes 13 tests. The complete suite passes 206 tests with three
intentional opt-in live OpenClaw skips and the already tracked TestClient deprecation warning.
Static checks, compilation, migration head, and zero schema drift also pass. M5.2 makes no provider
call.

## 6. Issues found and resolved

### ISSUE-018 - empty migration re-upgrade omitted the release seed

The first full regression run exposed an edge case in an older test that intentionally downgrades
an empty database and upgrades it after all ruleset rows have been truncated. The first M5.2
migration draft inserted the combat catalog without first restoring its parent SRD release row.
That caused one migration failure and a cascade of later fixture setup errors; it did not alter
development data or indicate a gameplay failure.

The migration now idempotently restores the immutable SRD release identity before inserting the
combat catalog, matching the earlier rules migrations. The exact empty downgrade/re-upgrade test,
the combined 13-test encounter/ruleset gate, and all 206 repository tests pass afterward.

## 7. Next boundary

M5.3 adds turn identities and budgets, stepwise movement, Dash, Disengage, Dodge, end-turn
advancement, and explicit Opportunity Attack reaction windows. It must reuse these encounter,
combatant, command, roll, event, revision, and replay boundaries rather than create parallel state.
