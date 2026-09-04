# Character and Deterministic Rules Specification

- **Status:** Active; M1.1–M1.4 verified and owner-accepted
- **Rules baseline:** SRD 5.2.1
- **Initial delivery scope:** M1.1–M1.4
- **Research basis:** [RES-001 review](../research/2026-08-30-character-system-adoption.md)
- **Rulings:** [Rules and product-rulings register](RULINGS.md)

This document defines the engineering contract for character creation and deterministic rules. It
does not claim that the described behavior exists until the project plan records implementation and
acceptance evidence.

## 1. Authority hierarchy

1. The immutable, licensed rules artifact and cited official pages define the selected SRD release.
2. Versioned normalized rule definitions encode the supported subset of that release.
3. Accepted entries in `RULINGS.md` define Gandalf interpretations, product policies, and house
   rules without mislabelling them as normative SRD text.
4. Code and migrations implement the selected definitions and rulings.
5. Automated and recorded manual tests establish whether the implementation works.
6. Narration explains validated outcomes but never overrides the sources above.

Every supported rule value exposed to a client must ultimately identify its ruleset release,
definition, and durable source citation.

## 2. Core invariants

### 2.1 Deterministic resolution

The following inputs must reproduce a semantically equivalent mechanical outcome:

```text
immutable pre-state
+ validated command
+ recorded dice faces
+ ruleset release and definition IDs
+ resolver/RNG algorithm versions
```

Dice may be unpredictable when generated. They become immutable replay input after recording.

### 2.2 Mechanical write boundary

Only a validated mechanical command processed by the rules/domain layer may create mechanical
events or projections. Model output and narrative text may propose a command but cannot directly
change HP, AC, ability scores, proficiency, conditions, resources, inventory, spell state, level, or
other mechanical properties.

### 2.3 Source facts and derived projections

Character selections and grants are canonical facts. Ability modifiers, proficiency bonus, check
modifiers, saving throws, maximum HP, AC candidates, initiative, speed, and similar values are pure
derivations from those facts and the pinned rules definitions.

Persisting a derived projection for performance is allowed only when it can be rebuilt, carries its
source revision, and is never accepted as an independent player/model edit.

### 2.4 Provenance

Every grant or choice records:

- character and campaign;
- ruleset release and rule-definition ID;
- source feature/background/species/class/feat/equipment definition;
- acquisition event and character revision;
- active/superseded state and permitted replacement timing;
- any choice slot that it satisfies.

### 2.5 Rules and narrative namespaces

Capitalized mechanical concepts such as the Frightened condition require a validated rule effect.
Narrative descriptions such as “the guard appears frightened” may be stored as memories or world
facts but are mechanically inert unless an accepted rule maps them to a typed effect.

## 3. M1 supported vertical slice

M1.2 verified the complete lifecycle for one level-one player character. M1.3 expanded the same
content slice into Party Commander: one human player directly controls multiple independently
addressable characters; M1.4 adds authoritative check/save resolution. Every initial party
character supports exactly:

- level one;
- Human species;
- Soldier background;
- Fighter class;
- standard-array ability generation;
- the legal ability assignment and background adjustment choices required for that path;
- all mandatory choices needed to finalize that path, including languages, skills, Fighting Style,
  Human Origin-feat choice, Fighter weapon mastery selections, and one defined starting-equipment
  route where the SRD requires them;
- derived ability modifiers, proficiency bonus, skills, saving throws, maximum HP, AC candidates,
  initiative, speed, Hit Die, proficiencies, carried/equipped items, features, and level-one Fighter
  resources;
- authoritative ability checks and saving throws with fixed-dice replay.

Combat execution, attack resolution, rests, broad conditions, spellcasting, levelling, custom
backgrounds, other species/classes, and arbitrary equipment shopping do not belong to the M1 exit
gate. Rule records may include prerequisites needed to explain the supported choices, but unsupported
options must be rejected rather than partially accepted.

Party Commander must not merge character sheets into one aggregate mechanical actor. Each command,
roll, event, state transition, resource, inventory record, and effect identifies its acting or
affected character. Supporting multiple characters from the same initial content slice proves party
state and action boundaries without prematurely expanding class/species breadth.

## 4. Character creation lifecycle

