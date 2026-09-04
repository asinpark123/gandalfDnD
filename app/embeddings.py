"""Versioned embedding providers used by the rebuildable memory index."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


class EmbeddingError(RuntimeError):
    """Base error for safe memory-index failure classification."""


class InvalidEmbeddingError(EmbeddingError):
    """Raised when a provider returns an unusable vector."""


class EmbeddingModelUnavailableError(EmbeddingError):
    """Raised when a pinned local model is absent or fails integrity verification."""


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Small provider boundary shared by offline tests and local CPU inference."""

    profile_key: str
    provider_kind: str
    model_name: str
    model_revision: str
    artifact_sha256: str
    license_id: str
    dimensions: int
    normalization: str
    adapter_version: str

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


def validate_embedding(vector: list[float], *, dimensions: int) -> list[float]:
    if len(vector) != dimensions:
        raise InvalidEmbeddingError(
            f"embedding dimension mismatch: expected {dimensions}, received {len(vector)}"
        )
    converted = [float(value) for value in vector]
    if not all(math.isfinite(value) for value in converted):
        raise InvalidEmbeddingError("embedding contains a non-finite value")
    if not any(value != 0.0 for value in converted):
        raise InvalidEmbeddingError("embedding must not be the zero vector")
    return converted


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class DeterministicEmbeddingProvider:
    """Stable offline feature hashing; useful for lifecycle tests, not semantic quality."""

    dimensions: int = 64
    profile_key: str = "deterministic-hash-v1"
    provider_kind: str = "deterministic"
    model_name: str = "sha256-feature-hash"
    model_revision: str = "1"
    artifact_sha256: str = hashlib.sha256(
        b"gandalfdnd:sha256-feature-hash:token+bigrams:signed:l2:v1"
    ).hexdigest()
    license_id: str = "project-internal"
    normalization: str = "l2"
    adapter_version: str = "memory-embedding-1.0.0"

    def __post_init__(self) -> None:
        if not 1 <= self.dimensions <= 4096:
            raise ValueError("deterministic embedding dimensions must be between 1 and 4096")
        if self.profile_key == "deterministic-hash-v1" and self.dimensions != 64:
            object.__setattr__(self, "profile_key", f"deterministic-hash-v1-{self.dimensions}d")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        tokens = re.findall(r"[a-z0-9]+", text.casefold())
        features = tokens + [
            f"{left}::{right}" for left, right in zip(tokens, tokens[1:], strict=False)
        ]
        vector = [0.0] * self.dimensions
        for feature in features or ["<empty>"]:
            digest = hashlib.sha256(feature.encode("utf-8")).digest()
            index = int.from_bytes(digest[:8], "big") % self.dimensions
            sign = 1.0 if digest[8] & 1 else -1.0
            vector[index] += sign
        magnitude = math.sqrt(sum(value * value for value in vector))
        return validate_embedding(
            [value / magnitude for value in vector], dimensions=self.dimensions
        )


class LocalFastEmbedProvider:
    """Pinned, checksum-verified FastEmbed/ONNX CPU provider."""

    def __init__(
        self,
        model_dir: Path,
        *,
        manifest_path: Path = Path("resources/embedding_models/bge-small-en-v1.5.json"),
        threads: int = 2,
    ) -> None:
        self.model_dir = model_dir
        self.manifest_path = manifest_path
        self.threads = threads
        self._model: Any | None = None
        try:
            self._manifest = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise EmbeddingModelUnavailableError("embedding model manifest is unavailable") from exc
        profile = self._manifest["profile"]
        self.profile_key = profile["profile_key"]
        self.provider_kind = "local_onnx"
        self.model_name = profile["model_name"]
        self.model_revision = profile["model_revision"]
        self.artifact_sha256 = profile["artifact_sha256"]
        self.license_id = profile["license_id"]
        self.dimensions = profile["dimensions"]
        self.normalization = profile["normalization"]
        self.adapter_version = profile["adapter_version"]
        self._verify_artifacts()

    def _verify_artifacts(self) -> None:
        if not self.model_dir.is_dir():
            raise EmbeddingModelUnavailableError(
                f"local embedding model is absent at {self.model_dir}"
            )
        for record in self._manifest["artifacts"]:
            path = self.model_dir / record["path"]
            try:
                size = path.stat().st_size
                digest = _file_sha256(path)
            except OSError as exc:
                raise EmbeddingModelUnavailableError(
                    f"local embedding artifact is absent: {record['path']}"
                ) from exc
            if size != record["size_bytes"] or digest != record["sha256"]:
                raise EmbeddingModelUnavailableError(
                    f"local embedding artifact failed verification: {record['path']}"
                )

    def _load(self) -> Any:
        if self._model is None:
            try:
                from fastembed import TextEmbedding

                self._model = TextEmbedding(
                    "BAAI/bge-small-en-v1.5",
                    specific_model_path=str(self.model_dir),
                    local_files_only=True,
                    providers=["CPUExecutionProvider"],
                    threads=self.threads,
                )
            except (ImportError, OSError, RuntimeError, ValueError) as exc:
                raise EmbeddingModelUnavailableError(
                    "verified local embedding model could not be loaded"
                ) from exc
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        values = self._load().passage_embed(texts, batch_size=max(1, min(len(texts), 32)))
        return [validate_embedding(value.tolist(), dimensions=self.dimensions) for value in values]

    def embed_query(self, text: str) -> list[float]:
        values = list(self._load().query_embed([text], batch_size=1))
        if len(values) != 1:
            raise InvalidEmbeddingError("local embedding provider returned the wrong batch size")
        return validate_embedding(values[0].tolist(), dimensions=self.dimensions)

    def close(self) -> None:
        """Release the native ONNX session before interpreter teardown."""

        self._model = None
