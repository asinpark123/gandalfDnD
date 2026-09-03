# M3 Persistent World Implementation Strategy

- **Status:** Done (2026-09-04)
- **Prepared:** 2026-09-03
- **Depends on:** M2 two-stage AI turn and model-authored feasibility (Done)
- **Owner input required now:** None for M3 closure; separate authorization is required only for the
  optional capped live OpenClaw supplement
- **Owner checkpoint:** M3.5 passed on 2026-09-04

## 1. Objective

M3 will make people, scenes, relationships, objectives, decisions, time, clues, and revealed
knowledge durable canonical campaign state. A player decision must produce a structured,
explainable consequence that survives application restart and remains isolated to the correct
campaign and actor.

M3 extends rather than replaces the M2 turn boundary:

```text
explicit player action, actor, and optional world target/choice
    -> typed interpretation
    -> deterministic rules resolution when required
    -> narration plus bounded typed world proposals
    -> world/visibility/stale-state validation
    -> one atomic commit of projections and causal events
```

The model may propose narrative state, but PostgreSQL and application services decide whether the
proposal is legal. Narrative prose never creates a fact, relationship, quest transition, revealed
clue, elapsed time, or mechanical effect by implication.

## 2. Evidence and current foundation

M3 starts from these verified M2 guarantees:

- Party Commander turns have explicit actor IDs and independently revised character state;
- application code owns rules, modifiers, dice, and accepted mechanical outcomes;
- interpretation and narration are typed, audited, retryable, and run outside open transactions;
- finalization atomically commits validated state changes and ordered events;
- stage leases recover interrupted work without rerolling;
- private OpenClaw and deterministic providers obey the same local validation boundary;
- provider context is compact and usage-audited.

The current `Location` row is an exact spatial fact but is not a complete scene. There are no
canonical NPCs, presence records, relationships, quests, choices, clock, or knowledge state. The
M2 live evaluation demonstrated the consequence: after the party moved away from the inn, a model
could still narrate a greeting to the innkeeper because no structured target or NPC-presence fact
existed. M3.1 addresses that specific gap first.

The preserved research recommends that SRD mechanics and narrative state meet through events,
with durable world facts carrying causal event IDs and optional explicitly validated mechanical
semantics. M3 adopts that boundary but deliberately implements it in small slices rather than
creating the research report's entire proposed schema at once.

## 3. Non-negotiable invariants

1. **Stable identity:** authoritative references use UUIDs, never name matching.
2. **Explicit target:** an action against an NPC carries the selected NPC ID in the command; the
   model does not silently decide which same-named entity was meant.
3. **Presence:** a target must be active, player-known, and present in the current scene unless a
   typed command explicitly supports remote interaction.
4. **Causality:** every accepted world projection cites the event that created or superseded it.
5. **No prose authority:** narration cannot establish a world or mechanical fact by itself.
6. **Mechanical firewall:** a narrative fact is mechanically inert unless an implemented rule or
   versioned house-rule definition authorizes its exact semantics.
7. **Explicit visibility:** player and DM-only records use data-layer filters; prompt instructions
   are not the security boundary.
8. **No hidden-context leak:** M3 providers receive only player-visible world facts. A hidden fact
   must pass a typed reveal transition before it can enter player narration context.
9. **Atomicity:** a rejected proposal changes no scene, NPC, fact, objective, decision, clock, or
   final event.
10. **World concurrency:** every canonical world change increments one campaign `world_revision`;
    a turn finalizes only against its stored character and world revisions.
11. **Append-only evidence:** corrective/superseding records preserve their causal history; APIs do
    not silently rewrite event history.
12. **Bounded context:** providers receive the current scene, present visible actors, relevant
    active objectives, and selected revealed facts—not the full world ledger or event history.

## 4. Scope and deferrals

M3 includes:

- current scenes tied to existing locations;
- stable NPC and faction identity plus scene presence;
- typed narrative world facts and relationships;
- quests/objectives with legal status transitions;
- explicit decision points and selected branches;
- monotonic narrative world time;
- clues/knowledge with controlled reveal;
- player-safe world reads and internal audience-filtered projections;
- provider context derived from the same canonical projection;
- restart, branching, visibility, rollback, and context-budget evidence.

M3 does not include:

