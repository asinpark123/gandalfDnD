# M2 Two-Stage AI Turn Implementation Strategy

- **Status:** Verification — M2.1–M2.4 Done; M2.5A settings accepted and Ready to implement
- **Prepared:** 2026-09-02
- **Depends on:** M1 Party character creation and deterministic mechanics (Done)
- **Owner input required now:** No — the owner selected the no-extra-cost evaluation path and
  accepted the initial content and environmental-consequence settings
- **Paid external model calls:** Not authorized; a later automated provider test requires a new,
  explicit authorization and cap

## 1. Objective

M2 will replace the legacy one-stage turn with a resumable two-stage workflow in which the model may
interpret intent and narrate an already-recorded outcome, but cannot invent dice, supply mechanical
modifiers, directly write canonical state, or cause partial game-state changes when a provider call
fails.

The milestone proves real model-authored structured-output feasibility with the existing
Human/Soldier/Fighter Party Commander slice. The first evaluation is a manual subscription-assisted
handoff so it incurs no provider API charge. This proves the typed content and deterministic game
boundary, but not unattended provider transport. It does not broaden character content, implement
combat, or create the persistent world model.

### 1.1 Subscription and API boundary

The [OpenAI developer quickstart](https://platform.openai.com/docs/quickstart/make-your-first-api-request)
requires an API key and directs API users to add platform credits. The
[API reference](https://developers.openai.com/api/reference/overview) likewise defines API
key authentication. A ChatGPT/Codex subscription is therefore not treated as a server-side
GandalfDnD credential. The project will not automate the ChatGPT web interface or invoke a Codex CLI
as a disguised production provider; those paths are brittle, do not prove the supported API
contract, and risk coupling gameplay to an interactive developer session.

## 2. Required turn flow

```text
idempotent player command + selected actor
    -> persist turn execution and canonical pre-state revision
    -> typed intent interpretation
    -> application validation and M1.4 authoritative resolution
    -> persist exact dice and typed mechanical outcome
    -> typed narration/finalization using that recorded outcome
    -> validate bounded state-change proposals
    -> atomically commit final mechanical changes and player-visible events
```

No database transaction or row lock remains open during an external provider call. Audit/lifecycle
records may persist between stages, but character, location, inventory, resource, and other gameplay
state changes occur only in the final validated transaction.

## 3. Architecture decisions for M2

### 3.1 Resumable state machine

Each turn has a client-generated `command_id` and an explicit lifecycle. The initial supported
states are:

```text
received -> interpreting -> intent_ready -> resolving -> resolved
         -> narrating -> completed
```

A provider or validation failure records `failed`, the failed stage, a stable error code, and
whether resumption is allowed. Resuming from a post-resolution failure must reuse the existing
immutable M1.4 resolution and dice. It must never roll again.

Only one nonterminal turn may exist for a campaign. Finalization locks the campaign and selected
character, verifies the saved pre-state revision is still current, and fails safely on stale state.

### 3.2 Two typed provider stages

Replace the legacy `generate_turn` contract with two provider-neutral operations:

1. `interpret_action` receives player-visible canonical state, the selected actor, and the player's
   text. It returns typed intent and, when needed, an adjudicated check/save request containing the
   resolution type, ability, optional skill, DC, purpose, and Advantage/Disadvantage reasons.
2. `narrate_outcome` receives the canonical state, player action, accepted intent, and immutable
   resolution outcome. It returns narration plus bounded state-change proposals.

Neither output schema contains a numeric dice modifier or dice result. The narration stage cannot
request another roll. The application fills ruleset/catalog pins and invokes only the M1.4 resolver.

### 3.3 Persistence and migration

Migration `0006` should evolve existing `turns` without discarding Phase 0/M1 history:

- add `command_id`, lifecycle status, stage/error fields, intent, resolution link, pre/post state
  revisions, prompt-contract versions, and completion timestamps;
- backfill legacy completed turns safely, using their existing UUID as the historical command ID;
- allow narration/final output to be absent while a turn is nonterminal;
- enforce campaign-scoped command idempotency and at most one active turn per campaign;
- guard downgrade after an M2 turn has entered the new workflow.

Add an immutable provider-call audit record for each interpretation or narration attempt. Record
turn/stage/attempt, provider, model, prompt version, status, latency, token usage when supplied,
structured output or stable error metadata, and timestamps. Never store credentials.

M1.4 `rule_resolutions` remain the authority for exact dice and check/save arithmetic. Do not copy
or recreate a second resolution engine inside the turn service.

### 3.4 API contract

The M2 turn API must support:

- idempotent turn creation with `command_id`, selected actor, and player action;
- reading a turn's current stage, resolution, final narration, state result, and safe failure detail;
- resuming a recoverable failed/interrupted turn;
- returning the existing turn for an identical repeated command;
- HTTP 409 for reuse of a command ID with different content;
- a stable turn ID in recoverable provider-error responses.

The existing owner-test endpoints and event history remain readable. Historical one-stage turns are
reported as legacy completed turns and are never silently reinterpreted.

### 3.5 Failure and retry policy

Tests must inject timeout, connection failure, refusal, empty parsed output, malformed structured
output, invalid intent, invalid state proposal, stale state, and interrupted/restarted process cases.

- Interpretation failure: no roll and no gameplay-state change.
- Resolution rejection: no roll when validation fails before rolling; no final narration or state
  change.
- Narration failure after resolution: preserve the turn and original resolution; no gameplay-state
  change; resumption reuses the original dice.
- Finalization rejection: preserve diagnostics and resolution; atomically reject every proposed
  gameplay-state change.
- Repeated/resumed success: exactly one completed turn and one ordered final event sequence.

### 3.6 Concurrency and event ordering

Use database constraints plus short transactions rather than Redis or a job queue. Campaign and
character revision checks prevent a delayed provider response from committing against changed
state. Event sequences are allocated only while the campaign is locked.

The minimum player-visible event sequence is:

```text
player_action -> rule_resolved (when required) -> dm_response -> state_changed (when present)
```

Provider-call attempts and failures are operational/audit records, not automatically player-visible
campaign facts.

## 4. Delivery slices

### M2.1 — Turn lifecycle and migration

**Status: Done (2026-09-02).**

- implement migration `0006`, status/idempotency/revision fields, provider-call audit storage, and
  read models;
- backfill legacy turns and add guarded migration tests;
- add create/read/resume API skeleton using only the deterministic provider.

Exit: lifecycle, idempotency, one-active-turn constraint, legacy backfill, and restart reads pass.

Implemented evidence:

- migration `0006_turn_lifecycle` backfills legacy turns as completed with `command_id = id`, adds
  lifecycle/checkpoint/failure/revision/prompt fields, links an optional immutable M1.4 resolution,
  and permits unfinished turns without invented narration;
- campaign-scoped command idempotency and a partial unique index enforce at most one active or
  resumable-failed turn per campaign;
- immutable `provider_calls` storage records complete interpretation/narration attempts without
  credentials; M2.1 intentionally records none because it makes no provider calls;
- `/turn-executions` create/list/read/cancel/resume/provider-call boundaries persist safely across
  engine disposal and return 409 for changed idempotency input or competing active turns;
- the legacy M1 `/turns` path remains available for regression compatibility, is marked
  `legacy-turn-1.0.0`, and cannot run while an M2 execution is active;
- a guarded downgrade refuses to discard any M2 execution or provider-call audit history;
- 51 automated tests pass at 91% total coverage, including five lifecycle fixtures, full M0/M1
  regression, provider-call update/delete rejection, guarded downgrade, lint, catalog validation,
  and zero Alembic drift.

M2.1 is an internal foundation, not a playable two-stage AI turn. Interpretation begins in M2.2;
narration/finalization begins in M2.3. The legacy provider call still holds its original transaction
lock and remains tracked debt until authoritative M2 turns replace it. No external or paid model
call was made.

### M2.2 — Typed interpretation and authoritative resolution

**Status: Done (2026-09-02).**

- introduce the provider-neutral interpretation contract and deterministic fixtures;
- validate adjudicated check/save requests and route them through M1.4;
- remove the legacy model-supplied modifier/dice-request path from authoritative turns;
- close `DEBT-001` when every new turn roll uses the M1.4 resolver.

Exit: actor-specific checks/saves use canonical modifiers and exact recorded dice; retries cannot
reroll or change the command.

Implemented evidence:

- a strict provider-neutral `TurnIntent` discriminated union permits either narrative intent or a
  check/save request with ability, optional skill, DC, purpose, and adjudicated
  Advantage/Disadvantage reasons; extra fields such as modifiers and dice results are rejected;
- deterministic offline interpretation advances persisted turns through `interpreting`,
  `intent_ready`, `resolving`, and `resolved` without holding a database transaction open during
  the provider operation;
- accepted checks and saves are pinned by the application and delegated to the unchanged M1.4
  resolver; exact dice, actor-derived modifier/provenance, outcome, resolution link, and turn-linked
  `rule_resolved` event are persisted;
- retrying a resolved command returns the same resolution and exact dice without invoking the
  provider or random source again;
- malformed provider output is audited as a recoverable interpretation failure; unknown skills are
  rejected before rolling; state changed during interpretation is detected using a forced fresh
  database read and rejected without resolution;
- the legacy one-stage endpoint now rejects every provider dice request before any turn, dice,
  event, or state write, so every accepted new turn roll uses authoritative M1.4 resolution and
  `DEBT-001` is closed;
- no schema migration was required beyond M2.1's `0006` lifecycle storage;
- nine focused M2.2 tests and the full 60-test suite pass at 90% coverage, including a direct
  assertion that no database transaction is open during interpretation, with lint, catalog
  validation, zero Alembic drift, and no external or paid model calls.

M2.2 stops at `intent_ready` for no-roll actions and `resolved` for checks/saves. It deliberately
does not narrate or apply gameplay changes; M2.3 owns that final stage and `DEBT-002` remains open.

### M2.3 — Outcome narration and atomic finalization

**Status: Done (2026-09-02).**

- introduce the narration/finalization contract with the immutable resolution in its input;
- validate bounded state proposals and commit them with final events atomically;
- prove narration matches success/failure and cannot establish an untyped mechanical effect;
- close `DEBT-002` when narration is produced only after resolution.

Exit: deterministic dialogue, movement, inventory, check, and bounded environmental-damage scenarios
complete with consistent narration and state.

Implemented evidence:

- a strict provider-neutral `TurnNarrationOutput` accepts narration, the exact acknowledged
  resolution/outcome, and only the existing bounded typed state proposals; extra fields, including
  attempted dice data, are rejected;
- `/turn-executions/{turn_id}/finalize` supplies the stored intent and immutable M1.4 resolution to
  narration only after interpretation/resolution has completed, closing `DEBT-002`;
- no database transaction remains open during narration; finalization then re-locks the campaign,
  selected actor, and current location and rejects a response generated against stale state;
- narration for a resolved check must echo the exact resolution ID and outcome. Contradictory
  acknowledgement becomes a recoverable narration failure without final events or state mutation;
- the application validates the complete proposal list before applying any part of it, then writes
  the provider audit, HP/inventory/location changes, `dm_response`, optional `state_changed`, and
  completed turn in one transaction;
- deterministic dialogue, movement, inventory use, successful climb, and failed-climb bounded
  environmental damage all complete with consistent state and ordered events. Prose that merely
  claims an HP change produces no mechanical effect;
- repeated finalization of a completed turn is idempotent and does not call the provider or append
  duplicate events;
- the first invalid-output fixture exposed a JSON-null-versus-SQL-NULL mismatch in failed
  provider-call audits. The constructor now leaves failed structured output unset, satisfying the
  database result-shape constraint; the regression passes;
- no schema migration was required beyond M2.1's `0006` storage;
- nine focused M2.3 tests and the full 69-test suite pass at 90% coverage, with lint, compilation,
  catalog validation, generated-schema freshness, zero Alembic drift, and no external or paid model
  calls.

M2.3 proves successful finalization and its immediate rejection boundaries. M2.4 now owns broader
provider exception normalization, resume/restart matrices, timeout/token observability, concurrency
hardening, and the ten consecutive deterministic Lantern scenarios.

### M2.4 — Failure, retry, observability, and restart hardening

**Status: Done (2026-09-02).**

- implement provider exception normalization, failed-stage metadata, safe resume, timeout handling,
  token/latency capture, stale-state rejection, and concurrency fixtures;
- run ten consecutive deterministic Lantern scenarios before enabling a live provider;
- verify migration drift, event ordering, audit immutability, and documentation freshness.

Exit: every injected failure preserves canonical gameplay state and every retry/resume is idempotent.

Implemented evidence:

- provider timeout, connection, refusal, empty-output, malformed-output, and generic failures map to
  stable safe codes rather than leaking provider exception text;
- recoverable 502 responses include the durable turn ID, failed stage, stable code, safe message,
  and resumability flag so a client can retain and resume the same command;
- the provider-neutral result envelope captures optional input/output token usage while the
  application measures nonnegative latency for every completed attempt; provider/model/prompt and
  immutable success/failure output remain auditable;
- migration `0007_turn_stage_recovery` adds a constrained `stage_started_at` lease. Fresh
  interpretation/resolution/narration stages reject competing recovery or provider calls, while an
  expired stage can return to its last safe checkpoint;
- interrupted interpretation returns to `received`; interrupted narration returns to
  `intent_ready` or `resolved`; interrupted resolution relinks an already committed M1.4 result or
  returns to `intent_ready`. Recovery after engine disposal reuses exact dice and records a hidden
  operational `turn_stage_recovered` event;
- provider failures and invalid proposals resume with incremented immutable attempt audits and no
  duplicate player-visible events. State changed outside the turn makes the stale command terminal
  instead of offering an unsafe retry;
- the ten consecutive offline Lantern scenarios completed in one two-character campaign, covering
  dialogue, movement, inventory use, successful and failed checks, bounded damage, character
  switching, saving throws, Advantage/Disadvantage behavior, and engine disposal/restart. All ten
  turns completed with 20 successful provider audits, no actor leakage, valid HP/inventory/location,
  and the required event ordering;
- 80 tests pass at 90% total coverage. Formatting, lint, compilation, ruleset/catalog integrity,
  generated-schema freshness, migration application, and zero Alembic drift pass; no external or
  paid model call was made.

M2.4 completes deterministic hardening. The two-stage OpenAI adapter remains deliberately disabled.
The owner does not authorize additional API spend, so M2.5 is split into a no-cost manual evaluation
and a separately gated automated-provider evaluation.

### M2.5A — No-cost subscription-assisted Lantern evaluation

**Status: Ready; owner settings accepted 2026-09-02.**

- export the exact typed interpretation or narration request as a human-transferable evaluation
  package with prompt-contract version, canonical context, schema, and correlation identifiers;
- have the owner submit each package to this Codex/ChatGPT conversation and save the returned JSON;
- import the response through an explicit evaluation-only boundary that applies the same schema,
  acknowledgement, validator, resolver, audit, resume, and atomic-finalization rules as a provider;
- run ten consecutive two-character Lantern scenarios covering dialogue, movement, inventory use,
  check, bounded damage, character switching, restart, resume, and narration/outcome agreement;
- categorize every failure and rework before acceptance.

Accepted evaluation settings:

- classic heroic fantasy;
- non-graphic violence and no explicit sexual content;
- respect player agency and never infer an irreversible major player decision;
- a failed minor climb proposes fixed 2 HP environmental harm only when at least 1 HP remains;
- at insufficient HP, use a lost-position/time narrative setback with no HP change;
- no combat, conditions, unconsciousness, death, or recovery mechanics.

The deterministic reference fixture now enforces the 1 HP floor, including a regression proving
that a character at 2 HP receives the narrative fallback rather than being reduced to 0 HP.

Exit: all ten consecutive model-authored runs complete without impossible state, invented
dice/modifiers, partial gameplay commits, actor leakage, rerolls on retry, or contradictory resume
narration. Record the manual-transfer procedure and distinguish human transfer errors from model,
schema, rules, or application failures.

This evaluation can establish narrative quality, typed-output compliance, outcome acknowledgement,
state safety, and restart/resume behavior with real model-authored responses. It cannot establish
API authentication, SDK compatibility, network timeout behavior, provider latency, token accounting,
rate-limit behavior, or unattended play.

### M2.5B — Optional automated-provider Lantern evaluation

**Status: Deferred; not authorized.**

- select and verify a supported provider/model only at implementation time;
- require a separately authenticated provider API; a ChatGPT/Codex or Claude subscription is not
  treated as an application credential;
- agree on a strict request/cost cap before any live call;
- implement provider-specific deadline, connection, refusal, empty-output, and usage mapping;
- rerun the same ten scenarios without manual transfer.

Exit: all M2.5A guarantees pass through the real network/provider path and the operational gaps
listed above have direct evidence.

## 5. Automated verification matrix

| Area | Required evidence |
| --- | --- |
| Lifecycle | legal transitions only; terminal turns cannot resume; one active turn per campaign |
| Idempotency | identical repeat returns same turn/resolution; changed command returns 409 |
| Actor isolation | two contrasting characters derive different canonical modifiers without leakage |
| Resolution | normal, Advantage, Disadvantage, cancellation, success, failure, and rejection |
| Provider failure | interpretation and narration timeout/refusal/malformed-output fixtures |
| Atomicity | rejected finalization changes no character, inventory, resource, location, or final events |
| Restart | resume before resolution and after resolution; post-resolution resume reuses exact dice |
| Concurrency | stale pre-state and competing active turn are rejected deterministically |
| Audit | provider/model/prompt version/attempt/latency/tokens/error recorded without credentials |
| Narration | structured outcome supplied; narration cannot invent a different roll or untyped mechanic |
| Migration | legacy backfill, full-chain upgrade, guarded downgrade, and zero Alembic drift |
| Regression | all M0/M1 ruleset, creation, party, provenance, validation, and resolution tests remain green |

## 6. Owner decision record and future gate

The owner decided on 2026-09-02:

1. do not incur separate model API charges while subscription-assisted evaluation can provide useful
   evidence;
2. use the classic heroic-fantasy, non-graphic, player-agency-preserving profile above;
3. keep the M2 damage fixture as non-lethal bounded environmental harm rather than combat.

No further input is required before M2.5A implementation. M2.5B requires a new owner decision on
provider, authorization, and maximum spend; a consumer subscription does not satisfy that gate.

## 7. Explicit non-goals

- combat initiative, attacks, damage dice, conditions, death, rests, or encounter balance;
- persistent NPC/quest/faction/world-consequence models (M3);
- semantic memory or pgvector (M4);
- broader character content or spellcasting (M1.5/future slices);
- companion autonomy or lone-hero compensation;
- frontend usability work (M7);
- Redis, Celery, Docker, background workers, or deployment infrastructure;
- any Clawvis change or integration.

## 8. Completion and rework rule

M2 is not Done on deterministic tests alone. It reaches Verification after M2.1–M2.4. M2.5A may
close the model-authored content-and-rules feasibility portion when ten consecutive manual runs
pass, while the automated-provider claim remains explicitly open as `TEST-001`/`GAP-005`. M2 may be
closed only with wording that does not claim unattended provider feasibility; otherwise it remains
in Verification until M2.5B. A model or provider failure is evidence to classify and fix, not
permission to weaken deterministic state, retry, or audit guarantees.
