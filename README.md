# GandalfDnD

GandalfDnD is a persistent D&D engine for a solo player, with an AI dungeon-master boundary. The
product direction is party-first: the player will initially command every party character, with
AI-assisted companions and a specially balanced lone-hero mode following later. Phase 0 proves the
smallest trustworthy loop: campaign state enters the model as data, the model returns typed
proposals, application code validates those proposals, dice are rolled by code, and the accepted
result is committed to PostgreSQL with an append-only event trail.

The roadmap, milestone gates, validation history, architectural decisions, and issue register are
maintained in the [living development plan](docs/PROJECT_PLAN.md).

## Project documentation

- [Living development plan](docs/PROJECT_PLAN.md) — current status, milestones, validation evidence,
  risks, decisions, bugs, and next actions
- [Research index](docs/research/README.md) — preserved research sources, provenance, integrity, and
  adoption reviews
- [Character and deterministic rules specification](docs/rules/CHARACTER_AND_RULES_SPEC.md) —
  canonical character state, rules boundaries, M1 scope, golden fixtures, and traceability
- [Rules and product-rulings register](docs/rules/RULINGS.md) — SRD interpretations, product
  policies, adjudications, house rules, and unresolved decisions
- [Player character-creation guide](docs/player/CHARACTER_CREATION.md) — supported choices,
  step-by-step API workflow, limitations, and rules-source notes
- [Beginner game-setup guide](docs/player/GAME_SETUP_GUIDE.md) — party modes, narrative profiles,
  content boundaries, environmental consequences, and the current evaluation preset
- [M1.3 owner acceptance checklist](docs/player/M1_3_ACCEPTANCE_CHECKLIST.md) — hands-on Party
  Commander verification and feedback record
- [M1.4 owner acceptance checklist](docs/player/M1_4_ACCEPTANCE_CHECKLIST.md) — authoritative
  check/save, rejection, attribution, and replay verification
- [M1.4 owner acceptance results](docs/testM1_4_ACCEPTANCE_CHECKLIST_RESULTS.md) — preserved
  nine-action runtime evidence
- [M2 implementation strategy](docs/M2_IMPLEMENTATION_STRATEGY.md) — resumable two-stage turns,
  authoritative resolution, failure safety, and live-evaluation gates
- [OpenClaw provider integration](docs/OPENCLAW_INTEGRATION.md) — subscription-backed transport,
  deployment boundary, security, activation, and model/GM-style strategy
- [M2.5A OpenClaw evaluation](docs/M2_5_OPENCLAW_EVALUATION.md) — live deployment, compatibility,
  ten-scenario acceptance, recovery, usage, and latency evidence
- [M3 implementation strategy](docs/M3_IMPLEMENTATION_STRATEGY.md) — persistent scenes, NPCs,
  facts, quests, decisions, time, visibility, and branching acceptance gates
- [M3 live OpenClaw evaluation](docs/M3_OPENCLAW_EVALUATION.md) — capped persistent-branch,
  presence, restart, coherence, usage, and duplicate-fact hardening evidence
- [M4 implementation strategy](docs/M4_IMPLEMENTATION_STRATEGY.md) — source-cited long-term memory,
  local embeddings, hybrid retrieval, re-indexing, and 500-event acceptance gates
- [M4 PostgreSQL/pgvector audit](docs/M4_POSTGRES_PGVECTOR_AUDIT.md) — read-only readiness findings,
  least privilege, package-impact boundary, and conditional provisioning plan
- [M4.1 memory foundation](docs/M4_1_MEMORY_FOUNDATION.md) — scoped extension enablement,
  migration `0012`, schema invariants, recovery, and acceptance evidence
- [M4.2 source indexing](docs/M4_2_SOURCE_INDEXING.md) — player-safe projection, local embeddings,
  durable recovery, and side-by-side profile lifecycle
- [M4.3 hybrid retrieval](docs/M4_3_HYBRID_RETRIEVAL.md) — filter-first exact/lexical ranking,
  bounded cited context, audit replay, and 500-document quality evidence
- [M4.4 summaries/provider integration](docs/M4_4_SUMMARIES_PROVIDER_INTEGRATION.md) — immutable
  source coverage, bounded untrusted context, prompt separation, and failure-safety evidence
- [M4.5 technical acceptance](docs/M4_5_TECHNICAL_ACCEPTANCE.md) — composed adversarial, restart,
  stale-index, re-index, 500-document quality, and owner-fixture evidence
