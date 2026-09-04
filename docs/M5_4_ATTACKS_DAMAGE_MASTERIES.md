# M5.4 Attacks, Damage, Equipment, and Masteries Evidence

- **Status:** Done
- **Completed:** 2026-09-05
- **Migration:** `0018_combat_attacks`
- **Depends on:** M5.3 turn, movement, effect, and reaction boundary
- **External provider calls:** None
- **Clawvis/infrastructure changes:** None

## 1. Outcome

M5.4 turns an active combat turn or selected Opportunity Attack into one authoritative, replayable
attack. The application derives the weapon, attack and damage modifiers, Armor Class, range,
Fighting Style, mastery, inventory, effects, and exact dice from canonical state and the pinned
combat catalog. A client supplies identities and intent only; it cannot supply a bonus, die face,
damage total, Armor Class, HP result, or effect.

Ordinary attacks spend the current actor's Action. A selected Opportunity Attack resolves inside
its named reaction window without spending the mover's Action, then changes the window to
`opportunity_attack_resolved` so the exact interrupted movement can continue. Every accepted attack
updates the encounter, both combatants, any affected character projection, inventory, effects,
rolls, and audit events in one transaction.

## 2. Durable records and guards

Migration `0018_combat_attacks` adds:

- `combat_attack_resolutions`, containing the exact command, pinned rules/catalog/resolver, actor
  and target revisions, deterministic inputs, resolved attack, damage application, roll references,
  and RNG version;
- `combat_attack` as an idempotent command type;
- `opportunity_attack_resolved` as the terminal successful reaction-window state;
- the guarded Slow-adjusted movement allowance for an affected combatant's turn.

Database triggers require the command, encounter, opposing actor/target, and optional reaction
window to agree; reject alteration or deletion of an attack resolution; preserve immutable reaction
identity while allowing only `pending -> passed/opportunity_attack_pending ->
opportunity_attack_resolved`; defer-check that active combatant HP equals canonical character HP at
transaction commit; and refuse migration downgrade once any attack has been recorded.

## 3. Supported mechanics

- Player attacks: Greatsword, Flail, and Javelin in their catalog-supported modes.
- Goblin Warrior attacks: Scimitar and Shortbow; the same catalog path also supports the scoped
  Goblin Minion attack.
- Natural 1 always misses; natural 20 always hits and doubles only damage dice; equality with Armor
  Class hits.
- Normal and long range, long-range Disadvantage, adjacent-hostile ranged Disadvantage, melee reach,
  and beyond-reach rejection before any attack roll.
- Canonical inventory and one free interaction to hold an available weapon; a thrown Javelin is
  removed from carried inventory exactly once. Battlefield recovery is completed with encounter
  recovery in M5.5 rather than being silently assumed.
- Great Weapon Fighting changes each eligible Greatsword damage die result of 1 or 2 to 3,
  including every doubled critical die. Defense remains represented in canonical AC. Archery does
  not apply to a thrown Javelin because the catalog classifies it as a melee weapon.
- Graze applies only the ability modifier on a qualifying Greatsword miss and does not create
  hit-only damage dice.
- Sap gives Disadvantage to exactly the affected target's next attack before expiring.
- Slow reduces the affected target's next active movement allowance by 10 feet and retains its
  source-turn expiry boundary.
- Damage updates monster or character combat projections atomically. M5.4 uses the required narrow
  interim zero-HP result—monster `dead`, player character `unconscious`; complete death-save,
  stabilization, knockout, and recovery semantics belong to M5.5.

## 4. API additions

- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks`
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks/{resolution_id}/replay`

The attack response contains both the immutable resolution and the resulting complete encounter
projection. Repeating an identical `command_id` returns the original resolution and encounter
result without rerolling. Reusing it with different content remains a conflict.

## 5. Verification

The focused kernel and integration gate proves:

- ordinary hit, below-AC and natural-1 miss, exact-AC hit, natural-20 critical, Great Weapon
  Fighting, and the exact original/adjusted dice;
- normal/long/adjacent range behavior and no-roll atomic rejection outside melee reach;
- Javelin inventory decrement, free-interaction equipment state, no Archery bonus, Slow persistence,
  and the target's 20-foot affected turn;
- Greatsword Graze miss damage, Flail Sap application/one-attack consumption, and all three mastery
  outcomes from canonical character grants;
- selected Goblin Opportunity Attack damage, one-Reaction consumption inherited from M5.3,
  terminal window resolution, and continuation of the original movement without spending its
  Action;
- command idempotency, attributed application dice, semantic replay from stored dice, exact
  reconnect state, opposing target isolation, two-way deferred character/combatant HP consistency,
  immutable attack evidence, and guarded downgrade;
- migration `0018` at head and zero model/schema drift in both development and test databases.

The focused pure-kernel plus persisted-combat gate passes 62 tests. Static lint/format, compilation,
ruleset integrity, generated-schema freshness, and both database migration/drift checks pass. The
complete repository suite passes 216 tests with three expected opt-in live OpenClaw skips and the
already tracked TestClient deprecation warning.

Two pre-commit defects were found and resolved by this gate. The first `0018` reaction guard treated
legitimate response fields as immutable before evaluating a legal status transition; it now
protects only identity and explicitly validates the allowed transitions. Critical damage also kept
the base weapon notation (`2d6`) while storing four faces; the resolver now records the actual
critical notation (`4d6`) for weapon and bonus damage. See ISSUE-019 and ISSUE-020 in the living
plan.

## 6. Next boundary

M5.5 completes the health and encounter lifecycle: Temporary HP ordering, Second Wind, full zero-HP
and death-save behavior, stabilization/first aid, damage while down, massive damage, explicit melee
knockout, monster death, defeat/surrender/flight/agreement outcomes, thrown-item recovery, bounded
material encounter summaries, and strict-SRD party difficulty measurements. No owner decision is
required before implementation; the first required owner combat playtest remains after M5.5.
