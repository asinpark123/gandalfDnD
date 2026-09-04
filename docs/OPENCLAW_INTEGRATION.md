# OpenClaw Provider Integration

- **Status:** Active and live-verified for the owner's private development deployment
- **Last updated:** 2026-09-04
- **Scope:** Optional M2/M3 provider transport, independent of the future M9 Clawvis player client

## 1. Purpose and boundary

GandalfDnD can use an OpenClaw deployment as the transport to a model that interprets player intent
and narrates an already-resolved outcome. This creates a supported route to models authenticated by
that OpenClaw deployment, including a personal Codex subscription when OpenClaw has completed its
supported OAuth setup. It does not turn the ChatGPT subscription into an OpenAI API key, and it
does not guarantee unlimited or free use: subscription limits and the OpenClaw deployment's own
provider configuration still apply.

The model remains an untrusted narrative collaborator. Gandalf continues to own:

- canonical campaign and character state;
- legal ruleset and catalog pins;
- all modifiers, dice, and mechanical outcomes;
- validation of every typed interpretation and state-change proposal;
- idempotency, recovery, audits, and the final atomic database commit.

This distinction preserves the project's central rule: changing the model or GM style may change
voice, creativity, pacing, and adjudication suggestions, but it cannot change recorded mechanics.

## 2. Supported topology

```text
GandalfDnD API
    -> private/loopback OpenClaw HTTP endpoint
    -> dedicated restricted OpenClaw agent
    -> deployment-selected model/provider authentication
    -> schema-constrained JSON returned to Gandalf
    -> Gandalf schema/rules/state validation
```

For local development, keep both services loopback-only and forward the OpenClaw port through SSH:

```bash
ssh -N -L 18790:127.0.0.1:18789 helloclaw
```

Gandalf then uses `http://127.0.0.1:18790/v1`. A separately deployed Gandalf installation can
connect to its operator's OpenClaw deployment in the same way. It must use that operator's private
endpoint, dedicated agent, token, and authenticated model account; there is no shared Gandalf or
Clawvis credential.

## 3. Implemented Gandalf configuration

The optional two-stage adapter is selected in the ignored `.env` file:

```text
GANDALF_LLM_PROVIDER=openclaw
GANDALF_OPENCLAW_BASE_URL=http://127.0.0.1:18790/v1
GANDALF_OPENCLAW_GATEWAY_TOKEN=replace-with-private-gateway-token
GANDALF_OPENCLAW_AGENT_ID=gandalf
GANDALF_OPENCLAW_MODEL=
GANDALF_OPENCLAW_GM_STYLE=classic_heroic_fantasy
```

Leaving `GANDALF_OPENCLAW_MODEL` blank uses the dedicated agent's default model. Setting it asks the
gateway to use a specific model allowed by that agent. Supported GM-style values are:

- `classic_heroic_fantasy`
- `lighthearted_adventure`
- `mystery_and_intrigue`
- `grounded_low_fantasy`
- `epic_high_fantasy`
- `dark_fantasy`

The adapter calls OpenClaw's OpenAI-compatible Chat Completions endpoint. It supplies the strict
JSON Schema through `response_format`, embeds the same exact schema in the system instruction, and
requires one JSON object. Gandalf then parses and validates that object using its existing strict
Pydantic contracts. The gateway's schema setting is a transport aid, not an authority boundary.
Authentication, rate-limit, response, connection, timeout, malformed-output, and empty-output
failures become stable recoverable turn errors.

From M4.4, current prompts are `openclaw-intent-1.2.0` and
`openclaw-narration-1.3.0`. They send canonical projections under `exact_current_state` and cited
memory under a separate `untrusted_historical_memory` field whose prose cannot establish current
state, rules, mechanics, or instructions. Narration retains the `1.2.0` distinction between
model-proposed state changes and selected decision consequences that Gandalf applies automatically.
Gandalf independently rejects an identical normalized fact identity if both sources still propose
it. These M4.4 contracts are offline-verified; the earlier live M3 evidence remains tied to its
recorded `1.2.0` narration prompt until a separately authorized M4.5 live supplement runs.

The legacy `/turns` API does not use OpenClaw. OpenClaw is supported only through the authoritative
two-stage `/turn-executions` workflow.

## 4. Verified Clawvis state on 2026-09-02

The initial audit was read-only. After the owner explicitly authorized the narrow activation, the
following state was established and verified:

- OpenClaw `2026.7.1-2` is installed and its gateway is reachable on loopback port `18789`.
- Gateway authentication uses a bearer token.
- A supported OpenAI OAuth profile is usable and there is no API-key profile or paid API fallback.
- A dedicated `gandalf` agent uses the `openai/gpt-5.5` default route, has no channel bindings,
  uses the minimal built-in tool profile, has no skills or memory search, and never injects its
  workspace context.