- embeddings, semantic search, pgvector, or unbounded prose memory (M4);
- combatants, initiative, attacks, damage, conditions, or encounter state (M5);
- the spoiler-safe Guide retrieval service (M6);
- a player frontend or visual quest journal (M7);
- companion autonomy, Lone Hero compensation, or broader character content;
- arbitrary numeric reputation, automatic bonuses from relationships, milestone levelling, or
  model-created mechanical curses;
- a generic rules DSL, workflow engine, graph database, Redis, Celery, or Docker.

## 5. Canonical data direction

The names below are the intended direction and may be narrowed during an implementation slice when
a test proves a smaller design is sufficient.

### 5.1 Campaign world checkpoint

Add `campaigns.world_revision`, defaulting and backfilling to `0`. Add
`turns.world_revision_before` and `turns.world_revision_after` so M2 recovery can reject narration
that was generated from stale world state just as it already rejects stale character state.

Every service that mutates a scene, NPC presence, fact, quest, decision, or clock must lock the
campaign, validate the expected revision, and increment it exactly once per atomic command/turn.

### 5.2 Scenes and NPCs

`scenes` provide the bounded current interaction context:

- campaign and location IDs;
- campaign-scoped sequence and stable title;
- `active` or `closed` status;
- revision plus opening/closing causal event IDs;
- short player-visible summary, bounded as context rather than an authoritative fact dump.

Exactly one scene is active per campaign. Existing campaigns are backfilled with one active scene
at their current location.

`npcs` provide stable identity:

- campaign ID, UUID, name, bounded public description;
- `active` or `inactive` lifecycle status;
- `player` or `dm_only` visibility;
- revision and introduction event ID.

`scene_npc_presences` link an NPC to a scene with `present`/`departed` state and arrival/departure
events. A partial uniqueness rule prevents one NPC from being presently active in two scenes.

Names are display data and need not be globally unique. UUIDs are authoritative.

### 5.3 World facts and relationships

`world_facts` store immutable or explicitly superseded structured facts:

- campaign, subject kind/ID, predicate, typed JSON value;
- optional object kind/ID for relationships;
- `player` or `dm_only` visibility;
- source event, superseded fact, and current/superseded status;
- nullable `mechanical_semantics`.

The application validates every subject/object reference and uses a small predicate registry rather
than accepting arbitrary behavior. Initial predicates are narrative-only and deliberately narrow:

- `attitude` with `friendly`, `indifferent`, or `hostile` labels;
- `relationship_note` with bounded text and no score;
- `promise` with `made`, `kept`, or `broken` state;
- `discovery` and `clue` with explicit visibility;
- `faction_membership` referencing an existing faction.

These labels can guide future narration but grant no modifier, Advantage, condition, item, feature,
or resource. Non-null mechanical semantics are rejected until a cited rule or house-rule resolver
exists.

### 5.4 Quests, objectives, and decisions

M3.3 `quests` group ordered objectives under stable campaign-scoped keys. Provider-authored quests
are player-visible and begin active. Quests and objectives use application-owned state machines:

```text
quest:     active -> completed | failed | abandoned
objective: pending -> active | skipped
           active  -> completed | failed | skipped
```

Illegal transitions fail before any projection or event write. Completion never grants XP, levels,
items, or other mechanics unless a separate typed rules/reward command is implemented later.

`decision_points` contain a stable ID and key, bounded prompt, visibility, open/selected state, and
two to four typed options with stable keys. `TurnExecutionCreate` may carry `decision_id` and
`decision_option_key`; the application—not the interpreter—validates campaign ownership,
visibility, open status, option identity, and the stored consequence list before provider work. A
successful finalization records the selected branch exactly once.

An option may contain up to ten prevalidated narrative consequences: a typed fact/attitude record,
a quest transition, or an objective transition. The immutable list is stored when the decision
opens, included only in provider context for the explicitly selected option, and applied atomically
at finalization. It cannot contain an HP, inventory, reward, resource, condition, or other
mechanical write.

### 5.5 Factions, time, clues, and knowledge

`factions` use stable campaign-scoped UUID/key identity, explicit visibility, lifecycle, revision,
and causal creation events. Dedicated `faction_relationships` hold one typed party attitude or
typed character/NPC memberships with their own revisions and causal create/update events. Values
are fixed narrative labels rather than numeric reputation and have no mechanical effect.

Narrative world time is monotonic elapsed minutes on the campaign. A typed
`narrative_time_advance` proposal advances 1 to 10,080 minutes, records its reason, and is limited to
one per turn. It does not trigger rests, resource recovery, spell durations, exhaustion, or travel
mechanics until those deterministic resolvers exist.

