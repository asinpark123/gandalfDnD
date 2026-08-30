import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.character_creation import (
    CharacterCreationCatalog,
    CharacterFinalizeRequest,
    finalize_character_choices,
)
from app.dice import DiceService
from app.llm.base import DMProvider
from app.models import (
    Campaign,
    CampaignEvent,
    Character,
    CharacterGrant,
    DiceRoll,
    Location,
    RulesetDataCatalog,
    RulesetRelease,
    Turn,
)
from app.rulesets import LoadedRulesetDataCatalog, LoadedRulesetRelease, get_ruleset_registry
from app.schemas import (
    CampaignCreate,
    CampaignState,
    CharacterCreate,
    HPDelta,
    InventoryChange,
    MoveLocation,
    TurnRead,
)
from app.validation import CharacterSnapshot, StateChangeValidator


class NotFoundError(LookupError):
    pass


class ConflictError(ValueError):
    pass


def _campaign_for_update(session: Session, campaign_id: uuid.UUID) -> Campaign:
    campaign = session.scalar(select(Campaign).where(Campaign.id == campaign_id).with_for_update())
    if campaign is None:
        raise NotFoundError("Campaign not found")
    return campaign


def _next_event_sequence(session: Session, campaign_id: uuid.UUID) -> int:
    current = session.scalar(
        select(func.max(CampaignEvent.sequence)).where(CampaignEvent.campaign_id == campaign_id)
    )
    return (current or 0) + 1


def _add_event(
    session: Session,
    campaign_id: uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
    *,
    turn_id: uuid.UUID | None = None,
    visibility: str = "player",
) -> CampaignEvent:
    pin = session.execute(
        select(Campaign.ruleset_release_id, Campaign.ruleset_data_catalog_id).where(
            Campaign.id == campaign_id
        )
    ).one_or_none()
    if pin is None:
        raise NotFoundError("Campaign not found")
    ruleset_release_id, ruleset_data_catalog_id = pin
    event = CampaignEvent(
        campaign_id=campaign_id,
        ruleset_release_id=ruleset_release_id,
        ruleset_data_catalog_id=ruleset_data_catalog_id,
        turn_id=turn_id,
        sequence=_next_event_sequence(session, campaign_id),
        event_type=event_type,
        visibility=visibility,
        payload=payload,
    )
    session.add(event)
    session.flush()
    return event


def _ensure_ruleset_release(
    session: Session, loaded_release: LoadedRulesetRelease
) -> RulesetRelease:
    manifest = loaded_release.manifest
    release = session.get(RulesetRelease, manifest.id)
    expected = {
        "title": manifest.title,
        "version": manifest.version,
        "publication_date": manifest.publication_date,
        "license_id": manifest.license.id,
        "source_url": str(manifest.source_page),
        "artifact_sha256": manifest.artifact.sha256,
        "artifact_size_bytes": manifest.artifact.size_bytes,
        "manifest_sha256": loaded_release.manifest_sha256,
        "data_schema_version": manifest.normalized_data.schema_version,
        "support_status": manifest.normalized_data.support_status,
    }
    if release is None:
        release = RulesetRelease(id=manifest.id, **expected)
        session.add(release)
        session.flush()
        return release
    actual = {field: getattr(release, field) for field in expected}
    if actual != expected:
        raise ConflictError(f"Registered ruleset release {manifest.id!r} is immutable and differs")
    return release


def _ensure_ruleset_data_catalog(
    session: Session,
    loaded_catalog: LoadedRulesetDataCatalog,
    ruleset_release_id: str,
) -> RulesetDataCatalog:
    document = loaded_catalog.document
    schema_version = document.schema_version
    support_status = (
        document.support_status if hasattr(document, "support_status") else "character_creation"
    )
    expected = {
        "ruleset_release_id": ruleset_release_id,
        "kind": loaded_catalog.kind,
        "schema_version": schema_version,
        "support_status": support_status,
        "catalog_sha256": loaded_catalog.sha256,
    }
    catalog = session.get(RulesetDataCatalog, loaded_catalog.id)
    if catalog is None:
        catalog = RulesetDataCatalog(id=loaded_catalog.id, **expected)
        session.add(catalog)
        session.flush()
        return catalog
    actual = {field: getattr(catalog, field) for field in expected}
    if actual != expected:
        raise ConflictError(f"Ruleset data catalog {loaded_catalog.id!r} is immutable and differs")
    return catalog


