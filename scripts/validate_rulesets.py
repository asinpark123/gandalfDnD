#!/usr/bin/env python3
import argparse
from pathlib import Path

from app.rulesets import RulesetRegistry


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the GandalfDnD ruleset registry")
    parser.add_argument("registry", nargs="?", type=Path, default=Path("rulesets/registry.json"))
    args = parser.parse_args()

    registry = RulesetRegistry.load(args.registry)
    for release_id in registry.release_ids:
        release = registry.get(release_id)
        print(
            f"{release_id}: manifest={release.manifest_sha256} "
            f"artifact={release.manifest.artifact.sha256} "
            f"status={release.manifest.normalized_data.support_status}"
        )
    print(f"Default release: {registry.default_release_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