Clues are typed world facts. A reveal creates an auditable player-visible successor or knowledge
record; it does not mutate a hidden row in place and lose history. Public APIs and provider context
must not contain the hidden fact's value before that reveal event.

## 6. API and provider contracts

### 6.1 Campaign setup

Extend campaign creation compatibly with an optional bounded `starting_scene` containing a title,
summary, and up to eight player-visible starting NPC definitions. Omitting it preserves existing
behavior: the starting location becomes an empty active scene.

This is a campaign-authoring input, not permission for later player turns to create arbitrary NPCs.
Future generated campaign setup can produce the same validated contract.

### 6.2 Player world read

Add one initial aggregate endpoint:

```text
GET /campaigns/{campaign_id}/world
```

It returns the campaign world revision and clock, active scene/location, present visible NPCs,
visible factions/facts, visible quests/objectives, visible decisions, and revealed
knowledge. It never accepts an `include_hidden` query switch.

Internal services use an explicit audience enum and separate projection functions. Raw ORM queries
must not become an accidental public serialization path.

### 6.3 Turn command

Extend the authoritative turn command with optional explicit fields:

```text
target_npc_id
decision_point_id
decision_option_key
```

The API validates campaign ownership, visibility, presence, and open-decision state before provider
work. Idempotent command retries must preserve the same target/choice and reject a changed payload.

### 6.4 Typed proposals

Refactor the narration `state_changes` union into clearly dispatched mechanical and world proposal
families without changing the existing JSON discriminator:

- existing HP, inventory, and location proposals;
- NPC introduce/arrive/depart proposals;
- fact create/supersede/reveal proposals;
- quest/objective/decision proposals;
- bounded time advancement.

Each proposal receives domain validation and produces a named event. The full proposal list is
validated before any mutation, then applied in the existing finalization transaction.

### 6.5 Context projections

M3 adds a stage-appropriate compact world projection containing:

- world revision and narrative clock;
- active scene/location;
- present player-visible NPCs and selected target;
- active visible objectives and open selected decision;
- only relevant player-visible current facts.

DM-only values are excluded in M3. This limits secret-aware story planning but gives an enforceable
spoiler boundary. A future planner/narrator separation may use hidden facts only after it has a
design that prevents them from reaching player output; that is not assumed here.

## 7. Delivery sequence

### M3.1 — Scene and NPC presence foundation

**Status:** Done (2026-09-03)

Player outcome: a player can target a known present NPC, while an absent, hidden, inactive, or
cross-campaign NPC is rejected before any provider call.

Deliver:

- campaign/turn world revisions;
- scenes, NPCs, scene presence, migration/backfill, and guarded downgrade;
- optional starting scene/NPC campaign input;
- player-safe aggregate world read;
- explicit turn target and provider context;
- movement closes/opens scenes and makes prior presences unavailable unless explicitly moved;
- causal events and atomic rollback.

Exit evidence: presence/absence, duplicate names, cross-campaign IDs, hidden NPC filtering,
movement, actor/target isolation, idempotency, stale-world finalization, restart, migration, and
context-budget fixtures pass.

Implemented evidence:

- migration `0008_world_presence` adds guarded/backfilled campaign and turn world revisions,
  scenes, stable NPC identities, scene presence, causal event links, and explicit NPC targets;
- campaign creation accepts up to eight optional starting NPCs, while omitted input remains
  compatible and creates a safe empty active scene;
- `GET /campaigns/{campaign_id}/world` returns only active, player-visible NPCs in the active scene;
- target UUID validation rejects hidden, inactive, absent, and cross-campaign NPCs before provider
  work, and command idempotency includes the target;
- interpretation and narration receive a bounded player-safe current-world projection and reject
  a changed `world_revision` after an external provider call;
- accepted movement closes the prior scene, opens the destination scene, advances the world
  revision once, emits causal events, and makes prior presences unavailable;
- six focused M3.1 tests plus the full 102-test normal suite, lint, and zero Alembic drift pass; the
  opt-in live OpenClaw test remains skipped and no external call or Clawvis change was made.

### M3.2 — Typed facts, relationships, and reveal

**Status:** Done (2026-09-03)

Player outcome: an NPC can remember a promise or attitude across turns and restart, while a hidden
clue remains absent until an explicit reveal.

Deliver:

