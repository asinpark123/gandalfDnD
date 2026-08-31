import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.character_creation import CharacterSheet
from app.character_state import CharacterMechanicalState, Loadout

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class CampaignCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ShortText
    ruleset_release_id: str = Field(default="srd-5.2.1", pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    starting_location: ShortText = "Roadside Inn"


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    ruleset_release_id: str
    ruleset_data_catalog_id: str
    status: str
    play_mode: str
    party_min_active: int
    party_max_active: int
    created_at: datetime


class CharacterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ShortText


class CharacterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ruleset_release_id: str
    ruleset_data_catalog_id: str
    name: str
    creation_status: str
    revision: int
    hp: int | None
    max_hp: int | None
    inventory: dict[str, int]
    character_sheet: CharacterSheet | None
    finalized_at: datetime | None
    party_position: int
    control_mode: str
    party_status: str
    state_revision: int
    equipped_items: Loadout
    resources: dict[str, int]
    mechanical_state: CharacterMechanicalState | None = None


class LoadoutUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    worn_armor_item_id: str | None = None
    held_item_ids: list[str] = Field(default_factory=list, max_length=2)


class CharacterGrantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ruleset_release_id: str
    ruleset_data_catalog_id: str
    acquisition_event_id: uuid.UUID
    revision: int
    grant_type: str
    choice_slot: str
    definition_key: str
    source_definition_key: str
    value: dict
    active: bool


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None


class HPDelta(BaseModel):
    type: Literal["hp_delta"]
    amount: int = Field(ge=-999, le=999)
    reason: ShortText


class MoveLocation(BaseModel):
    type: Literal["move_location"]
    location_name: ShortText
    description: str | None = Field(default=None, max_length=2000)


class InventoryChange(BaseModel):
    type: Literal["inventory_change"]
    item_name: ShortText
    quantity_delta: int = Field(ge=-999, le=999)
    reason: ShortText


StateChange = Annotated[
    HPDelta | MoveLocation | InventoryChange,
    Field(discriminator="type"),
]


class DiceRequest(BaseModel):
    notation: str = Field(pattern=r"^[1-9]\d*d([2-9]|[1-9]\d{1,2})$", max_length=20)
    modifier: int = Field(default=0, ge=-100, le=100)
    purpose: ShortText
    hidden: bool = False


class DMTurnOutput(BaseModel):
    narration: str = Field(min_length=1, max_length=8000)
    state_changes: list[StateChange] = Field(default_factory=list, max_length=20)
    dice_requests: list[DiceRequest] = Field(default_factory=list, max_length=10)


class TurnCreate(BaseModel):
    action: str = Field(min_length=1, max_length=4000)
    actor_character_id: uuid.UUID | None = None


class DiceRollRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ruleset_release_id: str
    ruleset_data_catalog_id: str
    notation: str
    rolls: list[int]
    modifier: int
    total: int
    purpose: str
    hidden: bool
    actor_character_id: uuid.UUID | None


class CampaignState(BaseModel):
    campaign: CampaignRead
    character: CharacterRead | None
    characters: list[CharacterRead]
    party_ready: bool
    location: LocationRead
    turn_count: int


class TurnRead(BaseModel):
    id: uuid.UUID
    sequence: int
    player_action: str
    narration: str
    actor_character_id: uuid.UUID | None
    dice_rolls: list[DiceRollRead]
    state: CampaignState


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ruleset_release_id: str
    ruleset_data_catalog_id: str
    sequence: int
    event_type: str
    visibility: str
    payload: dict
    actor_character_id: uuid.UUID | None
    created_at: datetime


class HealthRead(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]
    environment: str
