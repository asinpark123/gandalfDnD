import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.character_creation import (
    CharacterChoiceError,
    CharacterFinalizeRequest,
)
from app.character_state import CharacterCreationOptions, CharacterStateError
from app.config import Settings, get_settings
from app.db import get_session
from app.dice import DiceService, get_dice_service
from app.llm.base import DMProvider, TurnInterpretationProvider, TurnNarrationProvider
from app.llm.factory import get_dm_provider, get_turn_interpreter, get_turn_narrator
from app.resolution import ResolutionCreate, ResolutionError
from app.rulesets import UnknownRulesetDataCatalogError, UnknownRulesetError, get_ruleset_registry
from app.schemas import (
    CampaignCreate,
    CampaignRead,
    CampaignState,
    CharacterCreate,
    CharacterGrantRead,
    CharacterRead,
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
    add_character,
    cancel_turn_execution,
    create_campaign,
    create_rule_resolution,
    create_turn_execution,
    finalize_character,
    finalize_turn_execution,
    get_campaign_state,
    get_character_read,
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
    replay_rule_resolution,
    resume_turn_execution,
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
    )
    def turn_executions_create(
        campaign_id: uuid.UUID,
        data: TurnExecutionCreate,
        session: SessionDep,
    ) -> TurnExecutionRead:
        try:
            return create_turn_execution(session, campaign_id, data)
        except NotFoundError as exc:
            session.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
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
    ) -> TurnInterpretationRead:
        try:
            return interpret_turn_execution(
                session,
                campaign_id,
                turn_id,
                provider,
                dice_service,
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
    ) -> TurnFinalizationRead:
        try:
            return finalize_turn_execution(
                session,
                campaign_id,
                turn_id,
                provider,
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

    @app.get("/campaigns/{campaign_id}/events", response_model=list[EventRead])
    def events_list(campaign_id: uuid.UUID, session: SessionDep) -> list[EventRead]:
        try:
            return [EventRead.model_validate(event) for event in list_events(session, campaign_id)]
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


app = create_app()
