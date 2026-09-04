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

from app.character_creation import CharacterCreationCatalog
from app.character_state import CharacterStateCatalog
from app.combat import CombatRulesCatalog
from app.config import get_settings
from app.resolution import ResolutionRulesCatalog

ReleaseId = str
Sha256 = str


class RulesetRegistryError(ValueError):
    pass


class UnknownRulesetError(RulesetRegistryError):
    pass


class UnknownRulesetDataCatalogError(RulesetRegistryError):
    pass


class ArtifactIntegrityError(RulesetRegistryError):
    pass


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DataCatalogEntry(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,99}$")
    kind: Literal[
        "foundation", "character_creation", "character_state", "rules_resolution", "combat"
    ]
    path: str = Field(pattern=r"^[a-z0-9][a-z0-9./_-]*\.json$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class RegistryEntry(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    manifest: str = Field(pattern=r"^[a-z0-9][a-z0-9./-]*\.json$")
    default_data_catalog_id: str
    data_catalogs: list[DataCatalogEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_data_catalogs(self) -> RegistryEntry:
        catalog_ids = [catalog.id for catalog in self.data_catalogs]
        if len(catalog_ids) != len(set(catalog_ids)):
            raise ValueError("ruleset data catalog IDs must be unique")
        if self.default_data_catalog_id not in catalog_ids:
            raise ValueError("default_data_catalog_id must identify a registered data catalog")
        return self


class RegistryDocument(StrictModel):
    schema_uri: str | None = Field(default=None, alias="$schema")
    schema_version: Literal["1.3.0"]
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
    data_catalog_id: str
    ruleset_release_id: str
    support_status: Literal["foundation_only", "character_creation", "complete"]
    definition_files: list[str]


@dataclass(frozen=True)
class LoadedRulesetDataCatalog:
    id: str
    kind: Literal[
        "foundation", "character_creation", "character_state", "rules_resolution", "combat"
    ]
    path: Path
    sha256: Sha256
    document: (
        NormalizedDataIndex
        | CharacterCreationCatalog
        | CharacterStateCatalog
        | ResolutionRulesCatalog
        | CombatRulesCatalog
    )


@dataclass(frozen=True)
class LoadedCharacterCatalogs:
    selected: LoadedRulesetDataCatalog
    character_creation: CharacterCreationCatalog
    character_state: CharacterStateCatalog | None


@dataclass(frozen=True)
class LoadedResolutionCatalogs:
    character_creation: CharacterCreationCatalog
    character_state: CharacterStateCatalog
    resolution: LoadedRulesetDataCatalog


@dataclass(frozen=True)
class LoadedCombatCatalogs:
    character_creation: CharacterCreationCatalog
    character_state: CharacterStateCatalog
    combat: LoadedRulesetDataCatalog


@dataclass(frozen=True)
class LoadedRulesetRelease:
    manifest: RulesetManifest
    manifest_path: Path
    manifest_sha256: Sha256
    data_index: NormalizedDataIndex
    default_data_catalog_id: str
    data_catalogs: dict[str, LoadedRulesetDataCatalog]


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

            data_catalogs: dict[str, LoadedRulesetDataCatalog] = {}
            for catalog_entry in entry.data_catalogs:
                catalog_path = _resolve_inside(manifest_path.parent, catalog_entry.path)
                catalog_data, catalog_raw = _read_json(catalog_path)
                actual_sha256 = hashlib.sha256(catalog_raw).hexdigest()
                if actual_sha256 != catalog_entry.sha256:
                    raise RulesetRegistryError(
                        f"Data catalog {catalog_entry.id!r} failed checksum verification"
                    )
                try:
                    if catalog_entry.kind == "foundation":
                        catalog_document: (
                            NormalizedDataIndex
                            | CharacterCreationCatalog
                            | CharacterStateCatalog
                            | ResolutionRulesCatalog
                            | CombatRulesCatalog
                        ) = NormalizedDataIndex.model_validate(catalog_data)
                    elif catalog_entry.kind == "character_creation":
                        catalog_document = CharacterCreationCatalog.model_validate(catalog_data)
                    elif catalog_entry.kind == "character_state":
                        catalog_document = CharacterStateCatalog.model_validate(catalog_data)
                    elif catalog_entry.kind == "rules_resolution":
                        catalog_document = ResolutionRulesCatalog.model_validate(catalog_data)
                    else:
                        catalog_document = CombatRulesCatalog.model_validate(catalog_data)
                except ValueError as exc:
                    raise RulesetRegistryError(
                        f"Invalid ruleset data catalog: {catalog_path}"
                    ) from exc
                document_id = (
                    catalog_document.data_catalog_id
                    if isinstance(catalog_document, NormalizedDataIndex)
                    else catalog_document.id
                )
                if document_id != catalog_entry.id:
                    raise RulesetRegistryError("data catalog ID does not match its registry entry")
                if catalog_document.ruleset_release_id != manifest.id:
                    raise RulesetRegistryError("data catalog uses another ruleset release")
                data_catalogs[catalog_entry.id] = LoadedRulesetDataCatalog(
                    id=catalog_entry.id,
                    kind=catalog_entry.kind,
                    path=catalog_path,
                    sha256=actual_sha256,
                    document=catalog_document,
                )

            for catalog in data_catalogs.values():
                if not isinstance(catalog.document, CharacterStateCatalog):
                    continue
                base = data_catalogs.get(catalog.document.base_character_creation_catalog_id)
                if base is None or not isinstance(base.document, CharacterCreationCatalog):
                    raise RulesetRegistryError(
                        f"Character state catalog {catalog.id!r} has no creation base"
                    )
                if base.sha256 != catalog.document.base_character_creation_catalog_sha256:
                    raise RulesetRegistryError(
                        f"Character state catalog {catalog.id!r} base checksum does not match"
                    )

            for catalog in data_catalogs.values():
                if not isinstance(catalog.document, ResolutionRulesCatalog):
                    continue
                base = data_catalogs.get(catalog.document.base_character_state_catalog_id)
                if base is None or not isinstance(base.document, CharacterStateCatalog):
                    raise RulesetRegistryError(
                        f"Resolution catalog {catalog.id!r} has no character-state base"
                    )
                if base.sha256 != catalog.document.base_character_state_catalog_sha256:
                    raise RulesetRegistryError(
                        f"Resolution catalog {catalog.id!r} base checksum does not match"
                    )

            for catalog in data_catalogs.values():
                if not isinstance(catalog.document, CombatRulesCatalog):
                    continue
                base = data_catalogs.get(catalog.document.base_character_state_catalog_id)
                if base is None or not isinstance(base.document, CharacterStateCatalog):
                    raise RulesetRegistryError(
                        f"Combat catalog {catalog.id!r} has no character-state base"
                    )
                if base.sha256 != catalog.document.base_character_state_catalog_sha256:
                    raise RulesetRegistryError(
                        f"Combat catalog {catalog.id!r} base checksum does not match"
                    )

            releases[entry.id] = LoadedRulesetRelease(
                manifest=manifest,
                manifest_path=manifest_path,
                manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
                data_index=data_index,
                default_data_catalog_id=entry.default_data_catalog_id,
                data_catalogs=data_catalogs,
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

    def get_data_catalog(
        self, release_id: str, data_catalog_id: str | None = None
    ) -> LoadedRulesetDataCatalog:
        release = self.get(release_id)
        selected_id = data_catalog_id or release.default_data_catalog_id
        try:
            return release.data_catalogs[selected_id]
        except KeyError as exc:
            raise UnknownRulesetDataCatalogError(
                f"Unknown data catalog for {release_id}: {selected_id}"
            ) from exc

    def get_character_catalogs(
        self, release_id: str, data_catalog_id: str | None = None
    ) -> LoadedCharacterCatalogs:
        selected = self.get_data_catalog(release_id, data_catalog_id)
        if isinstance(selected.document, CharacterCreationCatalog):
            return LoadedCharacterCatalogs(
                selected=selected,
                character_creation=selected.document,
                character_state=None,
            )
        if isinstance(selected.document, CharacterStateCatalog):
            release = self.get(release_id)
            base = release.data_catalogs.get(selected.document.base_character_creation_catalog_id)
            if base is None or not isinstance(base.document, CharacterCreationCatalog):
                raise UnknownRulesetDataCatalogError(
                    f"Character state catalog {selected.id!r} has no creation base"
                )
            return LoadedCharacterCatalogs(
                selected=selected,
                character_creation=base.document,
                character_state=selected.document,
            )
        raise UnknownRulesetDataCatalogError(
            f"Data catalog {selected.id!r} does not support character creation"
        )

    def get_resolution_catalogs(
        self,
        release_id: str,
        character_state_catalog_id: str,
        resolution_catalog_id: str,
    ) -> LoadedResolutionCatalogs:
        character_catalogs = self.get_character_catalogs(release_id, character_state_catalog_id)
        if character_catalogs.character_state is None:
            raise UnknownRulesetDataCatalogError(
                f"Data catalog {character_state_catalog_id!r} does not support character state"
            )
        resolution = self.get_data_catalog(release_id, resolution_catalog_id)
        if not isinstance(resolution.document, ResolutionRulesCatalog):
            raise UnknownRulesetDataCatalogError(
                f"Data catalog {resolution_catalog_id!r} does not support rule resolution"
            )
        if resolution.document.base_character_state_catalog_id != character_state_catalog_id:
            raise UnknownRulesetDataCatalogError(
                f"Resolution catalog {resolution_catalog_id!r} does not extend "
                f"{character_state_catalog_id!r}"
            )
        return LoadedResolutionCatalogs(
            character_creation=character_catalogs.character_creation,
            character_state=character_catalogs.character_state,
            resolution=resolution,
        )

    def get_combat_catalogs(
        self,
        release_id: str,
        character_state_catalog_id: str,
        combat_catalog_id: str,
    ) -> LoadedCombatCatalogs:
        character_catalogs = self.get_character_catalogs(release_id, character_state_catalog_id)
        if character_catalogs.character_state is None:
            raise UnknownRulesetDataCatalogError(
                f"Data catalog {character_state_catalog_id!r} does not support character state"
            )
        combat = self.get_data_catalog(release_id, combat_catalog_id)
        if not isinstance(combat.document, CombatRulesCatalog):
            raise UnknownRulesetDataCatalogError(
                f"Data catalog {combat_catalog_id!r} does not support combat"
            )
        if combat.document.base_character_state_catalog_id != character_state_catalog_id:
            raise UnknownRulesetDataCatalogError(
                f"Combat catalog {combat_catalog_id!r} does not extend "
                f"{character_state_catalog_id!r}"
            )
        return LoadedCombatCatalogs(
            character_creation=character_catalogs.character_creation,
            character_state=character_catalogs.character_state,
            combat=combat,
        )


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
