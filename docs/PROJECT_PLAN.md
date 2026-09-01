# GandalfDnD Development Strategy and Living Project Plan

- **Document status:** Active
- **Last updated:** 2026-09-01
- **Rules baseline:** SRD 5.2.1 (pinned; character-state and check/save-resolution catalogs pass
  integrity and schema verification)
- **Current delivery stage:** M1.4 Verification — implementation and automated/runtime gates passed;
  owner acceptance remains
- **Canonical repository:** `~/Git/gandalfDnD`

## 1. Purpose of this document

This is the project's living engineering record. It combines the product roadmap, development
strategy, milestone acceptance criteria, validation evidence, architectural decisions, known
limitations, defects, risks, and workarounds.

Update this document in the same commit whenever a milestone changes state, an architectural
decision is made, a significant bug is found, or validation changes what the team believes about
the system. The objective is to preserve not only what was built, but whether it worked and what was
learned.

### 1.1 Documentation maintenance contract

Maintaining this record is a required part of development. A feature, fix, migration, operational
change, or investigation is not complete if it leaves this plan materially inaccurate.

Every development session must:

1. Start by reading the current delivery stage, milestone specification, open issue/debt register,
   risks, decisions, and immediate actions in this document, then compare them with Git and the
   actual repository state.
2. Record newly discovered bugs, limitations, workarounds, risks, or changed assumptions as soon as
   they are confirmed; do not wait for the end of a milestone.
3. Finish by updating affected milestone status and evidence, issues, risks, decisions, immediate
   actions, and the documentation change log before the implementation commit is considered done.
4. Update the `Last updated` date whenever the document's substance changes.

Accuracy rules:

- report implemented behavior separately from proposed behavior;
- mark a milestone `Done` only when its acceptance evidence is recorded;
- move completed work to `Rework` if later evidence invalidates the original result;
- close defects only with the resolution and regression evidence recorded;
- label workarounds as workarounds and retain the permanent-fix destination;
- correct superseded statements in place rather than leaving contradictory guidance;
- reference commits, migrations, tests, event IDs, or manual evaluations where available;
- never place credentials, personal data, unrevealed campaign content, or DM-only material here.

A documentation freshness review is mandatory at every milestone gate and before every player-facing
release. If code, tests, runtime state, and this document disagree, stop and investigate the
disagreement; update the incorrect source and record any defect exposed by the mismatch.

### 1.2 Long-term memory and audience contract

This plan is the master continuity record for future development sessions. It is designed to let a
developer reconstruct what exists, why it was built that way, what evidence supports it, what has
failed, and what should happen next without depending on chat history.

It also serves as the index for project and player documentation. Different audiences require
different levels of detail:

| Audience | This plan provides | Dedicated documentation as the project grows |
| --- | --- | --- |
| Developers | Architecture, milestones, evidence, debt, risks, and decisions | API, schema, rules-engine, testing, and operations references |
| Maintainers/operators | Infrastructure state, known operational issues, and deployment gates | Runbooks, backup/restore, migration, monitoring, and incident guides |
| Players | Supported features, limitations, release readiness, and links to safe guidance | Character creation, gameplay, rules help, campaign admin, and release notes |

Player-facing documents must contain only public product/rules information and player-visible
campaign concepts. They must never include hidden scenario data, DM prompts, secret DCs, future
encounters, or unrestricted retrieval details. This master plan should link to those documents as
they are created rather than becoming an unstructured replacement for all of them.

Source-of-truth hierarchy:

1. Runtime data, applied migrations, and executable code define what the system currently does.
2. Automated and recorded manual evaluations establish whether that behavior works as intended.
3. This plan records the verified current state, intent, interpretation, and development history.
4. The README provides concise setup and entry points.
5. Dedicated engineering, operations, and player documents explain their respective workflows.

The hierarchy does not permit silent drift: lower-level evidence that contradicts a higher-level
document creates a documentation defect that must be corrected and logged.

Current documentation index:

| Area | Authoritative project document |
| --- | --- |
| Development status, milestones, evidence, risks, and decisions | This living plan |
| Research provenance and historical research inputs | [`research/README.md`](research/README.md) |
| Character state and deterministic rules engineering contract | [`rules/CHARACTER_AND_RULES_SPEC.md`](rules/CHARACTER_AND_RULES_SPEC.md) |
| Rules interpretations, product policies, adjudications, and house rules | [`rules/RULINGS.md`](rules/RULINGS.md) |
| Supported player character-creation workflow and limitations | [`player/CHARACTER_CREATION.md`](player/CHARACTER_CREATION.md) |
| M1.4 deterministic-resolution owner verification | [`player/M1_4_ACCEPTANCE_CHECKLIST.md`](player/M1_4_ACCEPTANCE_CHECKLIST.md) |

## 2. Product objective

GandalfDnD will provide a persistent D&D experience for one human player, initially commanding an
adventuring party, with two eventually distinct AI roles:

1. A campaign-stateful Dungeon Master that conducts fair, coherent play over long campaigns.
2. A spoiler-safe Guide that teaches rules and explains player options without receiving hidden
   campaign information.

The application—not the language model—owns exact game state and mechanical truth. AI is used for
interpretation, roleplay, narration, and bounded proposals. Deterministic application services
resolve rules, dice, resources, and allowed state transitions.

## 3. Success criteria

The project succeeds when a solo player can create a legal adventuring party, play a long campaign,
restart the application, and continue with mechanically correct state and narratively coherent
recall.

The player must be able to trust that:

- character choices materially affect available actions and mechanical outcomes;
- identical state, rules, decision, and dice result produce the same mechanical outcome;
- dice rolls are generated and recorded by the application;
- the model cannot silently overwrite canonical state;
- hidden information never enters the Guide's retrieval context;
- prior people, places, clues, rulings, resources, and consequences can be recovered;
- failures can be reconstructed from events, prompt versions, model metadata, and retrieval logs.

## 4. Non-goals until the core is proven

- multiplayer support;
- voice or image generation;
- tactical map rendering;
- every published D&D option or edge case;
- a React frontend;
- Redis, Celery, or distributed job processing;
- Docker solely for local development;
- deployment on the Clawvis VM;
- a dedicated Gandalf application VM before the local vertical slice is reliable.

## 5. Architectural principles

### 5.1 Deterministic mechanics, generative narrative

Rules resolution is deterministic. Given the same canonical character/world state, declared
decision, rule version, and dice results, application code must produce the same mechanical result.
Narration can remain generative as long as it does not contradict that result.

### 5.2 PostgreSQL is authoritative

HP, ability scores, resources, inventory, equipment, conditions, location, quests, combat state,
visibility, and other exact facts live in structured PostgreSQL records. Model context and prose are
never authoritative.

### 5.3 The model proposes; application code decides

The model returns typed intent, narration, and proposed changes. Pydantic validates shape;
domain/rules services validate meaning; one database transaction commits the accepted result and
its audit events.

### 5.4 Dice are an application service

The model may request an appropriate roll, but it never invents the result. The rules resolver
calculates modifiers from canonical state, `DiceService` rolls, and the result is recorded before
outcomes are finalized.

### 5.5 Hidden knowledge is excluded by architecture

Player, DM-only, and eventually Guide-visible information must have explicit visibility. The Guide
must query a restricted data path that cannot return hidden records; prompt-only spoiler protection
is insufficient.

### 5.6 Append-only evidence

Campaign events, dice outcomes, rule resolutions, prompt/model versions, and retrieval decisions
must be sufficient to explain why a result occurred. Corrective events supersede mistakes; history
is not silently rewritten.

### 5.7 Source provenance and derived state

Character choices, grants, equipment state, resource expenditure, and effect instances are
canonical source facts with ruleset and acquisition provenance. Modifiers, maximums, proficiency
bonus, eligible Armor Class calculations, and similar values are derived projections. A cached
projection may be rebuilt but may never become independently editable mechanical truth.

