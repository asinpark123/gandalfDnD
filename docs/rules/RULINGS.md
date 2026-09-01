# Rules and Product-Rulings Register

- **Status:** Active
- **Rules baseline:** SRD 5.2.1
- **Owner:** GandalfDnD project

This register records every implementation interpretation, product policy, and house rule that can
change legal choices, mechanical outcomes, or persistent narrative consequences. It prevents a
reasonable implementation choice from being silently presented as official SRD text.

## Classification

| Classification | Meaning |
| --- | --- |
| SRD rule | Directly encoded from a durable citation in the selected immutable release |
| Implementation interpretation | Deterministic translation required where natural language does not map uniquely to software |
| Product policy | Supported content, default, UI, or campaign-setup choice that does not rewrite the underlying SRD |
| House rule | Gandalf-specific mechanical behavior that differs from or adds to the selected SRD |
| Adjudication | Explicit campaign/GM resolution for an intentionally open-ended situation |

Statuses are `Proposed`, `Accepted`, `Deferred`, `Superseded`, and `Rejected`. An accepted ruling
that changes mechanics must identify the applicable ruleset/house-rule release and regression tests
before shipping.

## Accepted rulings and policies

| ID | Classification | Decision and rationale | Scope | Required evidence |
| --- | --- | --- | --- | --- |
| RUL-001 | Product policy | Every initial M1 character uses the complete level-one Human/Soldier/Fighter path and standard array. M1.2 proved one character; M1.3 reuses the same content slice for multiple Party Commander characters. Content breadth remains deferred so party state and deterministic mechanics are proven end to end first. | M1.2–M1.4 | GF-001–GF-004; GF-015 |
| RUL-002 | Product policy | Standard array is the only M1 ability-generation method. This does not classify point buy or random generation as non-SRD; their product support is deferred. | M1 | Valid/invalid assignment tests |
| RUL-003 | Product policy | Alignment may guide bounded narration but never supplies an unstated mechanical modifier. | All releases | Narrative context and mechanical-write rejection tests |
| RUL-004 | Implementation interpretation | Contextual checks carry an explicit ability and optional skill/tool selection. Skills are not globally hard-locked to one ability. | D20 resolver | Typed check contract and fixtures |
| RUL-005 | Product architecture | Narrative text may describe, request, or react to mechanics but may not establish mechanics. Only validated rules events change mechanical state. | Entire application | GF-012 and provider/domain tests |
| RUL-006 | Product policy | Strict SRD behavior is implemented and measured before solo compensation. No feature silently gains self-targeting or an automatic companion. | Rules baseline and balance harness | Strict-SRD fixtures before any house-rule comparison |
| RUL-007 | Product policy | Character milestones and signature moments are narrative-only by default. SRD XP is the normative advancement track until a separate milestone-levelling house-rule package is approved. | Advancement/narrative state | Advancement and house-rule package tests |
| RUL-008 | Product architecture | A future rules release coexists immutably. Campaign conversion is explicit, validated, transactional, recorded, and never a mutable update of old rule definitions. | M1.1 and migrations | GF-013–GF-014; future migration fixtures |
| RUL-009 | Product architecture | Common rule semantics begin as typed data and pure functions and are generalized only from proven repetition. Exceptional rules may use versioned specialized resolvers. | All rules implementation | Review at each abstraction addition |
| RUL-010 | Product policy | Gandalf mechanical additions—including ultimate abilities, numerical reputation effects, solo buffs, or milestone levelling—must be separately identified and versioned as house rules. | Future house rules | Package identity, UI label, source/rationale and golden tests |
| RUL-021 | Product policy | The M1.2 Human Origin-feat menu supports Alert and Skilled. Magic Initiate is a valid SRD option but is deferred until spellcasting exists; Savage Attacker is already granted by Soldier and cannot be selected a second time in this slice. Source: SRD 5.2.1 Human p. 86, Soldier p. 83, feats pp. 87–88. | `srd-5.2.1-character-creation-v1` | Catalog-option, duplicate-grant, and finalization tests |
| RUL-022 | Product policy | Skilled initially grants three distinct supported skills. The SRD also permits tool choices, but arbitrary tool selection is deferred until tool definitions and their gameplay semantics are implemented. Source: SRD 5.2.1 Skilled, p. 87. | `srd-5.2.1-character-creation-v1` | Skilled cardinality, overlap, and unsupported-choice tests |
| RUL-023 | Product policy | M1.2 supports only Soldier equipment option A plus Fighter equipment option A. Fighter weapon-mastery choices are restricted to the three weapon definitions supplied by that fixed route: Javelin, Flail, and Greatsword. Other valid SRD packages and mastery choices are deferred, not reclassified as illegal. Source: SRD 5.2.1 Fighter pp. 47–48, Soldier p. 83, weapons/equipment pp. 91–97. | `srd-5.2.1-character-creation-v1` | Exact route, three-unique-masteries, inventory, and unsupported-option tests |
| RUL-024 | Product architecture | A normalized catalog is immutable and separately identified from its source release. New campaigns use the release's explicit default catalog; existing records retain their prior catalog until an explicit compatibility workflow converts them. | M1.2 onward | Hash/identity validation, migration backfill, pin immutability, and coexistence tests |
| RUL-025 | Product architecture | Solo-player modes are delivered in the order Party Commander, Protagonist with Companions, then Lone Hero. Party Commander directly controls every player character and establishes ordinary party mechanics. Delegated companion decisions later reuse the same deterministic engine. Lone-hero balance is designed last from measured baselines, and any compensation is an explicit house rule. | M1.3 onward | GF-015; party combat/world fixtures; companion equivalence/override tests; later strict-versus-house-rule solo benchmarks |
| RUL-026 | SRD rule | Alert grants proficiency in Initiative. The M1.3 golden Fighter therefore has initiative +4: Dexterity modifier +2 plus level-one PB +2. This corrects the earlier +2 fixture expectation, which omitted the selected feat; it is not a house rule. Source: SRD 5.2.1 Alert p. 87 and initiative/skill proficiency rules pp. 22–23. | `srd-5.2.1-party-state-v1` | GF-003 derived-state and provenance fixture |
| RUL-027 | Implementation interpretation | In the M1.3 loadout API, `held` means equipped/readied for mechanical use and consumes the weapon's required hands; `carried` includes an item merely being transported or physically handled without being readied. This preserves the Greatsword's Two-Handed attack requirement without claiming it is impossible to touch or carry one-handed. | `srd-5.2.1-party-state-v1` | Loadout hand-limit and equipment-position fixtures |
| RUL-028 | SRD rule | Human Resourceful supplies Heroic Inspiration when a day starts; a Long Rest is not encoded as the trigger. M1.3 therefore initializes one Heroic Inspiration but records no Short- or Long-Rest recovery. A future day-transition command must implement the cited timing explicitly. Source: SRD 5.2.1 playing rules p. 8 and Human p. 86. | `srd-5.2.1-party-state-v1` | Catalog recovery and derived-resource fixture |
| RUL-029 | SRD rule | Ability checks and saving throws succeed when the modified d20 total equals or exceeds the DC. The natural-20 hit and natural-1 miss exceptions are stated for attack rolls, so they are not applied to checks or saves. Source: SRD 5.2.1 D20 Tests pp. 6–7. | `srd-5.2.1-check-save-resolution-v1` | Natural 1 plus sufficient modifier succeeds; natural 20 plus insufficient modifier fails |
| RUL-030 | Implementation interpretation | A resolution command may carry explicit Advantage/Disadvantage reasons only as already-adjudicated application/GM context; it may never carry a numeric modifier. The resolver combines those reasons with rules-derived sources, rolls two d20s for either state, and cancels any mixture of Advantage and Disadvantage to one d20. Worn Chain Mail automatically supplies Disadvantage only to Dexterity (Stealth), not every contextual use of Stealth. Source: SRD 5.2.1 Advantage/Disadvantage pp. 7–8 and armor/equipment pp. 91–92. | `srd-5.2.1-check-save-resolution-v1` | Automatic-source, multiple-source, cancellation, contextual-ability, and extra-modifier rejection fixtures |
| RUL-031 | Product architecture | A turn interpreter may adjudicate whether a check/save is needed and supply its type, ability, optional skill, DC, purpose, and explicit Advantage/Disadvantage reasons, but it may never supply a modifier or dice result. The application validates that request, owns ruleset/catalog pins, and invokes M1.4. Legacy provider dice requests are rejected before any write. The deterministic phrase mappings are development fixtures, not universal D&D adjudication rules. | M2.2 onward | Typed extra-field rejection, actor-specific check/save, exact-dice retry, unknown-skill pre-roll rejection, stale-state, and legacy no-mutation fixtures |

