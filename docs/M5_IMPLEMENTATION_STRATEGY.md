# M5 Core Deterministic Combat Implementation Strategy

- **Status:** In progress at M5.2; M5.0-M5.1 Done
- **Prepared:** 2026-09-05
- **Depends on:** M1 character/rules foundation (Done), M3 persistent world (Done)
- **Uses:** M2 resumable provider boundary and M4 bounded memory, only after deterministic combat
- **Rules baseline:** SRD 5.2.1
- **Initial play mode:** Party Commander, 2-4 directly controlled player characters
- **Owner input required before M5.1:** None
- **First owner playtest:** After M5.5, before final provider/live evaluation

## 1. Objective

M5 adds one small but complete martial-combat loop whose results are reproducible from canonical
pre-state, typed commands, immutable rule definitions, and recorded dice. A player will be able to
start an encounter, roll initiative, act with each party member in order, move, attack, use Second
Wind, suffer damage and defeat, finish the encounter, reconnect, and replay the exact mechanics.

M5 does not attempt to implement all D&D combat. It proves the shared Party Commander engine that
later classes, spells, companions, and lone-hero balancing must reuse. Broader combat rules and
content are tracked explicitly in M10 rather than being left as an unnamed backlog.

```text
player or bounded GM intent
    -> typed combat command
    -> campaign/encounter/actor/target/revision validation
    -> application-owned dice
    -> pure versioned combat resolver
    -> one atomic state transition plus immutable combat/campaign evidence
    -> bounded exact outcome for narration
```

The model may propose an action or narrate an accepted result. It may not supply attack bonuses,
Armor Class, damage modifiers, dice faces, resource totals, conditions, initiative order, or state
writes.

## 2. Verified foundation to reuse

- Campaigns are pinned to immutable SRD release and normalized catalog identities.
- Party Commander already enforces 2-4 finalized, separately addressable characters.
- Every supported character exposes source-backed AC, initiative, Speed, current/maximum HP,
  equipped weapons, Fighting Style, weapon-mastery grants, Second Wind, and Hit Dice.
- `DiceService` owns randomness and records an algorithm version; fixed injected dice support exact
  tests.
- M1.4 proves canonical modifiers, Advantage/Disadvantage cancellation, immutable rolls,
  idempotency, and restart replay for checks and saves.
- M2 proves slow provider work can happen outside transactions and be rejected after a stale-state
  check without rerolling.
- M3 supplies stable scene/NPC identities and world revisions; world prose remains mechanically
  inert.
- M4 supplies bounded cited history separately from exact state and must not become combat truth.

M5 extends these contracts. It does not create a second character sheet, dice generator, world
identity system, or provider-controlled state path.

## 3. Source-backed initial rules slice

The initial normalized combat catalog will cite the pinned official SRD artifact and cover:

| Area | Initial supported rule | Printed SRD pages |
| --- | --- | ---: |
| Turn structure | rounds, turns, one Action, movement up to Speed, one Bonus Action when granted, one Reaction until next turn | 9-10, 13-14 |
| Initiative | Dexterity check, Advantage/Disadvantage, descending order, explicit tie decisions | 13, 183 |
| Grid | optional 5-foot squares, diagonal adjacency, occupancy, Speed in 5-foot steps | 13-14 |
| Attacks | target/range/modifier validation, AC comparison, Advantage/Disadvantage, natural 1/20 | 7, 14-15 |
| Damage | weapon dice, one ability modifier, critical damage dice twice, minimum zero | 16 |
| Health | Resistance/Vulnerability order, healing cap, Temporary HP, 0 HP, death saves, stabilization | 16-18 |
| Core actions | Attack, Dash, Disengage, Dodge, a narrow first-aid Help, movement, end turn | 9-10, 177-190 |
| Reaction | Opportunity Attack and reaction refresh | 10, 15, 184, 186 |
| Fighter | Second Wind, Fighting Style, Weapon Mastery | 47-48, 87-90 |
| Equipment | Greatsword, Flail, Javelin; Heavy, Thrown, Two-Handed, range | 89-91 |
| Masteries | Graze, Sap, Slow | 90 |
| Opponents | Goblin Minion and Goblin Warrior fixed stat blocks | 254-256, 290 |
| Encounter budget | level-one per-character Low/Moderate/High XP inputs | 202-203 |

The official PDF remains the normative source. The deep-research report supplies implementation and
test strategy, but its temporary citation tokens are not normative references.

## 4. Supported content and explicit deferrals

