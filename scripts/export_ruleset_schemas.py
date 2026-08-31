#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from app.character_creation import CharacterCreationCatalog
from app.character_state import CharacterStateCatalog
from app.rulesets import NormalizedDataIndex, RegistryDocument, RulesetManifest

REPOSITORY_ROOT = Path(__file__).parents[1]
SCHEMAS = {
    REPOSITORY_ROOT / "rulesets/schema/registry.schema.json": RegistryDocument,
    REPOSITORY_ROOT / "rulesets/srd-5.2.1/schema/manifest.schema.json": RulesetManifest,
    REPOSITORY_ROOT / "rulesets/srd-5.2.1/schema/data-index.schema.json": NormalizedDataIndex,
    REPOSITORY_ROOT
    / "rulesets/srd-5.2.1/schema/character-creation.schema.json": CharacterCreationCatalog,
    REPOSITORY_ROOT
    / "rulesets/srd-5.2.1/schema/character-state.schema.json": CharacterStateCatalog,
}


def _render_schema(model: type) -> str:
    return json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic ruleset JSON Schemas")
    parser.add_argument("--check", action="store_true", help="fail if checked-in schemas are stale")
    args = parser.parse_args()

    stale: list[Path] = []
    for path, model in SCHEMAS.items():
        rendered = _render_schema(model)
        if args.check:
            if not path.exists() or path.read_text() != rendered:
                stale.append(path.relative_to(REPOSITORY_ROOT))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)

    if stale:
        parser.error("stale schemas: " + ", ".join(str(path) for path in stale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
