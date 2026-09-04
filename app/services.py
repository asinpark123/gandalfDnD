import logging
import re
import uuid
from datetime import UTC, datetime, timedelta
from time import perf_counter
from typing import Any, Literal

from pydantic import TypeAdapter, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.character_creation import (
    CharacterCreationCatalog,
    CharacterFinalizeRequest,
    CharacterSheet,
    finalize_character_choices,
)
from app.character_state import (
    CharacterStateCatalog,
    GrantProvenanceFact,
    Loadout,
    derive_character_state,
    initial_loadout,
    initial_resources,
    validate_loadout,
)
from app.combat import CombatRulesCatalog, resolve_initiative
from app.dice import DiceService
from app.llm.base import (
    DMProvider,
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderEmptyOutputError,
    ProviderRateLimitError,
    ProviderRefusalError,
    ProviderResponseError,
    ProviderResult,
    ProviderTimeoutError,
    TurnInterpretationProvider,
    TurnNarrationProvider,
)
from app.memory_context import TurnMemoryContextService
from app.models import (
    NPC,
    Campaign,
    CampaignEvent,
    Character,
    CharacterGrant,
    Combatant,
    CombatCommand,
    CombatEffect,
    CombatEncounter,
    CombatEvent,
    CombatInitiativeTie,
    CombatReactionWindow,
    CombatTurn,
    DecisionOption,
    DecisionPoint,
    DecisionSelection,
    DiceRoll,
    Faction,
    FactionRelationship,
    Location,
    ProviderCall,
    Quest,
    QuestObjective,
    RuleResolution,
    RulesetDataCatalog,
    RulesetRelease,
    Scene,
    SceneNPCPresence,
    Turn,
    WorldFact,
)
from app.resolution import (
    AppliedAdjustmentSource,
    ResolutionCreate,
    ResolutionError,
    ResolutionRulesCatalog,
    determine_advantage_state,
    replay_d20_values,
    resolve_d20_test,
)
from app.rulesets import (
    LoadedRulesetDataCatalog,
    LoadedRulesetRelease,
    UnknownRulesetDataCatalogError,
    get_ruleset_registry,
)
from app.schemas import (
    CampaignCreate,
    CampaignState,
    CharacterCreate,
    CharacterRead,
    ClueRecord,
    CombatantRead,
    CombatEffectRead,
    CombatEncounterCreate,
    CombatEncounterRead,
    CombatEventRead,
    CombatInitiativeTieRead,
    CombatReactionWindowRead,
    CombatReplayRead,
    CombatStartCreate,
    CombatTieResolutionCreate,
    CombatTurnRead,
    DecisionConsequence,
    DecisionFactConsequence,
    DecisionObjectiveConsequence,
    DecisionOpen,
    DecisionQuestConsequence,
    DecisionRead,
    DiscoveryRecord,
    FactionAttitudeSet,
    FactionCreate,
    FactionMembershipSet,
    FactionRead,
    FactionRelationshipRead,
    HPDelta,
    InventoryChange,
    LoadoutUpdate,
    MoveLocation,
    NarrativeTimeAdvance,
    NPCArrive,
    NPCAttitudeSet,
    NPCDepart,
    NPCIntroduce,
    PromiseRecord,
    QuestCreate,
    QuestObjectiveRead,
    QuestObjectiveTransition,
    QuestRead,
    QuestTransition,
    RelationshipNoteAdd,
    RuleResolutionRead,
    RuleResolutionReplayRead,
    TurnExecutionCreate,
    TurnExecutionRead,
    TurnFinalizationRead,
    TurnInterpretationRead,
    TurnNarrationOutput,
    TurnRead,
    WorldFactReveal,
    WorldFactSupersede,
    WorldStateRead,
)
from app.turn_errors import TurnProviderError
from app.turn_interpretation import (
    D20TestIntent,
    TurnIntent,
    TurnInterpretationError,
    validate_turn_intent,
)
from app.validation import CharacterSnapshot, InvalidStateChange, StateChangeValidator

logger = logging.getLogger(__name__)


class NotFoundError(LookupError):
    pass


class ConflictError(ValueError):
    pass


class WorldTargetConflict(ConflictError):
    def __init__(self, detail: str, *, code: str, recovery: str) -> None:
        super().__init__(detail)
        self.code = code
        self.recovery = recovery


MAX_PROVIDER_WORLD_FACTS = 50
MAX_PROVIDER_QUESTS = 20
MAX_PROVIDER_DECISIONS = 20
MAX_PROVIDER_FACTIONS = 20
MAX_PROVIDER_FACTION_RELATIONSHIPS = 50
MAX_NARRATIVE_TIME_MINUTES = 2_147_483_647
DECISION_CONSEQUENCE_ADAPTER = TypeAdapter(list[DecisionConsequence])


class TurnNarrationError(TurnProviderError):
    pass


class _NarrationAcknowledgementError(ValueError):
    pass


TURN_WORKFLOW_LEGACY = "legacy-turn-1.0.0"
TURN_WORKFLOW_TWO_STAGE = "two-stage-turn-1.0.0"
ACTIVE_TURN_STATUSES = {
    "received",
    "interpreting",
    "intent_ready",
    "resolving",
    "resolved",
    "narrating",
}
RESOLUTION_CATALOG_ID = "srd-5.2.1-check-save-resolution-v1"
COMBAT_CATALOG_ID = "srd-5.2.1-combat-v2"


def _unpack_provider_result(result: Any) -> tuple[Any, int | None, int | None]:
    if isinstance(result, ProviderResult):
        return result.output, result.input_tokens, result.output_tokens
    return result, None, None


def _provider_failure(stage: str, exc: Exception) -> tuple[str, str]:
    if isinstance(exc, (ProviderTimeoutError, TimeoutError)):
        return "provider_timeout", f"{stage.title()} provider timed out"
    if isinstance(exc, (ProviderConnectionError, ConnectionError)):
        return "provider_connection_error", f"{stage.title()} provider could not be reached"
    if isinstance(exc, ProviderAuthenticationError):
        return (
            "provider_authentication_error",
            f"{stage.title()} provider authentication failed",
        )
    if isinstance(exc, ProviderRateLimitError):
        return "provider_rate_limit", f"{stage.title()} provider quota is unavailable"
    if isinstance(exc, ProviderResponseError):
        return "provider_response_error", f"{stage.title()} provider returned an error"
    if isinstance(exc, ProviderRefusalError):
        return "provider_refusal", f"{stage.title()} provider refused the request"
    if isinstance(exc, ProviderEmptyOutputError):
        return "provider_empty_output", f"{stage.title()} provider returned no structured output"
    if isinstance(exc, ValidationError):
        return (
            "invalid_structured_output",
            f"{stage.title()} provider returned invalid structured output",
        )
    return f"{stage}_provider_error", f"{stage.title()} provider failed"


def _campaign_for_update(session: Session, campaign_id: uuid.UUID) -> Campaign:
    campaign = session.scalar(
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if campaign is None:
        raise NotFoundError("Campaign not found")
    return campaign


def _next_event_sequence(session: Session, campaign_id: uuid.UUID) -> int:
    current = session.scalar(
        select(func.max(CampaignEvent.sequence)).where(CampaignEvent.campaign_id == campaign_id)
    )
    return (current or 0) + 1


def _project_completed_turn_best_effort(session: Session, turn: Turn) -> None:
    """Project only after canonical commit; indexing faults must never fail gameplay."""
    try:
        from app.memory import project_completed_turns

        project_completed_turns(
            session,
            campaign_id=turn.campaign_id,
            turn_id=turn.id,
            limit=1,
        )
        session.commit()
    except Exception:
        session.rollback()
        logger.exception(
            "memory source projection failed after completed turn",
            extra={"campaign_id": str(turn.campaign_id), "turn_id": str(turn.id)},
        )


def _add_event(
    session: Session,
    campaign_id: uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
    *,
    turn_id: uuid.UUID | None = None,
    visibility: str = "player",
    actor_character_id: uuid.UUID | None = None,
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
        actor_character_id=actor_character_id,
    )
    session.add(event)
    session.flush()
    return event


def _active_turn(session: Session, campaign_id: uuid.UUID) -> Turn | None:
    return session.scalar(
        select(Turn).where(
            Turn.campaign_id == campaign_id,
            (Turn.status.in_(ACTIVE_TURN_STATUSES))
            | ((Turn.status == "failed") & Turn.resumable.is_(True)),
        )
    )


def _validate_turn_actor(
    session: Session,
    campaign: Campaign,
    actor_character_id: uuid.UUID | None,
) -> Character | None:
    state = get_campaign_state(session, campaign.id)
    if campaign.play_mode == "party_commander":
        if not state.party_ready:
            raise ConflictError(
                f"At least {campaign.party_min_active} finalized active characters are required"
            )
        if actor_character_id is None:
            raise ConflictError("Party Commander turns require actor_character_id")
    character = None
    if actor_character_id is not None:
        character = session.scalar(
            select(Character).where(
                Character.campaign_id == campaign.id,
                Character.id == actor_character_id,
            )
        )
        if character is None:
            raise NotFoundError("Acting character not found in campaign")
        if character.creation_status != "finalized" or character.party_status != "active":
            raise ConflictError("Acting character must be finalized and active")
    elif len(state.characters) == 1:
        character = session.get(Character, state.characters[0].id)
    return character


def get_world_state(
    session: Session,
    campaign_id: uuid.UUID,
    *,
    audience: Literal["player", "dm"] = "player",
) -> WorldStateRead:
    if audience not in {"player", "dm"}:
        raise ValueError("Unsupported world-state audience")
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise NotFoundError("Campaign not found")
    scene = session.scalar(
        select(Scene).where(Scene.campaign_id == campaign_id, Scene.status == "active")
    )
    if scene is None:
        raise ConflictError("Campaign has no active scene")
    location = session.get(Location, scene.location_id)
    if location is None:
        raise ConflictError("Active scene has no location")
    npc_query = (
        select(NPC)
        .join(SceneNPCPresence, SceneNPCPresence.npc_id == NPC.id)
        .where(
            SceneNPCPresence.scene_id == scene.id,
            SceneNPCPresence.status == "present",
            NPC.status == "active",
        )
    )
    if audience == "player":
        npc_query = npc_query.where(NPC.visibility == "player")
    npcs = list(session.scalars(npc_query.order_by(NPC.created_at, NPC.id)))
    visibility_filter = ["player"] if audience == "player" else ["player", "dm_only"]
    facts = list(
        session.scalars(
            select(WorldFact)
            .where(
                WorldFact.campaign_id == campaign_id,
                WorldFact.status == "current",
                WorldFact.visibility.in_(visibility_filter),
            )
            .order_by(WorldFact.created_at, WorldFact.id)
        )
    )
    quests = list(
        session.scalars(
            select(Quest)
            .where(
                Quest.campaign_id == campaign_id,
                Quest.visibility.in_(visibility_filter),
            )
            .order_by(Quest.created_at, Quest.id)
        ).unique()
    )
    quest_reads = [
        QuestRead(
            id=quest.id,
            quest_key=quest.quest_key,
            title=quest.title,
            summary=quest.summary,
            status=quest.status,
            revision=quest.revision,
            objectives=[
                QuestObjectiveRead.model_validate(objective) for objective in quest.objectives
            ],
            created_at=quest.created_at,
        )
        for quest in quests
    ]
    decisions = list(
        session.scalars(
            select(DecisionPoint)
            .where(
                DecisionPoint.campaign_id == campaign_id,
                DecisionPoint.visibility.in_(visibility_filter),
            )
            .order_by(DecisionPoint.created_at, DecisionPoint.id)
        ).unique()
    )
    decision_reads = [DecisionRead.model_validate(decision) for decision in decisions]
    known_npc_ids = set(
        session.scalars(
            select(NPC.id).where(
                NPC.campaign_id == campaign_id,
                NPC.visibility.in_(visibility_filter),
            )
        )
    )
    factions = list(
        session.scalars(
            select(Faction)
            .where(
                Faction.campaign_id == campaign_id,
                Faction.visibility.in_(visibility_filter),
            )
            .order_by(Faction.created_at, Faction.id)
        ).unique()
    )
    faction_reads = []
    for faction in factions:
        relationships = [
            relation
            for relation in faction.relationships
            if relation.visibility in visibility_filter
            and (relation.npc_id is None or relation.npc_id in known_npc_ids)
        ]
        faction_reads.append(
            FactionRead(
                id=faction.id,
                faction_key=faction.faction_key,
                name=faction.name,
                description=faction.description,
                status=faction.status,
                revision=faction.revision,
                relationships=[
                    FactionRelationshipRead.model_validate(relation) for relation in relationships
                ],
                created_at=faction.created_at,
            )
        )
    return WorldStateRead(
        campaign_id=campaign.id,
        world_revision=campaign.world_revision,
        narrative_time_minutes=campaign.narrative_time_minutes,
        location=location,
        scene=scene,
        present_npcs=npcs,
        facts=facts,
        quests=quest_reads,
        decisions=decision_reads,
        factions=faction_reads,
    )


def list_world_facts(
    session: Session,
    campaign_id: uuid.UUID,
    *,
    visibility: str = "player",
    include_history: bool = False,
) -> list[WorldFact]:
    if session.get(Campaign, campaign_id) is None:
        raise NotFoundError("Campaign not found")
    if visibility not in {"player", "dm_only"}:
        raise ValueError("Invalid world fact visibility")
    statement = select(WorldFact).where(
        WorldFact.campaign_id == campaign_id,
        WorldFact.visibility == visibility,
    )
    if not include_history:
        statement = statement.where(WorldFact.status == "current")
    return list(session.scalars(statement.order_by(WorldFact.created_at, WorldFact.id)))


def _validate_fact_subject(
    session: Session,
    campaign_id: uuid.UUID,
    fact_type: str,
    subject_npc_id: uuid.UUID | None,
) -> NPC | None:
    if fact_type not in {
        "npc_attitude",
        "relationship_note",
        "promise",
        "discovery",
        "clue",
    }:
        raise InvalidStateChange("Unsupported world fact type")
    if fact_type in {"npc_attitude", "relationship_note", "promise"} and subject_npc_id is None:
        raise InvalidStateChange(f"{fact_type} requires an NPC subject")
    if subject_npc_id is None:
        return None
    npc = session.get(NPC, subject_npc_id)
    if npc is None or npc.campaign_id != campaign_id:
        raise InvalidStateChange("World fact NPC does not belong to the campaign")
    return npc


def _validate_fact_value(fact_type: str, value: str) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > 2000:
        raise InvalidStateChange("World fact value must contain 1 to 2000 characters")
    if fact_type == "npc_attitude" and normalized not in {
        "friendly",
        "neutral",
        "wary",
        "hostile",
    }:
        raise InvalidStateChange("Unsupported NPC attitude")
    return normalized


def record_world_fact(
    session: Session,
    campaign_id: uuid.UUID,
    *,
    fact_type: str,
    value: str,
    subject_npc_id: uuid.UUID | None = None,
    visibility: str = "player",
) -> WorldFact:
    """Record trusted setup/GM state; player APIs expose only player-visible facts."""
    campaign = _campaign_for_update(session, campaign_id)
    if visibility not in {"player", "dm_only"}:
        raise InvalidStateChange("Unsupported world fact visibility")
    _validate_fact_subject(session, campaign_id, fact_type, subject_npc_id)
    normalized = _validate_fact_value(fact_type, value)
    if fact_type == "npc_attitude":
        existing = session.scalar(
            select(WorldFact.id).where(
                WorldFact.campaign_id == campaign_id,
                WorldFact.subject_npc_id == subject_npc_id,
                WorldFact.fact_type == "npc_attitude",
                WorldFact.status == "current",
            )
        )
        if existing is not None:
            raise ConflictError("NPC already has a current attitude fact")
    fact_id = uuid.uuid4()
    next_revision = campaign.world_revision + 1
    event = _add_event(
        session,
        campaign_id,
        "world_fact_recorded",
        {
            "fact_id": str(fact_id),
            "fact_type": fact_type,
            "subject_npc_id": str(subject_npc_id) if subject_npc_id else None,
            "value": normalized,
            "world_revision": next_revision,
        },
        visibility=visibility,
    )
    fact = WorldFact(
        id=fact_id,
        campaign_id=campaign_id,
        subject_npc_id=subject_npc_id,
        fact_type=fact_type,
        value=normalized,
        status="current",
        visibility=visibility,
        revision=0,
        created_by_event_id=event.id,
    )
    session.add(fact)
    campaign.world_revision = next_revision
    session.commit()
    session.refresh(fact)
    return fact


def record_faction(
    session: Session,
    campaign_id: uuid.UUID,
    *,
    faction_key: str,
    name: str,
    description: str | None = None,
    visibility: str = "player",
) -> Faction:
    """Record trusted setup/GM faction state with an explicit audience."""
    campaign = _campaign_for_update(session, campaign_id)
    if visibility not in {"player", "dm_only"}:
        raise InvalidStateChange("Unsupported faction visibility")
    key = faction_key.strip()
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,79}", key) is None:
        raise InvalidStateChange("Faction key has an invalid format")
    faction_name = name.strip()
    if not faction_name or len(faction_name) > 160:
        raise InvalidStateChange("Faction name must contain 1 to 160 characters")
    if description is not None and len(description) > 2000:
        raise InvalidStateChange("Faction description cannot exceed 2000 characters")
    if session.scalar(
        select(Faction.id).where(Faction.campaign_id == campaign_id, Faction.faction_key == key)
    ):
        raise ConflictError("Faction key already exists in campaign")
    faction_id = uuid.uuid4()
    next_revision = campaign.world_revision + 1
    event = _add_event(
        session,
        campaign_id,
        "faction_created",
        {
            "faction_id": str(faction_id),
            "faction_key": key,
            "name": faction_name,
            "description": description,
            "world_revision": next_revision,
        },
        visibility=visibility,
    )
    faction = Faction(
        id=faction_id,
        campaign_id=campaign_id,
        faction_key=key,
        name=faction_name,
        description=description,
        status="active",
        visibility=visibility,
        revision=0,
        created_by_event_id=event.id,
    )
    session.add(faction)
    campaign.world_revision = next_revision
    session.commit()
    session.refresh(faction)
    return faction