### 4.1 Supported in M5

- current level-one Human/Soldier/Fighter characters in 2-4-member Party Commander parties;
- Greatsword, Flail, and Javelin melee attacks;
- thrown Javelin attacks, normal/long range, close-combat Disadvantage, and exact recoverable-item
  state;
- Defense and Great Weapon Fighting where their requirements are met;
- Archery correctly not applying to a thrown Javelin because Javelin is a Melee weapon;
- Two-Weapon Fighting remaining inert because the current equipment route supplies no Light-weapon
  pair;
- Graze, Sap, and Slow only when the actor has mastery for the used weapon;
- Goblin Minion Dagger and Goblin Warrior Scimitar/Shortbow actions;
- fixed average monster HP, exact stat-block AC/initiative/attacks, and SRD XP values;
- open rectangular 5-foot-square battlefields with explicit starting cells and movement paths;
- Attack, Dash, Disengage, Dodge, Opportunity Attack, Second Wind, first aid/stabilize, free
  attack-related equip/unequip, pass, and end-turn behavior;
- current HP, Temporary HP mechanics, Unconscious/Incapacitated/Prone/Stable/Dead states, and
  transient Dodge/Sap/Slow effects;
- ordinary monster death at 0 HP, explicit player-character death rules, explicit melee knockout,
  and encounter end by defeat, surrender, flight, or agreement;
- deterministic enemy policy for automated fixtures and a later strictly typed GM-provider intent.

Temporary HP and Resistance/Vulnerability are kernel and health-boundary coverage in M5; the
initial supported Fighter/Goblin content does not invent a feature that grants either one.

### 4.2 Deferred from M5

Most broader combat and rules content below has a durable destination in M10. Companion and
lone-hero behavior follows the separately recorded party-mode sequence, while presentation remains
in M7.

- spellcasting, concentration, magical damage, areas of effect, and spell-slot rules;
- classes/species/backgrounds or equipment routes not already supported by M1;
- full Grapple/Shove/Unarmed Strike, general Help, Hide, Ready, Search, Study, Influence, Magic, and
  arbitrary Utilize actions;
- cover, concealment, lighting, elevation, difficult terrain, mounts, underwater combat, flight,
  squeezing, and non-square maps;
- every condition beyond those required by this slice;
- broad monster import, Multiattack, recharge abilities, legendary actions, lairs, summons, and
  arbitrary monster traits;
- general Short/Long Rest execution, adventuring-day enforcement, XP awards, levelling, loot, and
  economy; Second Wind expenditure is in scope, while its rest refresh waits for a dedicated rest
  slice;
- companion autonomy, lone-hero compensation, or hidden encounter scaling;
- frontend combat presentation; M7 will render turn order, legal actions, rolls, damage, effects,
  errors, and cited explanations.

Unsupported commands must return a stable typed error before dice or state changes. They must not
be approximated through free-form prose.

The explicit knockout rule is a narrow exception to the general-rest deferral: M5 may represent its
required one-hour unconscious recovery boundary without exposing a voluntary Short Rest command or
refreshing unrelated rest-based resources.

## 5. Tactical representation

M5 uses a bounded integer grid internally because exact reach, weapon range, movement, occupancy,
and Opportunity Attacks require more than a narrative distance label. This is a Gandalf product
representation, not a claim that the SRD requires a grid.

- One cell is 5 feet; Small and Medium creatures occupy one cell.
- Orthogonal and diagonal entry each costs one 5-foot step on the initial open grid.
- The command supplies an ordered path; the server validates every adjacent cell, boundary,
  occupancy rule, and remaining movement. The server does not guess a path from prose.
- Movement can occur before and after actions through separate idempotent step commands.
- A movement step that leaves a visible hostile creature's reach opens a reaction window unless the
  mover Disengaged or another exact exception applies.
- The initial API may offer a theatre-of-the-mind client convenience later, but it must translate to
  this same canonical position/path contract before resolution.

This representation is deliberately smaller than a virtual tabletop: no map editor, token art,
fog of war, physics, or client framework belongs to M5.

## 6. State and persistence design

M5.2 will validate exact names, but the minimum durable concepts are:

### 6.1 `combat_encounters`

- campaign and active scene IDs;
- ruleset release, combat catalog, and resolver versions;
- setup/initiative/tie/active/completed/cancelled status;
- encounter revision, round number, active turn position, and elapsed combat rounds;
- bounded grid dimensions;
- outcome, winning side, end reason, and opening/completion event identities;
- exactly one active encounter per campaign.