### 5.8 Explicit rules, rulings, and house rules

Normative SRD definitions, Gandalf implementation interpretations, product policies, campaign
adjudications, and house rules are separate classifications. Natural-language narration never
creates a mechanical rule. Every mechanical Gandalf addition is labelled, versioned, tested, and
presented separately from the immutable SRD baseline.

## 6. Current infrastructure

| Component | Responsibility | Current state |
| --- | --- | --- |
| MacBook | Development, FastAPI, tests, Alembic, Git | Active |
| `postgresvm` | Isolated development and test databases | Active |
| `gandalfdnd_dev` | Manual development and play-test state | Provisioned and migrated |
| `gandalfdnd_test` | Automated integration-test state | Provisioned and migrated |
| Clawvis VM | Existing unrelated services | Intentionally untouched |
| Gandalf application VM | Future persistent runtime | Deferred |
| pgvector | Future semantic memory | Not installed; deferred to Milestone 4 |

Database roles are separate, non-superuser, non-`CREATEDB`, non-`CREATEROLE`, non-replication
accounts. Public database connectivity is revoked, and cross-database isolation has been tested.

## 7. Development workflow

### 7.1 Work in vertical slices

Each slice should cross API, schema, domain logic, persistence, events, and tests where applicable.
Avoid building large disconnected frameworks in anticipation of future features.

### 7.2 Standard implementation loop

1. Select one acceptance criterion and mark it `In progress`.
2. Write or update a failing test that expresses the criterion.
3. Add the smallest migration and domain change needed.
4. Implement the API/service behavior.
5. Run unit tests, PostgreSQL integration tests, lint, formatting, and migration-drift checks.
6. Run the milestone's manual scenario when AI behavior or usability is involved.
7. Inspect the full diff for secrets, unrelated changes, unsafe migrations, and hidden coupling.
8. Record results, limitations, issues, and decisions in this document.
9. Commit a coherent milestone or independently working slice.

### 7.3 Definition of ready

A slice is ready when it has a named player outcome, explicit inputs/outputs, canonical state
ownership, visibility classification, acceptance tests, and no unresolved decision that would
materially change its schema.

### 7.4 Definition of done

A slice is done only when:

- acceptance criteria pass;
- migrations apply from the previous revision and match ORM metadata;
- tests cannot accidentally target the development database;
- failure paths do not partially commit state;
- important decisions and events are observable;
- documentation describes setup and behavior;
- known compromises are recorded with an owner milestone;
- the worktree is inspected and the slice is committed.

### 7.5 Test strategy

| Layer | What it proves | Examples |
| --- | --- | --- |
| Unit | Pure deterministic rules and validation | modifiers, resource limits, dice parsing |
| Domain integration | Services plus PostgreSQL transactions | state changes, event ordering, rollback |
| API integration | External contract and persistence | campaign creation, turns, resume |
| Provider contract | Every LLM provider returns the same typed contract | mocked structured responses |
| Golden scenarios | Important rules remain stable across changes | checks, saves, attacks, rests |
| Memory stress | Retrieval works after long histories | clue planted early and recalled later |
| Security/visibility | Hidden records never cross a boundary | Guide spoiler-isolation tests |
| Manual play test | Experience is coherent and teachable | The Lantern Test and longer campaigns |

Tests involving randomness must inject a seeded or fixed source. Tests involving an external model
must separate deterministic provider-contract tests from explicitly paid live evaluations.

### 7.6 Project-owner input and player acceptance checkpoints

Development should continue autonomously from accepted specifications until a decision would
materially change rules behavior, product scope, schema compatibility, privacy, operating cost, or
the player experience. When such a decision is required, present the available evidence, a
recommendation, alternatives, and the consequences of each choice rather than asking for routine
implementation details.

The project owner tests stable verification candidates, not incomplete intermediate builds. Codex
continues to own automated unit, integration, API, migration, integrity, and regression testing on
every slice. Before each owner test, provide a short checklist containing setup, actions, expected
results, known limitations, and where observations will be recorded.

| Checkpoint | Owner input required | Owner testing expectation |
| --- | --- | --- |
| M1.2 guided creation | None; the supported slice and deferrals are already accepted | Optional API/Swagger review of valid creation, rejected invalid choices, finalized sheet, and provenance |
| M1.3 Party Commander and complete character state | Completed 2026-09-01; no further input required | Owner confirmed the API exposes the correct structured values; presentation clarity and end-user corrective guidance are deferred to the M7 interface checkpoint |
| M1.4 deterministic resolution | Decide only genuinely ambiguous adjudication/product policies that cannot be resolved from the pinned SRD and accepted rulings | Important acceptance test proving saved character choices change checks/saves and model-supplied modifiers cannot override canonical results |
| M2 live AI feasibility | Approve any paid live-model evaluation and provide desired narrative tone/content boundaries | Critical Lantern Test covering dialogue, movement, inventory, check, damage, restart, resume, and narration/mechanics agreement |
| M3 persistent world | Provide campaign-structure preferences when they affect consequence and quest design | Multi-session play test confirming decisions, NPC relationships, quests, and revealed facts persist coherently across restarts |
| M1.5 content expansion | Prioritize desired species, backgrounds, classes, feats, equipment routes, spellcasting, and play styles | Create contrasting supported characters and confirm their choices produce understandable, distinct state and later gameplay |
| M5 party combat | Provide difficulty/lethality feedback for standard party play; companion autonomy and lone-hero compensation remain later decisions | Repeated Party Commander combat tests across favorable, difficult, defeat, recovery, and restart scenarios |
| Protagonist with Companions | Choose desired companion autonomy, instruction granularity, personality influence, and player override behavior after Party Commander is proven | Compare delegated companion proposals with direct Party Commander control and verify the same deterministic rules constrain both |
| Lone Hero | Choose desired difficulty and whether measured compensation options should be offered as explicit house rules after the two party modes work | Run single-character benchmarks against the established party baseline; verify every adjustment is visible, optional, and versioned |
| M6 spoiler-safe Guide | Choose preferred guidance depth and proactive-versus-requested help | Ask campaign-sensitive questions and verify useful guidance never reveals DM-only facts |
| M7 player interface | Provide strong layout, accessibility, workflow, and usability feedback | Full ordinary-player journey without relying on direct API knowledge |
| M8 deployment | Choose availability, privacy, hosting-cost, backup, and recovery expectations | Operational acceptance covering access, restart, backup/restore, failure reporting, and recovery |

Owner test outcomes are durable evidence. Each observation must be classified as passed, defect,
usability issue, rules/ruling question, feature request, or accepted limitation. Defects enter the
issue register with reproduction evidence; mechanical ambiguities enter `docs/rules/RULINGS.md`;
scope changes return to the milestone plan. A milestone is not closed merely because automated tests
pass when its gate explicitly requires owner or live-play acceptance.

## 8. Status workflow

Use these values consistently:

| Status | Meaning |
| --- | --- |
| Proposed | Described but not accepted into the delivery sequence |
| Ready | Scoped with acceptance criteria and no blocking decisions |
| In progress | Actively being implemented |
| Blocked | Cannot proceed; blocker and required resolution are recorded |
| Verification | Implementation exists and is undergoing automated/manual validation |
| Done | Acceptance evidence is recorded and no required work remains |
| Rework | Previously completed behavior failed later validation or requirements changed |
| Deferred | Intentionally postponed with a destination milestone |

## 9. Milestone roadmap