def create_campaign(session: Session, data: CampaignCreate) -> Campaign:
    registry = get_ruleset_registry()
    loaded_release = registry.get(data.ruleset_release_id)
    loaded_catalog = registry.get_data_catalog(data.ruleset_release_id)
    _ensure_ruleset_release(session, loaded_release)
    _ensure_ruleset_data_catalog(session, loaded_catalog, loaded_release.manifest.id)
    campaign = Campaign(
        name=data.name,
        ruleset_release_id=loaded_release.manifest.id,
        ruleset_data_catalog_id=loaded_catalog.id,
    )
    session.add(campaign)
    session.flush()
    location = Location(
        campaign_id=campaign.id,
        name=data.starting_location,
        description="The campaign's starting point.",
        is_current=True,
    )
    session.add(location)
    _add_event(
        session,
        campaign.id,
        "campaign_created",
        {
            "name": campaign.name,
            "starting_location": location.name,
            "ruleset_release_id": campaign.ruleset_release_id,
            "ruleset_data_catalog_id": campaign.ruleset_data_catalog_id,
        },
    )
    session.commit()
    return campaign


def add_character(session: Session, campaign_id: uuid.UUID, data: CharacterCreate) -> Character:
    campaign = _campaign_for_update(session, campaign_id)
    existing = session.scalar(select(Character).where(Character.campaign_id == campaign_id))
    if existing is not None:
        raise ConflictError("A campaign supports one player character")
    loaded_catalog = get_ruleset_registry().get_data_catalog(
        campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
    )
    if loaded_catalog.kind != "character_creation":
        raise ConflictError("Campaign data catalog does not support guided character creation")
    character = Character(
        campaign_id=campaign_id,
        ruleset_release_id=campaign.ruleset_release_id,
        ruleset_data_catalog_id=campaign.ruleset_data_catalog_id,
        name=data.name,
        creation_status="draft",
        revision=0,
        max_hp=None,
        hp=None,
        inventory={},
    )
    session.add(character)
    session.flush()
    _add_event(
        session,
        campaign_id,
        "character_draft_created",
        {
            "character_id": str(character.id),
            "name": character.name,
            "ruleset_data_catalog_id": character.ruleset_data_catalog_id,
        },
    )
    session.commit()
    return character


def _catalog_definition_sources(catalog: CharacterCreationCatalog) -> dict[str, list[str]]:
    definitions = [
        *catalog.abilities,
        *catalog.alignments,
        *catalog.skills,
        *catalog.languages,
        *catalog.gaming_sets,
        catalog.standard_array,
        catalog.background,
        catalog.species,
        catalog.character_class,
        *catalog.features,
        *catalog.origin_feats,
        *catalog.fighting_styles,
        *catalog.weapons,
        *catalog.equipment_packages,
    ]
    return {definition.definition_key: definition.source_ids for definition in definitions}


