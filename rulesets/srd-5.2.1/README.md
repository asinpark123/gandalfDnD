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

## Normalized data status

`data/index.json` is intentionally `foundation_only`: it establishes the release identity and data
schema but contains no extracted rule definitions yet. Character-creation definitions will be added
in M1.2 as deterministic, source-cited data. Unsupported content must not be inferred from the PDF
or accepted through free-form input.

Regenerate or check the JSON Schemas with:

```bash
python -m scripts.export_ruleset_schemas
python -m scripts.export_ruleset_schemas --check
```
