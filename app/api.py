import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.character_creation import (
    CharacterChoiceError,
    CharacterFinalizeRequest,
)
from app.character_state import CharacterCreationOptions, CharacterStateError
from app.combat_attacks import execute_combat_attack, replay_combat_attack
from app.combat_health import execute_combat_health, resolve_combat_outcome
from app.combat_turns import (
    end_combat_turn,
    execute_combat_action,
    move_combatant,
    respond_to_combat_reaction,
)
from app.config import Settings, get_settings
from app.db import get_session
from app.dice import DiceService, get_dice_service
from app.llm.base import DMProvider, TurnInterpretationProvider, TurnNarrationProvider
from app.llm.factory import get_dm_provider, get_turn_interpreter, get_turn_narrator
from app.memory_context import TurnMemoryContextService, get_turn_memory_context_service
from app.resolution import ResolutionCreate, ResolutionError
from app.rulesets import UnknownRulesetDataCatalogError, UnknownRulesetError, get_ruleset_registry
from app.schemas import (
    APIErrorRead,
    CampaignCreate,
    CampaignRead,
    CampaignState,
    CharacterCreate,
    CharacterGrantRead,
    CharacterRead,
    CombatActionCreate,
    CombatAttackCreate,
    CombatAttackExecutionRead,
    CombatAttackReplayRead,
    CombatEncounterCreate,
    CombatEncounterRead,
    CombatEndTurnCreate,
    CombatHealthCreate,
    CombatHealthExecutionRead,
    CombatMoveCreate,
    CombatOutcomeCreate,
    CombatOutcomeExecutionRead,
    CombatReactionCreate,
    CombatReplayRead,
    CombatStartCreate,
    CombatTieResolutionCreate,
    EventRead,
    HealthRead,
    LoadoutUpdate,
    ProviderCallRead,
    RuleResolutionRead,
    RuleResolutionReplayRead,
    TurnCreate,
    TurnExecutionCreate,
    TurnExecutionRead,
    TurnFinalizationRead,
    TurnInterpretationRead,
    TurnRead,
    WorldStateRead,
)
from app.services import (
    ConflictError,
    NotFoundError,
    TurnNarrationError,
    WorldTargetConflict,
    add_character,
    cancel_turn_execution,
    create_campaign,
    create_combat_encounter,
    create_rule_resolution,
    create_turn_execution,
    finalize_character,
    finalize_turn_execution,
    get_campaign_state,
    get_character_read,
    get_combat_encounter,
    get_rule_resolution,
    get_turn_execution,
    get_world_state,
    interpret_turn_execution,
    list_character_grants,
    list_characters,
    list_events,
    list_provider_calls,
    list_rule_resolutions,
    list_turn_executions,
    process_turn,
    replay_combat_encounter,
    replay_rule_resolution,
    resolve_combat_initiative_tie,
    resume_turn_execution,
    start_combat_initiative,
    update_character_loadout,
)
from app.turn_interpretation import TurnInterpretationError
from app.validation import InvalidStateChange