| ID | Milestone | Status | Primary outcome |
| --- | --- | --- | --- |
| M0 | Persistence and safety foundation | Done | Canonical state and auditable turn skeleton |
| M1 | Party character creation and deterministic mechanics | In progress | The selected acting character's choices drive calculated outcomes |
| M2 | Two-stage AI turn and live feasibility | Proposed | Real DM uses recorded dice results safely |
| M3 | Persistent world model | Proposed | NPCs, quests, scenes, clues, time, and visibility |
| M4 | Long-term memory and retrieval | Proposed | Coherent recall without full history in context |
| M5 | Basic deterministic combat | Proposed | Reproducible initiative, actions, attacks, and damage |
| M6 | Spoiler-safe Guide | Proposed | Beginner help with enforceable knowledge boundaries |
| M7 | Play interface and campaign administration | Proposed | Usable play, recap, correction, and export workflows |
| M8 | Deployment and operations | Deferred | Dedicated reliable service with backups and monitoring |
| M9 | Optional Clawvis integration | Deferred | Clawvis acts only as an API client/interface |

### 9.1 Party-mode delivery sequence

Gandalf supports one human player through three modes, delivered in this order:

1. **Party Commander:** the player creates and directly decides actions for every player character.
   This most closely preserves ordinary party-oriented D&D rules and becomes the foundation of
   M1.3 character state, M1.4 resolution, M2 turns, M3 world consequences, and M5 combat.
2. **Protagonist with Companions:** the player directly controls a primary character and delegates
   bounded decisions for companions. Companion AI proposes intentions/actions, but canonical rules,
   resources, targets, dice, and consequences use the same deterministic party engine and remain
   subject to explicit player direction/override policies.
3. **Lone Hero:** a single-character campaign is productized only after both party modes and
   standard party combat are proven. Strict unmodified rules are measured first; any recovery,
   action-economy, encounter, or survivability compensation is optional, visible, versioned, and
   classified as a house rule rather than silently changing SRD behavior.

This sequence separates “one human player” from “one player character.” It avoids designing the
canonical mechanics around exceptional solo compensation and ensures later modes reuse—not fork—the
same character, action, event, and rules-resolution foundations.

## 10. Milestone specifications

### M0 — Persistence and safety foundation

- **Status:** Done
- **Completed:** 2026-08-29
- **Commits:** `88acb62`, `d58235f`, `02875dc`

Delivered:

- FastAPI health, campaigns, one minimal character, state, turns, and event endpoints;
- SQLAlchemy 2 models and Alembic migration;
- campaigns, characters, locations, turns, campaign events, and dice rolls;
- database-level append-only protection for campaign events;
- deterministic offline DM provider and OpenAI structured-output provider abstraction;
- HP, inventory, and location state-change validation;
- application-generated and persisted dice rolls;
- restart/connection-pool persistence test;
- isolated development/test databases and roles.

Validation evidence:

- 13 automated tests passed;
- 91% application statement coverage at completion;
- Ruff lint and formatting passed;
- Alembic reported no model/migration drift;
- development `/health` returned HTTP 200;
- cross-database access by the development role was rejected;
- secrets were excluded from Git and stored with owner-only local permissions.

What worked well:

- the canonical-state boundary is simple and testable;
- invalid HP and inventory proposals are rejected before commit;
- event ordering and dice results survive new database connections;
- provider substitution makes offline tests deterministic;
- no extra infrastructure or Clawvis changes were required.

Limitations discovered:

- the character is only name, HP, and inventory—not a legal D&D character sheet;
- the model currently supplies dice notation and modifiers instead of the rules engine calculating
  modifiers from character state;
- narration is produced before requested dice are rolled, so it cannot reliably reflect the roll;
- world consequences cover only HP, inventory, and current location;
- the OpenAI adapter has not yet been exercised in a paid live-model evaluation;
- no prompt-version or rule-resolution audit records exist yet.

Outcome: M0 proves persistence and the trust boundary, but not D&D-correct play. Character creation
and deterministic mechanics are therefore promoted ahead of broader live-model testing.

### M1 — Character creation and deterministic mechanics

- **Status:** In progress
- **Priority:** Immediate

Player outcome: a beginner can create multiple rules-valid level-one characters, understand their
choices, command the party directly, and receive mechanically reproducible checks derived from the
selected acting character's saved state.

Planning basis:

- the project owner accepted the findings in [RES-001](research/README.md) on 2026-08-30;
- the adopted, modified, and deferred recommendations are recorded in the
  [research review](research/2026-08-30-character-system-adoption.md);
- the engineering contract is [`rules/CHARACTER_AND_RULES_SPEC.md`](rules/CHARACTER_AND_RULES_SPEC.md);
- implementation interpretations and unresolved product choices must be recorded in
  [`rules/RULINGS.md`](rules/RULINGS.md);
- research adoption is planning evidence only and does not change M1 implementation status.

Initial supported content slice: every M1 character is a level-one Human with the Soldier background
and Fighter class using standard-array ability generation. M1.2 proved the complete lifecycle for
one character; M1.3 removed the campaign singleton assumption and established Party Commander with
multiple independently persisted characters. All mandatory choices for that path must be genuinely
rules-valid; unsupported options must be rejected rather than partially implemented. Reusing this
content slice across the initial party is a delivery constraint, not a claim that other SRD options
are invalid or a long-term requirement that party members share one build.

Planned slices:

#### M1.1 Versioned rules data

**Status:** Done

Approved source and distribution strategy:

- use the unchanged official SRD 5.2.1 PDF from `https://www.dndbeyond.com/srd` as the first
  authoritative source artifact;
- treat the complete licensed SRD accurately as an SRD, not as every rule or option from commercial
  D&D publications;
- preserve required CC-BY-4.0 attribution and clearly identify every Gandalf adaptation;
- store the original PDF as a versioned GitHub Release/download asset rather than repeatedly adding
  binary revisions to normal Git history;
- provide a fetch command that downloads the official artifact into an ignored local cache and
  refuses files whose SHA-256 checksum does not match the version manifest;
- store manifests, attribution, schemas, normalized rules, extraction code, and tests in Git;
- keep extracted machine-readable rules separate from the unchanged source document;
- add each future SRD/rules version alongside existing versions instead of overwriting one;
- pin every campaign to one immutable ruleset identifier;
- allow ruleset migration only through an explicit player/admin operation with compatibility
  validation, recorded conversion events, and rollback guidance;
- reject unsupported or cross-version character options at domain boundaries.

Planned repository layout:

```text
rulesets/
├── registry.json
└── srd-5.2.1/
    ├── manifest.json
    ├── ATTRIBUTION.md
    ├── README.md
    ├── schema/
    └── data/
```

M1.1 acceptance gates:

- the official PDF is retrievable from its official source and from a versioned project download;
- both copies match the manifest checksum;
- the manifest records source URL, publication/version data, license, attribution, checksum,
  extraction schema version, and Gandalf support status;
- the repository contains no unlicensed non-SRD D&D content;
- normalized data identifies its source version and can be regenerated deterministically;
- campaign creation requires a registered stable ruleset and never resolves `latest` dynamically;
- a newer mock ruleset can coexist without altering an existing campaign;
- migration between rulesets is impossible without an explicit compatibility workflow.

Implemented in M1.1:

- strict Pydantic-backed registry, manifest, normalized-data index, and deterministic generated JSON
  Schemas under `rulesets/`;
- exact SRD 5.2.1 source URL, publication metadata, CC-BY-4.0 attribution, 6,031,375-byte
  size, and SHA-256 `8974902d109d6e63672d7c490bde9ccf052410503d9cfa768237154fbc5e3d87`;
- ignored local cache and atomic verified fetch command with official/project source selection;
- stable release-specific identity with no `latest` alias or arbitrary campaign ruleset strings;
- immutable `ruleset_releases` PostgreSQL records and ruleset pins on campaigns, characters,
  campaign events, and dice rolls;
- migration `0002_ruleset_releases`, which preserves the legacy label, backfills recognized records,
  temporarily and transactionally handles the append-only event trigger, and aborts without data
  loss on an unmapped legacy value;
- release coexistence, immutability, API rejection, schema freshness, artifact-integrity, migration
  backfill/rollback, and provenance regression tests.

Verification evidence recorded 2026-08-30:

