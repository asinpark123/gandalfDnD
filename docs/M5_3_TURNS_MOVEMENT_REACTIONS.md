# M5.3 Turn Economy, Movement, and Reactions Evidence

- **Status:** Done
- **Completed:** 2026-09-05
- **Migration:** `0017_combat_turns_movement`
- **Depends on:** M5.2 encounter and initiative boundary
- **External provider calls:** None
- **Clawvis/infrastructure changes:** None

## 1. Outcome

M5.3 makes an active initiative order playable as exact combat turns. Each turn now has one Action,
one available Bonus Action, one free interaction, a 30-foot canonical movement allowance for the
current supported creatures, and a persistent Reaction owned by each combatant. The server, rather
than prose or a model, validates the active actor, revisions, path, occupancy, boundaries, budget,
action use, effect timing, and turn advancement.

This slice adds no attack or damage roll. It establishes the timing and state boundary that M5.4
will use for ordinary and Opportunity Attacks.

## 2. Durable records and guards

Migration `0017_combat_turns_movement` adds:

- `combat_turns` with round/order identity, active/completed state, movement allowance/spend,
  Action/Bonus Action/free-interaction availability, Disengage state, and encounter revisions;
- `combat_effects` with exact source/target, stacking identity, start/end round, source-turn expiry,
  and creating command;
- `combat_reaction_windows` with exact mover/reactor, round and boundary cells, opening/responding
  commands, response, and revisions;
- `combatants.reaction_available`, refreshed at the start of that combatant's next turn;
- the new idempotent command types `combat_move`, `combat_action`, `combat_reaction`, and
  `end_combat_turn`.

Database guards enforce encounter-scoped turn actors and initiative positions, movement allowance
bounded by Speed/Dash, one active turn per encounter, one turn per combatant per round, one active
effect per target/stacking key, opposing-side reaction identities, immutable source identities, and
refusal to downgrade after material turn data exists.

## 3. Supported behavior

### Movement

- A command supplies an ordered list of destination cells; the server never guesses a path.
- Orthogonal and diagonal entry each costs 5 feet.
- Every step must be adjacent, inside the bounded grid, and unoccupied.
- Movement can be split across multiple commands and cannot exceed the current allowance.
- Invalid, stale, occupied, over-budget, wrong-actor, and out-of-turn requests commit nothing.
- An idempotent retry returns the existing result without moving twice or adding another event.

### Actions and turns

- Dash spends the Action and adds the actor's Speed to this turn's movement allowance.
- Disengage spends the Action and prevents Opportunity Attack windows for this turn.
- Dodge spends the Action and creates one nonstacking effect that expires exactly at the start of
  the source combatant's next turn.
- End Turn completes the current immutable turn identity, advances exactly once to the next eligible
  initiative position, increments the round only after the last eligible combatant, refreshes the
  next actor's Reaction, expires source-turn effects, and opens a fresh budget.

### Reactions

- Leaving an active hostile combatant's 5-foot reach without Disengaging opens an explicit reaction
  window before movement is committed.
- `pass` leaves the Reaction available and allows a retried movement command across that exact
  boundary during the same round.
- `opportunity_attack` consumes the reactor's Reaction and changes the window to
  `opportunity_attack_pending`; movement and turn continuation remain blocked until M5.4 resolves
  the attack. This is an intentional fail-closed integration seam, not a completed zero-damage
  attack.
- A window cannot be answered by another combatant, answered twice, silently defaulted, or bypassed
  by continuing the turn.

## 4. API additions

- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/move`
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/actions`
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/reaction-windows/{window_id}`
- `POST /campaigns/{campaign_id}/combat-encounters/{encounter_id}/end-turn`

The encounter read model now includes the active turn, all typed effects, all reaction windows, and
per-combatant Reaction availability. Numeric movement allowance, spend, position, and effect timing
are server-owned.

## 5. Verification

The focused gate proves:

- split movement, persistent spend, Dash expansion, one-Action enforcement, and idempotent retry;
- wrong-actor rejection and occupied-cell rollback without revision changes;
- a complete three-combatant round advances to round two exactly once with a fresh first turn;
- Dodge remains active through intervening turns and expires on its source's next turn;
- the complete state is byte-for-byte equivalent through connection-pool recreation;
- leaving reach commits no movement until the named enemy explicitly passes;
- passing preserves the Reaction and permits the exact retried boundary movement;
- Disengage prevents the same reaction window;
- selecting an Opportunity Attack consumes one Reaction and blocks movement until attack
  resolution exists;
- migration `0017` upgrades/downgrades cleanly when empty and refuses material data loss;
- the full migration/ruleset/combat gate passes 18 tests.

The complete repository suite passes 210 tests with three expected opt-in live OpenClaw skips and
the already tracked TestClient deprecation warning. Static formatting/lint, compilation, migration
head, and schema-drift checks pass.

## 6. Next boundary

M5.4 will resolve ordinary and pending Opportunity Attacks through the immutable combat catalog,
record attack and damage dice once, apply exact range/equipment/style/mastery rules and HP changes,
then release or stop pending movement based on the deterministic result. It must not weaken M5.3's
turn, reaction, stale-state, idempotency, or no-partial-write guarantees.