def record_faction_relationship(
    session: Session,
    campaign_id: uuid.UUID,
    faction_id: uuid.UUID,
    *,
    relation_type: str,
    value: str,
    character_id: uuid.UUID | None = None,
    npc_id: uuid.UUID | None = None,
    visibility: str = "player",
) -> FactionRelationship:
    """Record trusted setup/GM faction relationships with an explicit audience."""
    campaign = _campaign_for_update(session, campaign_id)
    faction = session.get(Faction, faction_id)
    if faction is None or faction.campaign_id != campaign_id:
        raise InvalidStateChange("Faction does not belong to the campaign")
    if visibility not in {"player", "dm_only"}:
        raise InvalidStateChange("Unsupported faction relationship visibility")
    if faction.visibility == "dm_only" and visibility == "player":
        raise InvalidStateChange("Faction relationship cannot be more visible than its faction")
    if relation_type == "attitude":
        if character_id is not None or npc_id is not None:
            raise InvalidStateChange("Faction attitude must apply to the party")
        if value not in {"friendly", "neutral", "wary", "hostile"}:
            raise InvalidStateChange("Unsupported faction attitude")
    elif relation_type == "membership":
        if (character_id is None) == (npc_id is None):
            raise InvalidStateChange("Faction membership requires exactly one member")
        if value not in {"member", "associate", "former_member"}:
            raise InvalidStateChange("Unsupported faction membership")
        if character_id is not None:
            character = session.get(Character, character_id)
            if character is None or character.campaign_id != campaign_id:
                raise InvalidStateChange("Faction member character does not belong to campaign")
        if npc_id is not None:
            npc = session.get(NPC, npc_id)
            if npc is None or npc.campaign_id != campaign_id:
                raise InvalidStateChange("Faction member NPC does not belong to campaign")
            if npc.visibility == "dm_only" and visibility == "player":
                raise InvalidStateChange(
                    "Faction membership cannot be more visible than its NPC member"
                )
    else:
        raise InvalidStateChange("Unsupported faction relationship type")
    existing = session.scalar(
        select(FactionRelationship.id).where(
            FactionRelationship.faction_id == faction_id,
            FactionRelationship.relation_type == relation_type,
            FactionRelationship.character_id == character_id,
            FactionRelationship.npc_id == npc_id,
        )
    )
    if existing is not None:
        raise ConflictError("Faction relationship already exists")
    relationship_id = uuid.uuid4()
    next_world_revision = campaign.world_revision + 1
    event = _add_event(
        session,
        campaign_id,
        ("faction_attitude_set" if relation_type == "attitude" else "faction_membership_set"),
        {
            "faction_id": str(faction_id),
            "relationship_id": str(relationship_id),
            "relation_type": relation_type,
            "character_id": str(character_id) if character_id else None,
            "npc_id": str(npc_id) if npc_id else None,
            "value": value,
            "relationship_revision": 0,
            "world_revision": next_world_revision,
        },
        visibility=visibility,
    )
    relationship = FactionRelationship(
        id=relationship_id,
        campaign_id=campaign_id,
        faction_id=faction_id,
        relation_type=relation_type,
        character_id=character_id,
        npc_id=npc_id,
        value=value,
        visibility=visibility,
        revision=0,
        created_by_event_id=event.id,
    )
    session.add(relationship)
    campaign.world_revision = next_world_revision
    session.commit()
    session.refresh(relationship)
    return relationship


def _validate_turn_target(
    session: Session, campaign_id: uuid.UUID, target_npc_id: uuid.UUID | None
) -> NPC | None:
    if target_npc_id is None:
        return None
    npc = session.get(NPC, target_npc_id)
    if npc is None or npc.campaign_id != campaign_id:
        raise NotFoundError("Target NPC not found in campaign")
    if npc.visibility != "player":
        raise WorldTargetConflict(
            "Target NPC is not player-visible",
            code="world_target_not_visible",
            recovery="Choose a player-visible NPC or act without a target.",
        )
    if npc.status != "active":
        raise WorldTargetConflict(
            "Target NPC is not active",
            code="world_target_inactive",
            recovery="Choose an active NPC or act without a target.",
        )
    present = session.scalar(
        select(SceneNPCPresence.id)
        .join(Scene, Scene.id == SceneNPCPresence.scene_id)
        .where(
            Scene.campaign_id == campaign_id,
            Scene.status == "active",
            SceneNPCPresence.npc_id == npc.id,
            SceneNPCPresence.status == "present",
        )
    )
    if present is None:
        raise WorldTargetConflict(
            "Target NPC is not present in the current scene",
            code="world_target_not_present",
            recovery="Choose an NPC present in the current scene or act without a target.",
        )
    return npc


def _validated_turn_choice(
    session: Session,
    campaign_id: uuid.UUID,
    decision_id: uuid.UUID | None,
    option_key: str | None,
    *,
    occupied_quests: set[uuid.UUID] | None = None,
    occupied_objectives: set[uuid.UUID] | None = None,
    occupied_attitude_subjects: set[uuid.UUID] | None = None,
    occupied_fact_records: set[tuple[str, uuid.UUID | None, str]] | None = None,
) -> tuple[DecisionPoint, DecisionOption, list[DecisionConsequence]] | None:
    if decision_id is None or option_key is None:
        return None
    decision = session.get(DecisionPoint, decision_id)
    if decision is None or decision.campaign_id != campaign_id:
        raise NotFoundError("Decision not found in campaign")
    if decision.visibility != "player":
        raise ConflictError("Decision is not player-visible")
    if decision.status != "open":
        raise ConflictError("Decision has already been selected")
    option = session.scalar(
        select(DecisionOption).where(
            DecisionOption.decision_id == decision.id,
            DecisionOption.option_key == option_key,
        )
    )
    if option is None:
        raise ConflictError("Decision option is not valid for this decision")
    consequences = _parse_decision_consequences(option.consequences)
    _validate_decision_consequences(
        session,
        campaign_id,
        consequences,
        occupied_quests=occupied_quests,
        occupied_objectives=occupied_objectives,
        occupied_attitude_subjects=occupied_attitude_subjects,
        occupied_fact_records=occupied_fact_records,
    )
    return decision, option, consequences


def _choice_provider_context(
    choice: tuple[DecisionPoint, DecisionOption, list[DecisionConsequence]] | None,
) -> dict[str, Any] | None:
    if choice is None:
        return None
    decision, option, consequences = choice
    return {
        "decision_id": str(decision.id),
        "decision_key": decision.decision_key,
        "prompt": decision.prompt,
        "option_key": option.option_key,
        "label": option.label,
        "description": option.description,
        "consequences": [consequence.model_dump(mode="json") for consequence in consequences],
    }


def create_turn_execution(
    session: Session,
    campaign_id: uuid.UUID,
    data: TurnExecutionCreate,
) -> TurnExecutionRead:
    campaign = _campaign_for_update(session, campaign_id)
    existing = session.scalar(
        select(Turn).where(
            Turn.campaign_id == campaign_id,
            Turn.command_id == data.command_id,
        )
    )
    if existing is not None:
        if (
            existing.player_action != data.action
            or existing.actor_character_id != data.actor_character_id
            or existing.target_npc_id != data.target_npc_id
            or existing.decision_id != data.decision_id
            or existing.decision_option_key != data.decision_option_key
        ):
            raise ConflictError("command_id already exists with different turn input")
        if existing.workflow_version != TURN_WORKFLOW_TWO_STAGE:
            raise ConflictError("command_id belongs to a legacy turn")
        return TurnExecutionRead.model_validate(existing)

    active = _active_turn(session, campaign_id)
    if active is not None:
        raise ConflictError(f"Campaign already has active turn {active.id}")
    character = _validate_turn_actor(session, campaign, data.actor_character_id)
    target = _validate_turn_target(session, campaign_id, data.target_npc_id)
    _validated_turn_choice(
        session,
        campaign_id,
        data.decision_id,
        data.decision_option_key,
    )
    sequence = (
        session.scalar(select(func.max(Turn.sequence)).where(Turn.campaign_id == campaign_id)) or 0
    ) + 1
    turn = Turn(
        command_id=data.command_id,
        campaign_id=campaign_id,
        sequence=sequence,
        player_action=data.action,
        actor_character_id=character.id if character else None,
        target_npc_id=target.id if target else None,
        decision_id=data.decision_id,
        decision_option_key=data.decision_option_key,
        workflow_version=TURN_WORKFLOW_TWO_STAGE,
        status="received",
        resumable=False,
        state_revision_before=character.state_revision if character else None,
        world_revision_before=campaign.world_revision,
    )
    session.add(turn)
    session.flush()
    _add_event(
        session,
        campaign_id,
        "player_action",
        {
            "action": data.action,
            "actor_character_id": str(character.id) if character else None,
            "target_npc_id": str(target.id) if target else None,
            "decision_id": str(data.decision_id) if data.decision_id else None,
            "decision_option_key": data.decision_option_key,
            "command_id": str(data.command_id),
            "workflow_version": TURN_WORKFLOW_TWO_STAGE,
        },
        turn_id=turn.id,
        actor_character_id=character.id if character else None,
    )
    session.commit()
    session.refresh(turn)
    return TurnExecutionRead.model_validate(turn)


def get_turn_execution(
    session: Session, campaign_id: uuid.UUID, turn_id: uuid.UUID
) -> TurnExecutionRead:
    turn = session.scalar(select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id))
    if turn is None or turn.workflow_version != TURN_WORKFLOW_TWO_STAGE:
        raise NotFoundError("Turn execution not found")
    return TurnExecutionRead.model_validate(turn)


def list_turn_executions(session: Session, campaign_id: uuid.UUID) -> list[TurnExecutionRead]:
    if session.get(Campaign, campaign_id) is None:
        raise NotFoundError("Campaign not found")
    turns = session.scalars(
        select(Turn)
        .where(
            Turn.campaign_id == campaign_id,
            Turn.workflow_version == TURN_WORKFLOW_TWO_STAGE,
        )
        .order_by(Turn.sequence)
    )
    return [TurnExecutionRead.model_validate(turn) for turn in turns]


def cancel_turn_execution(
    session: Session, campaign_id: uuid.UUID, turn_id: uuid.UUID
) -> TurnExecutionRead:
    _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    if turn is None or turn.workflow_version != TURN_WORKFLOW_TWO_STAGE:
        raise NotFoundError("Turn execution not found")
    if turn.status in {"completed", "cancelled"} or (
        turn.status == "failed" and not turn.resumable
    ):
        raise ConflictError(f"Turn in {turn.status} status cannot be cancelled")
    turn.status = "cancelled"
    turn.failure_stage = None
    turn.error_code = None
    turn.error_detail = None
    turn.resumable = False
    turn.resume_status = None
    turn.stage_started_at = None
    turn.completed_at = datetime.now(UTC)
    _add_event(
        session,
        campaign_id,
        "turn_cancelled",
        {"command_id": str(turn.command_id)},
        turn_id=turn.id,
        actor_character_id=turn.actor_character_id,
    )
    session.commit()
    session.refresh(turn)
    return TurnExecutionRead.model_validate(turn)


def mark_turn_execution_failed(
    session: Session,
    campaign_id: uuid.UUID,
    turn_id: uuid.UUID,
    *,
    failure_stage: str,
    error_code: str,
    error_detail: str | None,
    resume_status: str | None,
) -> TurnExecutionRead:
    _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    if turn is None or turn.workflow_version != TURN_WORKFLOW_TWO_STAGE:
        raise NotFoundError("Turn execution not found")
    if turn.status in {"completed", "cancelled", "failed"}:
        raise ConflictError(f"Turn in {turn.status} status cannot fail")
    if resume_status not in {None, "received", "intent_ready", "resolved"}:
        raise ValueError("Invalid resume status")
    turn.status = "failed"
    turn.failure_stage = failure_stage
    turn.error_code = error_code
    turn.error_detail = error_detail
    turn.resumable = resume_status is not None
    turn.resume_status = resume_status
    turn.stage_started_at = None
    turn.completed_at = None if turn.resumable else datetime.now(UTC)
    session.commit()
    session.refresh(turn)
    return TurnExecutionRead.model_validate(turn)


def resume_turn_execution(
    session: Session,
    campaign_id: uuid.UUID,
    turn_id: uuid.UUID,
    *,
    stale_after_seconds: int = 120,
) -> TurnExecutionRead:
    _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    if turn is None or turn.workflow_version != TURN_WORKFLOW_TWO_STAGE:
        raise NotFoundError("Turn execution not found")
    checkpoint: str | None = None
    interrupted_stage: str | None = None
    if turn.status == "failed" and turn.resumable and turn.resume_status is not None:
        checkpoint = turn.resume_status
    elif turn.status in {"interpreting", "resolving", "narrating"}:
        if turn.stage_started_at is None:
            raise ConflictError("Turn stage has no recovery timestamp")
        recovery_cutoff = datetime.now(UTC) - timedelta(seconds=stale_after_seconds)
        if turn.stage_started_at > recovery_cutoff:
            raise ConflictError(f"Turn {turn.status} stage is still in progress")
        interrupted_stage = turn.status
        if turn.status == "interpreting":
            checkpoint = "received"
        elif turn.status == "resolving":
            resolution = session.scalar(
                select(RuleResolution).where(
                    RuleResolution.campaign_id == campaign_id,
                    RuleResolution.command_id == turn.command_id,
                )
            )
            if resolution is None:
                checkpoint = "intent_ready"
            else:
                roll = session.get(DiceRoll, resolution.dice_roll_id)
                if roll is None or roll.turn_id != turn.id:
                    raise ConflictError("Recovered resolution does not belong to this turn")
                turn.resolution_id = resolution.id
                checkpoint = "resolved"
        else:
            checkpoint = "resolved" if turn.resolution_id is not None else "intent_ready"
    else:
        raise ConflictError("Turn is not resumable")

    assert checkpoint is not None
    turn.status = checkpoint
    turn.failure_stage = None
    turn.error_code = None
    turn.error_detail = None
    turn.resumable = False
    turn.resume_status = None
    turn.stage_started_at = None
    turn.completed_at = None
    if interrupted_stage is not None:
        _add_event(
            session,
            campaign_id,
            "turn_stage_recovered",
            {
                "interrupted_stage": interrupted_stage,
                "restored_checkpoint": checkpoint,
                "command_id": str(turn.command_id),
            },
            turn_id=turn.id,
            visibility="dm_only",
            actor_character_id=turn.actor_character_id,
        )
    session.commit()
    session.refresh(turn)
    return TurnExecutionRead.model_validate(turn)


def list_provider_calls(
    session: Session, campaign_id: uuid.UUID, turn_id: uuid.UUID
) -> list[ProviderCall]:
    get_turn_execution(session, campaign_id, turn_id)
    return list(
        session.scalars(
            select(ProviderCall)
            .where(ProviderCall.campaign_id == campaign_id, ProviderCall.turn_id == turn_id)
            .order_by(ProviderCall.stage, ProviderCall.attempt)
        )
    )


def _stored_turn_intent(turn: Turn) -> TurnIntent:
    if turn.intent_output is None:
        raise ConflictError("Turn has no stored interpretation")
    try:
        return validate_turn_intent(turn.intent_output)
    except ValidationError as exc:
        raise ConflictError("Stored turn interpretation is invalid") from exc


def _next_provider_attempt(session: Session, turn_id: uuid.UUID, stage: str) -> int:
    current = session.scalar(
        select(func.max(ProviderCall.attempt)).where(
            ProviderCall.turn_id == turn_id,
            ProviderCall.stage == stage,
        )
    )
    return (current or 0) + 1


def _turn_interpretation_result(
    session: Session, turn: Turn, intent: TurnIntent
) -> TurnInterpretationRead:
    resolution = (
        get_rule_resolution(session, turn.campaign_id, turn.resolution_id)
        if turn.resolution_id is not None
        else None
    )
    return TurnInterpretationRead(
        turn=TurnExecutionRead.model_validate(turn),
        intent=intent,
        resolution=resolution,
    )