- typed world-fact registry and supersession;
- narrative-only attitudes, relationship notes, promises, discoveries, and clues;
- explicit audience-filtered projections;
- fact create/supersede/reveal proposals and causal events;
- rejection of arbitrary predicates and all unsupported mechanical semantics.

Exit evidence: fact persistence/supersession, no numeric reputation mechanics, hidden API/provider
exclusion, reveal history, rollback, restart, campaign isolation, and context-budget fixtures pass.

Implemented evidence:

- migration `0009_world_facts` adds typed current/history rows, causal event links, single-step
  supersession, guarded downgrade, fixed attitude labels, and database checks that require NPC
  subjects for relationships and promises;
- narration proposals support fixed NPC attitudes, relationship notes, promises, discoveries,
  clues, explicit fact supersession, and reveal; extra fields and unknown/mechanical shapes fail the
  strict provider contract;
- all proposals are prevalidated before mutation, campaign/NPC/revision ownership is enforced, and
  each accepted fact mutation advances `world_revision` and emits a named causal event;
- hidden facts can be recorded only through the trusted internal boundary, remain absent from the
  player world API, player events, interpretation context, and narration context, and become public
  only after an explicit reveal event;
- public current facts survive restart, superseded rows remain queryable history, and only facts for
  the current scene's NPCs plus campaign-wide facts enter provider context;
- provider context retains the newest 50 relevant facts and reports the omitted count, keeping the
  101-fact synthetic fixture below its serialized budget;
- seven focused M3.2 tests and all 109 normal tests pass with lint, compilation, and zero Alembic
  drift; the live OpenClaw scenario remains an optional post-closure supplement.

### M3.3 — Quests, objectives, and branching decisions

**Status:** Done (2026-09-03)

Player outcome: a visible choice can lead two otherwise identical campaigns to different durable
facts/objective states, with the selected branch explainable from events.

Deliver:

- quests/objectives and legal transitions;
- open decision points with two to four stable option keys;
- explicit choice fields in the turn command;
- prevalidated narrative consequence lists;
- exact-once branch selection and ordered events.

Exit evidence: legal/illegal transitions, changed-payload idempotency conflict, double-choice
rejection, two-campaign branch divergence, restart, partial-proposal rollback, and no implicit reward
mechanics pass.

Implemented evidence:

- migration `0010_quests_decisions` adds campaign-scoped quests, ordered objectives, open/selected
  decision points, two-to-four keyed options, immutable JSON consequence lists, exact-once
  selections, explicit turn choice fields, database constraints, causal links, and a guarded
  downgrade;
- strict narration proposals create quests/decisions and perform revision-checked legal quest or
  objective transitions; terminal, stale, duplicate-key, cross-campaign, and overlapping
  quest/objective writes fail before mutation;
- turn creation validates both choice fields, decision visibility/open status, option membership,
  and all stored narrative consequences before interpretation, while changed-payload retries
  conflict and identical retries return the original turn;
- finalization revalidates the choice against the locked world checkpoint, records one selection,
  then applies ordered typed fact/attitude or quest/objective consequences atomically before the DM
  response event; provider proposals cannot overlap the selected branch's transitions;
- the player world projection retains visible quest and decision history without exposing stored
  consequences, while provider context receives at most 20 active quests and 20 open decisions and
  receives only the selected option's consequence list;
- eight focused M3.3 tests prove persistence/restart, legal and illegal transitions, exact-once
  idempotency, double-choice rejection, two-campaign divergence, ordered causal events, atomic
  rollback, overlap rejection, guarded migration, and the absence of implicit reward mechanics;
  all 117 normal tests pass with one opt-in live test skipped, plus lint, compilation, and zero
  Alembic drift.

### M3.4 — Factions, narrative clock, and complete visibility projection

**Status:** Done (2026-09-03)

Player outcome: faction membership, elapsed narrative time, revealed clues, and current objectives
remain coherent after movement and restart without causing unimplemented rest/combat mechanics.

Deliver:

- faction identities and typed memberships/attitudes;
- bounded monotonic clock advancement;
- complete world aggregate and compact provider projection;
- visibility matrix across every M3 entity;
- migration and synthetic context-size checks.

Exit evidence: time monotonicity/bounds, no automatic resource refresh, faction isolation,
visibility adversarial suite, 100+ world-fact context budget, restart, and zero migration drift pass.

Implemented evidence:

- migration `0011_factions_time` adds nonnegative campaign elapsed minutes, stable faction rows,
  typed party-attitude and character/NPC-membership rows, revision/event links, constrained values,
  campaign ownership foreign keys, uniqueness rules, and guarded downgrade;
