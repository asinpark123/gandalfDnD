# Guided Character Creation

GandalfDnD currently supports one complete, rules-valid level-one path: a Human with the Soldier
background and Fighter class, using the standard array. This deliberately narrow first slice lets
the game validate every required choice, explain it to a new player, and preserve why the character
has each ability or proficiency.

This is a supported-content boundary, not a claim that other SRD choices are invalid.

## What you can choose

- character name, Medium or Small size, and alignment;
- two different languages in addition to Common;
- where to place the standard-array scores `15, 14, 13, 12, 10, 8`;
- Soldier ability increases: either `+2/+1` or `+1/+1/+1`, using Strength, Dexterity, and
  Constitution;
- two Fighter skills, one extra Human skill, and any additional non-overlapping skills granted by
  the Skilled feat;
- one supported Human Origin feat: Alert or Skilled;
- one gaming set, one supported Fighting Style, and mastery of the three weapons in the supported
  starting package;
- the fixed Soldier A plus Fighter A starting-equipment route.

The options endpoint supplies the actual allowed identifiers and beginner descriptions. A client
should build its form from that response instead of hard-coding or accepting free-form rules data.

## Creation flow

1. Create a campaign with `POST /campaigns`.
2. Fetch `GET /rulesets/srd-5.2.1/character-creation/options`.
3. Create a name-only draft with `POST /campaigns/{campaign_id}/character`.
4. Submit all catalog-backed choices to
   `POST /campaigns/{campaign_id}/character/finalize`.
5. Read the saved sheet from `GET /campaigns/{campaign_id}/state` and its source-linked grants from
   `GET /campaigns/{campaign_id}/character/grants`.

A draft may be read, but gameplay turns are blocked until finalization. Finalization validates all
choices together and either commits the complete character or changes nothing. Once finalized, the
creation facts and grants cannot be edited directly; future changes require an explicit advancement,
correction, administrative, or ruleset-migration workflow.

The interactive API at `http://127.0.0.1:8000/docs` shows the exact request schema and current option
catalog.

## What the game calculates

The finalized sheet contains the base, background increase, final score, and modifier for every
ability; proficiency bonus; skill and saving-throw proficiencies; maximum/current HP; armor and
weapon training; Origin feat, Fighting Style, weapon masteries, class/species features, Second Wind
maximum uses, and starting inventory.

Each campaign, character, event, dice roll, and character grant is pinned to both the immutable SRD
release and the exact normalized data catalog used. The grants endpoint exposes the definition,
source definition, acquisition event, choice slot, and cited source IDs for audit or explanation.

## Current limitations

- M1.2 currently permits one character per campaign. M1.3 will introduce Party Commander so one
  human player can create and directly control multiple independently persisted party characters;
  Protagonist with Companions and Lone Hero modes follow later in that order.
- Other species, backgrounds, classes, ability-generation methods, equipment routes, and most feats
  are deferred until after the initial deterministic-mechanics milestone.
- Magic Initiate is deferred because the first slice has no spellcasting engine.
- Skilled currently supports skill selections only; tool selections are deferred.
- Combat execution, rests, levelling, shopping, and authoritative ability-check/save resolution are
  not part of M1.2.
- The current turn skeleton still accepts its Phase 0 dice modifier contract. M1.4 will replace that
  with modifiers derived authoritatively from the saved character and rules state.

## Rules source

The implementation is derived from the Creative Commons SRD 5.2.1 and uses durable page references
for D20 tests/skills, character creation, Fighter, Soldier, Human, feats, and equipment. The unchanged
source PDF, license, attribution, size, and checksum are described in
[`rulesets/srd-5.2.1/README.md`](../../rulesets/srd-5.2.1/README.md) and
[`rulesets/srd-5.2.1/ATTRIBUTION.md`](../../rulesets/srd-5.2.1/ATTRIBUTION.md).
