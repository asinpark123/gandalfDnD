# Beginner Game Setup Guide

- **Status:** Living guide; some choices are planned and are not yet exposed by the API or a user
  interface
- **Last updated:** 2026-09-02
- **Current playable foundation:** Party Commander with two to four level-one
  Human/Soldier/Fighters

This guide explains the campaign choices GandalfDnD will present during setup. It also records the
settings used during development tests so a test result can be reproduced without mistaking a
temporary fixture for a universal D&D rule.

## 1. Choose a party mode

GandalfDnD is being built party-first:

1. **Party Commander** — you directly choose the actions for every character. This is the current
   mode and the recommended starting point because it most closely preserves ordinary party play.
2. **Protagonist with Companions** — you directly control a main character while the game proposes
   companion actions that remain subject to the same deterministic rules and player-override
   policy. This is planned after Party Commander combat works.
3. **Lone Hero** — you control one character. Any balance assistance will be optional, visible, and
   versioned as a house rule. This is planned last so it can be measured against a proven party
   baseline.

Beginner tip: start with Party Commander and two characters. It provides complementary strengths
without asking a new player to manage the maximum party size immediately.

## 2. Choose a narrative profile

A narrative profile guides descriptions, pacing, themes, and the kinds of complications the DM may
offer. It does not grant modifiers, change dice, or override canonical state.

| Profile | What to expect | Good fit for |
| --- | --- | --- |
| **Classic heroic fantasy** | Clear adventure, danger, courage, discovery, and hopeful momentum | A first campaign and the M2.5 evaluation |
| Lighthearted adventure | More humour, warmth, and forgiving narrative complications | Casual or family-style play |
| Mystery and intrigue | Clues, social uncertainty, investigation, and slower reveals | Players who enjoy deduction and dialogue |
| Grounded low fantasy | Scarcer magic, practical concerns, and restrained spectacle | Grittier travel and political stories |
| Epic high fantasy | Large threats, overt magic, mythic imagery, and higher narrative stakes | Cinematic campaigns |
| Dark fantasy | Bleaker atmosphere, horror themes, moral pressure, and costly choices | Experienced players who explicitly opt in |

Profiles are composable guidance rather than different rulesets. Future setup may let a player add
a short custom tone note while retaining safety and mechanics boundaries.

## 3. Choose content boundaries

The intended controls are independent so a player can tune them without changing the ruleset:

- violence detail: implied, non-graphic, or graphic;
- horror intensity: off, mild, moderate, or strong;
- romance: off, permitted, or fade-to-black;
- theme exclusions: player-supplied topics that must not appear;
- player agency: the DM never invents an irreversible major decision for a player character;
- safety override: a player can stop or redirect an uncomfortable scene without an in-world
  penalty.

The current M2.5 evaluation profile is **classic heroic fantasy, non-graphic violence, no explicit
sexual content, respect player agency, and no inferred irreversible major player decisions**.

## 4. Choose environmental-consequence severity

Environmental consequences cover hazards such as a failed climb. They are separate from combat,
which is not implemented yet.

| Setting | Mechanical effect | Status |
| --- | --- | --- |
| Narrative only | Lost position, time, opportunity, or a new complication; no HP loss | Supported as a bounded narration result |
| **Non-lethal minor harm** | A fixed small HP loss only when it leaves at least 1 HP; otherwise use a narrative setback | Current M2.5 test fixture |
| Rules-driven hazard damage | Application-owned damage dice and typed hazard definitions | Planned after the necessary resolver exists |
| Lethal environmental danger | May cause unconsciousness or death under explicit rules | Deferred until combat, conditions, death, and recovery exist |

For the M2.5 test, a failed minor climb costs **2 HP** only when the acting character will retain at
least **1 HP**. If the character has insufficient HP, the result is lost position/time with no HP
change. This is a Gandalf test policy, not a rule attributed to SRD 5.2.1.

## 5. Understand rulesets versus setup profiles

A ruleset determines mechanics and legal content. A setup profile determines presentation and
campaign preferences. GandalfDnD keeps those concepts separate:

- `srd-5.2.1` is the current immutable rules baseline;
- future rules releases will coexist rather than silently overwrite existing campaigns;
- tone and content settings never change a die result or mechanical modifier;
- a mechanical departure from the selected ruleset must be labelled and versioned as a house rule.

## 6. Current limitation

The API and frontend do not yet expose these setup selectors. The accepted M2.5 values are currently
development/evaluation policy. When campaign setup is implemented, this guide must be updated with
the exact fields, defaults, validation errors, and interface steps before ordinary-player testing.
