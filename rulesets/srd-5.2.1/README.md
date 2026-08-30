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
  SHA-256 `ddbd172feeeb191789f1b95f93762c661dda06888dad067e28c7fc6ffda391cb`.

New campaigns default to the character-creation catalog. Pre-existing records stay pinned to the
foundation catalog so adding normalized rules never changes old campaign semantics silently.

The M1.2 catalog includes the supported ability, skill, language, Human, Soldier, Fighter, feat,
Fighting Style, weapon-mastery, and fixed-equipment definitions plus beginner descriptions and
durable printed-page citations. It intentionally excludes unsupported character options; clients
must use the catalog rather than infer additional support from the PDF or submit free-form rules
content. Current product boundaries are recorded in `docs/rules/RULINGS.md`.

Regenerate or check the JSON Schemas with:

```bash
python -m scripts.export_ruleset_schemas
python -m scripts.export_ruleset_schemas --check
```