SessionDep = Annotated[Session, Depends(get_session)]
ProviderDep = Annotated[DMProvider, Depends(get_dm_provider)]
InterpreterDep = Annotated[TurnInterpretationProvider, Depends(get_turn_interpreter)]
NarratorDep = Annotated[TurnNarrationProvider, Depends(get_turn_narrator)]
DiceDep = Annotated[DiceService, Depends(get_dice_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
MemoryContextDep = Annotated[TurnMemoryContextService, Depends(get_turn_memory_context_service)]


def create_app() -> FastAPI:
    app = FastAPI(title="GandalfDnD", version="0.1.0")

    @app.get("/health", response_model=HealthRead)
    def health(session: SessionDep, settings: SettingsDep) -> HealthRead:
        session.execute(text("SELECT 1"))
        return HealthRead(status="ok", database="ok", environment=settings.environment)

    @app.post("/campaigns", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
    def campaigns_create(data: CampaignCreate, session: SessionDep) -> CampaignRead:
        try:
            return CampaignRead.model_validate(create_campaign(session, data))
        except UnknownRulesetError as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail="Campaign could not be created") from exc

    @app.post(
        "/campaigns/{campaign_id}/character",
        response_model=CharacterRead,
        status_code=status.HTTP_201_CREATED,
    )
    def characters_create(
        campaign_id: uuid.UUID, data: CharacterCreate, session: SessionDep
    ) -> CharacterRead:
        try:
            return CharacterRead.model_validate(add_character(session, campaign_id, data))
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/characters",
        response_model=CharacterRead,
        status_code=status.HTTP_201_CREATED,
    )
    def party_characters_create(
        campaign_id: uuid.UUID, data: CharacterCreate, session: SessionDep
    ) -> CharacterRead:
        return characters_create(campaign_id, data, session)

    @app.get("/campaigns/{campaign_id}/characters", response_model=list[CharacterRead])
    def party_characters_list(campaign_id: uuid.UUID, session: SessionDep) -> list[CharacterRead]:
        try:
            return [
                get_character_read(session, campaign_id, character.id)
                for character in list_characters(session, campaign_id)
            ]
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/rulesets/{ruleset_release_id}/character-creation/options",
        response_model=CharacterCreationOptions,
    )
    def character_creation_options(ruleset_release_id: str) -> CharacterCreationOptions:
        try:
            catalogs = get_ruleset_registry().get_character_catalogs(ruleset_release_id)
        except (UnknownRulesetError, UnknownRulesetDataCatalogError) as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return CharacterCreationOptions(
            selected_ruleset_data_catalog_id=catalogs.selected.id,
            character_creation=catalogs.character_creation,
            party=catalogs.character_state.party if catalogs.character_state else None,
        )

    @app.post(
        "/campaigns/{campaign_id}/character/finalize",
        response_model=CharacterRead,
    )
    def characters_finalize(
        campaign_id: uuid.UUID,
        data: CharacterFinalizeRequest,
        session: SessionDep,
    ) -> CharacterRead:
        try:
            character = finalize_character(session, campaign_id, data)
            return get_character_read(session, campaign_id, character.id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except CharacterChoiceError as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/characters/{character_id}/finalize",
        response_model=CharacterRead,
    )
    def party_characters_finalize(
        campaign_id: uuid.UUID,
        character_id: uuid.UUID,
        data: CharacterFinalizeRequest,
        session: SessionDep,
    ) -> CharacterRead:
        try:
            character = finalize_character(session, campaign_id, data, character_id)
            return get_character_read(session, campaign_id, character.id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except CharacterChoiceError as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.put(
        "/campaigns/{campaign_id}/characters/{character_id}/loadout",
        response_model=CharacterRead,
    )
    def party_character_loadout(
        campaign_id: uuid.UUID,
        character_id: uuid.UUID,
        data: LoadoutUpdate,
        session: SessionDep,
    ) -> CharacterRead:
        try:
            return update_character_loadout(session, campaign_id, character_id, data)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except CharacterStateError as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get(
        "/campaigns/{campaign_id}/character/grants",
        response_model=list[CharacterGrantRead],
    )
    def character_grants(campaign_id: uuid.UUID, session: SessionDep) -> list[CharacterGrantRead]:
        try:
            return [
                CharacterGrantRead.model_validate(grant)
                for grant in list_character_grants(session, campaign_id)
            ]
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/campaigns/{campaign_id}/characters/{character_id}/grants",
        response_model=list[CharacterGrantRead],
    )
    def party_character_grants(
        campaign_id: uuid.UUID, character_id: uuid.UUID, session: SessionDep
    ) -> list[CharacterGrantRead]:
        try:
            return [
                CharacterGrantRead.model_validate(grant)
                for grant in list_character_grants(session, campaign_id, character_id)
            ]
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/campaigns/{campaign_id}/state", response_model=CampaignState)
    def campaigns_state(campaign_id: uuid.UUID, session: SessionDep) -> CampaignState:
        try:
            return get_campaign_state(session, campaign_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/campaigns/{campaign_id}/world", response_model=WorldStateRead)
    def campaigns_world(campaign_id: uuid.UUID, session: SessionDep) -> WorldStateRead:
        try:
            return get_world_state(session, campaign_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/turns",
        response_model=TurnRead,
        status_code=status.HTTP_201_CREATED,
    )
    def turns_create(
        campaign_id: uuid.UUID,
        data: TurnCreate,
        session: SessionDep,
        provider: ProviderDep,
    ) -> TurnRead:
        try:
            return process_turn(
                session,
                campaign_id,
                data.action,
                provider,
                actor_character_id=data.actor_character_id,
            )
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except InvalidStateChange as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/turn-executions",
        response_model=TurnExecutionRead,
        status_code=status.HTTP_201_CREATED,
        responses={
            409: {
                "model": APIErrorRead,
                "description": "Turn input conflicts with the current campaign state.",
            }
        },
    )
    def turn_executions_create(
        campaign_id: uuid.UUID,
        data: TurnExecutionCreate,
        session: SessionDep,
    ) -> TurnExecutionRead | JSONResponse:
        try:
            return create_turn_execution(session, campaign_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except WorldTargetConflict as exc:
            session.rollback()
            return JSONResponse(
                status_code=409,
                content=APIErrorRead(
                    detail=str(exc),
                    code=exc.code,
                    recovery=exc.recovery,
                ).model_dump(),
            )
        except InvalidStateChange as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except (ConflictError, IntegrityError) as exc:
            session.rollback()
            detail = str(exc) if isinstance(exc, ConflictError) else "Campaign turn is busy"
            raise HTTPException(status_code=409, detail=detail) from exc

    @app.get(
        "/campaigns/{campaign_id}/turn-executions",
        response_model=list[TurnExecutionRead],
    )
    def turn_executions_list(
        campaign_id: uuid.UUID, session: SessionDep
    ) -> list[TurnExecutionRead]:
        try:
            return list_turn_executions(session, campaign_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/campaigns/{campaign_id}/turn-executions/{turn_id}",
        response_model=TurnExecutionRead,
    )
    def turn_executions_get(
        campaign_id: uuid.UUID, turn_id: uuid.UUID, session: SessionDep
    ) -> TurnExecutionRead:
        try:
            return get_turn_execution(session, campaign_id, turn_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/turn-executions/{turn_id}/cancel",
        response_model=TurnExecutionRead,
    )
    def turn_executions_cancel(
        campaign_id: uuid.UUID, turn_id: uuid.UUID, session: SessionDep
    ) -> TurnExecutionRead:
        try:
            return cancel_turn_execution(session, campaign_id, turn_id)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/turn-executions/{turn_id}/resume",
        response_model=TurnExecutionRead,
    )
    def turn_executions_resume(
        campaign_id: uuid.UUID,
        turn_id: uuid.UUID,
        session: SessionDep,
        settings: SettingsDep,
    ) -> TurnExecutionRead:
        try:
            return resume_turn_execution(
                session,
                campaign_id,
                turn_id,
                stale_after_seconds=settings.turn_stage_timeout_seconds,
            )
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get(
        "/campaigns/{campaign_id}/turn-executions/{turn_id}/provider-calls",
        response_model=list[ProviderCallRead],
    )
    def turn_execution_provider_calls(
        campaign_id: uuid.UUID, turn_id: uuid.UUID, session: SessionDep
    ) -> list[ProviderCallRead]:
        try:
            return [
                ProviderCallRead.model_validate(call)
                for call in list_provider_calls(session, campaign_id, turn_id)
            ]
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/turn-executions/{turn_id}/interpret",
        response_model=TurnInterpretationRead,
    )
    def turn_executions_interpret(
        campaign_id: uuid.UUID,
        turn_id: uuid.UUID,
        session: SessionDep,
        provider: InterpreterDep,
        dice_service: DiceDep,
        memory_context: MemoryContextDep,
    ) -> TurnInterpretationRead:
        try:
            return interpret_turn_execution(
                session,
                campaign_id,
                turn_id,
                provider,
                dice_service=dice_service,
                memory_context_service=memory_context,
            )
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ResolutionError as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except TurnInterpretationError as exc:
            session.rollback()
            raise HTTPException(status_code=502, detail=exc.api_detail()) from exc

    @app.post(
        "/campaigns/{campaign_id}/turn-executions/{turn_id}/finalize",
        response_model=TurnFinalizationRead,
    )
    def turn_executions_finalize(
        campaign_id: uuid.UUID,
        turn_id: uuid.UUID,
        session: SessionDep,
        provider: NarratorDep,
        memory_context: MemoryContextDep,
    ) -> TurnFinalizationRead:
        try:
            return finalize_turn_execution(
                session,
                campaign_id,
                turn_id,
                provider,
                memory_context_service=memory_context,
            )
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except InvalidStateChange as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except TurnNarrationError as exc:
            session.rollback()
            raise HTTPException(status_code=502, detail=exc.api_detail()) from exc

    @app.post(
        "/campaigns/{campaign_id}/resolutions",
        response_model=RuleResolutionRead,
        status_code=status.HTTP_201_CREATED,
    )
    def resolutions_create(
        campaign_id: uuid.UUID,
        data: ResolutionCreate,
        session: SessionDep,
        dice_service: DiceDep,
    ) -> RuleResolutionRead:
        try:
            return create_rule_resolution(session, campaign_id, data, dice_service)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ResolutionError as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get(
        "/campaigns/{campaign_id}/resolutions",
        response_model=list[RuleResolutionRead],
    )
    def resolutions_list(
        campaign_id: uuid.UUID,
        session: SessionDep,
    ) -> list[RuleResolutionRead]:
        try:
            return list_rule_resolutions(session, campaign_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/campaigns/{campaign_id}/resolutions/{resolution_id}",
        response_model=RuleResolutionRead,
    )
    def resolutions_get(
        campaign_id: uuid.UUID,
        resolution_id: uuid.UUID,
        session: SessionDep,
    ) -> RuleResolutionRead:
        try:
            return get_rule_resolution(session, campaign_id, resolution_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/resolutions/{resolution_id}/replay",
        response_model=RuleResolutionReplayRead,
    )
    def resolutions_replay(
        campaign_id: uuid.UUID,
        resolution_id: uuid.UUID,
        session: SessionDep,
    ) -> RuleResolutionReplayRead:
        try:
            return replay_rule_resolution(session, campaign_id, resolution_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ResolutionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    combat_errors = {
        404: {"model": APIErrorRead, "description": "Campaign or combat record not found"},
        409: {"model": APIErrorRead, "description": "Stale or illegal combat state"},
        422: {"model": APIErrorRead, "description": "Invalid combat command"},
    }

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters",
        response_model=CombatEncounterRead,
        status_code=status.HTTP_201_CREATED,
        responses=combat_errors,
    )
    def combat_encounters_create(
        campaign_id: uuid.UUID,
        data: CombatEncounterCreate,
        session: SessionDep,
    ) -> CombatEncounterRead:
        try:
            return create_combat_encounter(session, campaign_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat encounter could not be created"
            ) from exc

    @app.get(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}",
        response_model=CombatEncounterRead,
        responses=combat_errors,
    )
    def combat_encounters_get(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        session: SessionDep,
    ) -> CombatEncounterRead:
        try:
            return get_combat_encounter(session, campaign_id, encounter_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/start",
        response_model=CombatEncounterRead,
        responses=combat_errors,
    )
    def combat_encounters_start(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        data: CombatStartCreate,
        session: SessionDep,
        dice_service: DiceDep,
    ) -> CombatEncounterRead:
        try:
            return start_combat_initiative(session, campaign_id, encounter_id, data, dice_service)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat initiative could not start"
            ) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/initiative-ties/{tie_id}",
        response_model=CombatEncounterRead,
        responses=combat_errors,
    )
    def combat_initiative_ties_resolve(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        tie_id: uuid.UUID,
        data: CombatTieResolutionCreate,
        session: SessionDep,
    ) -> CombatEncounterRead:
        try:
            return resolve_combat_initiative_tie(session, campaign_id, encounter_id, tie_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Initiative tie could not be resolved"
            ) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/replay",
        response_model=CombatReplayRead,
        responses=combat_errors,
    )
    def combat_encounters_replay(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        session: SessionDep,
    ) -> CombatReplayRead:
        try:
            return replay_combat_encounter(session, campaign_id, encounter_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/move",
        response_model=CombatEncounterRead,
        responses=combat_errors,
    )
    def combat_encounters_move(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        data: CombatMoveCreate,
        session: SessionDep,
    ) -> CombatEncounterRead:
        try:
            return move_combatant(session, campaign_id, encounter_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat movement could not be applied"
            ) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/actions",
        response_model=CombatEncounterRead,
        responses=combat_errors,
    )
    def combat_encounters_action(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        data: CombatActionCreate,
        session: SessionDep,
    ) -> CombatEncounterRead:
        try:
            return execute_combat_action(session, campaign_id, encounter_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat action could not be applied"
            ) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/reaction-windows/{window_id}",
        response_model=CombatEncounterRead,
        responses=combat_errors,
    )
    def combat_reaction_windows_respond(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        window_id: uuid.UUID,
        data: CombatReactionCreate,
        session: SessionDep,
    ) -> CombatEncounterRead:
        try:
            return respond_to_combat_reaction(session, campaign_id, encounter_id, window_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat reaction could not be applied"
            ) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/end-turn",
        response_model=CombatEncounterRead,
        responses=combat_errors,
    )
    def combat_encounters_end_turn(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        data: CombatEndTurnCreate,
        session: SessionDep,
    ) -> CombatEncounterRead:
        try:
            return end_combat_turn(session, campaign_id, encounter_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail="Combat turn could not end") from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks",
        response_model=CombatAttackExecutionRead,
        responses=combat_errors,
    )
    def combat_attacks_create(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        data: CombatAttackCreate,
        session: SessionDep,
        dice_service: DiceDep,
    ) -> CombatAttackExecutionRead:
        try:
            return execute_combat_attack(session, campaign_id, encounter_id, data, dice_service)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat attack could not be applied"
            ) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attacks/{resolution_id}/replay",
        response_model=CombatAttackReplayRead,
        responses=combat_errors,
    )
    def combat_attacks_replay(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        resolution_id: uuid.UUID,
        session: SessionDep,
    ) -> CombatAttackReplayRead:
        try:
            return replay_combat_attack(session, campaign_id, encounter_id, resolution_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/health-actions",
        response_model=CombatHealthExecutionRead,
        responses=combat_errors,
    )
    def combat_health_create(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        data: CombatHealthCreate,
        session: SessionDep,
        dice_service: DiceDep,
    ) -> CombatHealthExecutionRead:
        try:
            return execute_combat_health(session, campaign_id, encounter_id, data, dice_service)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat health action could not be applied"
            ) from exc

    @app.post(
        "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/outcome",
        response_model=CombatOutcomeExecutionRead,
        responses=combat_errors,
    )
    def combat_outcome_create(
        campaign_id: uuid.UUID,
        encounter_id: uuid.UUID,
        data: CombatOutcomeCreate,
        session: SessionDep,
    ) -> CombatOutcomeExecutionRead:
        try:
            return resolve_combat_outcome(session, campaign_id, encounter_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Combat outcome could not be applied"
            ) from exc

    @app.get("/campaigns/{campaign_id}/events", response_model=list[EventRead])
    def events_list(campaign_id: uuid.UUID, session: SessionDep) -> list[EventRead]:
        try:
            return [EventRead.model_validate(event) for event in list_events(session, campaign_id)]
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


app = create_app()
