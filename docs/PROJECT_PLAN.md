# GandalfDnD Development Strategy and Living Project Plan

- **Document status:** Active
- **Last updated:** 2026-08-30
- **Rules baseline:** SRD 5.2.1 (provisional until rules ingestion is implemented)
- **Current delivery stage:** Planning Milestone 1 — Character creation and deterministic mechanics
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

## 2. Product objective

GandalfDnD will provide a persistent solo D&D experience with two eventually distinct AI roles:

1. A campaign-stateful Dungeon Master that conducts fair, coherent play over long campaigns.
2. A spoiler-safe Guide that teaches rules and explains player options without receiving hidden
   campaign information.

The application—not the language model—owns exact game state and mechanical truth. AI is used for
interpretation, roleplay, narration, and bounded proposals. Deterministic application services
resolve rules, dice, resources, and allowed state transitions.

## 3. Success criteria

The project succeeds when a solo player can create a legal character, play a long campaign, restart
the application, and continue with mechanically correct state and narratively coherent recall.

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
| M1 | Character creation and deterministic mechanics | Proposed | Character choices drive calculated outcomes |
| M2 | Two-stage AI turn and live feasibility | Proposed | Real DM uses recorded dice results safely |
| M3 | Persistent world model | Proposed | NPCs, quests, scenes, clues, time, and visibility |
| M4 | Long-term memory and retrieval | Proposed | Coherent recall without full history in context |
| M5 | Basic deterministic combat | Proposed | Reproducible initiative, actions, attacks, and damage |
| M6 | Spoiler-safe Guide | Proposed | Beginner help with enforceable knowledge boundaries |
| M7 | Play interface and campaign administration | Proposed | Usable play, recap, correction, and export workflows |
| M8 | Deployment and operations | Deferred | Dedicated reliable service with backups and monitoring |
| M9 | Optional Clawvis integration | Deferred | Clawvis acts only as an API client/interface |

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

- **Status:** Proposed
- **Priority:** Immediate

Player outcome: a beginner can create a rules-valid level-one character, understand their choices,
and receive mechanically reproducible checks derived from the saved character sheet.

Planned slices:

#### M1.1 Versioned rules data

**Status:** Ready

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

#### M1.2 Guided character creation

- draft/finalized character-creation lifecycle;
- rules-valid identity, abilities, class, background, level, and starting equipment choices;
- guided descriptions suitable for a first-time player;
- calculated starting HP and proficiencies;
- creation events record every consequential choice;
- finalized characters are immutable except through explicit advancement/admin workflows.

#### M1.3 Complete Phase 1 character state

- ability scores and modifiers;
- proficiency bonus, skills, and saving throws;
- armor class, initiative, speed, hit dice, and level;
- equipped versus carried inventory;
- features, conditions, and expendable resources;
- spellcasting fields only for the initially supported character options.

#### M1.4 Deterministic resolution service

- calculate modifiers from canonical state rather than model-provided numbers;
- resolve ability checks and saving throws first;
- record rule version, formula inputs, dice, and total in a rule-resolution record;
- reject actions blocked by conditions, missing proficiency, or unavailable resources where rules
  require it;
- return a typed outcome for later narration.

Acceptance gates:

- one complete supported level-one character can be created through the API without manual DB edits;
- all derived values match golden test fixtures;
- invalid option combinations and illegal point allocations are rejected;
- a check's modifier cannot be supplied or overridden by the model;
- identical state plus fixed dice produces an identical mechanical result;
- creation and resolution survive restart and can be reconstructed from events;
- a beginner-facing explanation exists for each creation choice in the supported slice;
- every rule-derived value identifies the immutable ruleset and normalized rule-data version used.

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
- run the real-model Lantern Test: dialogue, movement, inventory use, check, damage, restart, resume;
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

Exit gate: fixed combat fixtures replay to identical results, illegal actions are rejected, and a
restart during combat resumes the exact initiative and resource state.

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
| DEBT-001 | Architecture | Open | Model requests its own dice modifier | Fairness and correctness are incomplete | Calculate from character/rules state; M1.4 |
| DEBT-002 | Architecture | Open | Narration is generated before dice results | Narration may contradict outcome | Two-stage turn flow; M2 |
| GAP-001 | Product | Open | Character creation is only name, HP, inventory | Not sufficient for real D&D | M1.1–M1.3 |
| GAP-002 | Product | Open | No deterministic quest/world decision model | Decisions have limited lasting effects | M3 |
| TEST-001 | Validation | Open | OpenAI provider has no paid live evaluation | Real structured behavior unproven | Lantern Test; M2 |
| WARN-001 | Dependency | Monitoring | Current TestClient emits an `httpx` deprecation warning | No functional failure today | Reassess FastAPI/Starlette test client during dependency maintenance |
| OPS-001 | Source control | Resolved | Initial push was blocked because HTTPS lacked credentials and Git did not automatically select the nonstandard SSH key filename | GitHub was temporarily behind local `main` | Registered the existing Ed25519 key, verified GitHub's host fingerprint, configured this repository's SSH command, and synchronized `main`; 2026-08-30 |
| OPS-002 | Infrastructure | Deferred | pgvector is unavailable on `postgresvm` | No semantic memory yet | Evaluate/install only at M4 |

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

## 17. Immediate next actions

1. Create the M1.1 ruleset registry, directory structure, attribution, and manifest schema.
2. Download the official SRD 5.2.1 PDF, calculate and record its checksum, and add a verified fetch
   workflow plus ignored local cache.
3. Publish the unchanged source PDF as a versioned project download asset.
4. Specify the exact supported level-one character-creation slice for M1.2–M1.4.
5. Design versioned character/rules schemas before adding model prompts.
6. Implement golden fixtures and deterministic derived-stat calculations.
7. Implement guided character creation and finalize-character validation.
8. Add authoritative check/save resolution and rule-resolution audit records.
9. Review M1 evidence using the milestone review template before beginning the two-stage live AI flow.

## 18. Documentation change log

| Date | ID | Change | Reason/evidence | Follow-up |
| --- | --- | --- | --- | --- |
| 2026-08-29 | DOC-001 | Created the living strategy, M0 retrospective, M1–M9 roadmap, and issue/risk/decision registers | Phase 0 commits and test/migration evidence needed a durable project record | Maintain alongside every material development change |
| 2026-08-29 | DOC-002 | Adopted the documentation maintenance, long-term memory, and audience contracts | Project owner designated this plan as redundant long-term memory, dev log, project reference, and player documentation index | Add dedicated engineering, operations, and player documents when their milestones begin |
| 2026-08-29 | DOC-003 | Recorded the blocked GitHub synchronization attempt | Remote was a safe fast-forward, but HTTPS credentials were unavailable and both existing Mac SSH keys were rejected by GitHub | Register/authenticate one GitHub credential, push, then close OPS-001 with synchronization evidence |
| 2026-08-30 | DOC-004 | Closed OPS-001 after restoring authenticated GitHub synchronization | The registered Ed25519 key authenticated as `asinpark123`; the repository-specific SSH command selected it and `main` pushed successfully | Continue normal fetch-before-push workflow |
| 2026-08-30 | DOC-005 | Approved immutable, downloadable, multi-version SRD source artifacts with separate normalized rules data | Product owner approved preserving SRD 5.2.1 for reference/download and supporting future player-selected rulesets | Implement M1.1 registry, attribution, checksum verification, local cache, and release asset |