- [M4.5 owner checklist](docs/player/M4_5_ACCEPTANCE_CHECKLIST.md) — relevance, repetition,
  attribution, restart continuity, and player-facing result-count review
- [M4.5 targeted retest](docs/player/M4_5_TARGETED_RETEST.md) — focused verification of
  supporting-result suppression and two distinct NPCs named Mira
- [M4.5 targeted results](docs/testM4_5_TARGETED_RETEST_RESULTS.md) — accepted owner evidence and
  the M7 supporting-memory presentation requirement
- [M4 live OpenClaw evaluation](docs/M4_OPENCLAW_EVALUATION.md) — capped same-name recall,
  injection isolation, reconnect, state-safety, usage, and latency evidence
- [PostgreSQL 18 migration strategy](docs/POSTGRESQL_18_MIGRATION_STRATEGY.md) — parallel-cluster,
  Gandalf-only migration, acceptance, rollback, and longevity gates
- [PostgreSQL 18 readiness audit](docs/POSTGRESQL_18_READINESS_AUDIT.md) — verified package impact,
  shared-host boundaries, compatibility, isolation finding, and migration recommendation
- [PostgreSQL 18 foundation execution](docs/POSTGRESQL_18_FOUNDATION_EXECUTION.md) — recovery,
  signed package, parallel-cluster, HBA-isolation, restore, and test evidence
- [PostgreSQL 18 development rehearsal](docs/POSTGRESQL_18_DEVELOPMENT_REHEARSAL.md) — fresh
  development restore, exact source comparison, dual-runtime acceptance, and cutover gate
- [PostgreSQL 18 active cutover](docs/POSTGRESQL_18_CUTOVER_EXECUTION.md) — final recovery,
  rollback-protected tunnel/API switch, post-cutover acceptance, and stabilization boundary

Documentation distinguishes planned behavior from verified implementation. M1.3 Party Commander
and complete level-one character state are Done. M1.4 authoritative ability-check and saving-throw
resolution is also Done after automated and owner runtime verification. The complete M1 gate is
Done. M2 is also Done: the resumable two-stage workflow, deterministic Lantern suite, private
OpenClaw activation, and three passing ten-scenario live model-authored runs are verified. Direct
paid API integration remains deferred and paid model calls remain disabled. M3.1–M3.4 are Done with
exact scene/NPC presence, explicit target IDs, world-revision safety, typed narrative facts,
relationships, supersession, controlled reveal, durable quests/objectives, explicit exact-once
branch decisions, typed factions, bounded narrative time, and audience-safe world projections. M3
is Done after its corrected deterministic and owner-guided branching, NPC continuity, restart,
causal replay, and recoverable-error gates passed. Its separately authorized capped live OpenClaw
supplement also passed both persistent branches after exposing and resolving an exact duplicate
decision-fact edge case. M4 is Done after the staged PostgreSQL 18 migration, memory implementation,
technical gate, relevance rework, owner acceptance, and supplemental live evaluation. The database
foundation and restore rehearsals installed PostgreSQL 18.6 and pgvector 0.8.6 without changing
PostgreSQL 15 server/client; `18/gandalf` is checksum-enabled and
loopback-only; PG15 role isolation is hardened; and exact test/development copies passed the full
suite plus two complete dual-runtime comparisons while PostgreSQL 15 and Bluebuild remained
healthy. The rollback-protected active cutover then passed: Gandalf development and tests now use
PostgreSQL 18, its startup policy is automatic, and the post-cutover isolated suite passed again.
PostgreSQL 15 rollback copies/roles remain intact. M4.1 then enabled pgvector 0.8.6 only in the two
PostgreSQL 18 Gandalf databases and added the guarded `0012_memory_foundation` schema; 135 tests and
all migration, drift, isolation, vector, API, and shared-service gates pass. M4.2 added durable,
player-safe indexing with the pinned local BGE model. M4.3 now adds versioned exact-vector plus
lexical retrieval, strict source/context bounds, replayable raw-query-free audits, and a passing
500-record local-model gate. M4.4 adds immutable source-cited summaries and fail-soft historical
context to both provider stages while keeping exact state separate. M4.5's deterministic technical
gate passes, including a 500-document local-model fixture and atomic different-dimension re-indexing.
Its first owner review accepted every primary memory but triggered a focused correction for generic
supporting results and inconclusive same-name evidence. Versioned policy `1.1.0`, fixture v2, the
revised automated/local gate, and the targeted owner retest now pass. M4 is Done; M7 must present
genuinely qualifying cited supporting memories when they are available. The separately authorized
live M4 supplement also passed: the final prompt and retrieval contracts recalled two role-specific
Miras correctly, kept hostile quoted prose mechanically inert, excluded a DM-only secret, and left
exact state unchanged across a database reconnection.

