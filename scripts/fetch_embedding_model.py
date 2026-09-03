#!/usr/bin/env python3
"""Fetch the approved embedding artifact at its immutable revision and verify it."""

import argparse
import json
from pathlib import Path

from huggingface_hub import snapshot_download

from app.config import get_settings
from app.embeddings import LocalFastEmbedProvider

MANIFEST_PATH = Path("resources/embedding_models/bge-small-en-v1.5.json")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download and verify GandalfDnD's pinned local embedding model"
    )
    parser.add_argument("--destination", type=Path, default=get_settings().embedding_model_dir)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text())
    source = manifest["source"]
    snapshot_download(
        repo_id=source["onnx_repository"],
        revision=source["onnx_revision"],
        local_dir=args.destination,
        allow_patterns=[record["path"] for record in manifest["artifacts"]],
    )
    provider = LocalFastEmbedProvider(args.destination, manifest_path=MANIFEST_PATH)
    print(f"Verified {provider.profile_key} at {args.destination}")
    print(f"Model artifact SHA-256: {provider.artifact_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
