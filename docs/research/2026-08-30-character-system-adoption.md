# RES-001 Character-System Research Review and Adoption Record

- **Review date:** 2026-08-30
- **Last traceability update:** 2026-09-04
- **Research source:** [RES-001 verbatim report](sources/2026-08-30-gandalfdnd-character-system-deep-research.md)
- **Decision:** Adopt the architectural recommendations with an intentionally narrower delivery
  sequence.
- **Implementation status:** This review is a decision record rather than implementation evidence.
  M1–M3 are now Done and M4 is Ready; the living project plan links their executable evidence.

## Why the research was commissioned

The project needed a durable analysis of SRD 5.2.1 character creation, progression, deterministic
mechanics, persistent narrative consequences, solo-play balance, and ruleset versioning before
expanding Phase 0's minimal name/HP/inventory character.

The report did not inspect the repository. Its schema and service proposals must therefore be
reconciled with the existing FastAPI, SQLAlchemy, Alembic, PostgreSQL, campaign-event, dice, and
provider boundaries before implementation.

## Adopt now

The following recommendations are accepted as project architecture:

1. Pin campaigns, characters, mechanical events, and rolls to immutable ruleset releases.
2. Preserve stable concept identities separately from version-specific rule definitions.
3. Record source provenance for character choices, grants, resources, and derived calculations.
4. Derive modifiers, maximums, and alternative base calculations from canonical source facts.
5. Treat recorded dice as input to deterministic resolution and preserve the RNG algorithm version.
6. Permit only validated rules commands/events to change mechanical state.
7. Keep narrative memories and world facts separate from mechanical effects.
8. Encode target predicates, resource recharge policies, character/class-level scaling, stacking,
   replacement, and precedence explicitly.
9. Implement strict SRD behavior before measuring or introducing solo-play compensation.
10. Put every Gandalf-specific mechanical addition in a labelled, versioned house-rule package.
11. Build permanent golden fixtures for critical rules interactions and replay compatibility.
12. Maintain an explicit rulings layer for areas the SRD delegates to GM adjudication.

## Adopt with modification

| Research recommendation | Gandalf decision | Reason |
| --- | --- | --- |
| Implement every legal SRD level-one identity early | M1 supports one complete vertical slice: level-one Human, Soldier background, Fighter, standard array. Broader options are deferred. | A complete narrow path gives earlier executable evidence and isolates defects. |
| Introduce the full proposed normalized PostgreSQL model | Add tables only as an accepted slice requires them while preserving the proposed identities and provenance boundaries. | Avoid speculative schema and migration burden. |
| Use a structured rule-operator vocabulary | Begin with typed data plus pure deterministic functions. Generalize repeated semantics into operators; use versioned specialized resolvers for genuinely bespoke rules. | Avoid a premature universal rules DSL. |
| Build a broad level-one spell engine as part of initial character work | Defer spellcasting until martial creation and check/save resolution are proven; then add it as a separate vertical slice. | Spell access, slots, free casts, concentration, components, and targeting form a distinct risk area. |
| Create numerous dedicated services immediately | Preserve service responsibilities as boundaries, but extract services only when the current slice needs them. | Maintain clarity without framework-first development. |

## Defer

- all twelve classes, all nine species, all supplied/custom backgrounds, and all Origin feats;
- spell preparation, slot pools, free-cast entitlements, concentration, and spell effects;
- advancement through levels 2–20, subclasses, feats, Epic Boons, and post-level-20 options;
- multiclass prerequisites and interactions;
- full combat, weapon mastery interaction coverage, rests, and conditions beyond current slice needs;
- solo-balance changes, companions, or self-targeting exceptions;
- numerical reputation, signature mechanical bonuses, and ultimate abilities;
- cross-ruleset migration execution beyond the M1.1 prevention and compatibility foundation.

Deferral means the design must not make these features impossible. It does not make them acceptance
criteria for M1.

## Do not adopt

- silent mutation of an active rule definition when errata or another SRD version appears;
- generated prose as an authority for HP, conditions, resources, items, proficiency, or any other
  mechanical state;
- hidden solo buffs presented as though they were SRD rules;
- independently editable derived statistics;
- exhaustive enumeration of every character combination as the primary test strategy;
- an arbitrary Python subclass for every feature or an over-general expression language forced onto
  every exceptional natural-language rule.

## Consequences for the delivery plan

- M1.1 remains **Ready** and is the immediate implementation target.
- M1 remains **Proposed** until its slices satisfy readiness and implementation gates.
- M1.2–M1.4 use the fixed Human/Soldier/Fighter/standard-array vertical slice.
- Ability checks and saving throws precede combat.
- M5 remains the first combat milestone and starts with the supported martial slice.
- Comprehensive character options and spellcasting are tracked as deferred expansion, not hidden
  requirements of the first playable proof.
- The rules specification and rulings register become required inputs to future rule changes.

## M4 traceability update

The adopted separation of narrative memory from mechanical effects is now concrete in the M4
strategy. Completed player-visible turns/events become source-cited, rebuildable memory documents;
embeddings, retrieval scores, and summaries remain derived and mechanically inert. Exact M3 state
is supplied separately, and campaign/audience/profile filters apply before ranking. The 500-event
gate, local versioned embedding policy, re-index behavior, and pgvector operator boundary are
recorded in `docs/M4_IMPLEMENTATION_STRATEGY.md` and
`docs/M4_POSTGRES_PGVECTOR_AUDIT.md`. This update records traceability, not completed M4 behavior.

## Research limitations and safeguards

- RES-001 is analysis, not a machine-readable SRD corpus or production schema.
- Its probability and solo-balance sections establish methods and benchmarks, not validated product
  balance results.
- Its temporary inline citation tokens are non-durable; implementations must cite official sources.
- Any rule translation that requires interpretation must produce a documented ruling and test.
- Repository code, migrations, runtime state, and executed tests remain the evidence for what works.