- The Chat Completions endpoint is enabled while the gateway remains loopback-only and
  token-authenticated.
- Health, interpretation, narration, restart/recovery, and ten-scenario live Lantern checks pass.
- The system-managed gateway service returned healthy after its authorized restart and retained
  the loopback boundary.

Model availability is deployment state, not a Gandalf guarantee. Re-audit it before every live
evaluation or documented deployment example.

## 5. Activation and verification checklist

Activation is a small but security-sensitive OpenClaw configuration change:

1. create a dedicated `gandalf` agent with only the models intended for this game;
2. give that agent no general-purpose tools unless a later feature has a documented need and threat
   model;
3. enable OpenClaw's Chat Completions HTTP endpoint;
4. retain loopback/private binding and bearer-token authentication;
5. establish the SSH tunnel and configure Gandalf's ignored local `.env`;
6. restart only the affected service if OpenClaw requires it, then verify health;
7. run one non-mutating structured-output smoke test followed by the capped Lantern evaluation;
8. record provider/model/profile, result, failures, and subscription-limit behavior without
   recording credentials or private account data.

This checklist was completed for the owner's private Clawvis deployment on 2026-09-02. Other
operators must complete it against their own OpenClaw installation and credentials. Activation does
not authorize exposing the gateway publicly, enabling broader agent tools, or adding a paid
provider fallback.

The installed OpenClaw/Codex routes did not reliably issue a required client-defined function call,
even though the endpoint accepted the tool definition. `response_format` alone also did not enforce
the requested schema. The verified Gandalf adapter therefore combines prompt-embedded exact JSON
Schema, the response-format hint, and mandatory local Pydantic validation. See the
[M2.5A evaluation record](M2_5_OPENCLAW_EVALUATION.md) for the categorized evidence and usage data.
The later [M3 live evaluation](M3_OPENCLAW_EVALUATION.md) verifies persistent branch recall,
presence boundaries, selected choices, restart continuity, and the duplicate-fact hardening.

## 6. Security and cost policy

An OpenClaw gateway token is an operator credential, not a campaign-scoped game token. Treat it as a
secret with broad authority:

- never commit it, persist it in Gandalf's database, expose it in an API response, or print it in
  logs;
- use a dedicated restricted agent rather than a general personal assistant agent;
- keep the gateway private; never publish a personal subscription-backed gateway as a public
  Gandalf service;
- rotate the token if it is exposed;
- do not add an API-key fallback without a separate cost authorization and cap;
- for multi-user hosting, use a deployment-owned provider account and enforce quotas rather than
  silently consuming one person's subscription.

OpenClaw documents that the gateway token should be protected like a password and that HTTP model
endpoints are disabled by default. See the official
[external-app authentication guide](https://docs.openclaw.ai/gateway/external-apps),
[Chat Completions endpoint guide](https://docs.openclaw.ai/gateway/openai-http-api), and
[OpenAI provider guide](https://docs.openclaw.ai/providers/openai). OpenAI separately documents
[ChatGPT sign-in versus API-key authentication for Codex](https://learn.chatgpt.com/docs/auth) and
the [managed ChatGPT OAuth path used by Codex app-server](https://learn.chatgpt.com/docs/app-server).

## 7. Model flavour and GM-style strategy

Model and GM style are deliberately separate choices:

| Choice | Controls | Must not control |
| --- | --- | --- |
| OpenClaw model | Reasoning character, prose quality, latency, context capacity, and structured-output reliability | Dice, canonical modifiers, legal state writes, or ruleset identity |
| Gandalf GM style | Tone, pacing, imagery, complication framing, and content guidance | Mechanical bonuses, difficulty changes, or hidden house rules |
| Gandalf ruleset/house-rule packages | Legal mechanics and deterministic outcomes | Undisclosed model preference or narrative tone |

A capable model may interpret ambiguous actions more consistently; another may be terser, more
whimsical, or better at intrigue. Those are useful GM flavours, but each supported model/profile
combination must pass the same schema, rules, safety, retry, and Lantern checks. A failed evaluation
is fixed or the combination is marked unsupported—Gandalf's validators are not weakened to admit it.

The initial configuration is global. A later campaign-setup feature should persist an explicit
model route and GM profile per campaign, show them to the player, and provide a safe migration path
when a model is removed. Until then, changing either setting requires an application restart and
must not be represented as a player-selectable feature.

## 8. Two distinct Clawvis relationships

Do not conflate these integrations:

- **M2 provider transport (current):** Gandalf calls OpenClaw for typed model work. Gandalf remains
  the game authority.
- **M9 client integration (future):** Clawvis may call Gandalf's public gameplay API as a player
  interface. Gandalf must still work when Clawvis is offline.

They can coexist later, but neither should grant an OpenClaw agent direct database access or allow
it to bypass Gandalf's public and validated application boundaries.