### 6.2 `combatants`

- encounter-scoped UUID and side;
- exactly one character ID or one immutable monster definition/instance identity;
- optional world NPC identity without treating an NPC name as combat identity;
- starting/current/max HP, Temporary HP, AC, Speed, size, position, initiative modifier/count;
- active/unconscious/stable/dead/fled/surrendered state;
- source snapshot/catalog identity and per-combatant revision.

Character HP and resources remain canonical on `characters` and update atomically with their
combatant projection. Monster combat state lives on its encounter instance. Database constraints
must reject divergent character/combatant projections rather than allowing two truths.

### 6.3 `combat_turns` and effects

- immutable round/turn identity and active/completed state;
- action, Bonus Action, Reaction, free interaction, movement, and attack entitlements;
- transient typed effects with source, target, start/end boundary, stacking key, and active status;
- explicit reaction windows and responses so optional reactions are never assumed silently.

### 6.4 commands, resolutions, rolls, and events

- each command has a campaign-scoped idempotency key, actor, targets, expected encounter and
  combatant revisions, typed payload, status, and result;
- a combat resolution records all applied definitions, formulas, advantage sources, exact dice,
  attack/damage/healing outcome, and pre/post revisions;
- combat rolls extend the existing application dice boundary but identify encounter combatants, so
  monster rolls are not falsely attributed to a player character;
- immutable combat events provide fine-grained replay; bounded player-visible campaign events
  expose material outcomes without duplicating mutable truth.

`RuleResolution` remains the proven check/save record. M5 should not overload it with multi-roll
attack, damage, resource, reaction, and health transitions merely to avoid a focused combat record.

## 7. Transaction, concurrency, and replay rules

1. Validate campaign, active encounter, actor, target, turn ownership, catalog, range, equipment,
   resources, and expected revisions before rolling.
2. Lock the encounter plus every affected combatant/character in stable UUID order.
3. Generate each required roll once and record its algorithm version and purpose.
4. Resolve mechanics with a pure function that receives exact dice rather than calling randomness.
5. Persist the command, resolution, rolls, state projections, and ordered events in one transaction.
6. Repeated command IDs return the original result without a new roll or event.
7. Stale revisions, wrong actors, illegal timing, invalid targets, and insufficient resources reject
   atomically with no roll.
8. Replay recomputes from the recorded pre-state snapshot, catalog, command, and dice and compares
   semantic events and post-state.
9. Provider work happens outside the transaction. After it returns, the application reacquires
   locks and rejects a stale encounter before any dice.

No endpoint may accept client/model-supplied numeric bonuses, target AC, damage totals, remaining
HP, resource totals, effect duration, or initiative order as authority.

## 8. Resolution order and edge policies

- Attack Advantage/Disadvantage uses the existing cancellation semantics, then natural 1 always
  misses and natural 20 always hits and is critical.
- A normal hit requires the total to equal or exceed current target AC.
- Critical hits roll the attack's damage dice twice; fixed modifiers are added once.
- Great Weapon Fighting transforms eligible individual weapon-die faces of 1 or 2 to 3 before
  summing. It is not a reroll.
- Graze can apply ability-modifier weapon damage on a miss, including a natural 1, but cannot turn
  the miss into a hit or critical and cannot trigger on-hit effects.
- Resistance is applied after ordinary damage adjustments; Vulnerability follows Resistance.
- Temporary HP absorbs damage first and never counts as healing or consciousness recovery.
- Second Wind uses one Bonus Action and one resource use, rolls `1d10 + Fighter level`, and caps
  current HP at maximum.
- A player-character at 0 HP follows Unconscious/death-save rules; a monster ordinarily dies at 0.
- A melee attacker must explicitly choose knockout before resolution; the engine never infers mercy
  from tone or changes a completed lethal result afterward.
- Difficulty labels report only the published XP-budget category and warnings. They are not
  guarantees of safety or subjective balance.

Any unresolved interpretation discovered during implementation must be added to
`docs/rules/RULINGS.md` before code silently chooses behavior.

## 9. Delivery slices

### M5.0 - Strategy and source map

**Status:** Done on 2026-09-05.

- inspect the official pinned SRD combat, equipment, Fighter, glossary, monster, and encounter pages;
- reconcile the adopted research with current implementation;
- define the supported slice, deferrals, state boundaries, risks, fixtures, and owner checkpoints.

### M5.1 - Combat catalog and pure kernel