```text
DRAFT
  -> choose class
  -> choose origin: background, species, languages
  -> assign and adjust abilities
  -> choose alignment
  -> complete remaining required details and equipment
  -> validate all choices against one ruleset release
  -> FINALIZED
```

Requirements:

- Drafts may be incomplete but each recorded choice must be legal when made or explicitly pending a
  declared dependency.
- Candidate options come from the pinned normalized rules definitions, never free-form model text.
- Finalization is transactional and fails with structured, beginner-readable validation errors.
- Every consequential selection emits an auditable creation event.
- Finalized creation choices are immutable except through a defined advancement, replacement,
  migration, correction, or administrative workflow.
- Finalization records the exact ruleset, normalized-data schema, and resolver versions.
- Creation/finalization is per character; a Party Commander campaign becomes play-ready only when
  its required party members are finalized and no incomplete draft is being treated as an actor.

## 5. Canonical character-state families

| State family | Canonical source facts | Examples of derived output |
| --- | --- | --- |
| Identity and provenance | campaign, party membership/order, control mode, name, player-visible description, ruleset release, revision | completion and party-play readiness |
| Origin | species, background, languages, Origin feats, source choices | speed and granted proficiencies/features |
| Class progression | ordered class-level events, class choices, feature grants | total level, class level, proficiency bonus |
| Abilities | base assignments and source adjustment components | modifiers, save/check inputs |
| Proficiencies | skill/save/tool/weapon/armor grants and multipliers | context-specific check and save modifiers |
| Health | class Hit Die, Constitution dependency, HP damage/healing events | maximum/current HP and Hit Dice |
| Defense | armor/equipment state, eligible base calculations, bonuses | selected AC and alternatives |
| Equipment | item definitions, quantity, ownership, held/worn state | attacks or AC options available |
| Features/resources | grants, current spend, maximum policy, refresh policy | currently legal actions |
| Effects/conditions | typed effect instances, duration, source, stacking key | restrictions and temporary modifiers |
| Advancement | XP and ordered level/choice history | unlocked definitions and recalculated maxima |

Future spell state must distinguish access grants, ordinary preparation, free-cast entitlements,
spellbooks, Pact Magic pools, ordinary spell-slot pools, and concentration. These are not required by
the initial slice.

## 6. Rules-content and identifier model

Minimum conceptual records:

- `ruleset_release`: immutable key, version, license, source URL, artifact hash, schema version;
- `rule_source`: document, section, printed page range, durable official URL;
- `rule_concept`: cross-version semantic key such as `class.fighter`;
- `rule_definition`: immutable release-specific definition and structured behavior;
- `rule_relation`: grants, requires, replaces, unlocks, or membership relationships;
- `choice_definition`: timing, cardinality, candidates, prerequisites, replacement policy.

Use a stable concept key and a distinct release-specific definition key, for example:

```text
concept_key:    class_feature.fighter.second_wind
definition_key: srd-5.2.1:class_feature.fighter.second_wind
```

Never reuse one mutable definition row across rules releases. A campaign command built against a
different release must be rejected unless it is an explicit migration operation.

## 7. Derivation kernel

The M1 kernel must be pure and testable without database or provider access. Its initial outputs are:

- ability modifier from the SRD table, represented by `floor((score - 10) / 2)`;
- proficiency bonus for the current total level;
- skill/check modifier from selected ability, applicable proficiency multiplier, and explicit
  modifiers;
- saving-throw modifier;
- level-one maximum HP from Fighter Hit Die, Constitution modifier, and explicit source grants;
- eligible base-AC calculations and separately permitted additive bonuses;
- initiative, speed, Hit Die, passive Perception, and relevant proficiencies.

The implementation must not:

- hard-lock every skill to one ability when an accepted contextual adjudication selects another;
- add proficiency bonus more than once unless a specific multiplier such as Expertise applies;
- combine alternative base-AC calculations;
- accept a model-supplied modifier as authoritative;
- hide the definitions and source components used in the result.

## 8. Command, roll, and event envelope

An ability-check or saving-throw resolution records:

```text
command_id and idempotency key
campaign ID, acting character ID, affected/target character IDs, and relevant pre-state revisions
ruleset release and definition IDs
typed check/save context
selected ability and optional skill
all candidate and applied modifier sources
Advantage/Disadvantage sources and cancellation result
dice notation and exact faces
RNG algorithm version or accepted external-roll provenance
total, target if visible/appropriate, typed outcome
mechanical events and post-state revision
resolver version and timestamps
```