- strict proposals create player-visible factions, create or revision-update fixed-label
  relationships, and advance narrative time by 1–10,080 minutes at most once per turn; validation
  rejects stale, duplicate, unchanged, hidden, cross-campaign, and overflow states before writes;
- faction labels and elapsed time are mechanically inert: no HP, resource, inventory, rest,
  duration, travel, or condition behavior is inferred from them;
- `get_world_state` now supports explicit internal `player` or `dm` audiences and safely defaults
  to `player`, while the public API and both provider stages use the player projection; hidden NPCs, facts, quests,
  decisions, factions, relationships, and DM-only events remain absent from all player paths;
- the canonical player read retains complete visible current/history projections, while provider
  context keeps only 50 relevant facts, 20 active quests, 20 open decisions, 20 active factions,
  and 50 faction relationships with explicit omitted counts;
- six focused M3.4 tests prove typed relation create/update, time bounds and monotonicity, no
  mechanical refresh, atomic rollback, faction/member campaign isolation, full visibility
  adversarial projection, restart durability, 101-fact plus large-entity context budgets, and
  destructive-migration refusal; all 123 normal tests pass with one opt-in live test skipped, plus
  lint, compilation, ruleset/schema integrity, and zero Alembic drift.

### M3.5 — Branching Lantern verification and owner gate

**Status:** Done (2026-09-04)

Run a deterministic two-character world scenario that covers:

1. interaction with a present NPC;
2. rejection of an absent target before provider work;
3. movement and scene transition;
4. NPC arrival/departure;
5. promise/attitude persistence;
6. quest offer and acceptance;
7. explicit decision selection;
8. divergent branch outcomes in cloned initial campaigns;
9. hidden clue exclusion and typed reveal;
10. bounded time advancement;
11. database-engine disposal and restart;
12. complete causal-event and world-revision replay.

After deterministic gates pass, prepare a concise owner API checklist. The owner's subjective test
focuses on whether decisions, NPC continuity, and quest consequences feel coherent; automated tests
remain responsible for exact IDs, visibility, revisions, state transitions, rollback, and migration
safety. Request separate permission before a capped OpenClaw version of the scenario.

M3 reached Done after the deterministic scenario and owner API gate passed. A live OpenClaw run is
optional additional evidence and requires separate authorization; any model failure is classified
and corrected and never weakens the canonical state or visibility boundary.

Automated evidence:

- the completed two-character Lantern fixture creates two isolated campaigns from the same setup,
  accepts the same quest, then explicitly selects `signal_bridge` in one and `flooded_tunnel` in the
  other; both reach revision 20 and 90 elapsed minutes while producing different objective states
  and typed discoveries;
- present-NPC interaction, absent-target pre-provider rejection, movement, NPC introduction,
  automatic scene departure, explicit departure/arrival, promises, attitudes, quest acceptance,
  hidden-clue exclusion/reveal, faction relationships, and bounded time all cross real two-stage
  turn/finalization boundaries;
- movement now marks every old-scene presence departed with a causal event, and strict typed
  `npc_introduce`, `npc_arrive`, and `npc_depart` proposals validate campaign, lifecycle,
  visibility, current presence, duplicate mutation, and move-overlap rules before writes;
- engine disposal preserves byte-equivalent player world projections; an independent event fold
  reconstructs the exact scene, present cast, current facts, quests/objectives, decisions, faction
  relationships, clock, and every world revision from 0 through 20;
- every scene, presence, fact, quest, decision, faction, and faction relationship retains its
  required causal event link, and rejected mixed presence/movement proposals write no world state;
- two focused M3.5 tests and all 125 normal tests pass with one opt-in live test skipped, plus
  formatting, lint, compilation, ruleset/schema integrity, and zero Alembic drift on both databases;
- `player/M3_5_ACCEPTANCE_CHECKLIST.md` and the guarded development fixture runner supported the
  owner coherence/restart review. No Clawvis change or external model call was made.

The initial owner review confirmed the exact backend state, restart, causality, visibility, and
mechanical-isolation items, but its subjective result was inconclusive. The runner had already
selected both decisions, and duplicate-name NPCs created in one transaction could be ordered by
UUID, causing the returned Mira to differ from the promise subject. The corrected fixture identifies
the guide by stable role, asserts her ID across facts/travel/return, and pauses so the owner selects
quest acceptance and both routes while seeing staged world summaries. It also exposes a documented
HTTP 409 body with `world_target_not_present` and safe recovery guidance. The focused scenario, all
125 normal tests, static/integrity checks, both database drift checks, and a scripted end-to-end run
passed; at that checkpoint the narrowed owner retest remained the only required M3 gate.

