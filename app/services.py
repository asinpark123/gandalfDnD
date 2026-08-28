import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dice import DiceService
from app.llm.base import DMProvider
from app.models import Campaign, CampaignEvent, Character, DiceRoll, Location, Turn
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
    event = CampaignEvent(
        campaign_id=campaign_id,
        turn_id=turn_id,
        sequence=_next_event_sequence(session, campaign_id),
        event_type=event_type,
        visibility=visibility,
        payload=payload,
    )
    session.add(event)
    session.flush()
    return event


def create_campaign(session: Session, data: CampaignCreate) -> Campaign:
    campaign = Campaign(name=data.name, ruleset=data.ruleset)
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
        {"name": campaign.name, "starting_location": location.name},
    )
    session.commit()
    return campaign


def add_character(session: Session, campaign_id: uuid.UUID, data: CharacterCreate) -> Character:
    _campaign_for_update(session, campaign_id)
    existing = session.scalar(select(Character).where(Character.campaign_id == campaign_id))
    if existing is not None:
        raise ConflictError("Phase 0 supports one character per campaign")
    inventory = {name.strip(): quantity for name, quantity in data.inventory.items()}
    character = Character(
        campaign_id=campaign_id,
        name=data.name,
        max_hp=data.max_hp,
        hp=data.max_hp,
        inventory=inventory,
    )
    session.add(character)
    session.flush()
    _add_event(
        session,
        campaign_id,
        "character_created",
        {"character_id": str(character.id), "name": character.name, "max_hp": character.max_hp},
    )
    session.commit()
    return character


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
    _campaign_for_update(session, campaign_id)
    state_before = get_campaign_state(session, campaign_id)
    character = session.scalar(select(Character).where(Character.campaign_id == campaign_id))
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
