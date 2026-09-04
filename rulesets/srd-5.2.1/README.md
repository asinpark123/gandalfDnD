# SRD 5.2.1 Ruleset Package

This directory describes GandalfDnD's immutable `srd-5.2.1` ruleset release. The authoritative
source document is not committed to ordinary Git history.

## Source artifact

- Official landing page: https://www.dndbeyond.com/srd
- Official PDF: https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf
- Published: 2025-05-01 according to the official landing page
- Size: 6,031,375 bytes
- SHA-256: `8974902d109d6e63672d7c490bde9ccf052410503d9cfa768237154fbc5e3d87`
- License and required attribution: [ATTRIBUTION.md](ATTRIBUTION.md)

Run the verified fetch command from the repository root:

```bash
python -m scripts.fetch_ruleset --release srd-5.2.1
```

The command downloads to the ignored `.cache/rulesets/srd-5.2.1/` directory, streams the bytes to a
temporary file, verifies both size and SHA-256, and only then atomically installs the cached PDF. An
existing cache entry that fails verification is reported and never silently overwritten.

Use `--source official` or `--source project_release` to select a particular manifest source.

## Normalized data catalogs

The unchanged source artifact and Gandalf's normalized machine-readable data have separate immutable
identities. The release currently registers:

- `srd-5.2.1-foundation-v1` — the M1.1 identity-only foundation, SHA-256
  `f2014945cb0b81a6dd192e0a6c1e02fb136ba4d4734d35a8160f9e3e5e7a3893`;
- `srd-5.2.1-character-creation-v1` — the M1.2 source-cited Human/Soldier/Fighter creation catalog,
  SHA-256 `ddbd172feeeb191789f1b95f93762c661dda06888dad067e28c7fc6ffda391cb`;
- `srd-5.2.1-party-state-v1` — the M1.3 Party Commander character-state catalog, SHA-256
  `aba4fcdbffb037eece88c862c76be988ffc60808b46361cc9a9dda0730fe763b`;
- `srd-5.2.1-check-save-resolution-v1` — the M1.4 ability-check and saving-throw catalog, SHA-256
  `09d2b0a963a5fba5c28a0a018b8114bcad25dd65717efcf5e1b791cc4f751448`;
- `srd-5.2.1-combat-v1` — the M5.1 core-combat catalog, SHA-256
  `423b80e84593738d4cadc5537278d208a51fbebacbb074a2d79531f0ee023204`.

New campaigns default to the Party Commander state catalog. Supplemental check/save and combat
catalogs extend an exact base catalog checksum; they do not replace campaign pins or silently
change prior catalog identities. Pre-existing legacy records stay pinned to the foundation catalog.

The M1.2 catalog includes the supported ability, skill, language, Human, Soldier, Fighter, feat,
Fighting Style, weapon-mastery, and fixed-equipment definitions plus beginner descriptions and
durable printed-page citations. It intentionally excludes unsupported character options; clients
must use the catalog rather than infer additional support from the PDF or submit free-form rules
content. Current product boundaries are recorded in `docs/rules/RULINGS.md`.

The M5.1 combat catalog contains the deliberately narrow Fighter/Goblin rules data and pure-kernel
provenance described in `docs/M5_1_COMBAT_CATALOG_KERNEL.md`. Its registry presence does not make a
combat API available and does not add a database catalog row; M5.2 owns that guarded migration and
persistence boundary.

Regenerate or check the JSON Schemas with:

```bash
python -m scripts.export_ruleset_schemas
python -m scripts.export_ruleset_schemas --check
```