## Open and deferred rulings

| ID | Status | Issue | SRD/design boundary | Decision required before |
| --- | --- | --- | --- | --- |
| RUL-011 | Deferred | Point buy and random ability generation | Valid SRD methods but outside the first supported slice | Expanding character creation beyond M1 |
| RUL-012 | Deferred | Custom backgrounds | Official SRD customization, not inherently a house rule | Enabling background creation/customization |
| RUL-013 | Deferred | Exact companion autonomy and player-override policy | Companion presence is accepted after Party Commander, but delegation granularity, personality influence, consent, and override timing still affect agency and action economy | Scoping Protagonist with Companions after Party Commander combat is proven |
| RUL-014 | Proposed | Default-world firearms | Rules content availability is separate from whether a campaign setting exposes it | Equipment/world content expansion |
| RUL-015 | Proposed | Improvised-action DC/ability/skill selection | The SRD intentionally requires GM adjudication | M2/M3 improvised-action support |
| RUL-016 | Proposed | Narrative and mechanical curses | Descriptive curses may be narrative; active mechanics require versioned effects | Curse feature implementation |
| RUL-017 | Proposed | Paladin oath violation workflow | Persistent violation calls for adjudication rather than automatic reclassification | Paladin/subclass support |
| RUL-018 | Proposed | Resource maximum increasing mid-day | No safe universal semantic for every PB/ability-scaled resource was established | A supporting resource can change maximum during play |
| RUL-019 | Proposed | External non-SRD creature/content sources | Additional content requires lawful provenance and compatibility identity | Druid/monster content outside bundled SRD definitions |
| RUL-020 | Deferred | Post-level-20 optional feats | Optional official allowance, not mandatory progression | Level 20+ support |

