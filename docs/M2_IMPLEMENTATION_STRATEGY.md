# M2 Two-Stage AI Turn Implementation Strategy

- **Status:** In Progress — M2.1 Done; M2.2 Ready
- **Prepared:** 2026-09-02
- **Depends on:** M1 Party character creation and deterministic mechanics (Done)
- **Owner input required now:** None
- **Paid external model calls:** Forbidden until the M2.5 owner gate is explicitly approved

## 1. Objective

M2 will replace the legacy one-stage turn with a resumable two-stage workflow in which the model may
interpret intent and narrate an already-recorded outcome, but cannot invent dice, supply mechanical
modifiers, directly write canonical state, or cause partial game-state changes when a provider call
fails.

The milestone proves live feasibility with the existing Human/Soldier/Fighter Party Commander
slice. It does not broaden character content, implement combat, or create the persistent world model.

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

- introduce the provider-neutral interpretation contract and deterministic fixtures;
- validate adjudicated check/save requests and route them through M1.4;
- remove the legacy model-supplied modifier/dice-request path from authoritative turns;
- close `DEBT-001` when every new turn roll uses the M1.4 resolver.

Exit: actor-specific checks/saves use canonical modifiers and exact recorded dice; retries cannot
reroll or change the command.

### M2.3 — Outcome narration and atomic finalization

- introduce the narration/finalization contract with the immutable resolution in its input;
- validate bounded state proposals and commit them with final events atomically;
- prove narration matches success/failure and cannot establish an untyped mechanical effect;
- close `DEBT-002` when narration is produced only after resolution.

Exit: deterministic dialogue, movement, inventory, check, and bounded environmental-damage scenarios
complete with consistent narration and state.

### M2.4 — Failure, retry, observability, and restart hardening

- implement provider exception normalization, failed-stage metadata, safe resume, timeout handling,
  token/latency capture, stale-state rejection, and concurrency fixtures;
- run ten consecutive deterministic Lantern scenarios before enabling a live provider;
- verify migration drift, event ordering, audit immutability, and documentation freshness.

Exit: every injected failure preserves canonical gameplay state and every retry/resume is idempotent.

### M2.5 — Owner-approved live Lantern evaluation

- select the configured OpenAI model at evaluation time;
- agree on a strict cost/request cap and narrative/content boundaries;
- run ten consecutive two-character Lantern scenarios covering dialogue, movement, inventory use,
  check, bounded damage, character switching, restart, resume, and narration/outcome agreement;
- categorize every failure and rework before acceptance.

Exit: all ten consecutive live runs complete without impossible state, invented dice/modifiers,
partial gameplay commits, actor leakage, rerolls on retry, or contradictory resume narration.

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

## 6. Owner decision gate

No owner input is needed for M2.1–M2.4. Before M2.5, request these decisions together:

1. authorization for paid live-model calls and an agreed cap;
2. desired narrative tone and content boundaries;
3. confirmation that M2's damage fixture remains bounded environmental harm rather than combat.

Recommended starting content profile: classic heroic fantasy, non-graphic violence, no explicit
sexual content, respect player agency, and never infer an irreversible major player decision. This
is a recommendation only until the owner accepts or changes it.

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

M2 is not Done on deterministic tests alone. It reaches Verification after M2.1–M2.4 and becomes
Done only after the explicitly authorized ten-run live gate passes. A provider failure is evidence
to classify and fix, not permission to weaken deterministic state, retry, or audit guarantees.
