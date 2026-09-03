# M3 Live OpenClaw Evaluation

- **Status:** Passed after hardening
- **Evaluation date:** 2026-09-04
- **Scope:** Supplemental live-model verification of the completed M3 persistent-world milestone
- **Attempt ceiling authorized by owner:** 50 real provider attempts
- **Attempts used:** 25
- **Credentials recorded:** None

## 1. Outcome

The owner's private Clawvis/OpenClaw deployment successfully interpreted and narrated two complete
M3 campaign branches while Gandalf retained authority over identity, presence, choices, facts,
rules, and database writes. The corrected final run completed all 12 model calls, preserved each
branch across an engine restart, used the correct present guide, recalled the relevant earlier
outcome, and did not duplicate an automatically applied decision consequence.

This evaluation supplements rather than reopens M3. The deterministic and owner-guided M3 gates
were already complete. Its purpose was to test whether the live provider could consume and
narratively respect the richer persistent-world context under the same validators.

## 2. Evaluated deployment and safety boundary

- OpenClaw version: `2026.7.1-2`
- private gateway: loopback-only on Clawvis, reached through an SSH local port forward
- agent: dedicated `gandalf` agent with no channel bindings
- evaluated model route: `openai/gpt-5.5`
- Gandalf profile: `classic_heroic_fantasy`
- transport: OpenAI-compatible Chat Completions with exact JSON Schema plus local Pydantic checks
- SDK retries: disabled, so the recorded attempts are real model requests rather than hidden retries
- Clawvis changes during this evaluation: none

The gateway token was read only into the evaluation process environment. It was not printed,
committed, stored in Gandalf's database, or included in this evidence.

## 3. Scenario design

Each campaign first used the deterministic M3 Lantern fixture to establish canonical state through
real two-stage application boundaries. The campaigns then selected opposite persistent branches:

1. `signal_bridge`, where the patrol was rescued, followed by `light_beacon`;
2. `flooded_tunnel`, where the tunnel collapsed before the patrol was found, followed by
   `seal_cellar`.

The live provider performed three turns per branch, each with one interpretation and one narration:

1. recap the existing route and patrol-search consequence with the present guide;
2. narrate the player's explicit selection of a newly opened deterministic follow-up decision;
3. after disposing the database engine, explain what that follow-up choice means now.

An action targeting the absent caravan guard was also attempted in each campaign. Both requests
returned HTTP 409 with `world_target_not_present` before a provider call, proving the M3 presence
boundary still protects live-model usage.

## 4. Runs and usage evidence

| Run | Real attempts | Successful calls | Input tokens | Output tokens | Average latency | Maximum latency | Result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Harness diagnostic | 1 | Model returned valid output; recorder failed afterward | Not retained | Not retained | Not retained | Not retained | Test-only context-path defect; no canonical state committed |
| First complete run | 12 | 12 | 284,880 | 2,139 | 8,352 ms | 11,778 ms | Provider worked; exposed duplicate decision-fact proposal |
| Corrected complete run | 12 | 12 | 284,691 | 2,114 | 7,640 ms | 11,396 ms | Passed |
| **Total** | **25 / 50** | **24 complete audited calls plus one diagnostic response** | — | — | — | — | **Passed after hardening** |

The first diagnostic call received a valid provider response, but the evaluation recorder looked
for location data under the wrong context key and raised after the response. This was confined to
the new opt-in test harness. It made no canonical state change and was still counted against the
authorized ceiling.

## 5. Defect found and correction

The first complete run exposed `ISSUE-011`: on both decision turns, the narrator proposed the exact
same `DiscoveryRecord` already present in the selected option's deterministic consequences. The
application applied both because fact overlap validation previously covered NPC attitudes but not
an identical general fact identity. This produced duplicate canonical facts.

The correction has two independent layers:

1. OpenClaw narration prompt `openclaw-narration-1.2.0` explicitly says that selected-choice
   consequences are application-applied and must be acknowledged in prose but not repeated as
   state changes.
2. Finalization now compares normalized `(fact_type, subject_npc_id, value)` identities across
   narrator proposals and the selected decision consequences. An exact overlap returns a safe 422
   and atomically leaves the decision open and facts unchanged.

A deterministic regression proves the validator. The corrected live run then proved the model
followed the clarified contract: both follow-up consequence facts occurred exactly once. Distinct,
legal additions remained possible—the signal-bridge branch advanced time while lighting the
beacon and later stored a guide-attributed clue.

## 6. Corrected-run findings

- All 6 interpretations and all 6 narrations succeeded.
- Both recaps distinguished rescue from collapse and used only the relevant branch facts.
- Both decision narrations honored the exact selected option and its existing consequence.
- The same guide UUID remained selected and present; the absent NPC UUID remained outside context.
- The signal branch retained the rescue and beacon facts and finished at world revision 25.
- The flooded branch retained the collapse and sealed-cellar facts and finished at revision 23.
- Both post-choice turns worked after database-engine disposal.
- Each deterministic follow-up fact existed exactly once.
- No model output bypassed Gandalf's structured validation or deterministic application authority.

The narratives were coherent with the stored world. They did not confuse the two patrol outcomes,
move the party away from the Old Tower, substitute the absent guard, invent dice, or overwrite
mechanical state.

Post-correction repository gates also passed: 126 normal tests passed, the two explicitly opt-in
live suites skipped in the normal run, lint and formatting passed, Python compilation passed,
ruleset/catalog and generated-schema integrity passed, and Alembic reported zero drift for both
the development and isolated test databases. The one warning remains the already monitored
TestClient/httpx deprecation (`WARN-001`).

## 7. Reproduction and maintenance policy

The opt-in evaluation is `tests/test_openclaw_m3_live.py`. Normal test runs skip it. A future live
rerun must be explicitly authorized with a fresh attempt ceiling, use a private token supplied only
through the process environment, disable hidden SDK retries, and record provider/model/prompt
versions plus usage and categorized failures. Changing the model route or GM profile does not make
that combination supported until it passes the same boundaries.

No additional live M3 test is required for the evaluated configuration. Re-evaluate if the
OpenClaw transport, model route, provider projection, narration schema, selected-choice contract,
or relevant validators materially change.
