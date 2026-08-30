# Character and Deterministic Rules Specification

- **Status:** Active; M1.1 verified, M1.2–M1.4 implementation pending
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

M1.2–M1.4 initially support exactly:

- one level-one player character;
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

## 5. Canonical character-state families

| State family | Canonical source facts | Examples of derived output |
| --- | --- | --- |
| Identity and provenance | campaign, name, player-visible description, ruleset release, revision | completion status |
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
campaign/character ID and pre-state revision
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

## 10. House rules and solo play

- Strict SRD behavior is the measurement baseline.
- A feature that targets “another creature” does not silently self-target in solo play.
- Companions, solo recovery, encounter scaling, reputation mechanics, milestone levelling,
  signature mechanical rewards, and ultimate abilities require explicit product decisions.
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
| GF-001 | Creation completeness | Finalization rejects every missing or unsupported required choice | Planned |
| GF-002 | Soldier Fighter abilities | Standard array Str 15/Dex 14/Con 13 with Soldier +2 Str/+1 Con gives 17/14/14 and modifiers +3/+2/+2 | Planned |
| GF-003 | Level-one Fighter derivation | GF-002 produces HP 12 before any additional source grant, Strength save +5, Constitution save +4, initiative +2 | Planned |
| GF-004 | Provenance | Every value in GF-002/GF-003 identifies all contributing definitions and acquisition events | Planned |
| GF-005 | Skill and tool interaction | When both legitimately apply, PB is added once and Advantage is granted | Deferred to tool-enabled slice |
| GF-006 | Advantage cancellation | Any Advantage and any Disadvantage sources cancel to one d20 | Planned |
| GF-007 | Alternative base AC | Eligible base calculations are selected, never summed | Planned |
| GF-008 | Temporary HP | A new pool may replace or be declined; pools never add | Deferred to combat/resource slice |
| GF-009 | Condition stacking | Duplicate conditions do not stack; Exhaustion uses levelled state | Deferred to combat/effect slice |
| GF-010 | Fixed-dice replay | Same pre-state, command, dice and definitions produce equivalent events after restart | Planned |
| GF-011 | Model modifier rejection | Provider-supplied modifier cannot override the canonical derived modifier | Planned |
| GF-012 | Narrative write rejection | Prose alone cannot apply damage, healing, conditions, resources, items, or bonuses | Planned |
| GF-013 | Cross-release rejection | A command using definitions from another rules release is rejected | Planned |
| GF-014 | Ruleset coexistence | Adding a mock later release does not alter an existing campaign or fixture | Planned |

Later combat, spellcasting, rests, advancement, multiclassing, and solo-balance slices must append
their report-identified fixtures rather than weakening these contracts.

## 13. M1 requirement traceability

| Requirement | Normative/design source | Implementation | Migration | Verification | Status |
| --- | --- | --- | --- | --- | --- |
| Immutable rules release and definitions | SRD legal/source artifact; RES-001; ADR-009 | `app/rulesets.py`; `rulesets/`; versioned project release | `0002_ruleset_releases` | 22-test suite plus official/project artifact checksum verification | Verified foundation |
| Character source provenance | RES-001 canonical-state model; ADR-010 | Pending M1.2–M1.3 | Pending | GF-004 | Planned |
| Human/Soldier/Fighter creation | SRD 5.2.1 character creation/origins/classes | Pending M1.2 | Pending | GF-001–GF-003 | Planned |
| Pure derived statistics | SRD formulas; ADR-011 | Pending M1.3 | Pending | GF-002–GF-007 | Planned |
| Deterministic check/save resolution | SRD D20 tests; ADR-007/ADR-012 | Pending M1.4 | Pending | GF-006, GF-010–GF-011 | Planned |
| Narrative/mechanical separation | Product trust boundary; ADR-012 | Existing M0 boundary, M1 extension pending | As required | GF-012 | Partial foundation only |
| Explicit ruleset compatibility | RES-001 versioning; ADR-009 | Dynamic/cross-release rejection and coexistence implemented; migration execution intentionally deferred | `0002_ruleset_releases` pins existing records | GF-013–GF-014 foundation tests pass | Partial foundation verified |
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
6. measure solo behavior with exact probabilities and seeded simulation;
7. introduce optional solo/character-development house-rule packages only from measured needs.