Roll generation and consequence resolution are separate responsibilities. The roll service must not
decide consequences, and the rules resolver must not invoke hidden global randomness.

M1.4 implements this envelope for ability checks and saving throws through the immutable
`srd-5.2.1-check-save-resolution-v1` catalog. The catalog extends, but does not mutate or replace,
the campaign-pinned `srd-5.2.1-party-state-v1` catalog. Resolution commands contain no modifier
field: the resolver derives the acting character's ability and at-most-once proficiency components
from canonical state. Explicit Advantage/Disadvantage reasons represent already-adjudicated
application/GM context; rules-derived sources such as worn Chain Mail are added by the domain layer.

## 9. Narrative and world integration contract

```text
player/narrator intention
  -> typed narrative command
  -> narrative-only world fact/memory, or typed rules command
  -> rules validation and recorded roll when required
  -> immutable mechanical event
  -> character/world projections
  -> narration context
```

World facts can persist attitudes, relationships, discoveries, promises, oath evidence, quest
states, and other consequences. A world fact with mechanical semantics must cite the accepted rule
or house-rule definition. Open-ended oath, curse, improvised-action, or similar cases create an
`adjudication_required` result rather than an invented automatic mutation.

## 10. Party modes, house rules, and solo play

- Strict SRD behavior is the measurement baseline.
- A feature that targets “another creature” does not silently self-target in solo play.
- Party Commander is implemented first: the one human player directly decides every player
  character's actions using ordinary party mechanics.
- Protagonist with Companions follows only after Party Commander mechanics work. Delegated companion
  intent never bypasses the canonical actor/target, validation, resource, dice, or event pipeline.
- Lone Hero follows both party modes and strict party baselines. Solo recovery, encounter scaling,
  action-economy compensation, reputation mechanics, milestone levelling, signature mechanical
  rewards, and ultimate abilities require explicit product decisions.
- Every mechanical house rule has its own package/release identity, source/rationale, UI label,
  golden tests, and migration compatibility policy.
- Narrative milestones and signature moments are mechanically inert unless a selected house-rule
  definition says otherwise.

## 11. Incremental rules implementation

Use typed functions and data for the first supported slice. Promote repeated behavior to structured
operators such as grants, prerequisites, modifiers, alternative base calculations, resource spend,
conditions, and scaling only after concrete rules demonstrate the abstraction. Allow exceptional
rules to call deterministic, versioned specialized resolvers with focused tests.

Do not create every possible table or service from the research report before a vertical slice
requires it. Schema additions must preserve the invariants above and use forward-only Alembic
migrations.

## 12. Permanent golden fixtures