**Status:** Done on 2026-09-05. Evidence:
[`M5_1_COMBAT_CATALOG_KERNEL.md`](M5_1_COMBAT_CATALOG_KERNEL.md).

- add immutable `srd-5.2.1-combat-v1` definitions and generated schema;
- extend catalog composition without mutating existing campaign/character catalog identities;
- implement pure attack, damage, healing, Temporary HP, initiative, and effect-duration functions;
- cover Fighter weapons/styles/masteries and Goblin Minion/Warrior actions;
- add fixed-dice golden tests for boundary rolls and resolution order;
- make no database migration and no provider call in this slice.

Exit: catalog/hash/schema/source checks pass and every pure resolver fixture replays identically.

### M5.2 - Encounter persistence and initiative

**Status:** Ready.

- add guarded encounter/combatant/initiative/command/event schema;
- instantiate finalized party members and supported monster definitions with stable IDs;
- validate scene presence, one active encounter, fixed average monster HP, starting cells, and
  campaign isolation;
- roll initiative once, preserve exact faces, and resolve explicit tie groups without UUID-order or
  database-order accidents;
- expose create/read/start/tie/replay APIs and restart evidence.

Exit: a 2-4-member party and supported enemies enter the same exact order after replay/reconnect;
illegal or stale starts produce no rolls or partial encounter.

### M5.3 - Turn economy, movement, and reactions

- add active-turn enforcement and explicit move/action/Bonus Action/Reaction/free-interaction
  budgets;
- validate stepwise grid movement, split movement, Dash, Disengage, Dodge, and end turn;
- implement reaction windows and Opportunity Attack/pass choices without double reactions;
- reject inactive, wrong-side, out-of-turn, over-budget, occupied, out-of-bounds, and stale commands.

Exit: a complete round advances exactly once, every combatant acts only when legal, and reconnect
restores the exact active turn, remaining movement, action economy, effects, and reaction state.

### M5.4 - Attacks, damage, equipment, and masteries

- integrate Attack commands and immutable attack/damage resolutions;
- implement Greatsword, Flail, and melee/thrown Javelin plus the supported Goblin attacks;
- enforce hands, proficiency, range, close-ranged Disadvantage, Heavy, criticals, Fighting Styles,
  Graze, Sap, Slow, and thrown-item state;
- apply damage atomically and prove exact replay, idempotency, party/target isolation, and event order.

Exit: hit, miss, natural 1, natural 20, critical, long range, Opportunity Attack, and all three
mastery fixtures reproduce exact rolls and post-state after restart.

### M5.5 - Health, recovery, defeat, and encounter completion

- integrate Temporary HP, Resistance/Vulnerability order, Second Wind, 0 HP, death saves,
  stabilization, damage while down, massive damage, explicit knockout, and monster death;
- complete encounter outcomes for defeat, surrender, flight, or agreement;
- preserve character HP/resources after encounter and emit one bounded material encounter summary;
- add strict-SRD level-one XP-budget simulations without claiming guaranteed balance.

Exit: favorable, Low, Moderate, High, defeat, recovery, knockout, death-save, and reconnect fixtures
remain deterministic and never cross character/campaign boundaries.

### M5.6 - World/provider integration and acceptance

- add strict typed combat intents and outcome narration after deterministic resolution;
- send only the active combat slice plus bounded relevant world/memory context to the provider;
- reject model bonuses, dice, targets, resources, and state writes;
- ensure M4 stores bounded material combat memory rather than every atomic combat event;
- run the complete deterministic Party Commander scenario, owner backend checklist, context/usage
  measurements, and only then request separate authorization for a capped live OpenClaw supplement.

Exit: the owner accepts understandable combat outcomes and difficulty feedback; the complete fixed
scenario replays through restart; provider failure/staleness cannot roll twice or partially commit.

## 10. Permanent acceptance matrix