def _build_character_grants(
    character: Character,
    event: CampaignEvent,
    request: CharacterFinalizeRequest,
    catalog: CharacterCreationCatalog,
) -> list[CharacterGrant]:
    source_ids = _catalog_definition_sources(catalog)
    grants: list[tuple[str, str, str, str, dict[str, Any]]] = []

    def add(
        grant_type: str,
        slot: str,
        definition_key: str,
        source_definition_key: str,
        value: dict[str, Any],
    ) -> None:
        value = {**value, "source_ids": source_ids.get(definition_key, [])}
        grants.append((grant_type, slot, definition_key, source_definition_key, value))

    add(
        "selection",
        "identity.species",
        request.species_definition_key,
        request.species_definition_key,
        {"size": request.size},
    )
    add(
        "selection",
        "identity.background",
        request.background_definition_key,
        request.background_definition_key,
        {},
    )
    add(
        "selection",
        "identity.class",
        request.class_definition_key,
        request.class_definition_key,
        {"level": 1},
    )
    add(
        "selection",
        "abilities.method",
        request.ability_method_definition_key,
        request.ability_method_definition_key,
        {},
    )
    alignment = next(
        option for option in catalog.alignments if option.id == request.alignment.lower()
    )
    add(
        "selection",
        "identity.alignment",
        alignment.definition_key,
        alignment.definition_key,
        {"alignment": request.alignment},
    )
    language_by_id = {option.id: option for option in catalog.languages}
    add(
        "grant",
        "language.common",
        language_by_id["common"].definition_key,
        language_by_id["common"].definition_key,
        {"language": "common"},
    )
    for language in request.languages:
        definition_key = language_by_id[language].definition_key
        add(
            "selection",
            f"language.{language}",
            definition_key,
            request.species_definition_key,
            {"language": language},
        )
    ability_by_id = {option.id: option for option in catalog.abilities}
    for ability, score in request.base_ability_scores.items():
        add(
            "selection",
            f"ability.base.{ability}",
            ability_by_id[ability].definition_key,
            request.ability_method_definition_key,
            {"score": score},
        )
    for ability, increase in request.background_ability_increases.items():
        add(
            "grant",
            f"ability.background.{ability}",
            ability_by_id[ability].definition_key,
            request.background_definition_key,
            {"increase": increase},
        )
    skill_by_id = {option.id: option for option in catalog.skills}
    for skill in catalog.background.skill_proficiencies:
        add(
            "grant",
            f"skill.background.{skill}",
            skill_by_id[skill].definition_key,
            request.background_definition_key,
            {"proficient": True},
        )
    for skill in request.fighter_skills:
        add(
            "selection",
            f"skill.class.{skill}",
            skill_by_id[skill].definition_key,
            request.class_definition_key,
            {"proficient": True},
        )
    human_skillful = "srd-5.2.1:species_feature.human.skillful"
    add(
        "selection",
        f"skill.human.{request.human_skill}",
        skill_by_id[request.human_skill].definition_key,
        human_skillful,
        {"proficient": True},
    )
    for skill in request.skilled_feat_skills:
        add(
            "selection",
            f"skill.feat.{skill}",
            skill_by_id[skill].definition_key,
            request.origin_feat_definition_key,
            {"proficient": True},
        )
    add(
        "grant",
        "feat.background",
        catalog.background.granted_feat_definition_key,
        request.background_definition_key,
        {},
    )
    add(
        "selection",
        "feat.human",
        request.origin_feat_definition_key,
        "srd-5.2.1:species_feature.human.versatile",
        {},
    )
    gaming_set = next(option for option in catalog.gaming_sets if option.id == request.gaming_set)
    add(
        "selection",
        "tool.background.gaming_set",
        gaming_set.definition_key,
        request.background_definition_key,
        {"gaming_set": request.gaming_set},
    )
    add(
        "selection",
        "class.fighting_style",
        request.fighting_style_definition_key,
        "srd-5.2.1:class_feature.fighter.fighting_style",
        {},
    )
    for definition_key in request.weapon_mastery_definition_keys:
        add(
            "selection",
            f"class.weapon_mastery.{definition_key.rsplit('.', 1)[-1]}",
            definition_key,
            "srd-5.2.1:class_feature.fighter.weapon_mastery",
            {},
        )
    for package_key in (
        catalog.background.equipment_package_definition_key,
        catalog.character_class.equipment_package_definition_key,
    ):
        package_owner = package_key.split(".")[-2]
        add(
            "selection",
            f"equipment.{package_owner}",
            package_key,
            package_key,
            {"route": request.equipment_route_id},
        )
    for save in catalog.character_class.saving_throw_proficiencies:
        add(
            "grant",
            f"saving_throw.{save}",
            ability_by_id[save].definition_key,
            request.class_definition_key,
            {"proficient": True},
        )
    for feature_key in [
        *catalog.species.feature_definition_keys,
        *catalog.character_class.feature_definition_keys,
    ]:
        add(
            "grant",
            f"feature.{feature_key.rsplit('.', 1)[-1]}",
            feature_key,
            request.species_definition_key
            if ":species_feature." in feature_key
            else request.class_definition_key,
            {},
        )

    return [
        CharacterGrant(
            character_id=character.id,
            campaign_id=character.campaign_id,
            ruleset_release_id=character.ruleset_release_id,
            ruleset_data_catalog_id=character.ruleset_data_catalog_id,
            acquisition_event_id=event.id,
            revision=character.revision,
            grant_type=grant_type,
            choice_slot=slot,
            definition_key=definition_key,
            source_definition_key=source_definition_key,
            value=value,
            active=True,
        )
        for grant_type, slot, definition_key, source_definition_key, value in grants
    ]