## Versioned rulesets

Campaigns, characters, campaign events, and dice rolls are pinned to an immutable ruleset release.
The registered foundation release is `srd-5.2.1`; arbitrary names and dynamic aliases such as
`latest` are rejected.

Validate the registry and its generated JSON Schemas:

```bash
python -m scripts.validate_rulesets
python -m scripts.export_ruleset_schemas --check
```

Fetch the unchanged official SRD into the ignored local cache with manifest size and SHA-256
verification:

```bash
python -m scripts.fetch_ruleset --release srd-5.2.1
```

The PDF remains outside normal Git history. Its official and project-release download locations,
checksum, size, license, attribution, normalized-data catalogs, and schema versions are recorded in
[`rulesets/srd-5.2.1/manifest.json`](rulesets/srd-5.2.1/manifest.json).

## Current verified scope

- FastAPI API with health, campaigns, ordered parties, locations, turns, and player-visible events
- PostgreSQL as the canonical source of truth through SQLAlchemy 2 and Alembic
- guided draft/finalize creation for two to four independently persisted level-one
  Human/Soldier/Fighters using the standard array
- source-cited, immutable character choices and grants pinned to a normalized data catalog
- calculated ability scores/modifiers, level-one HP, proficiency bonus, skill and saving-throw
  modifiers, AC alternatives, initiative, passive Perception, Speed, features/resources, equipment
  positions, and source/acquisition provenance
- acting-character attribution on turns, dice, player-visible events, and isolated state changes
- authoritative ability checks and saving throws with canonical modifiers, contextual skill
  abilities, Advantage/Disadvantage cancellation, exact dice, typed outcomes, idempotency, immutable
  provenance, and restart replay
- resumable two-stage turn execution with typed intent, post-resolution narration, exact outcome
  acknowledgement, bounded proposals, stage leases, stale-state rejection, safe restart recovery,
  stable provider errors, usage audits, and atomic final events/state commit
- HP, inventory, and current-location state changes with pre-commit validation
- durable quests and ordered objectives with revision-checked legal transitions, plus visible
  two-to-four-option decisions selected explicitly and applied exactly once as typed narrative
  facts or quest/objective consequences; choices never imply rewards or mechanical effects
- stable factions with revisioned fixed-label party attitudes and character/NPC memberships, plus
  monotonic elapsed narrative minutes; neither can imply reputation modifiers, rest, recovery,
  durations, travel resolution, or other mechanics
- explicit player/DM world audiences with player-only public/provider use and bounded context caps
  for facts, active quests, open decisions, active factions, and faction relationships
- auditable application dice rolls, including internally logged hidden rolls
- provider-neutral DM interface
- deterministic offline provider for development and repeatable tests
- player-visible completed-turn memory with immutable sources, pinned local embeddings, exact-vector
  plus lexical retrieval, replayable score audits, source-complete summaries, and fail-soft cited
  context that remains separate from canonical state
- optional OpenClaw two-stage provider with layered strict-JSON/Pydantic validation, stable
  transport errors, a compact provider context, and independently configurable model route and GM
  style; the owner's private deployment passed the live ten-scenario gate
- legacy Phase 0 OpenAI Responses adapter with Pydantic structured output; the two-stage automated
  direct-API adapter remains disabled because API spend is not authorized

Not included yet: activated production memory profiles, approximate vector indexes, the spoiler-safe
Guide, combat, a web UI, Redis, Celery, or a permanent application VM.

## Local setup

Python 3.11 or newer is required. From the repository:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Gandalf reaches PostgreSQL through a local-only SSH tunnel:

```bash
ssh -N -L 5433:127.0.0.1:5432 postgresvm
```

Keep that terminal open. In another terminal:

```bash
source .venv/bin/activate
alembic upgrade head
uvicorn app.api:app --reload
```

The API is then available at `http://127.0.0.1:8000`; interactive API documentation is at
`http://127.0.0.1:8000/docs`.

## Model provider

The safe default is `GANDALF_LLM_PROVIDER=deterministic`, which performs no external calls.

