# M5.5 Health, Recovery, and Encounter Outcomes Evidence

- **Status:** Implemented; owner acceptance pending
- **Implemented:** 2026-09-05
- **Migration:** `0019_combat_health_outcomes`
- **Rules catalog:** `srd-5.2.1-combat-v2`
- **Depends on:** M5.4 deterministic attacks and damage
- **External provider calls:** None
- **Clawvis/infrastructure changes:** None

## 1. Outcome

M5.5 completes the deterministic lifecycle around the supported Fighter/Goblin combat slice. Combat
now derives and persists encounter difficulty inputs, Second Wind, death saves, first aid,
stabilization, damage while at 0 HP, massive death, explicit melee knockout, automatic victory or
defeat, explicit surrender/flight/agreement, thrown-Javelin recovery, and one bounded encounter
completion summary.

The application still owns every numeric mechanic. A client selects a typed action and exact
identities; it cannot supply HP, a modifier, an Armor Class, damage, a die face, or a resource
total. Temporary HP absorption and keep/replace semantics are implemented in the pure kernel and
damage resolver. This initial content slice deliberately exposes no Temporary HP grant command,
because its supported Fighters and Goblins have no canonical feature that grants a pool. A future
source-backed feature must derive the amount before that persistent operation is added.

## 2. Durable state and safeguards

Migration `0019_combat_health_outcomes` adds:

- difficulty label plus exact enemy XP and Low/Moderate/High party budgets on each encounter;
- outcome, bounded summary, and completion time on each completed encounter;
- death-save successes/failures and the encounter projection of canonical Second Wind uses;
- immutable `combat_health_resolutions` and `combat_outcome_resolutions`;
- `combat_dropped_items`, linking each thrown item to the attack that placed it on the battlefield;
- check constraints, encounter/command/catalog scope triggers, immutable-evidence triggers, and
  deferred two-way Second Wind consistency between a character and its active combatant.

The migration was proved in both directions while empty and was also proved upgrading an existing
active encounter. Downgrade refuses to discard recorded health, outcome, or recovery evidence.

## 3. Supported mechanics

- **Difficulty:** for the current level-one party, enemy XP is compared with published 50/75/100
  XP per-character Low/Moderate/High inputs. `favorable`, `low`, `moderate`, and `high` are strict
  boundary labels, not promises that an encounter is safe or balanced.
- **Second Wind:** the active Fighter spends one Bonus Action and one canonical use, rolls exactly
  `1d10 + Fighter level`, caps HP at maximum, records the die, and synchronizes both projections.
- **Death saves:** an unconscious player character at 0 HP rolls on its active turn. Natural 20
  restores 1 HP; natural 1 adds two failures; three successes stabilize; three failures kill.
- **First aid:** an adjacent active player character can spend its Action on a DC 10 Wisdom
  (Medicine) check to stabilize an unconscious player character.
- **Damage at 0 HP:** a close-range hit against an unconscious target is critical; damage while
  down adds failures, and sufficient remaining damage can cause instant death.
- **Temporary HP:** damage consumes Temporary HP before ordinary HP; Temporary HP is not healing,
  cannot restore consciousness, and pools do not add. No current public grant source exists.
- **Knockout:** only a pre-declared qualifying melee attack can leave the target unconscious at 1
  HP. A ranged request or after-the-fact retcon is rejected.
- **Completion:** no fighting enemies produces victory; no fighting party members produces defeat.
  Surrender, flight, and agreement are explicit typed outcomes. Completion closes the active turn,
  advances the campaign world revision, and emits exactly one material campaign summary.
- **Post-combat continuity:** a later encounter refuses any party member whose newest completed
  combat state is unconscious, stable, dead, fled, or surrendered, or whose canonical HP is 0.
  Gandalf does not silently heal, awaken, return, or resurrect them while the out-of-combat
  rest/recovery slice remains deferred.
- **Thrown recovery:** Javelins are recovered after victory, agreement, or enemy surrender. They
  remain dropped after defeat, party flight, or party surrender.

## 4. API additions and changes

- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/health-actions`
  supports `second_wind`, `death_save`, and `stabilize`.
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/outcome`
  supports explicit `surrender`, `flight`, and `agreement`.
- Attack requests add the optional Boolean `knock_out` intent.
- Encounter reads add difficulty inputs, death-save counters, Second Wind uses, outcome, completion
  summary, and completion time.
- New encounters default to immutable catalog `srd-5.2.1-combat-v2`; existing v1 encounters retain
  their exact behavior and identity.

Both new command paths are idempotent and revision-checked. Invalid, stale, wrong-turn, wrong-target,
or unsupported requests reject before dice and state changes.

## 5. Verification

The sequential M5 combat gate passes 85 tests. It covers exact difficulty boundaries; health
kernel boundaries; persistent Second Wind; death-save 1/20 and accumulated outcomes; first aid;
Temporary HP damage absorption; rejection of a caller-invented Temporary HP pool; explicit
knockout; close-range critical damage while down; massive death; monster death; automatic victory
and defeat; surrender, flight, and agreement; Javelin recovery; one bounded completion event;
idempotency; reconnect; projection consistency; migration reversal; upgrade over an existing active
encounter; and refusal to silently reactivate a defeated party in a later encounter.

Static lint, formatting, compilation, ruleset checksum/schema validation, migration head, and
schema-drift checks pass. The final complete repository suite passes 239 tests with three expected
opt-in live OpenClaw skips and the already tracked TestClient deprecation warning. M5.5 makes no
provider call.

The development database upgraded from `0018` to `0019` with zero schema drift. A dry run of the
owner fixture created nine isolated development campaigns and returned every documented value:
the four difficulty boundaries, 12 HP/one use/no Bonus Action after Second Wind, byte-equivalent
reconnect state, natural-20 revival at 1 HP, explicit 1-HP knockout victory, distinct stable and
unconscious defeat states, rejected no-recovery re-entry, and exactly one recovered Javelin plus
one completion event.

During verification, the long-lived disposable test schema exhausted PostgreSQL column slots from
repeated historical migration churn. Only `gandalfdnd_test.public` was rebuilt after a validated
PostgreSQL 18 custom-format backup; development data, roles, packages, services, Clawvis, and every
other database were untouched. A second gate found and fixed the ordering needed to backfill
Second Wind safely over an existing active encounter. A final continuity review closed the
new-encounter path that could otherwise reactivate a defeated character without recovery. These
are preserved as ISSUE-021 through ISSUE-023 in the living plan.

## 6. Owner gate and next boundary

Run the focused owner checklist in
[`player/M5_5_ACCEPTANCE_CHECKLIST.md`](player/M5_5_ACCEPTANCE_CHECKLIST.md). It creates isolated
development campaigns and prints concise deterministic evidence for difficulty wording, recovery,
death-save revival, explicit knockout, defeat, item recovery, and reconnect.

M5.6 must not start until that review is accepted or its findings are reworked. M5.6 then adds typed
provider combat intent and post-resolution narration, bounded M4 context, complete scenario replay,
and a separately authorized live OpenClaw supplement.