def finalize_character(
    session: Session, campaign_id: uuid.UUID, data: CharacterFinalizeRequest
) -> Character:
    campaign = _campaign_for_update(session, campaign_id)
    character = session.scalar(
        select(Character).where(Character.campaign_id == campaign_id).with_for_update()
    )
    if character is None:
        raise NotFoundError("Character draft not found")
    if character.creation_status != "draft":
        raise ConflictError("Character has already been finalized")
    loaded_catalog = get_ruleset_registry().get_data_catalog(
        campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
    )
    if loaded_catalog.kind != "character_creation" or not isinstance(
        loaded_catalog.document, CharacterCreationCatalog
    ):
        raise ConflictError("Campaign data catalog does not support guided character creation")
    sheet = finalize_character_choices(loaded_catalog.document, data)

    character.creation_status = "finalized"
    character.revision = 1
    character.max_hp = sheet.max_hp
    character.hp = sheet.max_hp
    character.inventory = sheet.starting_inventory
    character.character_sheet = sheet.model_dump(mode="json")
    character.finalized_at = datetime.now(UTC)
    session.flush()
    event = _add_event(
        session,
        campaign_id,
        "character_finalized",
        {
            "character_id": str(character.id),
            "revision": character.revision,
            "choices": data.model_dump(mode="json"),
            "sheet": sheet.model_dump(mode="json"),
        },
    )
    session.add_all(
        _build_character_grants(
            character,
            event,
            data,
            loaded_catalog.document,
        )
    )
    session.commit()
    return character


def list_character_grants(session: Session, campaign_id: uuid.UUID) -> list[CharacterGrant]:
    character = session.scalar(select(Character).where(Character.campaign_id == campaign_id))
    if character is None:
        raise NotFoundError("Character not found")
    return list(
        session.scalars(
            select(CharacterGrant)
            .where(CharacterGrant.character_id == character.id)
            .order_by(CharacterGrant.choice_slot, CharacterGrant.definition_key)
        )
    )


def get_campaign_state(session: Session, campaign_id: uuid.UUID) -> CampaignState:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise NotFoundError("Campaign not found")
    character = session.scalar(select(Character).where(Character.campaign_id == campaign_id))
    location = session.scalar(
        select(Location).where(Location.campaign_id == campaign_id, Location.is_current.is_(True))
    )
    if location is None:
        raise RuntimeError("Campaign has no current location")
    turn_count = session.scalar(
        select(func.count()).select_from(Turn).where(Turn.campaign_id == campaign_id)
    )
    return CampaignState(
        campaign=campaign,
        character=character,
        location=location,
        turn_count=turn_count or 0,
    )


def _provider_context(state: CampaignState) -> dict[str, Any]:
    return state.model_dump(mode="json")


def _apply_state_changes(
    session: Session,
    campaign_id: uuid.UUID,
    character: Character | None,
    changes: list,
) -> None:
    for change in changes:
        if isinstance(change, HPDelta):
            assert character is not None
            character.hp += change.amount
        elif isinstance(change, InventoryChange):
            assert character is not None
            inventory = dict(character.inventory)
            new_quantity = inventory.get(change.item_name, 0) + change.quantity_delta
            if new_quantity:
                inventory[change.item_name] = new_quantity
            else:
                inventory.pop(change.item_name, None)
            character.inventory = inventory
        elif isinstance(change, MoveLocation):
            current = session.scalar(
                select(Location).where(
                    Location.campaign_id == campaign_id, Location.is_current.is_(True)
                )
            )
            if current is not None:
                current.is_current = False
                session.flush()
            destination = session.scalar(
                select(Location).where(
                    Location.campaign_id == campaign_id, Location.name == change.location_name
                )
            )
            if destination is None:
                destination = Location(
                    campaign_id=campaign_id,
                    name=change.location_name,
                    description=change.description,
                    is_current=True,
                )
                session.add(destination)
            else:
                destination.is_current = True