Owner closure evidence (2026-09-04): both guided campaigns retained the promise-bearing watchful
innkeeper's exact UUID through travel and fresh API reads. The owner personally accepted both quests
and selected `flooded_tunnel` then `signal_bridge`; the first branch failed the objective and stored
only the collapse discovery, while the second completed it and stored only the rescue discovery.
Both final worlds remained at Old Tower, revision 20, after 90 minutes. The real absent-target call
returned documented HTTP 409 with `world_target_not_present` and recovery guidance, and all four
subjective questions passed. The raw result is preserved as
`testM3_5_TARGETED_RETEST_RESULTS.md`; no further M3 retest is required.

## 8. Verification matrix

| Area | Required evidence |
| --- | --- |
| Identity | Stable UUID target; duplicate names harmless; cross-campaign ID rejected |
| Presence | Present accepted; departed/hidden/inactive/other-scene target rejected pre-provider |
| Causality | Every projection links to a named event; supersession history remains readable |
| World concurrency | Stale world revision rejects finalization with no partial commit |
| Atomicity | One invalid world proposal rolls back the entire final proposal set |
| Visibility | DM-only records absent from public API, provider context, and player event list |
| Facts | Typed predicates/values only; unsupported mechanical semantics rejected |
| Decisions | Open visible option selected once; retries idempotent; altered choice conflicts |
| Branching | Same initial state plus different option produces explainably different projections |
| Time | Positive bounded monotonic advance; no implicit rest/resource effect |
| Restart | Exact scene, presence, facts, quest, choice, clock, and revisions survive engine disposal |
| Context | Current relevant projection remains bounded as historical world rows grow |
| Migration | Existing campaigns receive a safe empty active scene; full-chain upgrade and drift pass |
| Regression | All M0–M2 character, rules, turn, recovery, and OpenClaw contract tests remain green |

## 9. Failure and error policy

Add stable player-recoverable errors where applicable:

- `world_target_not_found`;
- `world_target_not_visible`;
- `world_target_not_present`;
- `world_state_stale`;
- `world_fact_invalid`;
- `world_mechanics_unsupported`;
- `quest_transition_invalid`;
- `decision_not_open`;
- `decision_option_invalid`;
- `world_time_invalid`.

Errors should include safe IDs and corrective context but never hidden names, facts, or option
content. As with M2, provider failure remains resumable only from a safe persisted checkpoint;
domain validation failure before provider work creates no provider audit.

The corrected M3.5 candidate implements documented `detail`, `code`, and `recovery` responses for
not-visible, inactive, and absent target conflicts. A missing/cross-campaign target retains the
existing safe 404 shape pending broader API error normalization in M7.

## 10. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Generic JSON facts become an untyped shadow database | Small predicate registry, typed commands, domain validators, and no arbitrary semantics |
| Hidden facts leak through API/model/audit output | Audience-filtered projections, no hidden M3 provider context, adversarial tests, safe errors |
| Names become accidental identity | UUID command targets; duplicate-name fixture; names remain display-only |
| Provider invents many duplicate NPCs/quests | Bounded proposals, stable IDs, lifecycle validation, and creation limits |
| World changes race with slow provider calls | Campaign `world_revision` checkpoint plus final locked fresh read |
| Full world state recreates M2 token overhead | Current-scene/relevant-fact projection and explicit serialized-size tests |
| Narrative labels silently affect mechanics | Nullable semantics rejected by default; explicit rule/house-rule resolver required |
| Early schema anticipates combat or RAG | Slice-specific tables only; combat remains M5 and vector memory remains M4 |

## 11. Rework and completion rule

Each slice is committed only when it crosses migration, ORM, schema, API, service, events, tests,
and documentation. A later slice that invalidates an earlier visibility, identity, causality, or
restart guarantee moves that slice back to Rework. M3 planning is complete with this document.
M3.1–M3.4 and M3.5 are verified and complete. The corrected deterministic branching Lantern
scenario, lifecycle, restart, event replay, guided choice flow, recoverable absent-target contract,
and owner checkpoint pass. M3 is Done; a capped live OpenClaw run remains optional supplemental
evidence and requires separate authorization.
