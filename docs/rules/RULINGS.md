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
| RUL-001 | Product policy | M1 supports one complete level-one Human/Soldier/Fighter path using standard array. Breadth is deferred so the first rules slice can be proven end to end. | M1.2–M1.4 | GF-001–GF-004 |
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

## Open and deferred rulings

| ID | Status | Issue | SRD/design boundary | Decision required before |
| --- | --- | --- | --- | --- |
| RUL-011 | Deferred | Point buy and random ability generation | Valid SRD methods but outside the first supported slice | Expanding character creation beyond M1 |
| RUL-012 | Deferred | Custom backgrounds | Official SRD customization, not inherently a house rule | Enabling background creation/customization |
| RUL-013 | Proposed | Solo companions | Companion presence materially changes action economy and ally-dependent class features | Designing recurring companions or solo-balance policies |
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