def process_turn(
    session: Session,
    campaign_id: uuid.UUID,
    player_action: str,
    provider: DMProvider,
    dice_service: DiceService | None = None,
) -> TurnRead:
    campaign = _campaign_for_update(session, campaign_id)
    character = session.scalar(select(Character).where(Character.campaign_id == campaign_id))
    if character is not None and character.creation_status == "draft":
        raise ConflictError("Character must be finalized before play begins")
    state_before = get_campaign_state(session, campaign_id)
    output = provider.generate_turn(_provider_context(state_before), player_action)

    snapshot = None
    if character is not None:
        snapshot = CharacterSnapshot(character.hp, character.max_hp, dict(character.inventory))
    StateChangeValidator().validate(snapshot, output.state_changes)

    turn_sequence = (
        session.scalar(select(func.max(Turn.sequence)).where(Turn.campaign_id == campaign_id)) or 0
    ) + 1
    turn = Turn(
        campaign_id=campaign_id,
        sequence=turn_sequence,
        player_action=player_action,
        dm_narration=output.narration,
        provider=provider.provider_name,
        model=provider.model_name,
        structured_output=output.model_dump(mode="json"),
    )
    session.add(turn)
    session.flush()

    _add_event(
        session,
        campaign_id,
        "player_action",
        {"action": player_action},
        turn_id=turn.id,
    )

    roller = dice_service or DiceService()
    roll_models: list[DiceRoll] = []
    for request in output.dice_requests:
        result = roller.roll(request.notation, request.modifier)
        roll_model = DiceRoll(
            campaign_id=campaign_id,
            ruleset_release_id=campaign.ruleset_release_id,
            ruleset_data_catalog_id=campaign.ruleset_data_catalog_id,
            turn_id=turn.id,
            notation=result.notation,
            rolls=result.rolls,
            modifier=result.modifier,
            total=result.total,
            purpose=request.purpose,
            hidden=request.hidden,
        )
        session.add(roll_model)
        session.flush()
        roll_models.append(roll_model)
        _add_event(
            session,
            campaign_id,
            "dice_rolled",
            {
                "roll_id": str(roll_model.id),
                "notation": result.notation,
                "rolls": result.rolls,
                "modifier": result.modifier,
                "total": result.total,
                "purpose": request.purpose,
            },
            turn_id=turn.id,
            visibility="dm_only" if request.hidden else "player",
        )

    _apply_state_changes(session, campaign_id, character, output.state_changes)
    _add_event(
        session,
        campaign_id,
        "dm_response",
        {"narration": output.narration},
        turn_id=turn.id,
    )
    if output.state_changes:
        _add_event(
            session,
            campaign_id,
            "state_changed",
            {"changes": [change.model_dump(mode="json") for change in output.state_changes]},
            turn_id=turn.id,
        )
    session.commit()
    state_after = get_campaign_state(session, campaign_id)
    return TurnRead(
        id=turn.id,
        sequence=turn.sequence,
        player_action=turn.player_action,
        narration=turn.dm_narration,
        dice_rolls=roll_models,
        state=state_after,
    )


def list_events(session: Session, campaign_id: uuid.UUID) -> list[CampaignEvent]:
    if session.get(Campaign, campaign_id) is None:
        raise NotFoundError("Campaign not found")
    return list(
        session.scalars(
            select(CampaignEvent)
            .where(
                CampaignEvent.campaign_id == campaign_id,
                CampaignEvent.visibility == "player",
            )
            .order_by(CampaignEvent.sequence)
        )
    )