| ID | Fixture | M1 expectation | Status |
| --- | --- | --- | --- |
| GF-001 | Creation completeness | Finalization rejects every missing or unsupported required choice | Verified M1.2 |
| GF-002 | Soldier Fighter abilities | Standard array Str 15/Dex 14/Con 13 with Soldier +2 Str/+1 Con gives 17/14/14 and modifiers +3/+2/+2 | Verified M1.2 |
| GF-003 | Level-one Fighter derivation | GF-002 with the selected Alert feat produces HP 12, Strength save +5, Constitution save +4, and initiative +4 (Dexterity +2 plus PB +2 from Initiative proficiency) | Verified M1.3 |
| GF-004 | Provenance | Every value in GF-002/GF-003 identifies all contributing definitions and acquisition events | Verified for M1.3 state and M1.4 resolution modifier components |
| GF-005 | Skill and tool interaction | When both legitimately apply, PB is added once and Advantage is granted | Deferred to tool-enabled slice |
| GF-006 | Advantage cancellation | Any Advantage and any Disadvantage sources cancel to one d20 | Verified M1.4, including automatic Chain Mail Stealth Disadvantage |
| GF-007 | Alternative base AC | Eligible base calculations are selected, never summed | Verified M1.3 for unarmored versus worn Chain Mail; future alternatives append fixtures |
| GF-008 | Temporary HP | A new pool may replace or be declined; pools never add | Pure keep/replace and damage-absorption boundaries verified M5.1; persistent integration remains M5.5 |
| GF-009 | Condition stacking | Duplicate conditions do not stack; Exhaustion uses levelled state | M5.1 catalog fixes Sap/Slow/Dodge at one stack; M5.3 verifies persistent nonstacking Dodge and exact source-turn expiry, Sap/Slow integration remains M5.4, and Exhaustion remains deferred |
| GF-010 | Fixed-dice replay | Same pre-state, command, dice and definitions produce equivalent events after restart | Verified M1.4 through immutable replay and resolver/catalog checks; M5.1 pure attack replay and M5.2 persistent initiative/restart replay pass, with complete action/health combat replay due M5.3-M5.5 |
| GF-011 | Model modifier rejection | Provider-supplied modifier cannot override the canonical derived modifier | Verified for authoritative M1.4 resolution commands; legacy Phase 0 turn dice remain non-authoritative until M2 |
| GF-012 | Narrative write rejection | Prose alone cannot apply damage, healing, conditions, resources, items, or bonuses | Verified at the final M1 gate: narration-only turn leaves characters/location unchanged and emits no roll or state-change event |
| GF-013 | Cross-release rejection | A command using definitions from another rules release is rejected | Verified for campaign creation and M1.4 resolution commands |
| GF-014 | Ruleset coexistence | Adding a mock later release does not alter an existing campaign or fixture | Verified M1.1: mock release coexists while the existing campaign remains pinned to SRD 5.2.1 |
| GF-015 | Party character isolation and attribution | A command for character A derives from and mutates only A unless an explicit typed effect names another target; every roll/event identifies the actor and affected character(s) | M1.3 state/turn boundaries and M1.4 resolution derivation, roll, record, and event attribution verified |
| GF-016 | Attack and damage boundaries | Natural 1 misses, natural 20 hits and is critical, equality with AC hits, critical dice double without doubling fixed modifiers, and recorded dice replay exactly | Pure boundaries and identical fixed-input replay verified M5.1; application-owned recorded-dice integration remains M5.4 |
| GF-017 | Fighter martial interactions | Great Weapon Fighting transforms eligible die faces; Graze applies only miss damage; Sap affects the next attack; Slow is nonstacking and expires at the exact boundary | Pure GWF/Graze/Sap/Slow results and effect boundaries verified M5.1; persistent action/effect integration remains M5.3-M5.4 |
| GF-018 | Combat turn economy | Movement, Action, granted Bonus Action, Reaction, free interaction, and Opportunity Attack timing cannot be exceeded or reused | M5.3 verifies active-actor enforcement, split/Dashed movement limits, one Action, persisted Bonus Action/free-interaction budgets, round advancement, Disengage, Dodge, explicit pass/Opportunity Attack selection, one Reaction consumption, and fail-closed pending-attack timing; attack resolution follows in M5.4 |
| GF-019 | Initiative and restart | Initiative derives from canonical state/stat blocks, every tie is explicitly resolved, and order/round/active-turn state survives reconnect | Verified M5.2 for canonical party/monster initiative, explicit exact tie decisions, round-one activation, connection-pool recreation, and pinned-catalog replay |
| GF-020 | Combat health and recovery | Damage ordering, Temporary HP, Second Wind, 0 HP, death saves, stability, knockout, and monster death reproduce exact state/events | Resistance/Vulnerability/Temporary HP/HP damage order, excess damage, healing cap, and Temporary HP offers verified in the M5.1 pure kernel; Second Wind and persistent 0-HP outcomes remain M5.5 |
| GF-021 | Combat party isolation | Every action, roll, effect, resource spend, HP change, and outcome identifies exact combatant/character targets and cannot cross party or campaign boundaries | M5.2 verifies encounter/party/scene/catalog scope and exact combatant attribution for initiative commands, rolls, and events; action/effect/resource/HP/outcome coverage remains M5.3-M5.6 |
| GF-022 | Combat provider rejection | A provider-supplied bonus, AC, damage, dice, resource total, condition, or untyped state write is rejected before an authoritative roll or mutation | Planned M5.6 |

Later combat, spellcasting, rests, advancement, multiclassing, and solo-balance slices must append
their report-identified fixtures rather than weakening these contracts.

## 13. M1 requirement traceability