def interpret_turn_execution(
    session: Session,
    campaign_id: uuid.UUID,
    turn_id: uuid.UUID,
    provider: TurnInterpretationProvider,
    dice_service: DiceService | None = None,
    memory_context_service: TurnMemoryContextService | None = None,
) -> TurnInterpretationRead:
    campaign = _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    if turn is None or turn.workflow_version != TURN_WORKFLOW_TWO_STAGE:
        raise NotFoundError("Turn execution not found")
    if turn.status == "resolved":
        return _turn_interpretation_result(session, turn, _stored_turn_intent(turn))
    if turn.status in {"completed", "cancelled", "failed", "narrating"}:
        raise ConflictError(f"Turn in {turn.status} status cannot be interpreted")
    if turn.status == "interpreting":
        raise ConflictError("Turn interpretation is already in progress")

    intent: TurnIntent
    if turn.status == "received":
        character = session.get(Character, turn.actor_character_id)
        if character is None:
            raise NotFoundError("Acting character not found in campaign")
        if character.state_revision != turn.state_revision_before:
            mark_turn_execution_failed(
                session,
                campaign_id,
                turn_id,
                failure_stage="interpretation",
                error_code="stale_character_state",
                error_detail="Acting character state changed after the turn was received",
                resume_status=None,
            )
            raise ConflictError("Acting character state changed after the turn was received")
        if campaign.world_revision != turn.world_revision_before:
            mark_turn_execution_failed(
                session,
                campaign_id,
                turn_id,
                failure_stage="interpretation",
                error_code="stale_world_state",
                error_detail="Campaign world changed after the turn was received",
                resume_status=None,
            )
            raise ConflictError("Campaign world changed after the turn was received")
        choice = _validated_turn_choice(
            session,
            campaign_id,
            turn.decision_id,
            turn.decision_option_key,
        )
        context = _provider_context(
            get_campaign_state(session, campaign_id),
            get_world_state(session, campaign_id),
            turn.target_npc_id,
            _choice_provider_context(choice),
        )
        attempt = _next_provider_attempt(session, turn.id, "interpretation")
        player_action = turn.player_action
        turn.status = "interpreting"
        turn.stage_started_at = datetime.now(UTC)
        session.commit()

        context = _with_historical_memory(
            context,
            memory_context_service,
            campaign_id=campaign_id,
            turn_id=turn_id,
            stage="interpretation",
            player_action=player_action,
        )

        started = perf_counter()
        try:
            provider_result = provider.interpret_action(context, player_action)
            provider_output, input_tokens, output_tokens = _unpack_provider_result(provider_result)
            if provider_output is None:
                raise ProviderEmptyOutputError
            intent = validate_turn_intent(provider_output)
        except Exception as exc:
            latency_ms = max(0, round((perf_counter() - started) * 1000))
            error_code, safe_detail = _provider_failure("interpretation", exc)
            session.rollback()
            _campaign_for_update(session, campaign_id)
            failed_turn = session.scalar(
                select(Turn)
                .where(Turn.campaign_id == campaign_id, Turn.id == turn_id)
                .with_for_update()
            )
            assert failed_turn is not None
            session.add(
                ProviderCall(
                    campaign_id=campaign_id,
                    turn_id=turn_id,
                    stage="interpretation",
                    attempt=attempt,
                    provider=provider.provider_name,
                    model=provider.model_name,
                    prompt_version=provider.interpretation_prompt_version,
                    status="failed",
                    latency_ms=latency_ms,
                    error_code=error_code,
                    error_detail=safe_detail,
                )
            )
            failed_turn.status = "failed"
            failed_turn.failure_stage = "interpretation"
            failed_turn.error_code = error_code
            failed_turn.error_detail = safe_detail
            failed_turn.resumable = True
            failed_turn.resume_status = "received"
            failed_turn.stage_started_at = None
            session.commit()
            raise TurnInterpretationError(
                safe_detail,
                turn_id=turn_id,
                stage="interpretation",
                error_code=error_code,
                resumable=True,
            ) from exc

        latency_ms = max(0, round((perf_counter() - started) * 1000))
        campaign = _campaign_for_update(session, campaign_id)
        turn = session.scalar(
            select(Turn)
            .where(Turn.campaign_id == campaign_id, Turn.id == turn_id)
            .with_for_update()
        )
        assert turn is not None
        if turn.status != "interpreting":
            raise ConflictError("Turn changed while interpretation was running")
        character = session.scalar(
            select(Character)
            .where(Character.id == turn.actor_character_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        stale_character = (
            character is None or character.state_revision != turn.state_revision_before
        )
        stale_world = campaign.world_revision != turn.world_revision_before
        session.add(
            ProviderCall(
                campaign_id=campaign_id,
                turn_id=turn_id,
                stage="interpretation",
                attempt=attempt,
                provider=provider.provider_name,
                model=provider.model_name,
                prompt_version=provider.interpretation_prompt_version,
                status="succeeded",
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                structured_output=intent.model_dump(mode="json"),
            )
        )
        turn.intent_output = intent.model_dump(mode="json")
        turn.interpretation_prompt_version = provider.interpretation_prompt_version
        if stale_character or stale_world:
            turn.status = "failed"
            turn.failure_stage = "interpretation"
            turn.error_code = "stale_world_state" if stale_world else "stale_character_state"
            turn.error_detail = (
                "Campaign world changed during interpretation"
                if stale_world
                else "Acting character state changed during interpretation"
            )
            turn.resumable = False
            turn.stage_started_at = None
            turn.completed_at = datetime.now(UTC)
        else:
            turn.status = "intent_ready"
            turn.stage_started_at = None
        session.commit()
        session.refresh(turn)
        if stale_character or stale_world:
            raise ConflictError(turn.error_detail or "Turn state changed during interpretation")
    elif turn.status in {"intent_ready", "resolving"}:
        intent = _stored_turn_intent(turn)
    else:
        raise ConflictError(f"Turn in {turn.status} status cannot be interpreted")

    if not isinstance(intent, D20TestIntent):
        return _turn_interpretation_result(session, turn, intent)

    if turn.status == "intent_ready":
        character = session.get(Character, turn.actor_character_id, populate_existing=True)
        if character is None or character.state_revision != turn.state_revision_before:
            mark_turn_execution_failed(
                session,
                campaign_id,
                turn_id,
                failure_stage="resolution",
                error_code="stale_character_state",
                error_detail="Acting character state changed before resolution",
                resume_status=None,
            )
            raise ConflictError("Acting character state changed before resolution")
        campaign = _campaign_for_update(session, campaign_id)
        if campaign.world_revision != turn.world_revision_before:
            mark_turn_execution_failed(
                session,
                campaign_id,
                turn_id,
                failure_stage="resolution",
                error_code="stale_world_state",
                error_detail="Campaign world changed before resolution",
                resume_status=None,
            )
            raise ConflictError("Campaign world changed before resolution")
        _campaign_for_update(session, campaign_id)
        turn = session.scalar(
            select(Turn)
            .where(Turn.campaign_id == campaign_id, Turn.id == turn_id)
            .with_for_update()
        )
        assert turn is not None
        turn.status = "resolving"
        turn.stage_started_at = datetime.now(UTC)
        session.commit()

    request = intent.resolution
    resolution_command = ResolutionCreate(
        command_id=turn.command_id,
        actor_character_id=turn.actor_character_id,
        ruleset_release_id=campaign.ruleset_release_id,
        character_state_catalog_id=campaign.ruleset_data_catalog_id,
        resolution_catalog_id=RESOLUTION_CATALOG_ID,
        resolution_type=request.resolution_type,
        ability=request.ability,
        skill=request.skill,
        difficulty_class=request.difficulty_class,
        advantage_reasons=request.advantage_reasons,
        disadvantage_reasons=request.disadvantage_reasons,
    )
    try:
        resolution = create_rule_resolution(
            session,
            campaign_id,
            resolution_command,
            dice_service,
            turn_id=turn_id,
        )
    except ResolutionError as exc:
        session.rollback()
        mark_turn_execution_failed(
            session,
            campaign_id,
            turn_id,
            failure_stage="resolution",
            error_code="invalid_resolution_request",
            error_detail=str(exc),
            resume_status=None,
        )
        raise
    _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    assert turn is not None
    if turn.resolution_id not in {None, resolution.id}:
        raise ConflictError("Turn is already linked to a different resolution")
    turn.resolution_id = resolution.id
    turn.status = "resolved"
    turn.stage_started_at = None
    session.commit()
    session.refresh(turn)
    return TurnInterpretationRead(
        turn=TurnExecutionRead.model_validate(turn), intent=intent, resolution=resolution
    )


def _turn_resolution(
    session: Session, campaign_id: uuid.UUID, turn: Turn
) -> RuleResolutionRead | None:
    if turn.resolution_id is None:
        return None
    return get_rule_resolution(session, campaign_id, turn.resolution_id)


def _turn_finalization_result(
    session: Session,
    campaign_id: uuid.UUID,
    turn: Turn,
    intent: TurnIntent,
) -> TurnFinalizationRead:
    return TurnFinalizationRead(
        turn=TurnExecutionRead.model_validate(turn),
        intent=intent,
        resolution=_turn_resolution(session, campaign_id, turn),
        state=get_campaign_state(session, campaign_id),
    )


def _character_snapshot(
    campaign: Campaign,
    character: Character,
) -> CharacterSnapshot:
    equipped_ids = {
        item_id
        for item_id in [
            character.equipped_items.get("worn_armor_item_id"),
            *character.equipped_items.get("held_item_ids", []),
        ]
        if item_id
    }
    catalogs = get_ruleset_registry().get_character_catalogs(
        campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
    )
    equipped_names = frozenset(
        item.item_name
        for item in (catalogs.character_state.equipment if catalogs.character_state else [])
        if item.item_id in equipped_ids
    )
    return CharacterSnapshot(
        character.hp or 0,
        character.max_hp or 0,
        dict(character.inventory),
        equipped_names,
    )


def _record_narration_failure(
    session: Session,
    campaign_id: uuid.UUID,
    turn_id: uuid.UUID,
    *,
    attempt: int,
    provider: TurnNarrationProvider,
    latency_ms: int,
    error_code: str,
    error_detail: str,
    resume_status: str | None,
    output: TurnNarrationOutput | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
) -> None:
    session.rollback()
    _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    assert turn is not None
    provider_call = ProviderCall(
        campaign_id=campaign_id,
        turn_id=turn_id,
        stage="narration",
        attempt=attempt,
        provider=provider.provider_name,
        model=provider.model_name,
        prompt_version=provider.narration_prompt_version,
        status="succeeded" if output is not None else "failed",
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        error_code=None if output is not None else error_code,
        error_detail=None if output is not None else error_detail,
    )
    if output is not None:
        provider_call.structured_output = output.model_dump(mode="json")
    session.add(provider_call)
    turn.status = "failed"
    turn.failure_stage = "narration"
    turn.error_code = error_code
    turn.error_detail = error_detail
    turn.resumable = resume_status is not None
    turn.resume_status = resume_status
    turn.stage_started_at = None
    turn.completed_at = None if turn.resumable else datetime.now(UTC)
    session.commit()


def finalize_turn_execution(
    session: Session,
    campaign_id: uuid.UUID,
    turn_id: uuid.UUID,
    provider: TurnNarrationProvider,
    memory_context_service: TurnMemoryContextService | None = None,
) -> TurnFinalizationRead:
    campaign = _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    if turn is None or turn.workflow_version != TURN_WORKFLOW_TWO_STAGE:
        raise NotFoundError("Turn execution not found")
    intent = _stored_turn_intent(turn)
    if turn.status == "completed":
        return _turn_finalization_result(session, campaign_id, turn, intent)
    if turn.status == "narrating":
        raise ConflictError("Turn narration is already in progress")
    resolution = _turn_resolution(session, campaign_id, turn)
    if isinstance(intent, D20TestIntent):
        if resolution is None or turn.status not in {"resolved", "narrating"}:
            raise ConflictError("A check/save turn must be resolved before narration")
        resume_status = "resolved"
    else:
        if resolution is not None or turn.status not in {"intent_ready", "narrating"}:
            raise ConflictError("Narrative turn is not ready for narration")
        resume_status = "intent_ready"

    character = session.scalar(
        select(Character)
        .where(Character.id == turn.actor_character_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if character is None:
        raise NotFoundError("Acting character not found in campaign")
    if character.state_revision != turn.state_revision_before:
        mark_turn_execution_failed(
            session,
            campaign_id,
            turn_id,
            failure_stage="narration",
            error_code="stale_character_state",
            error_detail="Acting character state changed before narration",
            resume_status=None,
        )
        raise ConflictError("Acting character state changed before narration")
    if campaign.world_revision != turn.world_revision_before:
        mark_turn_execution_failed(
            session,
            campaign_id,
            turn_id,
            failure_stage="narration",
            error_code="stale_world_state",
            error_detail="Campaign world changed before narration",
            resume_status=None,
        )
        raise ConflictError("Campaign world changed before narration")
    current_location = session.scalar(
        select(Location).where(
            Location.campaign_id == campaign_id,
            Location.is_current.is_(True),
        )
    )
    if current_location is None:
        raise ConflictError("Campaign has no current location")
    location_id_before = current_location.id
    choice = _validated_turn_choice(
        session,
        campaign_id,
        turn.decision_id,
        turn.decision_option_key,
    )
    context = _provider_context(
        get_campaign_state(session, campaign_id),
        get_world_state(session, campaign_id),
        turn.target_npc_id,
        _choice_provider_context(choice),
    )
    attempt = _next_provider_attempt(session, turn.id, "narration")
    player_action = turn.player_action
    turn.status = "narrating"
    turn.stage_started_at = datetime.now(UTC)
    session.commit()

    context = _with_historical_memory(
        context,
        memory_context_service,
        campaign_id=campaign_id,
        turn_id=turn_id,
        stage="narration",
        player_action=player_action,
    )

    started = perf_counter()
    try:
        provider_result = provider.narrate_outcome(
            context,
            player_action,
            intent,
            resolution,
        )
        provider_output, input_tokens, output_tokens = _unpack_provider_result(provider_result)
        if provider_output is None:
            raise ProviderEmptyOutputError
        output = TurnNarrationOutput.model_validate(provider_output)
        expected_resolution_id = resolution.id if resolution else None
        expected_outcome = resolution.outcome if resolution else None
        if output.resolution_id != expected_resolution_id:
            raise _NarrationAcknowledgementError(
                "Narration did not acknowledge the stored resolution"
            )
        if output.acknowledged_outcome != expected_outcome:
            raise _NarrationAcknowledgementError("Narration did not acknowledge the stored outcome")
    except Exception as exc:
        latency_ms = max(0, round((perf_counter() - started) * 1000))
        if isinstance(exc, _NarrationAcknowledgementError):
            error_code = "invalid_outcome_acknowledgement"
            safe_detail = str(exc)
        else:
            error_code, safe_detail = _provider_failure("narration", exc)
        _record_narration_failure(
            session,
            campaign_id,
            turn_id,
            attempt=attempt,
            provider=provider,
            latency_ms=latency_ms,
            error_code=error_code,
            error_detail=safe_detail,
            resume_status=resume_status,
        )
        raise TurnNarrationError(
            safe_detail,
            turn_id=turn_id,
            stage="narration",
            error_code=error_code,
            resumable=True,
        ) from exc

    latency_ms = max(0, round((perf_counter() - started) * 1000))
    campaign = _campaign_for_update(session, campaign_id)
    turn = session.scalar(
        select(Turn).where(Turn.campaign_id == campaign_id, Turn.id == turn_id).with_for_update()
    )
    assert turn is not None
    if turn.status != "narrating":
        raise ConflictError("Turn changed while narration was running")
    character = session.scalar(
        select(Character)
        .where(Character.id == turn.actor_character_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    current_location = session.scalar(
        select(Location)
        .where(
            Location.campaign_id == campaign_id,
            Location.is_current.is_(True),
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    stale_world = campaign.world_revision != turn.world_revision_before
    stale_state = (
        character is None
        or character.state_revision != turn.state_revision_before
        or current_location is None
        or current_location.id != location_id_before
        or stale_world
    )
    if stale_state:
        _record_narration_failure(
            session,
            campaign_id,
            turn_id,
            attempt=attempt,
            provider=provider,
            latency_ms=latency_ms,
            error_code="stale_world_state" if stale_world else "stale_campaign_state",
            error_detail=(
                "Campaign world changed during narration"
                if stale_world
                else "Campaign state changed during narration"
            ),
            resume_status=None,
            output=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        raise ConflictError(
            "Campaign world changed during narration"
            if stale_world
            else "Campaign state changed during narration"
        )
    assert character is not None
    try:
        StateChangeValidator().validate(
            _character_snapshot(campaign, character), output.state_changes
        )
        (
            touched_quests,
            touched_objectives,
            attitude_subjects,
            proposed_fact_records,
        ) = _validate_world_changes(session, campaign_id, output.state_changes)
        choice = _validated_turn_choice(
            session,
            campaign_id,
            turn.decision_id,
            turn.decision_option_key,
            occupied_quests=touched_quests,
            occupied_objectives=touched_objectives,
            occupied_attitude_subjects=attitude_subjects,
            occupied_fact_records=proposed_fact_records,
        )
    except InvalidStateChange as exc:
        _record_narration_failure(
            session,
            campaign_id,
            turn_id,
            attempt=attempt,
            provider=provider,
            latency_ms=latency_ms,
            error_code="invalid_state_proposal",
            error_detail=str(exc),
            resume_status=resume_status,
            output=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        raise

    session.add(
        ProviderCall(
            campaign_id=campaign_id,
            turn_id=turn_id,
            stage="narration",
            attempt=attempt,
            provider=provider.provider_name,
            model=provider.model_name,
            prompt_version=provider.narration_prompt_version,
            status="succeeded",
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            structured_output=output.model_dump(mode="json"),
        )
    )
    turn.dm_narration = output.narration
    turn.provider = provider.provider_name
    turn.model = provider.model_name
    turn.structured_output = output.model_dump(mode="json")
    turn.narration_prompt_version = provider.narration_prompt_version
    if choice is not None:
        _apply_decision_choice(
            session,
            campaign,
            turn,
            choice,
            actor_character_id=character.id,
        )
    _add_event(
        session,
        campaign_id,
        "dm_response",
        {
            "narration": output.narration,
            "resolution_id": str(resolution.id) if resolution else None,
            "outcome": resolution.outcome if resolution else None,
        },
        turn_id=turn.id,
        actor_character_id=character.id,
    )
    _apply_state_changes(
        session,
        campaign_id,
        character,
        output.state_changes,
        turn_id=turn.id,
        actor_character_id=character.id,
    )
    turn.state_revision_after = character.state_revision
    turn.world_revision_after = campaign.world_revision
    if output.state_changes:
        _add_event(
            session,
            campaign_id,
            "state_changed",
            {
                "changes": [change.model_dump(mode="json") for change in output.state_changes],
                "affected_character_ids": [str(character.id)],
            },
            turn_id=turn.id,
            actor_character_id=character.id,
        )
    turn.status = "completed"
    turn.stage_started_at = None
    turn.completed_at = datetime.now(UTC)
    session.commit()
    _project_completed_turn_best_effort(session, turn)
    session.refresh(turn)
    return _turn_finalization_result(session, campaign_id, turn, intent)


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
    support_status = getattr(document, "support_status", "character_creation")
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
    party_mode = isinstance(loaded_catalog.document, CharacterStateCatalog)
    if party_mode:
        catalogs = registry.get_character_catalogs(data.ruleset_release_id, loaded_catalog.id)
        base_catalog = loaded_release.data_catalogs.get(catalogs.character_creation.id)
        if base_catalog is not None:
            _ensure_ruleset_data_catalog(session, base_catalog, loaded_release.manifest.id)
    campaign = Campaign(
        name=data.name,
        ruleset_release_id=loaded_release.manifest.id,
        ruleset_data_catalog_id=loaded_catalog.id,
        play_mode="party_commander" if party_mode else "legacy_single",
        party_min_active=2 if party_mode else 1,
        party_max_active=4 if party_mode else 1,
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
    session.flush()
    _add_event(
        session,
        campaign.id,
        "campaign_created",
        {
            "name": campaign.name,
            "starting_location": location.name,
            "ruleset_release_id": campaign.ruleset_release_id,
            "ruleset_data_catalog_id": campaign.ruleset_data_catalog_id,
            "play_mode": campaign.play_mode,
            "party_size": {
                "minimum": campaign.party_min_active,
                "maximum": campaign.party_max_active,
            },
        },
    )
    scene_input = data.starting_scene
    scene = Scene(
        campaign_id=campaign.id,
        location_id=location.id,
        sequence=1,
        title=scene_input.title if scene_input else location.name,
        summary=scene_input.summary if scene_input else location.description,
        status="active",
        revision=0,
    )
    session.add(scene)
    session.flush()
    scene_event = _add_event(
        session,
        campaign.id,
        "scene_opened",
        {
            "scene_id": str(scene.id),
            "location_id": str(location.id),
            "title": scene.title,
            "world_revision": campaign.world_revision,
        },
    )
    scene.opened_by_event_id = scene_event.id
    for npc_input in scene_input.npcs if scene_input else []:
        npc = NPC(
            campaign_id=campaign.id,
            name=npc_input.name,
            public_description=npc_input.public_description,
            status="active",
            visibility="player",
            revision=0,
        )
        session.add(npc)
        session.flush()
        introduced = _add_event(
            session,
            campaign.id,
            "npc_introduced",
            {
                "npc_id": str(npc.id),
                "name": npc.name,
                "public_description": npc.public_description,
                "world_revision": campaign.world_revision,
            },
        )
        npc.introduced_by_event_id = introduced.id
        arrived = _add_event(
            session,
            campaign.id,
            "npc_arrived",
            {
                "npc_id": str(npc.id),
                "scene_id": str(scene.id),
                "world_revision": campaign.world_revision,
            },
        )
        session.add(
            SceneNPCPresence(
                campaign_id=campaign.id,
                scene_id=scene.id,
                npc_id=npc.id,
                status="present",
                revision=0,
                arrived_by_event_id=arrived.id,
            )
        )
    session.commit()
    return campaign


def add_character(session: Session, campaign_id: uuid.UUID, data: CharacterCreate) -> Character:
    campaign = _campaign_for_update(session, campaign_id)
    characters = list(
        session.scalars(
            select(Character)
            .where(Character.campaign_id == campaign_id)
            .order_by(Character.party_position)
            .with_for_update()
        )
    )
    if len(characters) >= campaign.party_max_active:
        raise ConflictError(f"A campaign supports at most {campaign.party_max_active} characters")
    try:
        catalogs = get_ruleset_registry().get_character_catalogs(
            campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
        )
    except UnknownRulesetDataCatalogError:
        raise ConflictError(
            "Campaign data catalog does not support guided character creation"
        ) from None
    if campaign.play_mode != "party_commander" or catalogs.character_state is None:
        raise ConflictError("Campaign data catalog does not support guided character creation")
    occupied = {character.party_position for character in characters}
    party_position = next(position for position in range(1, 5) if position not in occupied)
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
        party_position=party_position,
        control_mode="player",
        party_status="active",
        state_revision=0,
        equipped_items=Loadout().model_dump(mode="json"),
        resources={},
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
            "party_position": character.party_position,
            "control_mode": character.control_mode,
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
    session: Session,
    campaign_id: uuid.UUID,
    data: CharacterFinalizeRequest,
    character_id: uuid.UUID | None = None,
) -> Character:
    campaign = _campaign_for_update(session, campaign_id)
    query = select(Character).where(Character.campaign_id == campaign_id)
    if character_id is not None:
        query = query.where(Character.id == character_id)
    else:
        query = query.where(Character.creation_status == "draft").order_by(Character.party_position)
    character = session.scalar(query.with_for_update())
    if character is None:
        if character_id is None and session.scalar(
            select(Character.id).where(Character.campaign_id == campaign_id).limit(1)
        ):
            raise ConflictError("No character draft is available to finalize")
        raise NotFoundError("Character draft not found")
    if character.creation_status != "draft":
        raise ConflictError("Character has already been finalized")
    try:
        catalogs = get_ruleset_registry().get_character_catalogs(
            campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
        )
    except UnknownRulesetDataCatalogError:
        raise ConflictError(
            "Campaign data catalog does not support guided character creation"
        ) from None
    if catalogs.character_state is None:
        raise ConflictError("Campaign data catalog does not support guided character creation")
    sheet = finalize_character_choices(catalogs.character_creation, data)

    character.creation_status = "finalized"
    character.revision = 1
    character.max_hp = sheet.max_hp
    character.hp = sheet.max_hp
    character.inventory = sheet.starting_inventory
    character.character_sheet = sheet.model_dump(mode="json")
    character.finalized_at = datetime.now(UTC)
    character.equipped_items = initial_loadout(catalogs.character_state).model_dump(mode="json")
    character.resources = initial_resources(catalogs.character_state)
    character.state_revision = 1
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
            "party_position": character.party_position,
            "loadout": character.equipped_items,
            "resources": character.resources,
        },
        actor_character_id=character.id,
    )
    session.add_all(
        _build_character_grants(
            character,
            event,
            data,
            catalogs.character_creation,
        )
    )
    session.commit()
    return character


def list_character_grants(
    session: Session, campaign_id: uuid.UUID, character_id: uuid.UUID | None = None
) -> list[CharacterGrant]:
    query = select(Character).where(Character.campaign_id == campaign_id)
    if character_id is not None:
        query = query.where(Character.id == character_id)
    else:
        query = query.order_by(Character.party_position)
    character = session.scalar(query)
    if character is None:
        raise NotFoundError("Character not found")
    return list(
        session.scalars(
            select(CharacterGrant)
            .where(CharacterGrant.character_id == character.id)
            .order_by(CharacterGrant.choice_slot, CharacterGrant.definition_key)
        )
    )


def list_characters(session: Session, campaign_id: uuid.UUID) -> list[Character]:
    if session.get(Campaign, campaign_id) is None:
        raise NotFoundError("Campaign not found")
    return list(
        session.scalars(
            select(Character)
            .where(Character.campaign_id == campaign_id)
            .order_by(Character.party_position)
        )
    )


def get_character_read(
    session: Session, campaign_id: uuid.UUID, character_id: uuid.UUID
) -> CharacterRead:
    campaign = session.get(Campaign, campaign_id)
    character = session.scalar(
        select(Character).where(Character.campaign_id == campaign_id, Character.id == character_id)
    )
    if campaign is None or character is None:
        raise NotFoundError("Character not found")
    try:
        catalogs = get_ruleset_registry().get_character_catalogs(
            campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
        )
    except UnknownRulesetDataCatalogError:
        return CharacterRead.model_validate(character)
    return _character_read(
        session, character, catalogs.character_creation, catalogs.character_state
    )


def _character_read(
    session: Session,
    character: Character,
    creation_catalog: CharacterCreationCatalog,
    state_catalog: CharacterStateCatalog | None,
) -> CharacterRead:
    mechanical_state = None
    if character.creation_status == "finalized" and state_catalog is not None:
        sheet = CharacterSheet.model_validate(character.character_sheet)
        grants = list(
            session.scalars(
                select(CharacterGrant)
                .where(CharacterGrant.character_id == character.id, CharacterGrant.active.is_(True))
                .order_by(CharacterGrant.choice_slot, CharacterGrant.definition_key)
            )
        )
        grant_facts = [
            GrantProvenanceFact(
                choice_slot=grant.choice_slot,
                definition_key=grant.definition_key,
                source_definition_key=grant.source_definition_key,
                source_ids=list(grant.value.get("source_ids", [])),
                acquisition_event_id=str(grant.acquisition_event_id),
            )
            for grant in grants
        ]
        mechanical_state = derive_character_state(
            creation_catalog,
            state_catalog,
            sheet,
            hp=character.hp or 0,
            inventory=dict(character.inventory),
            loadout=Loadout.model_validate(character.equipped_items),
            resource_values=dict(character.resources),
            grants=grant_facts,
            character_revision=character.revision,
            state_revision=character.state_revision,
        )
    return CharacterRead.model_validate(character).model_copy(
        update={"mechanical_state": mechanical_state}
    )


def get_campaign_state(session: Session, campaign_id: uuid.UUID) -> CampaignState:
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise NotFoundError("Campaign not found")
    characters = list(
        session.scalars(
            select(Character)
            .where(Character.campaign_id == campaign_id)
            .order_by(Character.party_position)
        )
    )
    try:
        catalogs = get_ruleset_registry().get_character_catalogs(
            campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
        )
    except UnknownRulesetDataCatalogError:
        character_reads = [CharacterRead.model_validate(character) for character in characters]
    else:
        character_reads = [
            _character_read(
                session,
                character,
                catalogs.character_creation,
                catalogs.character_state,
            )
            for character in characters
        ]
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
        character=character_reads[0] if len(character_reads) == 1 else None,
        characters=character_reads,
        party_ready=sum(
            character.creation_status == "finalized" and character.party_status == "active"
            for character in characters
        )
        >= campaign.party_min_active,
        location=location,
        turn_count=turn_count or 0,
    )


def update_character_loadout(
    session: Session,
    campaign_id: uuid.UUID,
    character_id: uuid.UUID,
    data: LoadoutUpdate,
) -> CharacterRead:
    campaign = _campaign_for_update(session, campaign_id)
    character = session.scalar(
        select(Character)
        .where(Character.campaign_id == campaign_id, Character.id == character_id)
        .with_for_update()
    )
    if character is None:
        raise NotFoundError("Character not found")
    if character.creation_status != "finalized":
        raise ConflictError("Character must be finalized before changing loadout")
    catalogs = get_ruleset_registry().get_character_catalogs(
        campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
    )
    if catalogs.character_state is None:
        raise ConflictError("Campaign does not support equipment state")
    loadout = validate_loadout(
        catalogs.character_creation,
        catalogs.character_state,
        dict(character.inventory),
        Loadout.model_validate(data.model_dump()),
    )
    character.equipped_items = loadout.model_dump(mode="json")
    character.state_revision += 1
    _add_event(
        session,
        campaign_id,
        "character_loadout_changed",
        {
            "character_id": str(character.id),
            "state_revision": character.state_revision,
            "loadout": character.equipped_items,
        },
        actor_character_id=character.id,
    )
    session.commit()
    return _character_read(
        session,
        character,
        catalogs.character_creation,
        catalogs.character_state,
    )


def _resolution_read(resolution: RuleResolution) -> RuleResolutionRead:
    return RuleResolutionRead.model_validate(resolution)


def create_rule_resolution(
    session: Session,
    campaign_id: uuid.UUID,
    data: ResolutionCreate,
    dice_service: DiceService | None = None,
    *,
    turn_id: uuid.UUID | None = None,
) -> RuleResolutionRead:
    campaign = _campaign_for_update(session, campaign_id)
    active = _active_turn(session, campaign_id)
    if active is not None and (turn_id is None or active.id != turn_id):
        raise ConflictError(f"Campaign already has active turn {active.id}")
    command = data.model_dump(mode="json")
    existing = session.scalar(
        select(RuleResolution).where(
            RuleResolution.campaign_id == campaign_id,
            RuleResolution.command_id == data.command_id,
        )
    )
    if existing is not None:
        if existing.command != command:
            raise ConflictError("command_id was already used for a different resolution command")
        if turn_id is not None:
            existing_roll = session.get(DiceRoll, existing.dice_roll_id)
            if existing_roll is None or existing_roll.turn_id != turn_id:
                raise ConflictError("Existing resolution belongs to a different command path")
        return _resolution_read(existing)

    if data.ruleset_release_id != campaign.ruleset_release_id:
        raise ConflictError("Resolution ruleset release does not match the campaign pin")
    if data.character_state_catalog_id != campaign.ruleset_data_catalog_id:
        raise ConflictError("Resolution character-state catalog does not match the campaign pin")
    state = get_campaign_state(session, campaign_id)
    if campaign.play_mode == "party_commander" and not state.party_ready:
        raise ConflictError(
            f"At least {campaign.party_min_active} finalized active characters are required"
        )
    character = session.scalar(
        select(Character)
        .where(Character.campaign_id == campaign_id, Character.id == data.actor_character_id)
        .with_for_update()
    )
    if character is None:
        raise NotFoundError("Acting character not found in campaign")
    if character.creation_status != "finalized" or character.party_status != "active":
        raise ConflictError("Acting character must be finalized and active")

    registry = get_ruleset_registry()
    try:
        catalogs = registry.get_resolution_catalogs(
            campaign.ruleset_release_id,
            campaign.ruleset_data_catalog_id,
            data.resolution_catalog_id,
        )
    except UnknownRulesetDataCatalogError as exc:
        raise ConflictError(str(exc)) from exc
    resolution_catalog = catalogs.resolution.document
    if not isinstance(resolution_catalog, ResolutionRulesCatalog):
        raise ConflictError("Selected data catalog does not support rule resolution")
    _ensure_ruleset_data_catalog(session, catalogs.resolution, campaign.ruleset_release_id)

    character_read = _character_read(
        session,
        character,
        catalogs.character_creation,
        catalogs.character_state,
    )
    mechanical_state = character_read.mechanical_state
    if mechanical_state is None:
        raise ConflictError("Acting character has no authoritative mechanical state")
    if data.resolution_type == "ability_check" and data.skill is not None:
        known_skills = {skill.id for skill in catalogs.character_creation.skills}
        if data.skill not in known_skills:
            raise ResolutionError(f"Unknown skill for this ruleset: {data.skill}")

    automatic_disadvantage: list[AppliedAdjustmentSource] = []
    if (
        data.resolution_type == "ability_check"
        and data.ability == "dexterity"
        and data.skill == "stealth"
    ):
        loadout = Loadout.model_validate(character.equipped_items)
        worn = next(
            (
                item
                for item in catalogs.character_state.equipment
                if item.item_id == loadout.worn_armor_item_id
            ),
            None,
        )
        if worn is not None and worn.stealth_disadvantage:
            automatic_disadvantage.append(
                AppliedAdjustmentSource(
                    definition_key=worn.definition_key,
                    reason=f"Worn {worn.item_name} imposes Disadvantage on Stealth checks",
                    source_ids=list(worn.source_ids),
                    automatic=True,
                )
            )

    advantage_state = determine_advantage_state(
        has_advantage=bool(data.advantage_reasons),
        has_disadvantage=bool(data.disadvantage_reasons or automatic_disadvantage),
    )
    dice_notation = "1d20" if advantage_state == "normal" else "2d20"
    roller = dice_service or DiceService()
    rolled = roller.roll(dice_notation)
    resolved = resolve_d20_test(
        data,
        mechanical_state,
        catalogs.character_creation,
        catalogs.character_state,
        resolution_catalog,
        rolled.rolls,
        automatic_disadvantage_sources=automatic_disadvantage,
    )

    roll = DiceRoll(
        campaign_id=campaign_id,
        ruleset_release_id=campaign.ruleset_release_id,
        ruleset_data_catalog_id=resolution_catalog.id,
        turn_id=turn_id,
        notation=resolved.dice_notation,
        rolls=resolved.dice_faces,
        modifier=resolved.modifier,
        total=resolved.total,
        purpose=(
            f"{resolved.resolution_type}: {resolved.ability}"
            + (f" ({resolved.skill})" if resolved.skill else "")
        ),
        hidden=False,
        actor_character_id=character.id,
    )
    session.add(roll)
    session.flush()

    resolution = RuleResolution(
        command_id=data.command_id,
        campaign_id=campaign_id,
        actor_character_id=character.id,
        ruleset_release_id=campaign.ruleset_release_id,
        character_state_catalog_id=campaign.ruleset_data_catalog_id,
        ruleset_data_catalog_id=resolution_catalog.id,
        dice_roll_id=roll.id,
        character_revision=resolved.character_revision,
        state_revision=resolved.state_revision,
        resolution_type=resolved.resolution_type,
        ability=resolved.ability,
        skill=resolved.skill,
        difficulty_class=resolved.difficulty_class,
        rule_definition_keys=resolved.rule_definition_keys,
        source_ids=resolved.source_ids,
        command=command,
        modifier_formula=resolved.modifier_formula,
        modifier_components=[
            component.model_dump(mode="json") for component in resolved.modifier_components
        ],
        advantage_sources=[source.model_dump(mode="json") for source in resolved.advantage_sources],
        disadvantage_sources=[
            source.model_dump(mode="json") for source in resolved.disadvantage_sources
        ],
        advantage_state=resolved.advantage_state,
        dice_notation=resolved.dice_notation,
        dice_faces=resolved.dice_faces,
        selected_die=resolved.selected_die,
        modifier=resolved.modifier,
        total=resolved.total,
        outcome=resolved.outcome,
        resolver_version=resolved.resolver_version,
        rng_version=roller.algorithm_version,
    )
    session.add(resolution)
    session.flush()
    _add_event(
        session,
        campaign_id,
        "rule_resolved",
        {
            "resolution_id": str(resolution.id),
            "command_id": str(resolution.command_id),
            "actor_character_id": str(character.id),
            "resolution_catalog_id": resolution.ruleset_data_catalog_id,
            "character_state_catalog_id": resolution.character_state_catalog_id,
            "resolution": resolved.model_dump(mode="json"),
            "dice_roll_id": str(roll.id),
            "rng_version": resolution.rng_version,
        },
        turn_id=turn_id,
        actor_character_id=character.id,
    )
    session.commit()
    return _resolution_read(resolution)


def get_rule_resolution(
    session: Session,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
) -> RuleResolutionRead:
    resolution = session.scalar(
        select(RuleResolution).where(
            RuleResolution.campaign_id == campaign_id,
            RuleResolution.id == resolution_id,
        )
    )
    if resolution is None:
        raise NotFoundError("Rule resolution not found")
    return _resolution_read(resolution)


def list_rule_resolutions(
    session: Session,
    campaign_id: uuid.UUID,
) -> list[RuleResolutionRead]:
    if session.get(Campaign, campaign_id) is None:
        raise NotFoundError("Campaign not found")
    return [
        _resolution_read(resolution)
        for resolution in session.scalars(
            select(RuleResolution)
            .where(RuleResolution.campaign_id == campaign_id)
            .order_by(RuleResolution.created_at, RuleResolution.id)
        )
    ]


def replay_rule_resolution(
    session: Session,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
) -> RuleResolutionReplayRead:
    original = get_rule_resolution(session, campaign_id, resolution_id)
    try:
        catalogs = get_ruleset_registry().get_resolution_catalogs(
            original.ruleset_release_id,
            original.character_state_catalog_id,
            original.ruleset_data_catalog_id,
        )
    except UnknownRulesetDataCatalogError as exc:
        raise ResolutionError(str(exc)) from exc
    catalog = catalogs.resolution.document
    if not isinstance(catalog, ResolutionRulesCatalog):
        raise ResolutionError("Stored resolution catalog is not available")
    if catalog.resolver_version != original.resolver_version:
        raise ResolutionError("Stored resolution resolver version is not available")
    known_rule_keys = {rule.definition_key for rule in catalog.rules}
    if not set(original.rule_definition_keys) <= known_rule_keys:
        raise ResolutionError("Stored resolution cites definitions outside its pinned catalog")

    advantage_state = determine_advantage_state(
        has_advantage=bool(original.advantage_sources),
        has_disadvantage=bool(original.disadvantage_sources),
    )
    modifier = sum(
        component.value for component in original.modifier_components if component.applied
    )
    selected_die, total, outcome = replay_d20_values(
        advantage_state,
        original.dice_faces,
        modifier,
        original.difficulty_class,
    )
    equivalent = (
        advantage_state == original.advantage_state
        and modifier == original.modifier
        and selected_die == original.selected_die
        and total == original.total
        and outcome == original.outcome
    )
    replayed = original.model_copy(
        update={
            "advantage_state": advantage_state,
            "modifier": modifier,
            "selected_die": selected_die,
            "total": total,
            "outcome": outcome,
        }
    )
    return RuleResolutionReplayRead(
        resolution_id=resolution_id,
        equivalent=equivalent,
        replayed=replayed,
    )


def _combat_event(
    session: Session,
    encounter_id: uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
) -> CombatEvent:
    sequence = session.scalar(
        select(func.max(CombatEvent.sequence)).where(CombatEvent.encounter_id == encounter_id)
    )
    event = CombatEvent(
        encounter_id=encounter_id,
        sequence=(sequence or 0) + 1,
        event_type=event_type,
        visibility="player",
        payload=payload,
    )
    session.add(event)
    session.flush()
    return event


def _combat_encounter_read(session: Session, encounter: CombatEncounter) -> CombatEncounterRead:
    combatants = list(
        session.scalars(select(Combatant).where(Combatant.encounter_id == encounter.id))
    )
    combatants.sort(
        key=lambda item: (
            item.initiative_order if item.initiative_order is not None else 1_000,
            0 if item.side == "party" else 1,
            int(item.source_snapshot.get("party_position", 1_000)),
            int(item.source_snapshot.get("instance_ordinal", 1_000)),
            item.instance_name,
        )
    )
    ties = list(
        session.scalars(
            select(CombatInitiativeTie)
            .where(CombatInitiativeTie.encounter_id == encounter.id)
            .order_by(CombatInitiativeTie.initiative_total.desc())
        )
    )
    events = list(
        session.scalars(
            select(CombatEvent)
            .where(CombatEvent.encounter_id == encounter.id)
            .order_by(CombatEvent.sequence)
        )
    )
    current_turn = session.scalar(
        select(CombatTurn).where(
            CombatTurn.encounter_id == encounter.id,
            CombatTurn.status == "active",
        )
    )
    effects = list(
        session.scalars(
            select(CombatEffect)
            .where(CombatEffect.encounter_id == encounter.id)
            .order_by(CombatEffect.created_at, CombatEffect.id)
        )
    )
    reaction_windows = list(
        session.scalars(
            select(CombatReactionWindow)
            .where(CombatReactionWindow.encounter_id == encounter.id)
            .order_by(CombatReactionWindow.created_at, CombatReactionWindow.id)
        )
    )
    return CombatEncounterRead(
        id=encounter.id,
        campaign_id=encounter.campaign_id,
        scene_id=encounter.scene_id,
        ruleset_release_id=encounter.ruleset_release_id,
        character_state_catalog_id=encounter.character_state_catalog_id,
        combat_catalog_id=encounter.combat_catalog_id,
        combat_catalog_sha256=encounter.combat_catalog_sha256,
        resolver_version=encounter.resolver_version,
        status=encounter.status,
        revision=encounter.revision,
        grid_width=encounter.grid_width,
        grid_height=encounter.grid_height,
        round_number=encounter.round_number,
        active_turn_index=encounter.active_turn_index,
        difficulty_label=encounter.difficulty_label,
        enemy_xp=encounter.enemy_xp,
        low_xp_budget=encounter.low_xp_budget,
        moderate_xp_budget=encounter.moderate_xp_budget,
        high_xp_budget=encounter.high_xp_budget,
        outcome=encounter.outcome,
        outcome_summary=encounter.outcome_summary,
        completed_at=encounter.completed_at,
        combatants=[CombatantRead.model_validate(item) for item in combatants],
        initiative_ties=[CombatInitiativeTieRead.model_validate(item) for item in ties],
        current_turn=(CombatTurnRead.model_validate(current_turn) if current_turn else None),
        effects=[CombatEffectRead.model_validate(item) for item in effects],
        reaction_windows=[
            CombatReactionWindowRead.model_validate(item) for item in reaction_windows
        ],
        events=[CombatEventRead.model_validate(item) for item in events],
        created_at=encounter.created_at,
    )


def _existing_combat_command(
    session: Session,
    campaign_id: uuid.UUID,
    command_id: uuid.UUID,
    command_type: str,
    payload: dict[str, Any],
) -> CombatCommand | None:
    existing = session.scalar(
        select(CombatCommand).where(
            CombatCommand.campaign_id == campaign_id,
            CombatCommand.command_id == command_id,
        )
    )
    if existing is None:
        return None
    if existing.command_type != command_type or existing.payload != payload:
        raise ConflictError("command_id was already used for a different combat command")
    return existing


def _load_combat_catalog(
    session: Session,
    campaign: Campaign,
    combat_catalog_id: str,
) -> tuple[LoadedRulesetDataCatalog, CombatRulesCatalog, Any, Any]:
    try:
        catalogs = get_ruleset_registry().get_combat_catalogs(
            campaign.ruleset_release_id,
            campaign.ruleset_data_catalog_id,
            combat_catalog_id,
        )
    except UnknownRulesetDataCatalogError as exc:
        raise ConflictError(str(exc)) from exc
    document = catalogs.combat.document
    if not isinstance(document, CombatRulesCatalog):
        raise ConflictError("Selected data catalog does not support combat")
    _ensure_ruleset_data_catalog(session, catalogs.combat, campaign.ruleset_release_id)
    return catalogs.combat, document, catalogs.character_creation, catalogs.character_state


def create_combat_encounter(
    session: Session,
    campaign_id: uuid.UUID,
    data: CombatEncounterCreate,
) -> CombatEncounterRead:
    campaign = _campaign_for_update(session, campaign_id)
    payload = data.model_dump(mode="json")
    existing_command = _existing_combat_command(
        session, campaign_id, data.command_id, "create_encounter", payload
    )
    if existing_command is not None:
        encounter = session.get(CombatEncounter, existing_command.encounter_id)
        if encounter is None:
            raise ConflictError("Recorded combat command has no encounter")
        return _combat_encounter_read(session, encounter)
    if campaign.status != "active":
        raise ConflictError("Archived campaigns cannot start combat")
    if campaign.world_revision != data.expected_world_revision:
        raise ConflictError(
            f"Stale world revision: expected {data.expected_world_revision}, "
            f"current {campaign.world_revision}"
        )
    scene = session.scalar(
        select(Scene).where(
            Scene.id == data.scene_id,
            Scene.campaign_id == campaign_id,
            Scene.status == "active",
        )
    )
    if scene is None:
        raise ConflictError("Combat must use the campaign's active scene")
    open_encounter = session.scalar(
        select(CombatEncounter).where(
            CombatEncounter.campaign_id == campaign_id,
            CombatEncounter.status.in_(("setup", "tie_pending", "active")),
        )
    )
    if open_encounter is not None:
        raise ConflictError(f"Campaign already has open combat encounter {open_encounter.id}")

    active_characters = list(
        session.scalars(
            select(Character)
            .where(
                Character.campaign_id == campaign_id,
                Character.creation_status == "finalized",
                Character.party_status == "active",
            )
            .order_by(Character.party_position)
            .with_for_update()
        )
    )
    if not campaign.party_min_active <= len(active_characters) <= campaign.party_max_active:
        raise ConflictError(
            f"Combat requires {campaign.party_min_active}-{campaign.party_max_active} "
            "finalized active party characters"
        )
    requested_ids = {item.character_id for item in data.party}
    active_ids = {item.id for item in active_characters}
    if requested_ids != active_ids:
        raise ConflictError(
            "Combat setup must place every finalized active party character exactly once"
        )
    unavailable_characters: list[str] = []
    for character in active_characters:
        latest_combatant = session.scalar(
            select(Combatant)
            .join(CombatEncounter, CombatEncounter.id == Combatant.encounter_id)
            .where(
                Combatant.character_id == character.id,
                CombatEncounter.status == "completed",
            )
            .order_by(CombatEncounter.completed_at.desc(), CombatEncounter.created_at.desc())
            .limit(1)
        )
        if (
            character.hp is None
            or character.hp <= 0
            or (latest_combatant is not None and latest_combatant.state != "active")
        ):
            unavailable_characters.append(character.name)
    if unavailable_characters:
        raise ConflictError(
            "Combat cannot start while party characters require recovery: "
            f"{sorted(unavailable_characters)}. Out-of-combat recovery is not yet supported."
        )

    loaded, catalog, creation_catalog, state_catalog = _load_combat_catalog(
        session, campaign, data.combat_catalog_id
    )
    monster_by_id = {monster.id: monster for monster in catalog.monsters}
    unknown_monsters = {
        enemy.monster_definition_id
        for enemy in data.enemies
        if enemy.monster_definition_id not in monster_by_id
    }
    if unknown_monsters:
        raise ConflictError(f"Unsupported monster definitions: {sorted(unknown_monsters)}")

    party_size = len(active_characters)
    enemy_xp = sum(
        monster_by_id[enemy.monster_definition_id].experience_points for enemy in data.enemies
    )
    low_xp_budget = party_size * catalog.encounter_budget.low_xp_per_character
    moderate_xp_budget = party_size * catalog.encounter_budget.moderate_xp_per_character
    high_xp_budget = party_size * catalog.encounter_budget.high_xp_per_character
    difficulty_label = (
        "favorable"
        if enemy_xp < low_xp_budget
        else "low"
        if enemy_xp < moderate_xp_budget
        else "moderate"
        if enemy_xp < high_xp_budget
        else "high"
    )

    encounter = CombatEncounter(
        campaign_id=campaign_id,
        scene_id=scene.id,
        ruleset_release_id=campaign.ruleset_release_id,
        character_state_catalog_id=campaign.ruleset_data_catalog_id,
        combat_catalog_id=loaded.id,
        combat_catalog_sha256=loaded.sha256,
        resolver_version=catalog.resolver_version,
        status="setup",
        revision=0,
        grid_width=data.grid_width,
        grid_height=data.grid_height,
        round_number=0,
        active_turn_index=None,
        difficulty_label=difficulty_label,
        enemy_xp=enemy_xp,
        low_xp_budget=low_xp_budget,
        moderate_xp_budget=moderate_xp_budget,
        high_xp_budget=high_xp_budget,
        outcome=None,
        outcome_summary=None,
        completed_at=None,
    )
    session.add(encounter)
    session.flush()

    placement_by_character = {item.character_id: item for item in data.party}
    for character in active_characters:
        character_read = _character_read(session, character, creation_catalog, state_catalog)
        mechanics = character_read.mechanical_state
        if mechanics is None or character.hp is None or character.max_hp is None:
            raise ConflictError(f"Character {character.name!r} has no authoritative combat state")
        placement = placement_by_character[character.id]
        session.add(
            Combatant(
                encounter_id=encounter.id,
                side="party",
                character_id=character.id,
                monster_definition_id=None,
                instance_name=character.name,
                source_snapshot={
                    "character_revision": character.revision,
                    "state_revision": character.state_revision,
                    "party_position": character.party_position,
                    "character_state_resolver_version": mechanics.resolver_version,
                    "initiative_provenance": mechanics.initiative.provenance.model_dump(
                        mode="json"
                    ),
                },
                max_hp=character.max_hp,
                hp=character.hp,
                temporary_hp=0,
                armor_class=mechanics.armor_class.value,
                speed_feet=mechanics.speed_feet.value,
                position_x=placement.x,
                position_y=placement.y,
                initiative_modifier=mechanics.initiative.value,
                state="active",
                death_save_successes=0,
                death_save_failures=0,
                second_wind_remaining=character.resources.get("second_wind", 0),
                revision=0,
            )
        )
    for ordinal, enemy in enumerate(data.enemies, start=1):
        monster = monster_by_id[enemy.monster_definition_id]
        session.add(
            Combatant(
                encounter_id=encounter.id,
                side="enemy",
                character_id=None,
                monster_definition_id=monster.id,
                instance_name=enemy.instance_name,
                source_snapshot={
                    "definition_key": monster.definition_key,
                    "source_ids": list(monster.source_ids),
                    "instance_ordinal": ordinal,
                    "fixed_average_hit_points": True,
                },
                max_hp=monster.hit_points,
                hp=monster.hit_points,
                temporary_hp=0,
                armor_class=monster.armor_class,
                speed_feet=monster.speed_feet,
                position_x=enemy.x,
                position_y=enemy.y,
                initiative_modifier=monster.initiative_modifier,
                state="active",
                death_save_successes=0,
                death_save_failures=0,
                second_wind_remaining=None,
                revision=0,
            )
        )
    session.flush()
    combatants = list(
        session.scalars(select(Combatant).where(Combatant.encounter_id == encounter.id))
    )
    campaign.world_revision += 1
    _combat_event(
        session,
        encounter.id,
        "encounter_created",
        {
            "command_id": str(data.command_id),
            "scene_id": str(scene.id),
            "combat_catalog_id": loaded.id,
            "combat_catalog_sha256": loaded.sha256,
            "difficulty": {
                "label": difficulty_label,
                "enemy_xp": enemy_xp,
                "low_xp_budget": low_xp_budget,
                "moderate_xp_budget": moderate_xp_budget,
                "high_xp_budget": high_xp_budget,
                "interpretation": "published XP input, not a guaranteed balance result",
            },
            "grid": {"width": data.grid_width, "height": data.grid_height},
            "combatant_ids": [str(item.id) for item in combatants],
            "world_revision": campaign.world_revision,
        },
    )
    session.add(
        CombatCommand(
            command_id=data.command_id,
            campaign_id=campaign_id,
            encounter_id=encounter.id,
            command_type="create_encounter",
            expected_encounter_revision=None,
            payload=payload,
            result={"encounter_id": str(encounter.id), "encounter_revision": 0},
        )
    )
    _add_event(
        session,
        campaign_id,
        "combat_encounter_created",
        {
            "encounter_id": str(encounter.id),
            "scene_id": str(scene.id),
            "combatant_count": len(combatants),
            "combat_catalog_id": loaded.id,
            "world_revision": campaign.world_revision,
        },
    )
    session.commit()
    return _combat_encounter_read(session, encounter)


def get_combat_encounter(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
) -> CombatEncounterRead:
    encounter = session.scalar(
        select(CombatEncounter).where(
            CombatEncounter.id == encounter_id,
            CombatEncounter.campaign_id == campaign_id,
        )
    )
    if encounter is None:
        raise NotFoundError("Combat encounter not found")
    return _combat_encounter_read(session, encounter)


def _create_active_combat_turn(
    session: Session,
    encounter: CombatEncounter,
    combatants: list[Combatant],
) -> CombatTurn:
    if encounter.active_turn_index is None or encounter.round_number <= 0:
        raise ConflictError("Active encounter has no current turn position")
    actor = next(
        (item for item in combatants if item.initiative_order == encounter.active_turn_index),
        None,
    )
    if actor is None:
        raise ConflictError("Initiative order has no combatant for the active turn")
    if not actor.reaction_available:
        actor.reaction_available = True
        actor.revision += 1
    for effect in session.scalars(
        select(CombatEffect).where(
            CombatEffect.encounter_id == encounter.id,
            CombatEffect.source_combatant_id == actor.id,
            CombatEffect.status == "active",
            CombatEffect.expires_on_source_turn_start.is_(True),
        )
    ):
        effect.status = "expired"
        effect.ended_round = encounter.round_number
    slowed = session.scalar(
        select(CombatEffect.id).where(
            CombatEffect.encounter_id == encounter.id,
            CombatEffect.target_combatant_id == actor.id,
            CombatEffect.effect_id == "slow",
            CombatEffect.status == "active",
        )
    )
    turn = CombatTurn(
        encounter_id=encounter.id,
        combatant_id=actor.id,
        round_number=encounter.round_number,
        turn_index=encounter.active_turn_index,
        status="active",
        movement_allowance_feet=max(0, actor.speed_feet - (10 if slowed else 0)),
        movement_spent_feet=0,
        action_available=True,
        bonus_action_available=True,
        free_interaction_available=True,
        disengaged=False,
        started_encounter_revision=encounter.revision,
        completed_encounter_revision=None,
    )
    session.add(turn)
    session.flush()
    return turn


def start_combat_initiative(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    data: CombatStartCreate,
    dice_service: DiceService | None = None,
) -> CombatEncounterRead:
    campaign = _campaign_for_update(session, campaign_id)
    payload = data.model_dump(mode="json")
    existing_command = _existing_combat_command(
        session, campaign_id, data.command_id, "start_initiative", payload
    )
    if existing_command is not None:
        if existing_command.encounter_id != encounter_id:
            raise ConflictError("Existing combat command belongs to a different encounter")
        return get_combat_encounter(session, campaign_id, encounter_id)
    encounter = session.scalar(
        select(CombatEncounter)
        .where(CombatEncounter.id == encounter_id, CombatEncounter.campaign_id == campaign_id)
        .with_for_update()
    )
    if encounter is None:
        raise NotFoundError("Combat encounter not found")
    if encounter.status != "setup":
        raise ConflictError("Initiative can only start from encounter setup")
    if encounter.revision != data.expected_encounter_revision:
        raise ConflictError(
            f"Stale encounter revision: expected {data.expected_encounter_revision}, "
            f"current {encounter.revision}"
        )
    scene_active = session.scalar(
        select(Scene.id).where(
            Scene.id == encounter.scene_id,
            Scene.campaign_id == campaign_id,
            Scene.status == "active",
        )
    )
    if scene_active is None:
        raise ConflictError("Encounter scene is no longer active")
    loaded, catalog, _creation, _state = _load_combat_catalog(
        session, campaign, encounter.combat_catalog_id
    )
    if loaded.sha256 != encounter.combat_catalog_sha256:
        raise ConflictError("Pinned combat catalog hash is unavailable")

    combatants = list(
        session.scalars(
            select(Combatant).where(Combatant.encounter_id == encounter_id).with_for_update()
        )
    )
    for combatant in combatants:
        if combatant.character_id is None:
            continue
        character = session.get(Character, combatant.character_id)
        if character is None or (
            character.revision != combatant.source_snapshot["character_revision"]
            or character.state_revision != combatant.source_snapshot["state_revision"]
            or character.hp != combatant.hp
        ):
            raise ConflictError(
                f"Character {combatant.instance_name!r} changed after encounter setup; "
                "create a fresh encounter"
            )
    combatants.sort(
        key=lambda item: (
            0 if item.side == "party" else 1,
            int(item.source_snapshot.get("party_position", 1_000)),
            int(item.source_snapshot.get("instance_ordinal", 1_000)),
        )
    )
    command = CombatCommand(
        command_id=data.command_id,
        campaign_id=campaign_id,
        encounter_id=encounter_id,
        command_type="start_initiative",
        expected_encounter_revision=data.expected_encounter_revision,
        payload=payload,
        result={"encounter_id": str(encounter_id), "encounter_revision": 1},
    )
    session.add(command)
    session.flush()
    roller = dice_service or DiceService()
    roll_payloads: list[dict[str, Any]] = []
    for roll_index, combatant in enumerate(combatants):
        rolled = roller.roll("1d20")
        resolved = resolve_initiative(
            catalog,
            modifier=combatant.initiative_modifier,
            dice_faces=rolled.rolls,
        )
        combatant.initiative_dice_faces = resolved.d20.dice_faces
        combatant.initiative_selected_die = resolved.d20.selected_die
        combatant.initiative_total = resolved.d20.total
        roll = DiceRoll(
            campaign_id=campaign_id,
            ruleset_release_id=campaign.ruleset_release_id,
            ruleset_data_catalog_id=encounter.combat_catalog_id,
            turn_id=None,
            notation="1d20",
            rolls=resolved.d20.dice_faces,
            modifier=combatant.initiative_modifier,
            total=resolved.d20.total,
            purpose=f"combat initiative: {combatant.instance_name}",
            hidden=False,
            actor_character_id=combatant.character_id,
            combat_encounter_id=encounter_id,
            combatant_id=combatant.id,
            combat_command_id=command.id,
            roll_index=roll_index,
        )
        session.add(roll)
        session.flush()
        roll_payloads.append(
            {
                "dice_roll_id": str(roll.id),
                "combatant_id": str(combatant.id),
                "dice_faces": resolved.d20.dice_faces,
                "selected_die": resolved.d20.selected_die,
                "modifier": combatant.initiative_modifier,
                "total": resolved.d20.total,
                "rule_definition_keys": resolved.rule_definition_keys,
                "source_ids": resolved.source_ids,
            }
        )
    by_total: dict[int, list[Combatant]] = {}
    for combatant in combatants:
        assert combatant.initiative_total is not None
        by_total.setdefault(combatant.initiative_total, []).append(combatant)
    tied_groups = [(total, rows) for total, rows in by_total.items() if len(rows) > 1]
    if tied_groups:
        encounter.status = "tie_pending"
        for total, rows in sorted(tied_groups, reverse=True):
            session.add(
                CombatInitiativeTie(
                    encounter_id=encounter_id,
                    initiative_total=total,
                    participant_ids=[str(row.id) for row in rows],
                    decided_order=None,
                    status="pending",
                )
            )
    else:
        ordered = sorted(combatants, key=lambda item: item.initiative_total or 0, reverse=True)
        for order, combatant in enumerate(ordered):
            combatant.initiative_order = order
        encounter.status = "active"
        encounter.round_number = 1
        encounter.active_turn_index = 0
    encounter.revision = 1
    if encounter.status == "active":
        _create_active_combat_turn(session, encounter, combatants)
    session.flush()
    _combat_event(
        session,
        encounter_id,
        "initiative_rolled",
        {
            "command_id": str(data.command_id),
            "rng_version": roller.algorithm_version,
            "rolls": roll_payloads,
            "tie_totals": [total for total, _rows in sorted(tied_groups, reverse=True)],
            "status": encounter.status,
            "encounter_revision": encounter.revision,
        },
    )
    _add_event(
        session,
        campaign_id,
        "combat_initiative_rolled",
        {
            "encounter_id": str(encounter_id),
            "status": encounter.status,
            "tie_count": len(tied_groups),
            "encounter_revision": encounter.revision,
        },
    )
    session.commit()
    return _combat_encounter_read(session, encounter)


def _ordered_initiative(
    combatants: list[Combatant],
    ties: list[CombatInitiativeTie],
) -> list[Combatant]:
    by_id = {str(combatant.id): combatant for combatant in combatants}
    tie_order = {
        tie.initiative_total: list(tie.decided_order or [])
        for tie in ties
        if tie.status == "resolved"
    }
    ordered: list[Combatant] = []
    totals = sorted({combatant.initiative_total for combatant in combatants}, reverse=True)
    for total in totals:
        rows = [combatant for combatant in combatants if combatant.initiative_total == total]
        if len(rows) == 1:
            ordered.extend(rows)
        else:
            ids = tie_order.get(total)
            if ids is None:
                raise ConflictError(f"Initiative tie at {total} has not been resolved")
            ordered.extend(by_id[item_id] for item_id in ids)
    return ordered


def resolve_combat_initiative_tie(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    tie_id: uuid.UUID,
    data: CombatTieResolutionCreate,
) -> CombatEncounterRead:
    _campaign_for_update(session, campaign_id)
    payload = {**data.model_dump(mode="json"), "tie_id": str(tie_id)}
    existing_command = _existing_combat_command(
        session, campaign_id, data.command_id, "resolve_initiative_tie", payload
    )
    if existing_command is not None:
        if existing_command.encounter_id != encounter_id:
            raise ConflictError("Existing combat command belongs to a different encounter")
        return get_combat_encounter(session, campaign_id, encounter_id)
    encounter = session.scalar(
        select(CombatEncounter)
        .where(CombatEncounter.id == encounter_id, CombatEncounter.campaign_id == campaign_id)
        .with_for_update()
    )
    if encounter is None:
        raise NotFoundError("Combat encounter not found")
    if encounter.status != "tie_pending":
        raise ConflictError("Encounter has no pending initiative ties")
    if encounter.revision != data.expected_encounter_revision:
        raise ConflictError(
            f"Stale encounter revision: expected {data.expected_encounter_revision}, "
            f"current {encounter.revision}"
        )
    tie = session.scalar(
        select(CombatInitiativeTie)
        .where(CombatInitiativeTie.id == tie_id, CombatInitiativeTie.encounter_id == encounter_id)
        .with_for_update()
    )
    if tie is None:
        raise NotFoundError("Initiative tie not found")
    if tie.status != "pending":
        raise ConflictError("Initiative tie has already been resolved")
    submitted = [str(item) for item in data.ordered_combatant_ids]
    if set(submitted) != set(tie.participant_ids) or len(submitted) != len(tie.participant_ids):
        raise ConflictError("Tie decision must order every tied combatant exactly once")
    tie.decided_order = submitted
    tie.status = "resolved"
    encounter.revision += 1
    session.flush()
    ties = list(
        session.scalars(
            select(CombatInitiativeTie)
            .where(CombatInitiativeTie.encounter_id == encounter_id)
            .order_by(CombatInitiativeTie.initiative_total.desc())
        )
    )
    combatants = list(
        session.scalars(
            select(Combatant).where(Combatant.encounter_id == encounter_id).with_for_update()
        )
    )
    if all(item.status == "resolved" for item in ties):
        ordered = _ordered_initiative(combatants, ties)
        for order, combatant in enumerate(ordered):
            combatant.initiative_order = order
        encounter.status = "active"
        encounter.round_number = 1
        encounter.active_turn_index = 0
        _create_active_combat_turn(session, encounter, combatants)
    session.add(
        CombatCommand(
            command_id=data.command_id,
            campaign_id=campaign_id,
            encounter_id=encounter_id,
            command_type="resolve_initiative_tie",
            expected_encounter_revision=data.expected_encounter_revision,
            payload=payload,
            result={
                "encounter_id": str(encounter_id),
                "encounter_revision": encounter.revision,
                "tie_id": str(tie_id),
            },
        )
    )
    _combat_event(
        session,
        encounter_id,
        "initiative_tie_resolved",
        {
            "command_id": str(data.command_id),
            "tie_id": str(tie_id),
            "initiative_total": tie.initiative_total,
            "decided_order": submitted,
            "status": encounter.status,
            "encounter_revision": encounter.revision,
        },
    )
    session.commit()
    return _combat_encounter_read(session, encounter)


def replay_combat_encounter(
    session: Session,
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
) -> CombatReplayRead:
    encounter_read = get_combat_encounter(session, campaign_id, encounter_id)
    encounter = session.get(CombatEncounter, encounter_id)
    assert encounter is not None
    campaign = session.get(Campaign, campaign_id)
    assert campaign is not None
    loaded, catalog, _creation, _state = _load_combat_catalog(
        session, campaign, encounter.combat_catalog_id
    )
    if loaded.sha256 != encounter.combat_catalog_sha256:
        raise ConflictError("Pinned combat catalog hash is unavailable")
    combatants = list(
        session.scalars(select(Combatant).where(Combatant.encounter_id == encounter_id))
    )
    equivalent = True
    for combatant in combatants:
        if combatant.initiative_dice_faces is None:
            continue
        replayed = resolve_initiative(
            catalog,
            modifier=combatant.initiative_modifier,
            dice_faces=list(combatant.initiative_dice_faces),
        )
        equivalent = equivalent and (
            replayed.d20.selected_die == combatant.initiative_selected_die
            and replayed.d20.total == combatant.initiative_total
            and replayed.resolver_version == encounter.resolver_version
        )
    ties = list(
        session.scalars(
            select(CombatInitiativeTie).where(CombatInitiativeTie.encounter_id == encounter_id)
        )
    )
    if combatants and all(item.initiative_total is not None for item in combatants):
        if all(tie.status == "resolved" for tie in ties):
            replayed_order = [item.id for item in _ordered_initiative(combatants, ties)]
        elif not ties:
            replayed_order = [
                item.id
                for item in sorted(
                    combatants, key=lambda row: row.initiative_total or 0, reverse=True
                )
            ]
        else:
            replayed_order = []
    else:
        replayed_order = []
    stored_order = [
        item.id
        for item in sorted(
            (row for row in combatants if row.initiative_order is not None),
            key=lambda row: row.initiative_order or 0,
        )
    ]
    equivalent = equivalent and replayed_order == stored_order
    return CombatReplayRead(
        encounter_id=encounter_id,
        equivalent=equivalent,
        replayed_initiative_order=replayed_order,
        stored_initiative_order=stored_order,
        encounter=encounter_read,
    )


def _provider_context(
    state: CampaignState,
    world: WorldStateRead | None = None,
    target_npc_id: uuid.UUID | None = None,
    selected_choice: dict[str, Any] | None = None,
) -> dict[str, Any]:
    campaign = state.campaign.model_dump(
        mode="json",
        include={
            "id",
            "name",
            "ruleset_release_id",
            "ruleset_data_catalog_id",
            "status",
            "play_mode",
        },
    )
    characters: list[dict[str, Any]] = []
    for character in state.characters:
        compact_character: dict[str, Any] = character.model_dump(
            mode="json",
            include={
                "id",
                "name",
                "creation_status",
                "revision",
                "hp",
                "max_hp",
                "inventory",
                "party_position",
                "control_mode",
                "party_status",
                "state_revision",
                "equipped_items",
                "resources",
            },
        )
        if character.character_sheet is not None:
            compact_character["identity"] = character.character_sheet.model_dump(
                mode="json",
                include={
                    "level",
                    "species_definition_key",
                    "background_definition_key",
                    "class_definition_key",
                    "size",
                    "alignment",
                    "languages",
                    "feature_definition_keys",
                },
            )
        if character.mechanical_state is not None:
            mechanics = character.mechanical_state.model_dump(mode="json")
            compact_character["mechanics"] = {
                "abilities": mechanics["abilities"],
                "ability_modifiers": {
                    ability: derived["value"]
                    for ability, derived in mechanics["ability_modifiers"].items()
                },
                "proficiency_bonus": mechanics["proficiency_bonus"]["value"],
                "saving_throws": {
                    ability: {
                        "modifier": modifier["value"],
                        "proficient": modifier["proficient"],
                    }
                    for ability, modifier in mechanics["saving_throws"].items()
                },
                "skills": {
                    skill: {
                        "modifier": modifier["value"],
                        "ability": modifier["ability"],
                        "proficient": modifier["proficient"],
                    }
                    for skill, modifier in mechanics["skills"].items()
                },
                "armor_class": mechanics["armor_class"]["value"],
                "initiative": mechanics["initiative"]["value"],
                "passive_perception": mechanics["passive_perception"]["value"],
                "speed_feet": mechanics["speed_feet"]["value"],
                "equipment": [
                    {
                        "item_id": item["item_id"],
                        "name": item["name"],
                        "quantity": item["quantity"],
                        "equipped_quantity": item["equipped_quantity"],
                        "position": item["position"],
                    }
                    for item in mechanics["equipment"]
                ],
                "resources": {
                    resource_id: {
                        "current": resource["current"],
                        "maximum": resource["maximum"],
                        "die": resource["die"],
                    }
                    for resource_id, resource in mechanics["resources"].items()
                },
            }
        characters.append(compact_character)
    context: dict[str, Any] = {
        "campaign": campaign,
        "characters": characters,
        "party_ready": state.party_ready,
        "location": state.location.model_dump(mode="json"),
        "turn_count": state.turn_count,
    }
    if world is not None:
        selected_target = next((npc for npc in world.present_npcs if npc.id == target_npc_id), None)
        relevant_npc_ids = {npc.id for npc in world.present_npcs}
        relevant_facts = [
            fact
            for fact in world.facts
            if fact.subject_npc_id is None or fact.subject_npc_id in relevant_npc_ids
        ]
        omitted_fact_count = max(0, len(relevant_facts) - MAX_PROVIDER_WORLD_FACTS)
        if omitted_fact_count:
            relevant_facts = relevant_facts[-MAX_PROVIDER_WORLD_FACTS:]
        relevant_quests = [quest for quest in world.quests if quest.status == "active"]
        omitted_quest_count = max(0, len(relevant_quests) - MAX_PROVIDER_QUESTS)
        if omitted_quest_count:
            relevant_quests = relevant_quests[-MAX_PROVIDER_QUESTS:]
        relevant_decisions = [decision for decision in world.decisions if decision.status == "open"]
        omitted_decision_count = max(0, len(relevant_decisions) - MAX_PROVIDER_DECISIONS)
        if omitted_decision_count:
            relevant_decisions = relevant_decisions[-MAX_PROVIDER_DECISIONS:]
        relevant_factions = [faction for faction in world.factions if faction.status == "active"]
        omitted_faction_count = max(0, len(relevant_factions) - MAX_PROVIDER_FACTIONS)
        if omitted_faction_count:
            relevant_factions = relevant_factions[-MAX_PROVIDER_FACTIONS:]
        faction_payload: list[dict[str, Any]] = []
        remaining_relationships = MAX_PROVIDER_FACTION_RELATIONSHIPS
        for faction in reversed(relevant_factions):
            relationships = faction.relationships
            included_count = min(len(relationships), remaining_relationships)
            included = relationships[-included_count:] if included_count else []
            remaining_relationships -= included_count
            compact_faction = faction.model_dump(mode="json", exclude={"relationships"})
            compact_faction["relationships"] = [
                relationship.model_dump(mode="json") for relationship in included
            ]
            compact_faction["relationships_truncated"] = len(relationships) - included_count
            faction_payload.append(compact_faction)
        faction_payload.reverse()
        context["world"] = {
            "world_revision": world.world_revision,
            "narrative_time_minutes": world.narrative_time_minutes,
            "scene": world.scene.model_dump(mode="json"),
            "present_npcs": [npc.model_dump(mode="json") for npc in world.present_npcs],
            "facts": [fact.model_dump(mode="json") for fact in relevant_facts],
            "facts_truncated": omitted_fact_count,
            "quests": [quest.model_dump(mode="json") for quest in relevant_quests],
            "quests_truncated": omitted_quest_count,
            "decisions": [decision.model_dump(mode="json") for decision in relevant_decisions],
            "decisions_truncated": omitted_decision_count,
            "factions": faction_payload,
            "factions_truncated": omitted_faction_count,
            "selected_target": (
                selected_target.model_dump(mode="json") if selected_target is not None else None
            ),
            "selected_choice": selected_choice,
        }
    return context


def _with_historical_memory(
    context: dict[str, Any],
    service: TurnMemoryContextService | None,
    *,
    campaign_id: uuid.UUID,
    turn_id: uuid.UUID,
    stage: Literal["interpretation", "narration"],
    player_action: str,
) -> dict[str, Any]:
    if service is None:
        return context
    try:
        historical_memory = service.build(
            campaign_id=campaign_id,
            turn_id=turn_id,
            stage=stage,
            player_action=player_action,
        )
    except Exception:
        logger.exception(
            "historical memory context failed safely",
            extra={"campaign_id": str(campaign_id), "turn_id": str(turn_id), "stage": stage},
        )
        return context
    if historical_memory is None:
        return context
    return {**context, "historical_memory": historical_memory}


def _proposal_fact_parts(change: Any) -> tuple[str, uuid.UUID | None, str] | None:
    if isinstance(change, NPCAttitudeSet):
        return "npc_attitude", change.npc_id, change.attitude
    if isinstance(change, RelationshipNoteAdd):
        return "relationship_note", change.npc_id, change.note
    if isinstance(change, PromiseRecord):
        return "promise", change.npc_id, change.promise
    if isinstance(change, DiscoveryRecord):
        return "discovery", change.subject_npc_id, change.discovery
    if isinstance(change, ClueRecord):
        return "clue", change.subject_npc_id, change.clue
    return None


def _require_provider_fact_subject(
    session: Session, campaign_id: uuid.UUID, fact_type: str, subject_npc_id: uuid.UUID | None
) -> None:
    npc = _validate_fact_subject(session, campaign_id, fact_type, subject_npc_id)
    if npc is None:
        return
    if npc.status != "active" or npc.visibility != "player":
        raise InvalidStateChange("World fact NPC is not an active player-visible subject")
    presence = session.scalar(
        select(SceneNPCPresence.id)
        .join(Scene, Scene.id == SceneNPCPresence.scene_id)
        .where(
            Scene.campaign_id == campaign_id,
            Scene.status == "active",
            SceneNPCPresence.npc_id == npc.id,
            SceneNPCPresence.status == "present",
        )
    )
    if presence is None:
        raise InvalidStateChange("World fact NPC is not present in the active scene")


def _quest_for_change(session: Session, campaign_id: uuid.UUID, quest_id: uuid.UUID) -> Quest:
    quest = session.get(Quest, quest_id)
    if quest is None or quest.campaign_id != campaign_id or quest.visibility != "player":
        raise InvalidStateChange("Quest does not belong to the player-visible campaign state")
    return quest


def _objective_for_change(
    session: Session, campaign_id: uuid.UUID, objective_id: uuid.UUID
) -> QuestObjective:
    objective = session.get(QuestObjective, objective_id)
    if objective is None or objective.campaign_id != campaign_id:
        raise InvalidStateChange("Quest objective does not belong to the campaign")
    quest = _quest_for_change(session, campaign_id, objective.quest_id)
    if quest.status != "active":
        raise InvalidStateChange("Only an active quest objective can transition")
    return objective


def _validate_quest_transition(quest: Quest, expected_revision: int, status: str) -> None:
    if quest.revision != expected_revision:
        raise InvalidStateChange("Quest revision is stale")
    if quest.status != "active":
        raise InvalidStateChange("Only an active quest can transition")
    if status not in {"completed", "failed", "abandoned"}:
        raise InvalidStateChange("Unsupported quest transition")


def _validate_objective_transition(
    objective: QuestObjective, expected_revision: int, status: str
) -> None:
    if objective.revision != expected_revision:
        raise InvalidStateChange("Quest objective revision is stale")
    allowed = {
        "pending": {"active", "skipped"},
        "active": {"completed", "failed", "skipped"},
    }
    if status not in allowed.get(objective.status, set()):
        raise InvalidStateChange(
            f"Illegal quest objective transition from {objective.status} to {status}"
        )


def _parse_decision_consequences(raw: list[dict[str, Any]]) -> list[DecisionConsequence]:
    try:
        return DECISION_CONSEQUENCE_ADAPTER.validate_python(raw)
    except ValidationError as exc:
        raise InvalidStateChange("Stored decision consequences are invalid") from exc


def _validate_decision_consequences(
    session: Session,
    campaign_id: uuid.UUID,
    consequences: list[DecisionConsequence],
    *,
    occupied_quests: set[uuid.UUID] | None = None,
    occupied_objectives: set[uuid.UUID] | None = None,
    occupied_attitude_subjects: set[uuid.UUID] | None = None,
    occupied_fact_records: set[tuple[str, uuid.UUID | None, str]] | None = None,
) -> None:
    touched_quests = set(occupied_quests or set())
    touched_objectives = set(occupied_objectives or set())
    attitude_subjects = set(occupied_attitude_subjects or set())
    fact_records = set(occupied_fact_records or set())
    for consequence in consequences:
        if isinstance(consequence, DecisionFactConsequence):
            npc = _validate_fact_subject(
                session,
                campaign_id,
                consequence.fact_type,
                consequence.subject_npc_id,
            )
            if npc is not None and (npc.status != "active" or npc.visibility != "player"):
                raise InvalidStateChange(
                    "Decision consequence NPC must be active and player-visible"
                )
            value = _validate_fact_value(consequence.fact_type, consequence.value)
            identity = (consequence.fact_type, consequence.subject_npc_id, value)
            if identity in fact_records:
                raise InvalidStateChange(
                    "A decision consequence cannot duplicate a narrator fact proposal"
                )
            fact_records.add(identity)
            if consequence.fact_type == "npc_attitude":
                assert consequence.subject_npc_id is not None
                if consequence.subject_npc_id in attitude_subjects:
                    raise InvalidStateChange(
                        "A decision option can set an NPC attitude at most once"
                    )
                attitude_subjects.add(consequence.subject_npc_id)
                existing = session.scalar(
                    select(WorldFact).where(
                        WorldFact.campaign_id == campaign_id,
                        WorldFact.subject_npc_id == consequence.subject_npc_id,
                        WorldFact.fact_type == "npc_attitude",
                        WorldFact.status == "current",
                    )
                )
                if existing is not None:
                    if existing.visibility != "player":
                        raise InvalidStateChange(
                            "A hidden NPC attitude cannot be replaced by a player choice"
                        )
                    if existing.value == value:
                        raise InvalidStateChange(
                            "Decision consequence would not change NPC attitude"
                        )
        elif isinstance(consequence, DecisionQuestConsequence):
            if consequence.quest_id in touched_quests:
                raise InvalidStateChange("A quest can be changed at most once per turn")
            for objective_id in touched_objectives:
                objective = session.get(QuestObjective, objective_id)
                assert objective is not None
                if objective.quest_id == consequence.quest_id:
                    raise InvalidStateChange(
                        "A quest and one of its objectives cannot transition in the same turn"
                    )
            touched_quests.add(consequence.quest_id)
            quest = _quest_for_change(session, campaign_id, consequence.quest_id)
            _validate_quest_transition(quest, consequence.expected_revision, consequence.status)
        elif isinstance(consequence, DecisionObjectiveConsequence):
            if consequence.objective_id in touched_objectives:
                raise InvalidStateChange("A quest objective can be changed at most once per turn")
            touched_objectives.add(consequence.objective_id)
            objective = _objective_for_change(session, campaign_id, consequence.objective_id)
            if objective.quest_id in touched_quests:
                raise InvalidStateChange(
                    "A quest and one of its objectives cannot transition in the same turn"
                )
            _validate_objective_transition(
                objective, consequence.expected_revision, consequence.status
            )


def _faction_for_change(session: Session, campaign_id: uuid.UUID, faction_id: uuid.UUID) -> Faction:
    faction = session.get(Faction, faction_id)
    if faction is None or faction.campaign_id != campaign_id:
        raise InvalidStateChange("Faction does not belong to the campaign")
    if faction.status != "active" or faction.visibility != "player":
        raise InvalidStateChange("Faction must be active and player-visible")
    return faction


def _active_scene_for_change(session: Session, campaign_id: uuid.UUID) -> Scene:
    scene = session.scalar(
        select(Scene).where(Scene.campaign_id == campaign_id, Scene.status == "active")
    )
    if scene is None:
        raise InvalidStateChange("Campaign has no active scene")
    return scene


def _npc_for_presence_change(session: Session, campaign_id: uuid.UUID, npc_id: uuid.UUID) -> NPC:
    npc = session.get(NPC, npc_id)
    if npc is None or npc.campaign_id != campaign_id:
        raise InvalidStateChange("NPC does not belong to the campaign")
    if npc.status != "active" or npc.visibility != "player":
        raise InvalidStateChange("NPC must be active and player-visible")
    return npc


def _current_npc_presence(
    session: Session, campaign_id: uuid.UUID, npc_id: uuid.UUID
) -> SceneNPCPresence | None:
    return session.scalar(
        select(SceneNPCPresence).where(
            SceneNPCPresence.campaign_id == campaign_id,
            SceneNPCPresence.npc_id == npc_id,
            SceneNPCPresence.status == "present",
        )
    )


def _faction_relationship_for_change(
    session: Session,
    campaign_id: uuid.UUID,
    change: FactionAttitudeSet | FactionMembershipSet,
) -> tuple[Faction, FactionRelationship | None, uuid.UUID | None, uuid.UUID | None]:
    faction = _faction_for_change(session, campaign_id, change.faction_id)
    character_id = None
    npc_id = None
    relation_type = "attitude"
    if isinstance(change, FactionMembershipSet):
        relation_type = "membership"
        if change.member_type == "character":
            character = session.get(Character, change.member_id)
            if character is None or character.campaign_id != campaign_id:
                raise InvalidStateChange("Faction member character does not belong to campaign")
            if character.creation_status != "finalized" or character.party_status != "active":
                raise InvalidStateChange("Faction member character must be finalized and active")
            character_id = character.id
        else:
            npc = session.get(NPC, change.member_id)
            if npc is None or npc.campaign_id != campaign_id:
                raise InvalidStateChange("Faction member NPC does not belong to campaign")
            if npc.status != "active" or npc.visibility != "player":
                raise InvalidStateChange("Faction member NPC must be active and player-visible")
            npc_id = npc.id
    relation = session.scalar(
        select(FactionRelationship).where(
            FactionRelationship.faction_id == faction.id,
            FactionRelationship.relation_type == relation_type,
            FactionRelationship.character_id == character_id,
            FactionRelationship.npc_id == npc_id,
        )
    )
    if relation is None:
        if change.expected_revision is not None:
            raise InvalidStateChange("Faction relationship revision is stale")
    else:
        if relation.visibility != "player":
            raise InvalidStateChange("A hidden faction relationship cannot be changed here")
        if change.expected_revision is None or relation.revision != change.expected_revision:
            raise InvalidStateChange("Faction relationship revision is stale")
        value = change.attitude if isinstance(change, FactionAttitudeSet) else change.membership
        if relation.value == value:
            raise InvalidStateChange("Faction relationship already has the proposed value")
    return faction, relation, character_id, npc_id


def _validate_world_changes(
    session: Session, campaign_id: uuid.UUID, changes: list
) -> tuple[
    set[uuid.UUID],
    set[uuid.UUID],
    set[uuid.UUID],
    set[tuple[str, uuid.UUID | None, str]],
]:
    touched_facts: set[uuid.UUID] = set()
    attitude_subjects: set[uuid.UUID] = set()
    proposed_fact_records: set[tuple[str, uuid.UUID | None, str]] = set()
    touched_quests: set[uuid.UUID] = set()
    touched_objectives: set[uuid.UUID] = set()
    new_quest_keys: set[str] = set()
    new_decision_keys: set[str] = set()
    new_faction_keys: set[str] = set()
    touched_faction_relationships: set[
        tuple[uuid.UUID, str, uuid.UUID | None, uuid.UUID | None]
    ] = set()
    touched_npc_presences: set[uuid.UUID] = set()
    time_advance_count = 0
    has_location_move = any(isinstance(change, MoveLocation) for change in changes)
    if has_location_move and any(
        isinstance(change, (NPCIntroduce, NPCArrive, NPCDepart)) for change in changes
    ):
        raise InvalidStateChange(
            "NPC presence changes and location movement must use separate turns"
        )
    for change in changes:
        parts = _proposal_fact_parts(change)
        if parts is not None:
            fact_type, subject_npc_id, value = parts
            _require_provider_fact_subject(session, campaign_id, fact_type, subject_npc_id)
            normalized_value = _validate_fact_value(fact_type, value)
            identity = (fact_type, subject_npc_id, normalized_value)
            if identity in proposed_fact_records:
                raise InvalidStateChange("A turn cannot record the same world fact more than once")
            proposed_fact_records.add(identity)
            if fact_type == "npc_attitude":
                assert subject_npc_id is not None
                if subject_npc_id in attitude_subjects:
                    raise InvalidStateChange("A turn can set an NPC attitude at most once")
                attitude_subjects.add(subject_npc_id)
                existing = session.scalar(
                    select(WorldFact).where(
                        WorldFact.campaign_id == campaign_id,
                        WorldFact.subject_npc_id == subject_npc_id,
                        WorldFact.fact_type == "npc_attitude",
                        WorldFact.status == "current",
                    )
                )
                if existing is not None:
                    if existing.id in touched_facts:
                        raise InvalidStateChange(
                            "A world fact can be changed at most once per turn"
                        )
                    touched_facts.add(existing.id)
                    if existing.visibility != "player":
                        raise InvalidStateChange("A hidden NPC attitude cannot be replaced here")
                    if existing.value == value:
                        raise InvalidStateChange("NPC already has the proposed attitude")
            continue
        if isinstance(change, (WorldFactSupersede, WorldFactReveal)):
            if change.fact_id in touched_facts:
                raise InvalidStateChange("A world fact can be changed at most once per turn")
            touched_facts.add(change.fact_id)
            fact = session.get(WorldFact, change.fact_id)
            if fact is None or fact.campaign_id != campaign_id:
                raise InvalidStateChange("World fact does not belong to the campaign")
            if fact.status != "current":
                raise InvalidStateChange("Only a current world fact can be changed")
            if fact.revision != change.expected_revision:
                raise InvalidStateChange("World fact revision is stale")
            if isinstance(change, WorldFactSupersede):
                if fact.visibility != "player":
                    raise InvalidStateChange("A hidden world fact cannot be superseded here")
                _require_provider_fact_subject(
                    session, campaign_id, fact.fact_type, fact.subject_npc_id
                )
                _validate_fact_value(fact.fact_type, change.value)
                if fact.value == change.value.strip():
                    raise InvalidStateChange("Superseding value must change the world fact")
            elif fact.visibility != "dm_only":
                raise InvalidStateChange("Only a hidden world fact can be revealed")
        elif isinstance(change, QuestCreate):
            if change.quest_key in new_quest_keys:
                raise InvalidStateChange("A turn cannot create duplicate quest keys")
            new_quest_keys.add(change.quest_key)
            existing = session.scalar(
                select(Quest.id).where(
                    Quest.campaign_id == campaign_id, Quest.quest_key == change.quest_key
                )
            )
            if existing is not None:
                raise InvalidStateChange("Quest key already exists in campaign")
        elif isinstance(change, QuestTransition):
            if change.quest_id in touched_quests:
                raise InvalidStateChange("A quest can be changed at most once per turn")
            for objective_id in touched_objectives:
                objective = session.get(QuestObjective, objective_id)
                assert objective is not None
                if objective.quest_id == change.quest_id:
                    raise InvalidStateChange(
                        "A quest and one of its objectives cannot transition in the same turn"
                    )
            touched_quests.add(change.quest_id)
            quest = _quest_for_change(session, campaign_id, change.quest_id)
            _validate_quest_transition(quest, change.expected_revision, change.status)
        elif isinstance(change, QuestObjectiveTransition):
            if change.objective_id in touched_objectives:
                raise InvalidStateChange("A quest objective can be changed at most once per turn")
            touched_objectives.add(change.objective_id)
            objective = _objective_for_change(session, campaign_id, change.objective_id)
            if objective.quest_id in touched_quests:
                raise InvalidStateChange(
                    "A quest and one of its objectives cannot transition in the same turn"
                )
            _validate_objective_transition(objective, change.expected_revision, change.status)
        elif isinstance(change, DecisionOpen):
            if change.decision_key in new_decision_keys:
                raise InvalidStateChange("A turn cannot create duplicate decision keys")
            new_decision_keys.add(change.decision_key)
            existing = session.scalar(
                select(DecisionPoint.id).where(
                    DecisionPoint.campaign_id == campaign_id,
                    DecisionPoint.decision_key == change.decision_key,
                )
            )
            if existing is not None:
                raise InvalidStateChange("Decision key already exists in campaign")
        elif isinstance(change, NPCIntroduce):
            _active_scene_for_change(session, campaign_id)
        elif isinstance(change, (NPCArrive, NPCDepart)):
            if change.npc_id in touched_npc_presences:
                raise InvalidStateChange("An NPC's presence can be changed at most once per turn")
            touched_npc_presences.add(change.npc_id)
            _npc_for_presence_change(session, campaign_id, change.npc_id)
            active_scene = _active_scene_for_change(session, campaign_id)
            presence = _current_npc_presence(session, campaign_id, change.npc_id)
            if isinstance(change, NPCArrive):
                if presence is not None:
                    raise InvalidStateChange("NPC is already present in a scene")
            elif presence is None or presence.scene_id != active_scene.id:
                raise InvalidStateChange("NPC is not present in the active scene")
        elif isinstance(change, FactionCreate):
            if change.faction_key in new_faction_keys:
                raise InvalidStateChange("A turn cannot create duplicate faction keys")
            new_faction_keys.add(change.faction_key)
            existing = session.scalar(
                select(Faction.id).where(
                    Faction.campaign_id == campaign_id,
                    Faction.faction_key == change.faction_key,
                )
            )
            if existing is not None:
                raise InvalidStateChange("Faction key already exists in campaign")
        elif isinstance(change, (FactionAttitudeSet, FactionMembershipSet)):
            _faction, _relation, character_id, npc_id = _faction_relationship_for_change(
                session, campaign_id, change
            )
            relation_type = "attitude" if isinstance(change, FactionAttitudeSet) else "membership"
            identity = (change.faction_id, relation_type, character_id, npc_id)
            if identity in touched_faction_relationships:
                raise InvalidStateChange(
                    "A faction relationship can be changed at most once per turn"
                )
            touched_faction_relationships.add(identity)
        elif isinstance(change, NarrativeTimeAdvance):
            time_advance_count += 1
            if time_advance_count > 1:
                raise InvalidStateChange("A turn can advance narrative time at most once")
            campaign = session.get(Campaign, campaign_id)
            assert campaign is not None
            if campaign.narrative_time_minutes + change.minutes > MAX_NARRATIVE_TIME_MINUTES:
                raise InvalidStateChange("Narrative time exceeds the supported campaign range")
    for change in changes:
        if not isinstance(change, DecisionOpen):
            continue
        for option in change.options:
            _validate_decision_consequences(
                session,
                campaign_id,
                option.consequences,
                occupied_quests=touched_quests,
                occupied_objectives=touched_objectives,
                occupied_attitude_subjects=attitude_subjects,
                occupied_fact_records=proposed_fact_records,
            )
    return touched_quests, touched_objectives, attitude_subjects, proposed_fact_records


def _record_fact_projection(
    session: Session,
    campaign: Campaign,
    *,
    fact_type: str,
    subject_npc_id: uuid.UUID | None,
    value: str,
    turn_id: uuid.UUID | None,
    actor_character_id: uuid.UUID | None,
) -> WorldFact:
    current_attitude = None
    if fact_type == "npc_attitude":
        current_attitude = session.scalar(
            select(WorldFact).where(
                WorldFact.campaign_id == campaign.id,
                WorldFact.subject_npc_id == subject_npc_id,
                WorldFact.fact_type == "npc_attitude",
                WorldFact.status == "current",
            )
        )
    fact_id = uuid.uuid4()
    next_revision = campaign.world_revision + 1
    if current_attitude is None:
        event_type = "world_fact_recorded"
        revision = 0
        supersedes_fact_id = None
    else:
        event_type = "world_fact_superseded"
        revision = current_attitude.revision + 1
        supersedes_fact_id = current_attitude.id
    event = _add_event(
        session,
        campaign.id,
        event_type,
        {
            "fact_id": str(fact_id),
            "supersedes_fact_id": str(supersedes_fact_id) if supersedes_fact_id else None,
            "fact_type": fact_type,
            "subject_npc_id": str(subject_npc_id) if subject_npc_id else None,
            "value": value.strip(),
            "world_revision": next_revision,
        },
        turn_id=turn_id,
        actor_character_id=actor_character_id,
    )
    if current_attitude is not None:
        current_attitude.status = "superseded"
        current_attitude.superseded_by_event_id = event.id
    fact = WorldFact(
        id=fact_id,
        campaign_id=campaign.id,
        subject_npc_id=subject_npc_id,
        fact_type=fact_type,
        value=value.strip(),
        status="current",
        visibility="player",
        revision=revision,
        supersedes_fact_id=supersedes_fact_id,
        created_by_event_id=event.id,
    )
    session.add(fact)
    campaign.world_revision = next_revision
    return fact


def _apply_world_fact_change(
    session: Session,
    campaign: Campaign,
    change: Any,
    *,
    turn_id: uuid.UUID | None,
    actor_character_id: uuid.UUID | None,
) -> bool:
    parts = _proposal_fact_parts(change)
    if parts is not None:
        fact_type, subject_npc_id, value = parts
        _record_fact_projection(
            session,
            campaign,
            fact_type=fact_type,
            subject_npc_id=subject_npc_id,
            value=value,
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        return True
    if isinstance(change, WorldFactSupersede):
        fact = session.get(WorldFact, change.fact_id)
        assert fact is not None
        next_revision = campaign.world_revision + 1
        new_fact_id = uuid.uuid4()
        event = _add_event(
            session,
            campaign.id,
            "world_fact_superseded",
            {
                "fact_id": str(new_fact_id),
                "supersedes_fact_id": str(fact.id),
                "fact_type": fact.fact_type,
                "subject_npc_id": str(fact.subject_npc_id) if fact.subject_npc_id else None,
                "value": change.value.strip(),
                "world_revision": next_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        fact.status = "superseded"
        fact.superseded_by_event_id = event.id
        session.add(
            WorldFact(
                id=new_fact_id,
                campaign_id=campaign.id,
                subject_npc_id=fact.subject_npc_id,
                fact_type=fact.fact_type,
                value=change.value.strip(),
                status="current",
                visibility="player",
                revision=fact.revision + 1,
                supersedes_fact_id=fact.id,
                created_by_event_id=event.id,
            )
        )
        campaign.world_revision = next_revision
        return True
    if isinstance(change, WorldFactReveal):
        fact = session.get(WorldFact, change.fact_id)
        assert fact is not None
        next_revision = campaign.world_revision + 1
        event = _add_event(
            session,
            campaign.id,
            "world_fact_revealed",
            {
                "fact_id": str(fact.id),
                "fact_type": fact.fact_type,
                "subject_npc_id": str(fact.subject_npc_id) if fact.subject_npc_id else None,
                "value": fact.value,
                "world_revision": next_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        fact.visibility = "player"
        fact.revision += 1
        fact.revealed_by_event_id = event.id
        campaign.world_revision = next_revision
        return True
    return False


def _apply_quest_transition(
    session: Session,
    campaign: Campaign,
    quest: Quest,
    status: str,
    *,
    turn_id: uuid.UUID | None,
    actor_character_id: uuid.UUID | None,
) -> None:
    next_revision = campaign.world_revision + 1
    event = _add_event(
        session,
        campaign.id,
        "quest_status_changed",
        {
            "quest_id": str(quest.id),
            "quest_key": quest.quest_key,
            "previous_status": quest.status,
            "status": status,
            "quest_revision": quest.revision + 1,
            "world_revision": next_revision,
        },
        turn_id=turn_id,
        actor_character_id=actor_character_id,
    )
    quest.status = status
    quest.revision += 1
    quest.transitioned_by_event_id = event.id
    campaign.world_revision = next_revision


def _apply_objective_transition(
    session: Session,
    campaign: Campaign,
    objective: QuestObjective,
    status: str,
    *,
    turn_id: uuid.UUID | None,
    actor_character_id: uuid.UUID | None,
) -> None:
    next_revision = campaign.world_revision + 1
    event = _add_event(
        session,
        campaign.id,
        "quest_objective_status_changed",
        {
            "quest_id": str(objective.quest_id),
            "objective_id": str(objective.id),
            "objective_key": objective.objective_key,
            "previous_status": objective.status,
            "status": status,
            "objective_revision": objective.revision + 1,
            "world_revision": next_revision,
        },
        turn_id=turn_id,
        actor_character_id=actor_character_id,
    )
    objective.status = status
    objective.revision += 1
    objective.transitioned_by_event_id = event.id
    campaign.world_revision = next_revision


def _apply_quest_decision_change(
    session: Session,
    campaign: Campaign,
    change: Any,
    *,
    turn_id: uuid.UUID | None,
    actor_character_id: uuid.UUID | None,
) -> bool:
    if isinstance(change, QuestCreate):
        quest_id = uuid.uuid4()
        objective_ids = [uuid.uuid4() for _ in change.objectives]
        next_revision = campaign.world_revision + 1
        event = _add_event(
            session,
            campaign.id,
            "quest_created",
            {
                "quest_id": str(quest_id),
                "quest_key": change.quest_key,
                "title": change.title,
                "objectives": [
                    {
                        "objective_id": str(objective_id),
                        "objective_key": objective.objective_key,
                        "title": objective.title,
                        "status": objective.status,
                    }
                    for objective_id, objective in zip(
                        objective_ids, change.objectives, strict=True
                    )
                ],
                "world_revision": next_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        quest = Quest(
            id=quest_id,
            campaign_id=campaign.id,
            quest_key=change.quest_key,
            title=change.title,
            summary=change.summary,
            status="active",
            visibility="player",
            revision=0,
            created_by_event_id=event.id,
        )
        session.add(quest)
        for position, (objective_id, objective) in enumerate(
            zip(objective_ids, change.objectives, strict=True), start=1
        ):
            session.add(
                QuestObjective(
                    id=objective_id,
                    campaign_id=campaign.id,
                    quest_id=quest_id,
                    objective_key=objective.objective_key,
                    title=objective.title,
                    description=objective.description,
                    status=objective.status,
                    position=position,
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
        campaign.world_revision = next_revision
        return True
    if isinstance(change, QuestTransition):
        quest = session.get(Quest, change.quest_id)
        assert quest is not None
        _apply_quest_transition(
            session,
            campaign,
            quest,
            change.status,
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        return True
    if isinstance(change, QuestObjectiveTransition):
        objective = session.get(QuestObjective, change.objective_id)
        assert objective is not None
        _apply_objective_transition(
            session,
            campaign,
            objective,
            change.status,
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        return True
    if isinstance(change, DecisionOpen):
        decision_id = uuid.uuid4()
        option_ids = [uuid.uuid4() for _ in change.options]
        next_revision = campaign.world_revision + 1
        event = _add_event(
            session,
            campaign.id,
            "decision_opened",
            {
                "decision_id": str(decision_id),
                "decision_key": change.decision_key,
                "prompt": change.prompt,
                "options": [
                    {
                        "option_id": str(option_id),
                        "option_key": option.option_key,
                        "label": option.label,
                        "description": option.description,
                    }
                    for option_id, option in zip(option_ids, change.options, strict=True)
                ],
                "world_revision": next_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        session.add(
            DecisionPoint(
                id=decision_id,
                campaign_id=campaign.id,
                decision_key=change.decision_key,
                prompt=change.prompt,
                status="open",
                visibility="player",
                revision=0,
                created_by_event_id=event.id,
            )
        )
        for position, (option_id, option) in enumerate(
            zip(option_ids, change.options, strict=True), start=1
        ):
            session.add(
                DecisionOption(
                    id=option_id,
                    campaign_id=campaign.id,
                    decision_id=decision_id,
                    option_key=option.option_key,
                    label=option.label,
                    description=option.description,
                    position=position,
                    consequences=[
                        consequence.model_dump(mode="json") for consequence in option.consequences
                    ],
                )
            )
        campaign.world_revision = next_revision
        return True
    return False


def _apply_faction_time_change(
    session: Session,
    campaign: Campaign,
    change: Any,
    *,
    turn_id: uuid.UUID | None,
    actor_character_id: uuid.UUID | None,
) -> bool:
    if isinstance(change, FactionCreate):
        faction_id = uuid.uuid4()
        next_revision = campaign.world_revision + 1
        event = _add_event(
            session,
            campaign.id,
            "faction_created",
            {
                "faction_id": str(faction_id),
                "faction_key": change.faction_key,
                "name": change.name,
                "description": change.description,
                "world_revision": next_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        session.add(
            Faction(
                id=faction_id,
                campaign_id=campaign.id,
                faction_key=change.faction_key,
                name=change.name,
                description=change.description,
                status="active",
                visibility="player",
                revision=0,
                created_by_event_id=event.id,
            )
        )
        campaign.world_revision = next_revision
        return True
    if isinstance(change, (FactionAttitudeSet, FactionMembershipSet)):
        faction, relation, character_id, npc_id = _faction_relationship_for_change(
            session, campaign.id, change
        )
        relation_type = "attitude" if isinstance(change, FactionAttitudeSet) else "membership"
        value = change.attitude if isinstance(change, FactionAttitudeSet) else change.membership
        relation_id = relation.id if relation is not None else uuid.uuid4()
        next_relation_revision = relation.revision + 1 if relation is not None else 0
        next_world_revision = campaign.world_revision + 1
        event_type = (
            "faction_attitude_set"
            if isinstance(change, FactionAttitudeSet)
            else "faction_membership_set"
        )
        event = _add_event(
            session,
            campaign.id,
            event_type,
            {
                "faction_id": str(faction.id),
                "faction_key": faction.faction_key,
                "relationship_id": str(relation_id),
                "relation_type": relation_type,
                "character_id": str(character_id) if character_id else None,
                "npc_id": str(npc_id) if npc_id else None,
                "previous_value": relation.value if relation is not None else None,
                "value": value,
                "relationship_revision": next_relation_revision,
                "world_revision": next_world_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        if relation is None:
            session.add(
                FactionRelationship(
                    id=relation_id,
                    campaign_id=campaign.id,
                    faction_id=faction.id,
                    relation_type=relation_type,
                    character_id=character_id,
                    npc_id=npc_id,
                    value=value,
                    visibility="player",
                    revision=0,
                    created_by_event_id=event.id,
                )
            )
        else:
            relation.value = value
            relation.revision = next_relation_revision
            relation.updated_by_event_id = event.id
        campaign.world_revision = next_world_revision
        return True
    if isinstance(change, NarrativeTimeAdvance):
        previous_minutes = campaign.narrative_time_minutes
        next_minutes = previous_minutes + change.minutes
        next_world_revision = campaign.world_revision + 1
        _add_event(
            session,
            campaign.id,
            "narrative_time_advanced",
            {
                "minutes": change.minutes,
                "reason": change.reason,
                "previous_time_minutes": previous_minutes,
                "narrative_time_minutes": next_minutes,
                "world_revision": next_world_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        campaign.narrative_time_minutes = next_minutes
        campaign.world_revision = next_world_revision
        return True
    return False


def _apply_npc_presence_change(
    session: Session,
    campaign: Campaign,
    change: Any,
    *,
    turn_id: uuid.UUID | None,
    actor_character_id: uuid.UUID | None,
) -> bool:
    if not isinstance(change, (NPCIntroduce, NPCArrive, NPCDepart)):
        return False
    scene = _active_scene_for_change(session, campaign.id)
    next_world_revision = campaign.world_revision + 1
    if isinstance(change, NPCIntroduce):
        npc = NPC(
            campaign_id=campaign.id,
            name=change.name,
            public_description=change.public_description,
            status="active",
            visibility="player",
            revision=0,
        )
        session.add(npc)
        session.flush()
        introduced = _add_event(
            session,
            campaign.id,
            "npc_introduced",
            {
                "npc_id": str(npc.id),
                "name": npc.name,
                "public_description": npc.public_description,
                "world_revision": next_world_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        npc.introduced_by_event_id = introduced.id
        npc_id = npc.id
    else:
        npc_id = change.npc_id
    if isinstance(change, NPCDepart):
        presence = _current_npc_presence(session, campaign.id, npc_id)
        assert presence is not None
        departed = _add_event(
            session,
            campaign.id,
            "npc_departed",
            {
                "npc_id": str(npc_id),
                "scene_id": str(scene.id),
                "world_revision": next_world_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        presence.status = "departed"
        presence.revision += 1
        presence.departed_by_event_id = departed.id
    else:
        arrived = _add_event(
            session,
            campaign.id,
            "npc_arrived",
            {
                "npc_id": str(npc_id),
                "scene_id": str(scene.id),
                "world_revision": next_world_revision,
            },
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
        session.add(
            SceneNPCPresence(
                campaign_id=campaign.id,
                scene_id=scene.id,
                npc_id=npc_id,
                status="present",
                revision=0,
                arrived_by_event_id=arrived.id,
            )
        )
    campaign.world_revision = next_world_revision
    return True


def _apply_decision_consequence(
    session: Session,
    campaign: Campaign,
    consequence: DecisionConsequence,
    *,
    turn_id: uuid.UUID,
    actor_character_id: uuid.UUID | None,
) -> None:
    if isinstance(consequence, DecisionFactConsequence):
        _record_fact_projection(
            session,
            campaign,
            fact_type=consequence.fact_type,
            subject_npc_id=consequence.subject_npc_id,
            value=consequence.value,
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
    elif isinstance(consequence, DecisionQuestConsequence):
        quest = session.get(Quest, consequence.quest_id)
        assert quest is not None
        _apply_quest_transition(
            session,
            campaign,
            quest,
            consequence.status,
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )
    elif isinstance(consequence, DecisionObjectiveConsequence):
        objective = session.get(QuestObjective, consequence.objective_id)
        assert objective is not None
        _apply_objective_transition(
            session,
            campaign,
            objective,
            consequence.status,
            turn_id=turn_id,
            actor_character_id=actor_character_id,
        )


def _apply_decision_choice(
    session: Session,
    campaign: Campaign,
    turn: Turn,
    choice: tuple[DecisionPoint, DecisionOption, list[DecisionConsequence]],
    *,
    actor_character_id: uuid.UUID | None,
) -> None:
    decision, option, consequences = choice
    next_revision = campaign.world_revision + 1
    event = _add_event(
        session,
        campaign.id,
        "decision_selected",
        {
            "decision_id": str(decision.id),
            "decision_key": decision.decision_key,
            "option_id": str(option.id),
            "option_key": option.option_key,
            "world_revision": next_revision,
        },
        turn_id=turn.id,
        actor_character_id=actor_character_id,
    )
    decision.status = "selected"
    decision.selected_option_key = option.option_key
    decision.revision += 1
    decision.selected_by_event_id = event.id
    session.add(
        DecisionSelection(
            campaign_id=campaign.id,
            decision_id=decision.id,
            option_id=option.id,
            turn_id=turn.id,
            actor_character_id=actor_character_id,
            world_revision=next_revision,
            event_id=event.id,
        )
    )
    campaign.world_revision = next_revision
    for consequence in consequences:
        _apply_decision_consequence(
            session,
            campaign,
            consequence,
            turn_id=turn.id,
            actor_character_id=actor_character_id,
        )


def _apply_state_changes(
    session: Session,
    campaign_id: uuid.UUID,
    character: Character | None,
    changes: list,
    *,
    turn_id: uuid.UUID | None = None,
    actor_character_id: uuid.UUID | None = None,
) -> None:
    character_changed = False
    campaign = session.get(Campaign, campaign_id)
    assert campaign is not None
    for change in changes:
        if isinstance(change, HPDelta):
            assert character is not None
            character.hp = (character.hp or 0) + change.amount
            character_changed = True
        elif isinstance(change, InventoryChange):
            assert character is not None
            inventory = dict(character.inventory)
            new_quantity = inventory.get(change.item_name, 0) + change.quantity_delta
            if new_quantity:
                inventory[change.item_name] = new_quantity
            else:
                inventory.pop(change.item_name, None)
            character.inventory = inventory
            character_changed = True
        elif isinstance(change, MoveLocation):
            active_scene = session.scalar(
                select(Scene).where(
                    Scene.campaign_id == campaign_id,
                    Scene.status == "active",
                )
            )
            if active_scene is None:
                raise ConflictError("Campaign has no active scene")
            next_world_revision = campaign.world_revision + 1
            active_presences = list(
                session.scalars(
                    select(SceneNPCPresence).where(
                        SceneNPCPresence.scene_id == active_scene.id,
                        SceneNPCPresence.status == "present",
                    )
                )
            )
            for presence in active_presences:
                departed = _add_event(
                    session,
                    campaign_id,
                    "npc_departed",
                    {
                        "npc_id": str(presence.npc_id),
                        "scene_id": str(active_scene.id),
                        "world_revision": next_world_revision,
                    },
                    turn_id=turn_id,
                    actor_character_id=actor_character_id,
                )
                presence.status = "departed"
                presence.revision += 1
                presence.departed_by_event_id = departed.id
            closed_event = _add_event(
                session,
                campaign_id,
                "scene_closed",
                {
                    "scene_id": str(active_scene.id),
                    "location_id": str(active_scene.location_id),
                    "world_revision": next_world_revision,
                },
                turn_id=turn_id,
                actor_character_id=actor_character_id,
            )
            active_scene.status = "closed"
            active_scene.revision += 1
            active_scene.closed_by_event_id = closed_event.id
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
            session.flush()
            scene_sequence = (
                session.scalar(
                    select(func.max(Scene.sequence)).where(Scene.campaign_id == campaign_id)
                )
                or 0
            ) + 1
            new_scene = Scene(
                campaign_id=campaign_id,
                location_id=destination.id,
                sequence=scene_sequence,
                title=destination.name,
                summary=destination.description,
                status="active",
                revision=0,
            )
            session.add(new_scene)
            session.flush()
            opened_event = _add_event(
                session,
                campaign_id,
                "scene_opened",
                {
                    "scene_id": str(new_scene.id),
                    "location_id": str(destination.id),
                    "title": new_scene.title,
                    "world_revision": next_world_revision,
                },
                turn_id=turn_id,
                actor_character_id=actor_character_id,
            )
            new_scene.opened_by_event_id = opened_event.id
            campaign.world_revision = next_world_revision
        else:
            handled = _apply_npc_presence_change(
                session,
                campaign,
                change,
                turn_id=turn_id,
                actor_character_id=actor_character_id,
            )
            if not handled:
                handled = _apply_world_fact_change(
                    session,
                    campaign,
                    change,
                    turn_id=turn_id,
                    actor_character_id=actor_character_id,
                )
            if not handled:
                handled = _apply_quest_decision_change(
                    session,
                    campaign,
                    change,
                    turn_id=turn_id,
                    actor_character_id=actor_character_id,
                )
            if not handled:
                _apply_faction_time_change(
                    session,
                    campaign,
                    change,
                    turn_id=turn_id,
                    actor_character_id=actor_character_id,
                )
    if character_changed and character is not None:
        character.state_revision += 1


def process_turn(
    session: Session,
    campaign_id: uuid.UUID,
    player_action: str,
    provider: DMProvider,
    actor_character_id: uuid.UUID | None = None,
    dice_service: DiceService | None = None,
) -> TurnRead:
    campaign = _campaign_for_update(session, campaign_id)
    active = _active_turn(session, campaign_id)
    if active is not None:
        raise ConflictError(f"Campaign already has active turn {active.id}")
    state_before = get_campaign_state(session, campaign_id)
    if campaign.play_mode == "party_commander":
        if not state_before.party_ready:
            raise ConflictError(
                f"At least {campaign.party_min_active} finalized active characters are required"
            )
        if actor_character_id is None:
            raise ConflictError("Party Commander turns require actor_character_id")
    character = None
    if actor_character_id is not None:
        character = session.scalar(
            select(Character).where(
                Character.campaign_id == campaign_id,
                Character.id == actor_character_id,
            )
        )
        if character is None:
            raise NotFoundError("Acting character not found in campaign")
        if character.creation_status != "finalized" or character.party_status != "active":
            raise ConflictError("Acting character must be finalized and active")
    elif len(state_before.characters) == 1:
        character = session.get(Character, state_before.characters[0].id)
    output = provider.generate_turn(_provider_context(state_before), player_action)
    if output.dice_requests:
        raise ConflictError(
            "Legacy provider dice requests are disabled; use the authoritative turn-execution path"
        )

    snapshot = None
    if character is not None:
        equipped_ids = {
            item_id
            for item_id in [
                character.equipped_items.get("worn_armor_item_id"),
                *character.equipped_items.get("held_item_ids", []),
            ]
            if item_id
        }
        catalogs = get_ruleset_registry().get_character_catalogs(
            campaign.ruleset_release_id, campaign.ruleset_data_catalog_id
        )
        equipped_names = frozenset(
            item.item_name
            for item in (catalogs.character_state.equipment if catalogs.character_state else [])
            if item.item_id in equipped_ids
        )
        snapshot = CharacterSnapshot(
            character.hp or 0,
            character.max_hp or 0,
            dict(character.inventory),
            equipped_names,
        )
    StateChangeValidator().validate(snapshot, output.state_changes)
    _validate_world_changes(session, campaign_id, output.state_changes)

    turn_sequence = (
        session.scalar(select(func.max(Turn.sequence)).where(Turn.campaign_id == campaign_id)) or 0
    ) + 1
    turn = Turn(
        command_id=uuid.uuid4(),
        campaign_id=campaign_id,
        sequence=turn_sequence,
        player_action=player_action,
        dm_narration=output.narration,
        provider=provider.provider_name,
        model=provider.model_name,
        structured_output=output.model_dump(mode="json"),
        actor_character_id=character.id if character else None,
        workflow_version=TURN_WORKFLOW_LEGACY,
        status="completed",
        resumable=False,
        state_revision_before=character.state_revision if character else None,
        state_revision_after=None,
        world_revision_before=campaign.world_revision,
        world_revision_after=None,
        completed_at=datetime.now(UTC),
    )
    session.add(turn)
    session.flush()

    _add_event(
        session,
        campaign_id,
        "player_action",
        {
            "action": player_action,
            "actor_character_id": str(character.id) if character else None,
        },
        turn_id=turn.id,
        actor_character_id=character.id if character else None,
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
            actor_character_id=character.id if character else None,
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
            actor_character_id=character.id if character else None,
        )

    _apply_state_changes(session, campaign_id, character, output.state_changes)
    turn.state_revision_after = character.state_revision if character else None
    turn.world_revision_after = campaign.world_revision
    _add_event(
        session,
        campaign_id,
        "dm_response",
        {"narration": output.narration},
        turn_id=turn.id,
        actor_character_id=character.id if character else None,
    )
    if output.state_changes:
        _add_event(
            session,
            campaign_id,
            "state_changed",
            {
                "changes": [change.model_dump(mode="json") for change in output.state_changes],
                "affected_character_ids": [str(character.id)] if character else [],
            },
            turn_id=turn.id,
            actor_character_id=character.id if character else None,
        )
    session.commit()
    _project_completed_turn_best_effort(session, turn)
    state_after = get_campaign_state(session, campaign_id)
    return TurnRead(
        id=turn.id,
        sequence=turn.sequence,
        player_action=turn.player_action,
        narration=turn.dm_narration,
        actor_character_id=turn.actor_character_id,
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
