#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Literal, cast

from app.config import get_settings
from app.rulesets import RulesetRegistry, fetch_ruleset_artifact


def main() -> int:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Fetch and verify an immutable ruleset artifact")
    parser.add_argument("--release", default="srd-5.2.1", help="stable ruleset release ID")
    parser.add_argument(
        "--source",
        choices=("auto", "official", "project_release"),
        default="auto",
        help="artifact source from the versioned manifest",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=settings.ruleset_registry_path,
        help="path to rulesets/registry.json",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=settings.ruleset_cache_dir,
        help="ignored local artifact cache",
    )
    args = parser.parse_args()

    registry = RulesetRegistry.load(args.registry)
    release = registry.get(args.release)
    source = cast(Literal["auto", "official", "project_release"], args.source)
    path = fetch_ruleset_artifact(release, args.cache_dir, source=source)
    print(f"Verified {release.manifest.id}: {path}")
    print(f"SHA-256: {release.manifest.artifact.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