- 22 automated tests passed with 91% application statement coverage;
- Ruff lint and formatting passed; immutable research sources are formatter-excluded;
- generated ruleset JSON Schemas matched the checked-in schemas;
- both the official PDF and the versioned project-release download matched the manifest's
  6,031,375-byte size and SHA-256;
- GitHub Release
  [`ruleset-srd-5.2.1-source-v1`](https://github.com/asinpark123/gandalfDnD/releases/tag/ruleset-srd-5.2.1-source-v1)
  published the unchanged source artifact and reported the same SHA-256 digest;
- Alembic reported no ORM/migration drift in development or test;
- `gandalfdnd_dev` and `gandalfdnd_test` reached `0002_ruleset_releases (head)`;
- development `/health` returned HTTP 200;
- both Gandalf databases contained no legacy campaign rows before migration;
- Clawvis and unrelated PostgreSQL databases/services were not accessed or changed.

M1.1 milestone review:

- **Review date:** 2026-08-30
- **Implementation commit / migration:** `bada61c`; `0002_ruleset_releases`
- **Acceptance result:** all gates passed; proceed to M1.2.
- **What worked well:** a single manifest drives database identity, retrieval integrity, schema
  validation, API boundaries, and regression tests; transactional migration tests caught and fixed
  trigger/nullability edge cases before development migration.
- **Issues encountered:** the first release command used an abbreviated commit as
  `target_commitish`, which GitHub rejected before creating any release; retrying against the
  already-pushed `main` branch succeeded without partial state.
- **Workaround or debt at M1.1 closure:** normalized data was intentionally `foundation_only`; that
  planned work was subsequently completed for the supported creation slice in M1.2. The existing
  Starlette/httpx test deprecation warning is non-blocking and should be resolved during dependency
  maintenance.
- **Architecture/scope result:** immutable release provenance is accepted; explicit cross-version
  conversion remains deferred until a real migration requirement exists.
- **Go / rework / stop decision:** Go. Begin source-cited Human/Soldier/Fighter character records
  and guided creation; rework M1.1 only if new integrity or migration evidence fails.

#### M1.2 Guided character creation

**Status:** Done

Implemented:

- an immutable, separately checksummed `srd-5.2.1-character-creation-v1` data catalog with durable
  SRD page citations and beginner descriptions;
- a draft/finalized lifecycle in which turns are blocked until successful finalization;
- strict Human/Soldier/Fighter validation covering standard array, Soldier increases, languages,
  non-overlapping skills, Human Origin feat, gaming set, Fighting Style, weapon masteries, size,
  alignment, and the supported Soldier A plus Fighter A equipment route;
- pure level-one ability-modifier and maximum-HP calculations plus the creation-time sheet projection
  for proficiencies, equipment, features, and Second Wind maximum uses;
- immutable character grants linking each consequential choice or grant to its ruleset release,
  catalog, source definition, acquisition event, choice slot, revision, and source citation IDs;
- database protection for rules-data catalogs, character grants, finalized creation facts, and
  campaign ruleset/catalog pins;
- API routes for catalog options, name-only drafts, transactional finalization, and grant provenance;
- safe migration backfill: pre-M1.2 records retain the foundation catalog while new campaigns use
  the guided-creation catalog;
- a player-facing guide for the supported workflow and limitations.

Verification evidence recorded 2026-08-31:

- 38 automated tests passed with 91% application statement coverage;
- GF-001, GF-002, and the M1.2 portion of GF-003 pass, including the golden 17/14/14 ability result,
  +3/+2/+2 modifiers, and level-one maximum HP 12;
- invalid catalog IDs, incomplete/duplicate/overlapping choices, invalid standard arrays, invalid
  Soldier increases, and unsupported free-form input are rejected without finalizing the draft;
- source-linked grants, finalized creation facts, catalog metadata, and campaign pins reject
  direct database updates or deletes;
- schema generation/freshness, normalized-catalog checksums, Ruff lint, and formatting checks passed;
- migration `0003_guided_character_creation` applied to development and passed transactional upgrade,
  backfill, immutability, and guarded-downgrade tests in the isolated test database;
- Alembic reported no ORM/migration drift; development `/health` returned HTTP 200;
- Clawvis and unrelated PostgreSQL databases/services were not accessed or changed.

M1.2 milestone review:

- **Review date:** 2026-08-31
- **Implementation/migration:** `ba7bca8`; `0003_guided_character_creation`
- **Acceptance result:** all M1.2 gates passed; proceed to M1.3.
- **What worked well:** the catalog response drives both beginner guidance and strict validation;
  the same immutable acquisition event and source IDs make the finalized sheet auditable without
  allowing API/model text to become rules data.
- **Issues encountered:** isolated migration tests intentionally clear application tables, which can
  remove the M1.1 release seed before testing M1.2 from a synthetic baseline. The migration now
  restores the exact known release row with `ON CONFLICT DO NOTHING`; it never updates an existing
  release or broadens database access.
- **Workaround or debt:** Magic Initiate, Skilled tool choices, alternate equipment packages, and
  broader creation content are explicitly deferred. M1.2 projects several starting statistics, but
  complete equipment state, AC alternatives, resources, and reproducible component provenance remain
  M1.3 work. The existing Starlette/httpx deprecation warning remains non-blocking.
- **Architecture/scope result:** source artifacts, releases, and normalized catalogs have distinct
  immutable identities; existing records never silently adopt a new catalog.
- **Go / rework / stop decision:** Go. Build M1.3 from the saved source facts and grants; do not
  expand character breadth before the deterministic M1.4 exit gate.

#### M1.3 Party Commander and complete Phase 1 character state

**Status:** Done

**Completed:** 2026-09-01

- campaign-level party identity and multiple independently addressable player characters;
- explicit `party_commander` campaign mode and player-controlled character ownership/control state;
- removal of singleton persistence/API assumptions without weakening per-character provenance;
- ability scores and modifiers;
- proficiency bonus, skills, and saving throws;
- armor class, initiative, speed, hit dice, and level;
- equipped versus carried inventory;
- supported Fighter/Human/background features and expendable resources;
- eligible alternative base calculations remain distinct rather than being added together;
- derived values remain reproducible projections of versioned source choices and grants;
- commands, state changes, events, and later resolutions identify the acting/affected character;
- no spellcasting fields are required by the initial supported slice.

Owner checkpoint completed. Because this milestone exposes a backend API rather than a player
interface, its acceptance gate evaluates structured-value correctness, format, attribution, and
state isolation. Presentation clarity, visual discoverability, and ordinary-player recovery from
errors are M7 interface acceptance criteria.

Implemented:

- new campaigns pin immutable `srd-5.2.1-party-state-v1` and explicit `party_commander` mode with
  two required and four maximum active, player-controlled characters;
- ordered, ID-addressable draft/finalize/grants/loadout APIs remove the singleton assumption while
  legacy foundation records remain pinned and are not silently upgraded;
- the versioned pure character-state kernel derives every ability/save/skill modifier, PB, AC
  candidate and selected AC, Alert-aware initiative, passive Perception, Speed, level-one HP, Hit
  Die, carried/worn/held equipment, and current/maximum supported resources;
- every derived number records formula, definition/source IDs, relevant acquisition-event IDs,
  character/state revisions, and resolver version;
- party play is blocked until two active characters are finalized; drafts cannot act; turns require
  an in-campaign acting character and attribute turns, dice, events, and affected character IDs;
- state changes apply only to the selected actor in this slice, and equipped items cannot be removed
  from inventory until loadout is changed.

Automated verification evidence recorded 2026-08-31:

- 39 tests passed with 92% total statement coverage; the new state kernel measured 95% and services
  92%; Ruff lint/format, JSON Schema freshness, registry/catalog checksums, and `git diff --check`
  passed;
- GF-003 now correctly records initiative +4 for the golden Alert Fighter (Dexterity +2 and PB +2),
  correcting the earlier research-derived +2 expectation that omitted Alert's Initiative
  proficiency; Strength save +5, Constitution save +4, HP 12, Chain Mail plus Defense AC 17, and
  passive Perception 12 pass;
- multi-character creation, the two-character readiness boundary, four-character maximum, draft
  exclusion, actor requirement, cross-campaign actor rejection, isolated HP/inventory mutation,
  actor-attributed dice/events, legal loadout changes, hand limits, and AC recomputation pass;
- migration `0004_party_commander_state` passed legacy backfill, guarded downgrade, and full-chain
  tests; it applied to `gandalfdnd_dev`, Alembic reports head with zero drift, development health is
  HTTP 200, and the empty development database remains at zero campaigns/characters;
- Clawvis and unrelated PostgreSQL databases/services were not accessed or changed.

First owner acceptance run and correction, 2026-08-31:

- the owner completed the ten-action workflow and confirmed campaign/party setup, two finalized
  sheets, golden values, party readiness, loadout isolation, a valid actor-attributed turn, and
  post-restart state persistence;
- the captured response exposed that the dynamically selected Dice Set and aggregated GP projected
  empty source/acquisition provenance even though their canonical grants existed; the projection now
  maps Dice Set to its gaming-set and package definitions and GP to both contributing equipment
  packages;
- the regression requires every projected starting-equipment row to carry non-empty contributing
  definition keys, source IDs, and acquisition-event IDs; the full 39-test suite and all schema,
  ruleset, lint, formatting, and diff gates pass;
- the first actor-omission attempt sent `actor_character_id: ""`, correctly producing schema-level
  HTTP 422 rather than exercising the intended domain-level HTTP 409, and the event read was not
  recorded. Only the provenance, omitted-property, and event-attribution checks must be repeated;
  the owner will then provide the five subjective answers.

Targeted owner retest, 2026-09-01:

- the existing two-character campaign projected non-empty definition, source, and acquisition-event
  provenance for every Dice Set and GP row on both characters; Dice Set identifies its selected
  gaming-set definition and Soldier package, while GP identifies both Soldier and Fighter packages;
- omitting `actor_character_id` entirely produced domain HTTP 409 with the corrective detail
  `Party Commander turns require actor_character_id`;
- the event log returned HTTP 200 and both the successful `player_action` and corresponding
  `dm_response` identify SugarHigh (`2039690f-15ca-4154-8822-1fbd4190daf1`) as actor;
- all three targeted technical checks passed. No further API rerun is required; only the five
  subjective readability and usability answers remained before the owner gate could close.

Owner usability assessment and milestone decision, 2026-09-01:

- for questions 1–4, the owner judged visual obviousness and usability to be premature while
  interacting directly with JSON; correct values in the correct structured format are the relevant
  backend criterion, and that criterion passed;
- the owner found the API error sufficiently informative for debugging, but not sufficient by
  itself for an ordinary player to recover through a future frontend;
- M7 must show the selected acting character, explain calculated state and isolated changes in
  player language, and map typed backend errors to contextual corrective instructions;
- this is a deferred interface requirement, not an M1.3 backend defect. M1.3 is accepted as Done and
  development may proceed to M1.4.

Known non-blocking limitation: the existing Starlette/httpx TestClient deprecation warning remains
under `WARN-001`. Resource expenditure/recovery and authoritative check/save resolution belong to
M1.4 or later and are not implied by exposing their current/max state.

#### M1.4 Deterministic resolution service

- **Status:** Verification
- **Migration:** `0005_check_save_resolution`
- **Owner gate:** Complete
  [`player/M1_4_ACCEPTANCE_CHECKLIST.md`](player/M1_4_ACCEPTANCE_CHECKLIST.md), record findings, and
  either fix defects or accept M1.4 as Done.

Implemented scope:

- authoritative ability checks and saving throws require an acting character and derive the ability
  and at-most-once proficiency components only from that character's canonical state;
- the command schema forbids client/model-supplied modifiers and rejects incompatible releases,
  catalogs, actors, skills, and saving-throw skill fields;
- contextual skill abilities are supported; Chain Mail automatically supplies Disadvantage only to
  Dexterity (Stealth), while already-adjudicated Advantage/Disadvantage reasons support application
  or GM context and cancel according to SRD 5.2.1;
- immutable resolution records preserve command identity, actor and state revisions, both catalog
  identities, formula components and provenance, exact dice faces, selected die, rule/source IDs,
  resolver/RNG versions, DC, total, and typed outcome;
- duplicate commands are idempotent, changed reuse of a command ID is rejected, and replay uses the
  stored dice and pinned definitions to prove the same result after restart;
- a successful resolution and its actor-attributed `rule_resolved` campaign event commit atomically.

Automated and runtime evidence, 2026-09-01:

- 45 tests pass with 91% total coverage and 95% coverage of the resolution module; deterministic
  fixtures cover normal, Advantage,
  Disadvantage, cancellation, contextual abilities, actor isolation, natural 1/20 check behavior,
  malformed/cross-release commands, idempotency, immutability, restart replay, and guarded downgrade;
- Ruff lint and format checks, normalized-catalog validation, generated-schema freshness, and the
  full diff whitespace check pass;
- catalog `srd-5.2.1-check-save-resolution-v1` has verified SHA-256
  `09d2b0a963a5fba5c28a0a018b8114bcad25dd65717efcf5e1b791cc4f751448` and explicitly extends the
  immutable M1.3 state catalog rather than silently changing it;
- the development database is at migration head with no Alembic drift, `/health` returns HTTP 200,
  the new route is loaded, and the pre-acceptance `rule_resolutions` table remains empty;
- the test database guard remains active and no Clawvis or unrelated database/service was touched.

Known limitations and follow-up boundaries:

- attacks, damage, combat, conditions, tools, Heroic Inspiration expenditure/rerolls, mechanical
  consequences, and narration are not part of M1.4;
- supplied Advantage/Disadvantage reasons are adjudicated context, not free-form rules inference;
  additional automatic sources arrive with their concrete rules slices;
- the legacy Phase 0 turn flow still carries a non-authoritative provider-requested modifier; M2
  must replace that path with this resolver before final narration. `DEBT-001` therefore remains in
  progress even though the authoritative API itself is protected.

#### M1.5 Deferred character-content expansion

- **Status:** Deferred until M1.4 evidence is accepted

Add other species, backgrounds, ability-generation methods, feats, classes, equipment routes, and
level-one spellcasting in complete vertical slices. Later advancement, multiclassing, spell and
combat interactions must use equivalence-class and boundary fixtures rather than an exhaustive
species × background × class × feat × spell matrix. This expansion does not block M2's feasibility
proof with the initial supported party content slice.

M1.1–M1.4 acceptance gates (M1.5 is not required):

- a Party Commander campaign can create and independently address at least two complete supported
  level-one characters through the API without manual DB edits;
- all derived values match golden test fixtures;
- invalid option combinations and illegal standard-array assignments are rejected;
- every consequential choice and derived component retains source provenance;
- a check's modifier cannot be supplied or overridden by the model;
- identical state plus fixed dice produces an identical mechanical result;
- creation and resolution survive restart and can be reconstructed from events;
- prose alone cannot apply a mechanical condition, bonus, damage, healing, resource, proficiency,
  or item change;
- a command referencing another rules release is rejected outside an explicit migration workflow;
- a beginner-facing explanation exists for each creation choice in the supported slice;
- every rule-derived value identifies the immutable ruleset and normalized rule-data version used;
- one character's choices, damage, resources, inventory, and events cannot mutate or be attributed to
  another character without an explicit typed multi-character effect.

Golden fixtures and requirement-to-source/implementation/test traceability are maintained in
[`rules/CHARACTER_AND_RULES_SPEC.md`](rules/CHARACTER_AND_RULES_SPEC.md). Update that matrix in the
same commit as the corresponding code, migration, or verification evidence.

### M2 — Two-stage AI turn and live feasibility

- **Status:** Proposed
- **Depends on:** M1

Target flow:

```text
player action
    -> intent and requested resolution
    -> deterministic rules validation
    -> application dice roll
    -> typed mechanical outcome
    -> model narration and bounded world proposals
    -> state validation and atomic commit
```

Planned work:

- split turns into resolution and finalization stages;
- introduce pending/resolved/failed turn status and idempotency keys;
- handle provider timeout, retry, refusal, malformed output, and cancellation safely;
- record provider, model, prompt version, latency, and token usage;
- ensure a provider failure never partially changes canonical state;
- run the real-model Lantern Test with at least two player-controlled characters: dialogue,
  movement, inventory use, check, damage, character switching, restart, and resume;
- compare model narration with the recorded mechanical outcome.

Exit gate: ten consecutive Lantern Test runs complete without impossible state, invented dice,
partial commits, or contradictory resume output. Failures are categorized before proceeding.

### M3 — Persistent world model

- **Status:** Proposed
- **Depends on:** M2

Add NPCs, relationships, factions, scenes, quests/objectives, world time, clues, knowledge entries,
and explicit visibility. Decisions must update structured world state and create explainable events.

Exit gate: player decisions produce persistent branching consequences across restarts, while
DM-only facts remain absent from player-visible APIs.

### M4 — Long-term memory and retrieval

- **Status:** Proposed
- **Depends on:** M3

Install pgvector only here. Add semantic memory for prose and conversations, structured filters,
summaries, embedding versioning, retrieval logs, and re-indexing. Exact state must continue to come
from relational tables, not vector retrieval.

Exit gate: in a synthetic campaign of at least 500 events, a relevant early clue is retrieved late
without placing full history in the prompt, while irrelevant/hidden records remain excluded.

### M5 — Basic deterministic combat

- **Status:** Proposed
- **Depends on:** M1 and M3

Add encounters, combatants, initiative, rounds/turn order, action economy, attacks, damage, healing,
conditions, defeat, and encounter completion. Start with a deliberately small supported rules
subset.

Exit gate: fixed Party Commander combat fixtures replay to identical results, illegal actions are
rejected, and a restart during combat resumes the exact per-character initiative and resource state.

### M6 — Spoiler-safe Guide

- **Status:** Proposed
- **Depends on:** M3 and preferably M4

Build a separate Guide service and retrieval policy. It may access public rules, the player's sheet,
and revealed campaign facts. It must not share the DM provider's unrestricted context path.

Exit gate: automated adversarial tests prove that DM-only facts are never retrieved for the Guide;
after an explicit reveal event, the same fact becomes available.

### M7 — Play interface and campaign administration

- **Status:** Proposed
- **Depends on:** Stable M2–M3 APIs

Add the simplest useful play interface, character creation screens, state summaries, recaps, event
inspection, campaign export, and explicit corrective/admin events. Choose frontend technology only
after API workflows are proven.

The interface must make party membership and the selected acting character visible; present
calculated values, provenance explanations, loadout changes, and per-character isolation in
player-oriented language; and translate typed API errors into contextual instructions that tell a
player what happened and how to correct it. Raw backend detail may remain available for diagnostics
without being the primary player message.

### M8 — Deployment and operations

- **Status:** Deferred
- **Depends on:** Stable core campaign loop

Deploy on a dedicated Gandalf application VM, not Clawvis. Add service supervision, environment
management, migrations, health monitoring, structured logs, backups, restore tests, and a documented
rollback procedure.

### M9 — Optional Clawvis integration

- **Status:** Deferred
- **Depends on:** M8

Clawvis may become a client for Gandalf's public API. Gandalf must remain independently playable and
deployable if Clawvis is offline.

## 11. Issue and technical-debt register

| ID | Type | Status | Description | Impact | Resolution/owner milestone |
| --- | --- | --- | --- | --- | --- |
| ISSUE-001 | Environment | Resolved | VM template revoked `CREATE` on `public`, initially blocking Alembic | Tests/migrations failed | Granted each restricted role schema creation only in its own DB; M0 |
| DEBT-001 | Architecture | In progress | The M1.4 authoritative check/save API rejects supplied modifiers and derives them from canonical state, but the legacy Phase 0 turn provider contract still requests a non-authoritative modifier | Direct resolution is protected; live AI turns are not yet routed through it | Replace the legacy turn dice request with M1.4 resolution before narration; M2 |
| DEBT-002 | Architecture | Open | Narration is generated before dice results | Narration may contradict outcome | Two-stage turn flow; M2 |
| GAP-001 | Product | Resolved | M1.3 supports an ordered 2–4 character Party Commander party with independently derived equipment/defense/resource state and actor isolation | Party Commander foundation now exists; character content breadth remains intentionally narrow | Automated evidence passed in migration `0004` and 39-test suite; record owner checkpoint, then expand breadth only in M1.5 |
| GAP-002 | Product | Open | No deterministic quest/world decision model | Decisions have limited lasting effects | M3 |
| TEST-001 | Validation | Open | OpenAI provider has no paid live evaluation | Real structured behavior unproven | Lantern Test; M2 |
| WARN-001 | Dependency | Monitoring | Current TestClient emits an `httpx` deprecation warning | No functional failure today | Reassess FastAPI/Starlette test client during dependency maintenance |
| OPS-001 | Source control | Resolved | Initial push was blocked because HTTPS lacked credentials and Git did not automatically select the nonstandard SSH key filename | GitHub was temporarily behind local `main` | Registered the existing Ed25519 key, verified GitHub's host fingerprint, configured this repository's SSH command, and synchronized `main`; 2026-08-30 |
| OPS-002 | Infrastructure | Deferred | pgvector is unavailable on `postgresvm` | No semantic memory yet | Evaluate/install only at M4 |
| DOC-001 | Documentation | Open | RES-001's verbatim export contains temporary Deep Research citation tokens | Tokens are not durable implementation citations | Preserve the source unchanged; use official URLs and SRD pages in specifications and rule definitions; M1.1 onward |
| GAP-003 | Rules | Resolved | Authoritative ability checks and saving throws now derive from actor-bound canonical state and preserve exact dice, rules/catalog provenance, typed outcomes, and replay evidence | Character choices now produce reproducible check/save outcomes through the dedicated resolution API | Migration `0005`, 45-test suite, fixed-dice/restart replay, modifier rejection, schema/catalog integrity, and development runtime checks passed; owner workflow remains the M1.4 acceptance gate |
| GAP-004 | Product | Open | Solo balance has a research framework but no measured product results | Encounter/class support cannot yet claim solo balance | Establish strict-SRD baselines in M5; build balance harness after supported combat |
| DEBT-003 | Architecture | Open | The research proposes greenfield service/table boundaries that have not been reconciled with Phase 0 models | Premature adoption could create redundant schema or services | Reconcile per vertical slice; do not bulk-create the proposed model; M1 onward |
| ISSUE-002 | Migration/test fixture | Resolved | Synthetic M1.2 migration tests could begin after isolated cleanup had removed the M1.1 seed row | The new foreign-key-backed catalog seed could not be installed from that test baseline | `0003` inserts the exact immutable M1.1 release with `ON CONFLICT DO NOTHING`; transactional migration tests and the full suite pass |
| ISSUE-003 | Migration/test fixture | Resolved | The first M1.3 run found the isolated test DB at migration `0003` after fixture cleanup had removed immutable seed rows | `0004` initially could not insert its state catalog because the known release FK row was absent | `0004` idempotently restores only the exact pinned release before inserting the new catalog; focused migration smoke, full-chain tests, and 39-test suite pass |
| ISSUE-004 | Character-state provenance | Resolved | The first M1.3 owner run showed empty projected source/acquisition provenance for Dice Set and GP; ordinary package items were unaffected | The visible equipment projection did not meet GF-004 even though canonical grants remained intact | The corrected projection and exhaustive regression passed 39 automated tests; the 2026-09-01 owner retest confirmed complete Dice Set/GP definition, source, and acquisition-event provenance for both existing characters |
| UX-001 | Player interface | Deferred | Backend errors are adequate for developer diagnosis but do not yet provide contextual, player-oriented recovery guidance; JSON also cannot validate visual actor/state clarity | Ordinary players may not know what happened or how to correct an invalid action when the frontend is introduced | In M7, map stable typed API errors to actionable messages and test actor visibility, calculated-value explanations, and isolated character changes through the full player journey |

New entries must include reproduction steps or evidence when applicable. Do not close an issue only
because a workaround exists; record both the workaround and the permanent resolution.

## 12. Risk register

| ID | Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| RISK-001 | Model invents or contradicts mechanics | High | High | Typed two-stage flow; deterministic resolver; reject invalid proposals |
| RISK-002 | Character schema expands without versioning | Medium | High | Version rules and migrations; golden character fixtures |
| RISK-003 | Guide receives spoilers | Medium | High | Separate query path; visibility filters; adversarial tests |
| RISK-004 | RAG replaces exact state | Medium | High | Relational state always injected separately; retrieval contracts |
| RISK-005 | Provider outage partially commits a turn | Medium | High | Turn state machine, idempotency, atomic finalization |
| RISK-006 | Concurrent turns create ordering conflicts | Medium | Medium | Campaign locking, unique sequences, idempotency keys |
| RISK-007 | Rules corpus, attribution, or adaptations drift from the licensed source | Medium | High | Immutable source artifact, CC-BY attribution, checksummed manifests, source references, and regeneration tests |
| RISK-008 | Context/token cost grows with campaign age | High | Medium | Filtered state, summaries, retrieval budgets, usage logging |
| RISK-009 | SSH tunnel interrupts local development | Medium | Low | Clear health errors and tunnel runbook; later private app VM |
| RISK-010 | Overbuilding infrastructure delays gameplay proof | Medium | Medium | Vertical slices and milestone gates; defer optional systems |
| RISK-011 | Binary rules documents make Git history unnecessarily large | Medium | Low | Store official PDFs as versioned GitHub Release assets; keep only manifests and derived data in Git |
| RISK-012 | Supporting all character options before one complete slice delays executable evidence | High | High | Fixed Human/Soldier/Fighter M1 slice; defer breadth to M1.5 |
| RISK-013 | A generic rules DSL is designed before concrete semantics are proven | Medium | High | Start with typed data and pure functions; generalize only repeated rules; permit focused versioned resolvers |
| RISK-014 | Natural-language SRD exceptions are translated silently or incorrectly | High | High | Durable source/page citations, explicit rulings, specialized fixtures, and “specific beats general” review |
| RISK-015 | Narration creates hidden mechanical effects | High | High | Mechanical write boundary, typed commands/events, world-fact namespace, and rejection fixture |
| RISK-016 | Party-oriented encounter guidance is treated as a lone-hero safety guarantee | High | High | Prove Party Commander first; later run strict single-character benchmarks, action-economy metrics, seeded simulations, and labelled house-rule comparisons |
| RISK-017 | Gandalf additions are mistaken for official SRD rules | Medium | High | Separate versioned house-rule packages, UI labels, source/rationale, tests, and migration identity |
| RISK-018 | Research recommendations drift from code or are mistaken for implemented behavior | Medium | Medium | Research index/reviews, traceability matrix, implementation-status labels, and milestone evidence gates |
| RISK-019 | Multi-character state or action attribution leaks across party members | Medium | High | Explicit actor/target IDs, per-character revisions and provenance, isolation/rollback tests, and GF-015 at every party-aware boundary |

## 13. Architectural decision log

| ID | Date | Decision | Reason | Revisit when |
| --- | --- | --- | --- | --- |
| ADR-001 | 2026-08-29 | PostgreSQL is canonical campaign state | Exact state must survive context loss and restart | Never, unless storage requirements fundamentally change |
| ADR-002 | 2026-08-29 | Model output is structured and application-validated | Models must not directly mutate state | Provider contract changes |
| ADR-003 | 2026-08-29 | Dice are rolled and logged by application code | Fairness, reproducibility, and auditability | Never for authoritative rolls |
| ADR-004 | 2026-08-29 | Development runs on MacBook with isolated DBs on `postgresvm` | Fast loop without another application VM | M8 deployment |
| ADR-005 | 2026-08-29 | Clawvis remains isolated | Avoid coupling and operational risk | M9 only |
| ADR-006 | 2026-08-29 | Defer pgvector until exact world state works | Semantic memory cannot repair weak canonical state | M4 |
| ADR-007 | 2026-08-29 | Deterministic mechanics, generative narrative | Character choices and rules must have trustworthy effects | If product direction changes |
| ADR-008 | 2026-08-29 | Build character creation before broad live-model play | Phase 0 exposed that minimal HP/inventory cannot validate D&D outcomes | After M1 acceptance |
| ADR-009 | 2026-08-30 | Preserve immutable versioned SRD artifacts separately from normalized rules data | Players need downloadable references while the engine needs reproducible structured rules and existing campaigns must never change silently | If licensing, source distribution, or artifact-hosting requirements change |
| ADR-010 | 2026-08-30 | Preserve provenance for character grants/choices and derive calculated values from canonical source facts | Advancement, explanation, replay, replacement, and ruleset migration require knowing why each value exists | Only if a proven storage constraint requires a rebuildable cache/projection |
| ADR-011 | 2026-08-30 | Use one complete Human/Soldier/Fighter/standard-array vertical slice for M1 before broad character content | RES-001 is comprehensive but implementing all level-one options first would delay evidence and hide defects | After M1.4 acceptance |
| ADR-012 | 2026-08-30 | Only validated rules commands/events may change mechanical state; narration and world facts cannot silently establish mechanics | Persistent narrative freedom must not compromise deterministic, auditable D&D outcomes | Never for authoritative mechanics |
| ADR-013 | 2026-08-30 | Measure strict SRD solo behavior before adding separately versioned solo house rules | Party-dependent features and encounter action economy cannot be corrected safely through invisible exceptions | After supported combat produces balance evidence |
| ADR-014 | 2026-08-30 | Introduce structured rule operators incrementally from proven semantics, with versioned specialized resolvers for exceptions | Avoid both feature-specific subclass sprawl and a premature universal rules language | When repeated implemented rules justify a new operator |
| ADR-015 | 2026-08-31 | Give normalized data catalogs immutable identities separate from source releases and pin every record to both | The official artifact can remain unchanged while supported machine-readable subsets evolve; old campaigns must not silently adopt later semantics | When an explicit catalog/ruleset conversion workflow is implemented |
| ADR-016 | 2026-08-31 | Deliver solo-player control modes in the order Party Commander, Protagonist with Companions, then Lone Hero | Direct control of a normal adventuring party aligns most closely with D&D's party mechanics; delegated companions can then reuse that trusted foundation, while exceptional single-character balance should be designed last from measured party and companion evidence | Revisit sequencing only if executable evidence shows Party Commander cannot establish the common mechanical foundation |
| ADR-017 | 2026-09-01 | Add check/save definitions as a separately identified immutable supplemental catalog that explicitly extends the pinned character-state catalog | Existing campaigns must gain a compatible resolver without rewriting their historical catalog identity, while resolution records still need an exact machine-readable rules version | When catalog composition or an explicit campaign conversion workflow is designed |

## 14. Milestone review template

Copy this section under the relevant milestone when it reaches `Verification` or `Done`:

```text
Milestone:
Review date:
Status:
Commits/migration revisions:

Acceptance criteria passed:
-

Automated evidence:
- tests:
- coverage:
- lint/format:
- migration drift:

Manual scenarios and results:
-

What worked well:
-

What did not work:
-

Bugs/issues discovered:
-

Workarounds used:
-

Architecture or scope changes:
-

Follow-up work and destination milestone:
-

Go / rework / stop decision:
Rationale:
```

## 15. Bug report template

```text
ID:
Title:
Detected in milestone/commit:
Status and severity:
Environment:

Expected behavior:
Actual behavior:
Reproduction steps:
Evidence/log/event IDs:
State or data affected:

Immediate containment/workaround:
Suspected root cause:
Permanent fix:
Regression test:
Destination milestone:
```

## 16. Change-control rules

- Schema changes require Alembic migrations; never edit an applied migration after it has been shared.
- Rules behavior changes require a rule-version or compatibility decision and golden regression tests.
- Visibility changes require spoiler-boundary tests.
- Provider changes require contract tests and a recorded live evaluation before becoming default.
- Destructive data operations require explicit scope verification and backup/restore consideration.
- New infrastructure must solve an observed requirement, not a hypothetical future need.
- A completed milestone moves to `Rework` when later evidence invalidates its acceptance result.
- Every workaround receives either a permanent-fix milestone or an explicit acceptance decision.
- No implementation or fix is complete while this plan or affected player documentation is stale.
- Every player-facing release requires a supported-features/limitations review and safe release notes.
- Every new research artifact must be preserved/indexed when lawful, reviewed separately, and linked
  to the decisions or milestones it influences.
- Every rules implementation interpretation or product policy that changes legal choices or outcomes
  must be recorded in `docs/rules/RULINGS.md` with durable source citations and required fixtures.
- Research recommendations remain non-implemented until the traceability matrix and milestone
  evidence identify the corresponding code, migration, and passing verification.

## 17. Immediate next actions

1. Run the M1.4 owner workflow in
   [`player/M1_4_ACCEPTANCE_CHECKLIST.md`](player/M1_4_ACCEPTANCE_CHECKLIST.md); record every result
   as evidence, defect, ruling question, documentation clarification, or accepted limitation.
2. Fix and retest any M1.4 defect, or mark the milestone Done when owner acceptance passes.
3. Review complete M1 evidence and documentation freshness before M2; keep broader character options
   in M1.5 rather than expanding the M1 exit gate.
4. Design M2's two-stage turn so the legacy provider dice request is replaced by the authoritative
   M1.4 resolver before narration, closing `DEBT-001`.

## 18. Documentation change log

| Date | ID | Change | Reason/evidence | Follow-up |
| --- | --- | --- | --- | --- |
| 2026-08-29 | DOC-001 | Created the living strategy, M0 retrospective, M1–M9 roadmap, and issue/risk/decision registers | Phase 0 commits and test/migration evidence needed a durable project record | Maintain alongside every material development change |
| 2026-08-29 | DOC-002 | Adopted the documentation maintenance, long-term memory, and audience contracts | Project owner designated this plan as redundant long-term memory, dev log, project reference, and player documentation index | Add dedicated engineering, operations, and player documents when their milestones begin |
| 2026-08-29 | DOC-003 | Recorded the blocked GitHub synchronization attempt | Remote was a safe fast-forward, but HTTPS credentials were unavailable and both existing Mac SSH keys were rejected by GitHub | Register/authenticate one GitHub credential, push, then close OPS-001 with synchronization evidence |
| 2026-08-30 | DOC-004 | Closed OPS-001 after restoring authenticated GitHub synchronization | The registered Ed25519 key authenticated as `asinpark123`; the repository-specific SSH command selected it and `main` pushed successfully | Continue normal fetch-before-push workflow |
| 2026-08-30 | DOC-005 | Approved immutable, downloadable, multi-version SRD source artifacts with separate normalized rules data | Product owner approved preserving SRD 5.2.1 for reference/download and supporting future player-selected rulesets | Implement M1.1 registry, attribution, checksum verification, local cache, and release asset |
| 2026-08-30 | DOC-006 | Preserved and indexed RES-001, recorded its adoption review, created the character/rules specification and rulings register, and revised M1 scope/risks/decisions/traceability | Project owner approved the reviewed recommendations and required research to remain durable long-term development memory | Implement M1.1 from the fixed vertical slice; keep research, rulings, specifications, and evidence synchronized |
| 2026-08-30 | DOC-007 | Recorded M1.1 registry, artifact verification, database pinning, migration safety, tests, and `Verification` status | 22 tests, 91% coverage, exact official artifact checksum, schema validation, HTTP 200 health, and zero migration drift | Publish and verify the GitHub Release mirror, then close M1.1 and begin source-cited character definitions |
| 2026-08-30 | DOC-008 | Closed M1.1 and advanced current delivery to M1.2 | Commit `bada61c`, migration `0002_ruleset_releases`, the official artifact, and the published project release all passed the recorded integrity, migration, API, schema, lint, runtime, and regression gates | Implement the source-cited Human/Soldier/Fighter guided-creation slice |
| 2026-08-31 | DOC-009 | Closed M1.2, added the player character-creation guide, and advanced current delivery to M1.3 | Commit `ba7bca8`, 38 tests, 91% coverage, migration `0003`, immutable source-linked grants, schema/catalog integrity checks, zero Alembic drift, and development health all passed | Complete reproducible Phase 1 character state without expanding the supported creation slice |
| 2026-08-31 | DOC-010 | Added project-owner decision gates and milestone-specific player acceptance checkpoints | The owner requested a durable record of when input is required and when hands-on testing is useful; M1.3 has no blocking input and receives a verification-stage sheet review | Provide a concise setup/actions/expected-results checklist at every applicable verification gate and record all outcomes |
| 2026-08-31 | DOC-011 | Adopted party-first solo-player architecture and sequenced Party Commander, Protagonist with Companions, then Lone Hero | The owner selected standard party play as the mechanical foundation so delegated companions reuse proven rules and exceptional single-character compensation is designed last from evidence | Make M1.3 party-aware before adding further deterministic state; retain the fixed Human/Soldier/Fighter content slice until M1.4 passes |
| 2026-08-31 | DOC-012 | Advanced M1.3 to Verification and recorded Party Commander/state implementation, corrected Alert initiative, migration/runtime evidence, limitations, and owner gate | Migration `0004`, immutable state catalog, 39 tests, 92% coverage, zero Alembic drift, dev health 200, and actor-isolation/loadout fixtures passed | Complete the owner checklist, record feedback, then either fix defects or close M1.3 and begin M1.4 |
| 2026-08-31 | DOC-013 | Recorded the first owner acceptance run, resolved its Dice Set/GP projection-provenance defect, and narrowed the remaining gate to three targeted checks plus subjective feedback | Owner evidence confirmed the main workflow and exposed ISSUE-004; the corrected projection and exhaustive equipment-provenance regression pass the full 39-test suite | Run the targeted retest, record subjective answers, and close or rework M1.3 from that evidence |
| 2026-09-01 | DOC-014 | Recorded the successful targeted M1.3 owner retest and closed ISSUE-004 | Both characters now expose complete Dice Set/GP provenance, omitted actor selection returns the intended domain 409, and both successful turn events retain SugarHigh's actor ID | Record the five subjective answers, then close or rework M1.3 without repeating the technical workflow |
| 2026-09-01 | DOC-015 | Closed M1.3 and converted the owner's backend-versus-frontend usability distinction into explicit M7 acceptance requirements | Structured-value correctness passed; JSON output cannot meaningfully prove visual clarity, and API errors need frontend context before ordinary players can self-correct | Begin M1.4; implement and test UX-001 during M7 rather than treating it as an M1.3 backend defect |
| 2026-09-01 | DOC-016 | Advanced M1.4 to Verification and recorded the authoritative check/save service, supplemental immutable catalog, migration, automated/runtime evidence, limitations, decision, and owner checklist | Migration `0005`, 45 tests at 91% total coverage and 95% resolution-module coverage, lint/format/schema/catalog/diff checks, zero Alembic drift, development health, modifier rejection, actor isolation, immutable provenance, and restart replay passed | Complete the M1.4 owner checklist; fix defects or close M1.4, then review the complete M1 gate before M2 |