OpenClaw can provide an optional subscription-backed transport through its private authenticated
gateway. This is not an OpenAI API credential and does not guarantee unlimited or free use;
subscription limits and the deployment's provider configuration still apply. A dedicated,
restricted OpenClaw agent is required. After completing the documented activation and verification
checklist for the operator's deployment, configure the ignored
`.env` file:

```text
GANDALF_LLM_PROVIDER=openclaw
GANDALF_OPENCLAW_BASE_URL=http://127.0.0.1:18790/v1
GANDALF_OPENCLAW_GATEWAY_TOKEN=...
GANDALF_OPENCLAW_AGENT_ID=gandalf
GANDALF_OPENCLAW_MODEL=
GANDALF_OPENCLAW_GM_STYLE=classic_heroic_fantasy
```

See the [OpenClaw integration guide](docs/OPENCLAW_INTEGRATION.md) before enabling it. The gateway
token must remain private and must never be committed.

Direct OpenAI API use still requires separate API authentication and may incur separate charges.
No such spend is currently authorized. The legacy OpenAI adapter can be configured only for a
future explicitly approved test:

```text
GANDALF_LLM_PROVIDER=openai
GANDALF_OPENAI_API_KEY=...
GANDALF_OPENAI_MODEL=gpt-5.4
```

The legacy adapter uses the Responses API's Pydantic parsing path. No model output is written
directly to canonical state: all proposed changes pass through Gandalf's typed validation and
authoritative deterministic services first.

## API surface

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Confirm the API can reach its configured database |
| `POST` | `/campaigns` | Create a campaign and starting location |
| `GET` | `/rulesets/{release}/character-creation/options` | Read supported choices and beginner explanations |
| `POST` | `/campaigns/{id}/characters` | Create an ordered Party Commander character draft |
| `GET` | `/campaigns/{id}/characters` | Read the ordered party and calculated sheets |
| `POST` | `/campaigns/{id}/characters/{character_id}/finalize` | Validate and finalize one character's required choices |
| `GET` | `/campaigns/{id}/characters/{character_id}/grants` | Read one character's immutable choice/grant provenance |
| `PUT` | `/campaigns/{id}/characters/{character_id}/loadout` | Select worn armor and held/readied weapons |
| `GET` | `/campaigns/{id}/state` | Read canonical campaign, party, character, and location state |
| `GET` | `/campaigns/{id}/world` | Read visible scene, NPCs, facts, quests, objectives, and decisions |
| `POST` | `/campaigns/{id}/turn-executions` | Start an idempotent typed turn with an explicit actor, target, or decision choice |
| `POST` | `/campaigns/{id}/turn-executions/{turn_id}/interpret` | Classify the action and resolve any required authoritative check/save |
| `POST` | `/campaigns/{id}/turn-executions/{turn_id}/finalize` | Narrate and atomically apply validated state or branch consequences |
| `POST` | `/campaigns/{id}/turns` | Process one actor-attributed player action after party readiness |
| `POST` | `/campaigns/{id}/resolutions` | Resolve an actor-bound ability check or saving throw from canonical state |
| `GET` | `/campaigns/{id}/resolutions` | List immutable authoritative resolutions |
| `GET` | `/campaigns/{id}/resolutions/{resolution_id}` | Read one authoritative resolution and its provenance |
| `POST` | `/campaigns/{id}/resolutions/{resolution_id}/replay` | Recompute stored dice/modifier inputs and verify equivalence |
| `GET` | `/campaigns/{id}/events` | Read the ordered player-visible event trail |

## Verification

Tests are hard-guarded to a database whose name begins with `gandalfdnd_test`.

```bash
source .venv/bin/activate
ruff check .
ruff format --check .
pytest
```

The integration tests recreate only GandalfDnD-owned rows inside the dedicated test database. They
never target the development database or any pre-existing service database.

## Design constraints

- PostgreSQL state wins over model prose.
- Campaign events are immutable after insertion.
- Every model output is typed and validated before commit.
- Dice outcomes come from `DiceService`, never model invention.
- Authoritative check/save commands contain no modifier field; canonical character state supplies
  every applied modifier component.
- Ruleset releases are immutable; changing versions requires a future explicit migration workflow.
- Normalized data catalogs are immutable; pre-M1.2 records retain their original foundation catalog
  rather than silently acquiring later rules semantics.
- The development and test credentials are separate and ignored by Git.
- Clawvis is outside GandalfDnD's Phase 0 topology and must remain untouched.