| Requirement | Normative/design source | Implementation | Migration | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| Immutable rules release and definitions | SRD legal/source artifact; RES-001; ADR-009/ADR-015 | `app/rulesets.py`; `rulesets/`; versioned source release and separately hashed creation, state, and resolution catalogs | `0002_ruleset_releases`; `0003_guided_character_creation`; `0004_party_commander_state`; `0005_check_save_resolution` | 45-test suite, generated-schema freshness, catalog/source checksums, immutable resolution records, and nine-action owner run | Verified and owner-accepted through M1.4 |
| Character source provenance | RES-001 canonical-state model; ADR-010 | `CharacterGrant`; `app/character_creation.py`; `app/character_state.py`; `app/services.py`; grants/state/resolution APIs | `0003_guided_character_creation`; `0004_party_commander_state`; `0005_check_save_resolution` | creation/grant immutability; GF-004 state and resolution components; exhaustive equipment provenance regression | Verified through M1.4 automated gate |
| Human/Soldier/Fighter creation | SRD 5.2.1 character creation pp. 19–23; Fighter pp. 47–48; Soldier p. 83; Human p. 86; feats pp. 87–88; equipment pp. 91–97 | character-creation catalog, validator, options/draft/finalize APIs, player guide | `0003_guided_character_creation` | GF-001–GF-003 creation tests and API golden workflow | Verified M1.2 |
| Pure derived statistics | SRD formulas; ADR-011 | `app/character_creation.py`; pure `app/character_state.py` state kernel; `app/resolution.py` check/save kernel | `0003` stores creation facts; `0004` stores mutable state; `0005` stores immutable resolutions | GF-002–GF-004, GF-006–GF-007, and GF-010–GF-011 pass | Verified through M1.4 automated gate |
| Party Commander state and actor attribution | Owner-approved mode sequence; ADR-016; RUL-025 | 2–4 ordered player-controlled characters, readiness gate, ID-based APIs, isolated actor state, and actor-attributed turns/dice/events/resolutions | `0004_party_commander_state`; `0005_check_save_resolution` | GF-015 uses contrasting actors and ability arrays | Verified through M1.4 automated gate |
| Deterministic check/save resolution | SRD 5.2.1 D20 Tests pp. 6–9; ADR-007/ADR-012; RUL-004/RUL-029/RUL-030 | `app/resolution.py`; resolution create/read/list/replay APIs; canonical state derivation; application dice | `0005_check_save_resolution` with immutable records and guarded downgrade | GF-006, GF-010–GF-011, natural 1/20, idempotency, cross-release, provenance, restart fixtures, and owner acceptance run | Verified and owner-accepted M1.4 |
| Narrative/mechanical separation | Product trust boundary; ADR-012 | Typed state-change boundary and final M1 narration-only no-mutation integration path; outcome-aware two-stage narration remains M2 work | Existing M0/M1 schema | GF-012 plus validator rejection fixtures | M1 prose-only boundary verified; two-stage outcome coupling deferred to M2 |
| Explicit ruleset compatibility | RES-001 versioning; ADR-009/ADR-015 | Dynamic/cross-release rejection, coexistence, and exact release/catalog pins implemented; conversion execution intentionally deferred | `0002_ruleset_releases`; `0003` preserves legacy foundation pins | GF-013–GF-014 API/catalog tests pass | M1 compatibility boundary verified; conversion execution deferred until required |
| Solo/house-rule separation | RES-001 balance findings; ADR-013 | Pending ruleset support | Pending | Future strict-SRD comparisons | Planned |

Update this table in the same commit as implementation, migration, or evidence changes. A status may
become `Implemented` only with links to code/migrations, and `Verified` only with recorded passing
evidence.

## 14. Deferred expansion sequence

After M1 evidence:

1. expand backgrounds/species and non-spellcasting level-one options in complete vertical slices;
2. prove basic martial combat and resource/rest behavior;
3. add level-one spell access and execution as a separate spell-engine slice;
4. add advancement and straight-class higher levels;
5. add multiclassing and interaction-boundary suites;
6. prove Party Commander combat and persistent-world play;
7. add Protagonist with Companions by delegating bounded intent through the same party engine;
8. measure Lone Hero behavior against the party baseline with exact probabilities and seeded
   simulation;
9. introduce optional solo/character-development house-rule packages only from measured needs.
