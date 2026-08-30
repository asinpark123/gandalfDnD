import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_session
from app.llm.base import DMProvider
from app.llm.factory import get_dm_provider
from app.rulesets import UnknownRulesetError
from app.schemas import (
    CampaignCreate,
    CampaignRead,
    CampaignState,
    CharacterCreate,
    CharacterRead,
    EventRead,
    HealthRead,
    TurnCreate,
    TurnRead,
)
from app.services import (
    ConflictError,
    NotFoundError,
    add_character,
    create_campaign,
    get_campaign_state,
    list_events,
    process_turn,
)
from app.validation import InvalidStateChange

SessionDep = Annotated[Session, Depends(get_session)]
ProviderDep = Annotated[DMProvider, Depends(get_dm_provider)]
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

    @app.get("/campaigns/{campaign_id}/state", response_model=CampaignState)
    def campaigns_state(campaign_id: uuid.UUID, session: SessionDep) -> CampaignState:
        try:
            return get_campaign_state(session, campaign_id)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

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
            return process_turn(session, campaign_id, data.action, provider)
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except InvalidStateChange as exc:
            session.rollback()
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/campaigns/{campaign_id}/events", response_model=list[EventRead])
    def events_list(campaign_id: uuid.UUID, session: SessionDep) -> list[EventRead]:
        try:
            return [EventRead.model_validate(event) for event in list_events(session, campaign_id)]
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


app = create_app()