## Ruling template

```text
ID:
Date:
Status:
Classification:
Ruleset/house-rule release:
Issue and triggering scenario:
Official source and page:
What the source establishes:
Decision:
Rationale and rejected alternatives:
State/schema/API impact:
Migration/compatibility impact:
Required fixtures:
Player-facing explanation:
Revisit condition:
```

## Change log

| Date | Change |
| --- | --- |
| 2026-08-30 | Created the register from the accepted RES-001 review; recorded M1 scope and foundational boundaries while preserving unresolved policies as open/deferred. |
| 2026-08-31 | Recorded the accepted M1.2 feat, Skilled, equipment/mastery, and immutable data-catalog support policies with source pages and regression requirements. |
| 2026-08-31 | Accepted party-mode sequencing in RUL-025, revised the M1 content slice to support multiple Party Commander characters, and narrowed RUL-013 to the later unresolved companion-autonomy policy. |
| 2026-08-31 | Recorded the source-backed Alert initiative correction plus explicit loadout/readiness and Resourceful timing semantics in RUL-026–RUL-028 after M1.3 catalog verification. |
| 2026-09-01 | Recorded M1.4 check/save DC semantics, natural-one/twenty boundaries, and the adjudicated-versus-rules-derived Advantage/Disadvantage contract in RUL-029–RUL-030. |
| 2026-09-02 | Recorded M2.2's typed interpretation boundary, application-owned resolution inputs, legacy dice-request rejection, and deterministic-fixture limitation in RUL-031. |
