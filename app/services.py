import uuid
from datetime import UTC, datetime, timedelta
from time import perf_counter
from typing import Any

from pydantic import ValidationError
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
from app.models import (
    NPC,
    Campaign,
    CampaignEvent,
    Character,
    CharacterGrant,
    DiceRoll,
    Location,
    ProviderCall,
    RuleResolution,
    RulesetDataCatalog,
    RulesetRelease,
    Scene,
    SceneNPCPresence,
    Turn,
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
    HPDelta,
    InventoryChange,
    LoadoutUpdate,
    MoveLocation,
    RuleResolutionRead,
    RuleResolutionReplayRead,
    TurnExecutionCreate,
    TurnExecutionRead,
    TurnFinalizationRead,
    TurnInterpretationRead,
    TurnNarrationOutput,
    TurnRead,
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


class NotFoundError(LookupError):
    pass


class ConflictError(ValueError):
    pass


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


def get_world_state(session: Session, campaign_id: uuid.UUID) -> WorldStateRead:
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
    npcs = list(
        session.scalars(
            select(NPC)
            .join(SceneNPCPresence, SceneNPCPresence.npc_id == NPC.id)
            .where(
                SceneNPCPresence.scene_id == scene.id,
                SceneNPCPresence.status == "present",
                NPC.status == "active",
                NPC.visibility == "player",
            )
            .order_by(NPC.created_at, NPC.id)
        )
    )
    return WorldStateRead(
        campaign_id=campaign.id,
        world_revision=campaign.world_revision,
        location=location,
        scene=scene,
        present_npcs=npcs,
    )


def _validate_turn_target(
    session: Session, campaign_id: uuid.UUID, target_npc_id: uuid.UUID | None
) -> NPC | None:
    if target_npc_id is None:
        return None
    npc = session.get(NPC, target_npc_id)
    if npc is None or npc.campaign_id != campaign_id:
        raise NotFoundError("Target NPC not found in campaign")
    if npc.visibility != "player":
        raise ConflictError("Target NPC is not player-visible")
    if npc.status != "active":
        raise ConflictError("Target NPC is not active")
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
        raise ConflictError("Target NPC is not present in the current scene")
    return npc


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
        context = _provider_context(
            get_campaign_state(session, campaign_id),
            get_world_state(session, campaign_id),
            turn.target_npc_id,
        )
        attempt = _next_provider_attempt(session, turn.id, "interpretation")
        player_action = turn.player_action
        turn.status = "interpreting"
        turn.stage_started_at = datetime.now(UTC)
        session.commit()

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
    context = _provider_context(
        get_campaign_state(session, campaign_id),
        get_world_state(session, campaign_id),
        turn.target_npc_id,
    )
    attempt = _next_provider_attempt(session, turn.id, "narration")
    player_action = turn.player_action
    turn.status = "narrating"
    turn.stage_started_at = datetime.now(UTC)
    session.commit()

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


def _provider_context(
    state: CampaignState,
    world: WorldStateRead | None = None,
    target_npc_id: uuid.UUID | None = None,
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
        selected_target = next(
            (npc for npc in world.present_npcs if npc.id == target_npc_id), None
        )
        context["world"] = {
            "world_revision": world.world_revision,
            "scene": world.scene.model_dump(mode="json"),
            "present_npcs": [npc.model_dump(mode="json") for npc in world.present_npcs],
            "selected_target": (
                selected_target.model_dump(mode="json") if selected_target is not None else None
            ),
        }
    return context


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
