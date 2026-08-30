# GandalfDnD Research Index

This directory is the durable index for research used to design, implement, test, or revise
GandalfDnD. Research is evidence and design input; it does not override implemented behavior, the
living project plan, an accepted Gandalf ruling, or the authoritative licensed rules source.

## Maintenance contract

For every research artifact added here:

1. Preserve the received source unchanged under `sources/` when licensing and privacy permit.
2. Record its date, provenance, integrity hash, review status, and relevant development scope.
3. Add a separate review when recommendations are adopted, modified, rejected, or deferred.
4. Replace or supplement temporary citation markers with durable source URLs and page references in
   the review or implementation specification.
5. Link any resulting decisions, risks, milestones, rules, fixtures, or implementation changes.
6. Never treat a research claim as implemented until code, migrations, and tests provide evidence.

Research sources are append-only historical evidence. Correct errors in a new review or superseding
artifact rather than silently rewriting the received source.

## Artifact index

| ID | Date | Title | Source and integrity | Review status | Development use |
| --- | --- | --- | --- | --- | --- |
| RES-001 | 2026-08-30 | GandalfDnD Character-System Research and Implementation Study for SRD 5.2.1 | [Verbatim Markdown source](sources/2026-08-30-gandalfdnd-character-system-deep-research.md), SHA-256 `eabfb9c01e49a51d9b062967e531211200a33d263928018ef2f00832c513a83c`; supplied by the project owner from a separate ChatGPT Deep Research session | [Reviewed and adopted with modifications](2026-08-30-character-system-adoption.md) | M1 rules foundation, character state, deterministic resolution, later combat/spell/advancement work, and solo-balance planning |

## Authority and citation note

The original RES-001 export contains Deep Research citation tokens such as `cite...`. Those
tokens are preserved because the file is a verbatim historical source, but they are not durable
repository citations. Normative implementation claims must cite the official SRD document and page
or another durable primary source. The principal official sources identified by RES-001 are:

- [System Reference Document landing page](https://www.dndbeyond.com/srd)
- [System Reference Document 5.2.1 PDF](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf)
- [Converting to SRD 5.2.1](https://media.dndbeyond.com/compendium-images/srd/guide/converting-to-srd-5.2.1.pdf)
- [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
