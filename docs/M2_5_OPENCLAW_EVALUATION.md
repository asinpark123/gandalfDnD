# M2.5A OpenClaw Lantern Evaluation

- **Status:** Passed
- **Evaluation date:** 2026-09-02
- **Scope:** Private Clawvis/OpenClaw transport and ten-scenario two-stage turn gate
- **Credentials/personal data:** Intentionally omitted

## 1. Evaluated deployment

The owner authorized the narrow Clawvis change described in
[`OPENCLAW_INTEGRATION.md`](OPENCLAW_INTEGRATION.md). The resulting deployment used:

- OpenClaw `2026.7.1-2`;
- a loopback-only, bearer-authenticated gateway on Clawvis, reached through a local SSH tunnel;
- a dedicated `gandalf` agent with no channel bindings;
- the agent's OpenAI OAuth-backed `openai/gpt-5.5` default route, with no API-key fallback;
- the minimal built-in tool profile, no skills, no memory search, and no workspace context injection;
- low reasoning effort and Gandalf's `classic_heroic_fantasy` narration profile;
- `openclaw-intent-1.1.0` and `openclaw-narration-1.1.0` prompt contracts;
- the dedicated `gandalfdnd_test` PostgreSQL database only.

The gateway token was supplied ephemerally to the test process. It was not committed, written to
the database, copied into this document, or included in application output.

## 2. Compatibility finding and resolution

The installed gateway accepted OpenAI-style client function definitions and required-tool
selection, but the tested Codex routes did not reliably emit the required client function call.
The endpoint also accepted `response_format=json_schema`, but that field alone did not make the
returned content conform to an arbitrary schema.

The accepted transport contract therefore uses three layers:

1. send the strict JSON Schema in `response_format`;
2. include the same exact compact schema in the system instruction and require one JSON object;
3. parse and validate the returned object with Gandalf's existing Pydantic contract before any
   rules resolution or state commit.

This passed real interpretation and narration smoke calls. OpenClaw remains transport only;
Gandalf's validator and deterministic services remain authoritative.

## 3. Ten-scenario result

All three runs—the initial full-state run, compact-context rerun, and exact-final-prompt rerun—
completed the same sequence:

| # | Coverage | Result |
| --- | --- | --- |
| 1 | Dialogue/no-resolution turn | Passed |
| 2 | Location movement | Passed; one typed movement change |
| 3 | Inventory use | Passed; one actor-scoped inventory change |
| 4 | Ability check and movement consequence | Passed |
| 5 | Contrasting actor, failed check, bounded HP consequence | Passed |
| 6 | Actor switching and narrative-only turn | Passed |
| 7 | Saving throw across database-engine disposal | Passed |
| 8 | Check, injected narration timeout, engine disposal, resume | Passed; exact resolution and dice reused |
| 9 | Second actor inventory use | Passed; no cross-character mutation |
| 10 | Consecutive narrative turn | Passed |

Final assertions passed:

- 10 unique turns reached `completed`;
- 20 real OpenClaw calls succeeded, one interpretation and one narration call per turn;
- the one failed provider attempt was deliberately injected and was followed by a successful
  resume;
- every structured narration matched the stored resolution ID and outcome when a resolution
  existed;
- event ordering, actor attribution, no-reroll recovery, HP bounds, inventory non-negativity, and
  character isolation all held;
- no provider, authentication, schema, rules, application, or subscription-limit failure occurred.

## 4. Usage and latency evidence

The first passing run exposed avoidable context overhead because the complete provenance-heavy
character projection was sent on every call. Gandalf was changed to send a compact, mechanically
complete provider projection that omits timestamps and derivation provenance while retaining the
facts needed for interpretation and safe narration.

| Passing run | Input tokens | Output tokens | Average latency | Maximum latency |
| --- | ---: | ---: | ---: | ---: |
| Initial full-state context | 754,469 | 3,271 | 7,590 ms | 10,911 ms |
| Compact provider context | 419,727 | 3,130 | 7,753 ms | 10,065 ms |
| Final versioned prompts | 419,782 | 3,162 | 7,409 ms | 10,402 ms |

The compact projection reduced input usage by approximately **44.4%** with no behavioral
regression. The remaining overhead is still material and stays covered by `RISK-008`; later world
state and memory work must use explicit context and retrieval budgets rather than returning to
unbounded full-state injection.

## 5. Narrative-quality observation

The generated prose was coherent with the stored mechanical outcomes. Two repeated greeting
actions occurred after the party had moved away from the original inn; the model narrated the
greeting as carrying through the open air instead of rejecting the absent target. This did not
invent a mechanical effect and was correctly accepted under M2's minimal location model. It is
evidence for M3's planned structured NPC presence, scenes, and world-state validation—not an M2
deterministic-rules failure.

## 6. Acceptance decision

M2.5A passes. Together with M2.1–M2.4 evidence, this closes M2. The exact final prompt versions passed
the third complete run. The optional separately billed
direct-provider path remains deferred and is not required for M2 acceptance.

The final repository gate passed 96 normal tests with the opt-in live test correctly skipped, plus
formatting, lint, compilation, ruleset/catalog integrity, generated-schema freshness, zero Alembic
drift, and diff checks. The live test separately passed immediately beforehand against the dedicated
test database.