| Fixture | Required result |
| --- | --- |
| Initiative boundaries | Advantage/Disadvantage and Alert derive from state; every tie needs an explicit legal decision; reconnect preserves order |
| Attack roll boundaries | Natural 1 misses, natural 20 hits/criticals, equality with AC hits, and no client modifier is accepted |
| Critical damage | Damage dice double, modifiers do not; every original/transformed face is retained |
| Great Weapon Fighting | Eligible Greatsword damage faces 1/2 become 3; ineligible weapons/styles do not receive it |
| Graze | Greatsword mastery damage can occur on a miss but never triggers hit-only behavior |
| Sap | Flail hit gives exactly the target's next attack Disadvantage before the attacker's next turn |
| Slow | Javelin hit reduces Speed by 10 feet once and expires at the correct start-turn boundary |
| Range/equipment | Melee, normal range, long-range Disadvantage, beyond-range rejection, close-range Disadvantage, hands, and thrown inventory are exact |
| Action economy | One Action, at most one granted Bonus Action, one Reaction/reset, split movement, and free interaction cannot be exceeded |
| Opportunity Attack | Leaving visible hostile reach opens the correct reaction; Disengage and forced-movement exclusions prevent it |
| Damage order | adjustments, Resistance, Vulnerability, Temporary HP, then HP follow the exact order and rounding |
| Temporary HP | pools never add; keep/replace is explicit; healing does not restore them; 0 HP plus Temporary HP stays unconscious |
| Second Wind | consumes one Bonus Action/use, rolls once, caps healing, rejects zero uses, and survives reconnect |
| Zero HP | monster death, PC unconsciousness, death-save 1/20, three successes/failures, damage while down, massive damage, stability, and healing are exact |
| Knockout | only an explicit melee choice produces 1 HP plus Unconscious; ranged attacks and post-result retcons reject |
| Party isolation | every command/roll/effect/event identifies the actor and target; one member's resources and HP never alter another's |
| Idempotency/concurrency | retries return the original result; stale/out-of-turn commands create no roll, event, or partial state |
| Replay | fixed pre-state, catalog, commands, and dice reproduce initiative, every resolution/event, final HP/resources/effects, and outcome |
| Provider boundary | generated prose cannot change mechanics and generated numeric mechanics are rejected before dice |
| Memory boundary | only bounded material combat outcomes become cited memory; exact current combat state remains relational |

## 11. Difficulty and balance evidence

M5 reports the published per-character level-one XP inputs: 50 Low, 75 Moderate, and 100 High. It
will test at least 2- and 4-character parties against supported goblin compositions at under-budget,
exact-budget, and high-budget points. Seeded simulations record:

- win/defeat rate;
- rounds to completion;
- HP and Second Wind use by character;
- characters reaching 0 HP or dying;
- attacks and damage by side;
- Action/Bonus Action/Reaction utilization;
- initiative and first-turn advantage;
- retreat/knockout/recovery outcomes.

These are engineering observations, not official balance ratings or promises. Party Commander
results become the baseline for later companion and lone-hero comparison. No M5 result authorizes
silent encounter scaling or player-character buffs.

## 12. Owner checkpoints

- **Before M5.1:** no input required. The strict rules/content slice is already constrained by the
  accepted character and Party Commander decisions.
- **After M5.2:** optional review of the grid/turn-order API. The default remains a 5-foot grid unless
  practical evidence shows it is too cumbersome.
- **After M5.4:** optional structured-output review; visual usability remains an M7 question.
- **After M5.5:** required playtest of favorable, difficult, defeat, recovery, and restart cases,
  focusing on whether outcomes feel fair and understandable rather than whether JSON looks polished.
- **After M5.6:** final owner acceptance and a separate decision on any live OpenClaw call cap.

The owner need not choose companion autonomy, lone-hero buffs, spell priorities, or broad monster
content during M5.

## 13. Risks and stop conditions

- Stop if an implementation would duplicate canonical character HP/resources rather than enforce
  atomic equivalence.
- Stop if a combat command can roll before every legal-state and stale-revision check passes.
- Stop if initiative or simultaneous-effect ties are resolved by incidental UUID/database order.
- Stop if a provider can supply numeric mechanics or an unvalidated target.
- Stop if broad rules generalization grows faster than the concrete Fighter/Goblin slice.
- Stop and add a ruling when natural-language SRD behavior needs a deterministic interpretation.
- Reassess context projection if a representative combat provider call materially exceeds M4's
  measured input size without a mechanically necessary reason.
- Keep Clawvis, PostgreSQL packages/clusters, and unrelated services unchanged during repository-only
  M5 slices. Any infrastructure or live-model operation remains separately authorized.

## 14. Immediate implementation order

1. Design the guarded M5.2 schema against the state/persistence boundaries in section 6.
2. Add encounter, combatant, initiative, idempotent command, roll, and event persistence through one
   Alembic migration with downgrade refusal after material combat records exist.
3. Add create/read/start/tie/replay APIs with exact campaign, scene, party, catalog, and revision
   validation before dice.
4. Prove campaign isolation, exact ties, retries, rollback, reconnect, and migration safety.
5. Record M5.2 evidence and update this strategy before advancing to M5.3.
