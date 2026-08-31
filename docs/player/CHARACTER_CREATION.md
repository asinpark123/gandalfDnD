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

## Party Commander creation flow

1. Create a campaign with `POST /campaigns`.
2. Fetch `GET /rulesets/srd-5.2.1/character-creation/options`.
3. Create two to four name-only drafts with `POST /campaigns/{campaign_id}/characters`.
4. Submit each character's catalog-backed choices to
   `POST /campaigns/{campaign_id}/characters/{character_id}/finalize`.
5. Read the ordered party and calculated sheets from `GET /campaigns/{campaign_id}/state`; read one
   character's source-linked grants from
   `GET /campaigns/{campaign_id}/characters/{character_id}/grants`.
6. Optionally change worn/held equipment with
   `PUT /campaigns/{campaign_id}/characters/{character_id}/loadout`.
7. Once at least two active characters are finalized, submit a turn with that turn's
   `actor_character_id`. Draft characters cannot act.

A draft may be read, but it cannot act, and gameplay turns are blocked until at least two active
characters are finalized. Finalization validates all choices together and either commits the
complete character or changes nothing. Once finalized, the
creation facts and grants cannot be edited directly; future changes require an explicit advancement,
correction, administrative, or ruleset-migration workflow.

The interactive API at `http://127.0.0.1:8000/docs` shows the exact request schema and current option
catalog.

## What the game calculates

The finalized sheet contains the base, background increase, final score, and modifier for every
ability; proficiency bonus; every skill and saving-throw modifier; maximum/current HP; AC and its
eligible alternatives; initiative; passive Perception; Speed; Hit Die; carried, worn, and held
equipment; armor and weapon training; Origin feat, Fighting Style, weapon masteries, class/species
features; current/maximum Second Wind, Heroic Inspiration, and Hit Dice; and starting inventory.
Calculated values include their formula, rule definitions, source citations, acquisition events,
character revision, state revision, and resolver version.

In the loadout response, `held` means readied for mechanical use and consumes the weapon's required
hands; otherwise an owned item remains `carried`. Heroic Inspiration begins at one for the supported
Human but is not marked as Long-Rest recovery: Resourceful applies when a day starts.

Each campaign, character, event, dice roll, and character grant is pinned to both the immutable SRD
release and the exact normalized data catalog used. The grants endpoint exposes the definition,
source definition, acquisition event, choice slot, and cited source IDs for audit or explanation.

## Current limitations

- Party Commander currently requires at least two and supports at most four active characters. The
  human player directly controls all of them; Protagonist with Companions and Lone Hero modes follow
  later in that order.
- Other species, backgrounds, classes, ability-generation methods, equipment routes, and most feats
  are deferred until after the initial deterministic-mechanics milestone.
- Magic Initiate is deferred because the first slice has no spellcasting engine.
- Skilled currently supports skill selections only; tool selections are deferred.
- Combat execution, resource spending/recovery, rests, levelling, shopping, and authoritative
  ability-check/save resolution are not part of M1.3.
- The current turn skeleton still accepts its Phase 0 dice modifier contract. M1.4 will replace that
  with modifiers derived authoritatively from the saved character and rules state.

## Rules source

The implementation is derived from the Creative Commons SRD 5.2.1 and uses durable page references
for D20 tests/skills, character creation, Fighter, Soldier, Human, feats, and equipment. The unchanged
source PDF, license, attribution, size, and checksum are described in
[`rulesets/srd-5.2.1/README.md`](../../rulesets/srd-5.2.1/README.md) and
[`rulesets/srd-5.2.1/ATTRIBUTION.md`](../../rulesets/srd-5.2.1/ATTRIBUTION.md).
