from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Callable, Iterator
from contextlib import closing
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import BinaryIO, Literal
from urllib.request import urlopen

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.config import get_settings

ReleaseId = str
Sha256 = str


class RulesetRegistryError(ValueError):
    pass


class UnknownRulesetError(RulesetRegistryError):
    pass


class ArtifactIntegrityError(RulesetRegistryError):
    pass


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RegistryEntry(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    manifest: str = Field(pattern=r"^[a-z0-9][a-z0-9./-]*\.json$")


class RegistryDocument(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["1.0.0"]
    default_release_id: str
    releases: list[RegistryEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_release_ids(self) -> RegistryDocument:
        release_ids = [release.id for release in self.releases]
        if len(release_ids) != len(set(release_ids)):
            raise ValueError("ruleset release IDs must be unique")
        if self.default_release_id not in release_ids:
            raise ValueError("default_release_id must identify a registered release")
        if any(release_id == "latest" for release_id in release_ids):
            raise ValueError("dynamic ruleset release ID 'latest' is forbidden")
        return self


class ArtifactSource(StrictModel):
    name: Literal["official", "project_release"]
    url: AnyHttpUrl


class ArtifactDefinition(StrictModel):
    filename: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    media_type: Literal["application/pdf"]
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(gt=0)
    sources: list[ArtifactSource] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_sources(self) -> ArtifactDefinition:
        names = [source.name for source in self.sources]
        if len(names) != len(set(names)):
            raise ValueError("artifact source names must be unique")
        if "official" not in names:
            raise ValueError("an official artifact source is required")
        return self


class LicenseDefinition(StrictModel):
    id: Literal["CC-BY-4.0"]
    name: str
    url: AnyHttpUrl
    attribution_file: str


class NormalizedDataDefinition(StrictModel):
    schema_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    index_path: str = Field(pattern=r"^[a-z0-9][a-z0-9./_-]*\.json$")
    support_status: Literal["foundation_only", "character_creation", "complete"]


class RulesetManifest(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["1.0.0"]
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    title: str
    version: str
    publication_date: date
    source_page: AnyHttpUrl
    license: LicenseDefinition
    artifact: ArtifactDefinition
    normalized_data: NormalizedDataDefinition

    @field_validator("id")
    @classmethod
    def reject_dynamic_id(cls, value: str) -> str:
        if value == "latest":
            raise ValueError("dynamic ruleset release ID 'latest' is forbidden")
        return value


class NormalizedDataIndex(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    ruleset_release_id: str
    support_status: Literal["foundation_only", "character_creation", "complete"]
    definition_files: list[str]


@dataclass(frozen=True)
class LoadedRulesetRelease:
    manifest: RulesetManifest
    manifest_path: Path
    manifest_sha256: Sha256
    data_index: NormalizedDataIndex


def _read_json(path: Path) -> tuple[dict, bytes]:
    try:
        raw = path.read_bytes()
        return json.loads(raw), raw
    except (OSError, json.JSONDecodeError) as exc:
        raise RulesetRegistryError(f"Could not read ruleset JSON: {path}") from exc


def _resolve_inside(root: Path, relative_path: str) -> Path:
    target = (root / relative_path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise RulesetRegistryError(f"Ruleset path escapes registry root: {relative_path}") from exc
    return target


class RulesetRegistry:
    def __init__(
        self,
        document: RegistryDocument,
        releases: dict[ReleaseId, LoadedRulesetRelease],
    ) -> None:
        self.document = document
        self._releases = releases

    @classmethod
    def load(cls, path: Path) -> RulesetRegistry:
        registry_path = path.resolve()
        data, _ = _read_json(registry_path)
        try:
            document = RegistryDocument.model_validate(data)
        except ValueError as exc:
            raise RulesetRegistryError(f"Invalid ruleset registry: {registry_path}") from exc

        releases: dict[str, LoadedRulesetRelease] = {}
        for entry in document.releases:
            manifest_path = _resolve_inside(registry_path.parent, entry.manifest)
            manifest_data, manifest_raw = _read_json(manifest_path)
            try:
                manifest = RulesetManifest.model_validate(manifest_data)
            except ValueError as exc:
                raise RulesetRegistryError(f"Invalid ruleset manifest: {manifest_path}") from exc
            if manifest.id != entry.id:
                raise RulesetRegistryError(
                    f"Registry ID {entry.id!r} does not match manifest ID {manifest.id!r}"
                )

            index_path = _resolve_inside(manifest_path.parent, manifest.normalized_data.index_path)
            index_data, _ = _read_json(index_path)
            try:
                data_index = NormalizedDataIndex.model_validate(index_data)
            except ValueError as exc:
                raise RulesetRegistryError(f"Invalid normalized-data index: {index_path}") from exc
            if data_index.ruleset_release_id != manifest.id:
                raise RulesetRegistryError("normalized-data index uses another ruleset release")
            if data_index.schema_version != manifest.normalized_data.schema_version:
                raise RulesetRegistryError("normalized-data schema versions do not match")
            if data_index.support_status != manifest.normalized_data.support_status:
                raise RulesetRegistryError("normalized-data support statuses do not match")

            releases[entry.id] = LoadedRulesetRelease(
                manifest=manifest,
                manifest_path=manifest_path,
                manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
                data_index=data_index,
            )
        return cls(document, releases)

    @property
    def release_ids(self) -> tuple[str, ...]:
        return tuple(self._releases)

    @property
    def default_release_id(self) -> str:
        return self.document.default_release_id

    def get(self, release_id: str) -> LoadedRulesetRelease:
        if release_id == "latest":
            raise UnknownRulesetError("Dynamic ruleset alias 'latest' is not supported")
        try:
            return self._releases[release_id]
        except KeyError as exc:
            raise UnknownRulesetError(f"Unknown ruleset release: {release_id}") from exc


@lru_cache
def get_ruleset_registry() -> RulesetRegistry:
    return RulesetRegistry.load(get_settings().ruleset_registry_path)


def _artifact_source_urls(
    release: LoadedRulesetRelease,
    source: Literal["auto", "official", "project_release"],
) -> Iterator[str]:
    sources = release.manifest.artifact.sources
    if source == "auto":
        order = {"official": 0, "project_release": 1}
        sources = sorted(sources, key=lambda item: order[item.name])
    else:
        sources = [item for item in sources if item.name == source]
    if not sources:
        raise RulesetRegistryError(f"No {source!r} source exists for {release.manifest.id}")
    for artifact_source in sources:
        url = str(artifact_source.url)
        if not url.startswith("https://"):
            raise RulesetRegistryError("Ruleset artifacts must use HTTPS")
        yield url


def _verify_artifact(path: Path, expected_sha256: str, expected_size: int) -> bool:
    if not path.is_file() or path.stat().st_size != expected_size:
        return False
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest() == expected_sha256


def fetch_ruleset_artifact(
    release: LoadedRulesetRelease,
    cache_dir: Path,
    *,
    source: Literal["auto", "official", "project_release"] = "auto",
    opener: Callable[[str], BinaryIO] = urlopen,
) -> Path:
    artifact = release.manifest.artifact
    target_dir = cache_dir / release.manifest.id
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / artifact.filename
    if target.exists():
        if _verify_artifact(target, artifact.sha256, artifact.size_bytes):
            return target
        raise ArtifactIntegrityError(f"Cached artifact failed integrity verification: {target}")

    errors: list[str] = []
    for url in _artifact_source_urls(release, source):
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(dir=target_dir, delete=False) as temporary:
                temporary_path = Path(temporary.name)
                digest = hashlib.sha256()
                size = 0
                with closing(opener(url)) as response:
                    while chunk := response.read(1024 * 1024):
                        temporary.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
            if size != artifact.size_bytes or digest.hexdigest() != artifact.sha256:
                raise ArtifactIntegrityError(
                    f"Downloaded artifact from {url} did not match the manifest"
                )
            os.replace(temporary_path, target)
            return target
        except (OSError, ArtifactIntegrityError) as exc:
            errors.append(str(exc))
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    raise ArtifactIntegrityError("; ".join(errors) or "Artifact download failed")
