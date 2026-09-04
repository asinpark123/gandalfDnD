# M5.1 Combat Catalog and Pure Kernel Evidence

- **Status:** Done
- **Completed:** 2026-09-05
- **Rules baseline:** SRD 5.2.1
- **Catalog:** `srd-5.2.1-combat-v1`
- **Catalog SHA-256:**
  `423b80e84593738d4cadc5537278d208a51fbebacbb074a2d79531f0ee023204`
- **Resolver:** `combat-resolution-1.0.0`
- **Migration:** None
- **API/provider/infrastructure changes:** None

## 1. Outcome

M5.1 establishes the immutable data and pure mechanical kernel that later encounter persistence,
turn economy, and combat APIs must call. Given the same catalog, canonical numeric inputs, and
recorded dice faces, the functions return the same structured result without reading a database,
generating randomness, or contacting a model.

This slice does not make combat playable through the API. That begins with M5.2 encounter and
initiative persistence and continues through M5.3-M5.6.

## 2. Immutable combat catalog

The new supplemental catalog extends the existing
`srd-5.2.1-party-state-v1` identity by its exact SHA-256. It does not change the existing
character-creation, state, or check/save catalog files or hashes.

It contains source-cited definitions for:

- initiative, attack-roll, natural 1/20, Critical Hit, damage, healing, Resistance,
  Vulnerability, and Temporary Hit Point rules;
- Javelin, Flail, Greatsword, Dagger, Scimitar, and Shortbow attack data;
- all four currently selectable Fighter Fighting Styles, including the rule that Archery applies
  to Ranged weapons and not a thrown Javelin, which remains a Melee weapon;
- enabled Graze, Sap, and Slow masteries plus exact Sap/Slow/Dodge duration records;
- fixed average HP, AC, initiative, Speed, XP, and supported attacks for Goblin Minion and Goblin
  Warrior;
- the published level-one Low/Moderate/High per-character XP inputs, explicitly without promising
  a safe or balanced outcome.

The printed Nick and Vex properties of monster weapons are preserved as source facts but are not
enabled masteries in M5. Unsupported content is never silently approximated.

The registry format advances to `1.3.0` to recognize `combat` as a supplemental catalog kind.
`get_combat_catalogs()` verifies the complete creation -> state -> combat dependency chain and each
base checksum before returning a composed rules view. The existing party-state catalog remains the
default campaign catalog; M5.2 will add the database catalog record and encounter pins in a guarded
migration.

## 3. Pure resolver contracts

`app/combat.py` provides strict structured inputs/results for:

- **Initiative:** Advantage/Disadvantage cancellation, exact one/two-d20 requirements, selected
  face, modifier, total, rules/catalog provenance, and resolver version.
- **Character attacks:** the exact three-weapon player slice, supported attack mode, natural 1 miss,
  natural 20 hit/Critical Hit, equality with AC, exact damage-die count, fixed modifier once, thrown
  Javelin Archery exclusion, Great Weapon Fighting, and enabled mastery effects.
- **Monster attacks:** catalog-owned attack/damage modifiers and Goblin Warrior extra damage when
  the net attack state actually has Advantage; criticals double both applicable damage-die groups.
- **Damage application:** Resistance first, then Vulnerability, then Temporary HP, then ordinary
  HP, preserving excess damage for later M5.5 massive-damage evaluation.
- **Healing:** maximum-HP cap with Temporary HP unchanged.
- **Temporary HP offers:** explicit keep/replace behavior; pools never add.
- **Timed effects:** Sap consumption on the affected target's next attack and source-turn expiry;
  Slow and Dodge source-turn expiry; unrelated boundaries leave the effect active.

The pure character attack function accepts derived attack/damage modifiers only as a kernel input.
It is not an endpoint. M5.4 must derive those values from the locked canonical character state and
must reject client/model numeric fields before calling the kernel.

## 4. Golden boundary evidence

The focused tests cover:

- catalog strictness, source/reference uniqueness, exact supported definition sets, dependency
  composition, and malformed range/mastery/reference rejection;
- Initiative Advantage, Disadvantage, cancellation, exact dice count, and invalid face rejection;
- natural 1 despite a high modifier, natural 20 despite AC 100, equality with AC, and critical die
  doubling without modifier doubling;
- Great Weapon Fighting transforming each eligible 1/2 face to 3 while retaining original faces;
- Archery not applying to a thrown Melee weapon, with broader non-M5 player weapons rejected even
  though their monster-facing source data remains available;
- Graze damage on a miss including a natural 1, Sap on a hit, Slow only on a damaging hit, and
  unsupported monster-weapon mastery rejection;
- Goblin catalog modifiers, ordinary advantage damage, and critical advantage damage;
- impossible attack modes, unknown identities, invalid AC/modifiers/faces, miss-with-damage input,
  and unearned bonus damage rejection;
- Resistance/Vulnerability order on an odd value, Temporary HP absorption, excess damage, healing
  cap, explicit Temporary HP keep/replace, and invalid health-state rejection;
- Sap consumption/expiry, unrelated effect boundaries, and unknown-effect rejection;
- exact semantic equality from two resolutions with identical catalog/input/dice.

## 5. Acceptance results

| Gate | Result |
| --- | --- |
| Focused combat tests | 48 passed |
| `app/combat.py` focused coverage | 97% (466 statements, 12 defensive-only lines uncovered) |
| Ruleset compatibility/migration tests | 9 passed sequentially |
| Complete repository suite | 202 passed, 3 expected opt-in live OpenClaw skips |
| Formatting and lint | Passed |
| Registry/catalog integrity | Passed with the pinned combat SHA-256 |
| Generated schema freshness | Passed; `combat.schema.json` and registry schema current |
| External calls | None |
| Database schema/data changes | None |

The existing Starlette TestClient/httpx deprecation warning remains `WARN-001`; it caused no test
failure.

## 6. Verification incident and durable lesson

An initial verification command launched `tests/test_combat.py` and `tests/test_rulesets.py` as
separate parallel pytest processes against the same configured test database. The ruleset suite
intentionally performs migration downgrade tests while the other process runs the global cleanup
fixture, producing missing-table and duplicate-type errors.

This was a test-orchestration collision, not a combat failure and not a migration defect. The
isolated `gandalfdnd_test` database was restored to head, its required tables were verified, and
both focused suites plus the complete suite passed sequentially. The development database was not
changed. Database-backed pytest processes must remain sequential unless each worker receives its
own isolated database.

## 7. Deferred boundaries

M5.1 deliberately does not add:

- encounter, combatant, command, roll, effect-instance, or combat-event tables;
- initiative ordering/tie decisions or restart persistence;
- range/distance, equipment, resource, turn-budget, or target authorization services;
- Second Wind execution, death saves, knockout, defeat, or encounter completion;
- HTTP endpoints, player checklists, provider prompts, narration, or live OpenClaw evaluation.

Those remain assigned to M5.2-M5.6. Temporary HP and Resistance/Vulnerability are kernel boundary
coverage only; the supported Fighter/Goblin roster does not invent a feature that grants them.

## 8. Next gate

M5.2 will add a guarded Alembic migration and API/service slice for encounter identity,
combatants, fixed starting state, initiative rolls, explicit tie decisions, immutable commands and
events, idempotency, campaign isolation, and exact restart/replay. It must reuse this catalog and
kernel rather than duplicate their mechanics.
