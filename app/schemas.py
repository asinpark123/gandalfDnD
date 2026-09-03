import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.character_creation import CharacterSheet
from app.character_state import CharacterMechanicalState, Loadout
from app.resolution import (
    AdvantageState,
    AppliedAdjustmentSource,
    ModifierComponent,
    ResolutionCreate,
    ResolutionOutcome,
    ResolutionType,
)
from app.turn_interpretation import TurnIntent

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
NPCName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
NarrativeText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
]
WorldFactType = Literal[
    "npc_attitude", "relationship_note", "promise", "discovery", "clue"
]


class StartingNPCCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: NPCName
    public_description: str | None = Field(default=None, max_length=2000)


class StartingSceneCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: ShortText
    summary: str | None = Field(default=None, max_length=2000)
    npcs: list[StartingNPCCreate] = Field(default_factory=list, max_length=8)


class CampaignCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ShortText
    ruleset_release_id: str = Field(default="srd-5.2.1", pattern=r"^[a-z0-9][a-z0-9.-]{2,79}$")
    starting_location: ShortText = "Roadside Inn"
    starting_scene: StartingSceneCreate | None = None


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
    world_revision: int
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


class SceneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sequence: int
    title: str
    summary: str | None
    status: str
    revision: int
    created_at: datetime


class NPCRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    public_description: str | None
    status: str
    revision: int
    created_at: datetime


class WorldFactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_npc_id: uuid.UUID | None
    fact_type: WorldFactType
    value: str
    status: str
    revision: int
    created_at: datetime


class WorldStateRead(BaseModel):
    campaign_id: uuid.UUID
    world_revision: int
    location: LocationRead
    scene: SceneRead
    present_npcs: list[NPCRead]
    facts: list[WorldFactRead]


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


class NPCAttitudeSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["npc_attitude_set"]
    npc_id: uuid.UUID
    attitude: Literal["friendly", "neutral", "wary", "hostile"]


class RelationshipNoteAdd(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["relationship_note_add"]
    npc_id: uuid.UUID
    note: NarrativeText


class PromiseRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["promise_record"]
    npc_id: uuid.UUID
    promise: NarrativeText


class DiscoveryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["discovery_record"]
    subject_npc_id: uuid.UUID | None = None
    discovery: NarrativeText


class ClueRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["clue_record"]
    subject_npc_id: uuid.UUID | None = None
    clue: NarrativeText


class WorldFactSupersede(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["world_fact_supersede"]
    fact_id: uuid.UUID
    expected_revision: int = Field(ge=0)
    value: NarrativeText


class WorldFactReveal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["world_fact_reveal"]
    fact_id: uuid.UUID
    expected_revision: int = Field(ge=0)


StateChange = Annotated[
    HPDelta
    | MoveLocation
    | InventoryChange
    | NPCAttitudeSet
    | RelationshipNoteAdd
    | PromiseRecord
    | DiscoveryRecord
    | ClueRecord
    | WorldFactSupersede
    | WorldFactReveal,
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


class TurnNarrationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    narration: str = Field(min_length=1, max_length=8000)
    resolution_id: uuid.UUID | None = None
    acknowledged_outcome: ResolutionOutcome | None = None
    state_changes: list[StateChange] = Field(default_factory=list, max_length=20)


class TurnCreate(BaseModel):
    action: str = Field(min_length=1, max_length=4000)
    actor_character_id: uuid.UUID | None = None


class TurnExecutionCreate(TurnCreate):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    target_npc_id: uuid.UUID | None = None


class TurnExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    command_id: uuid.UUID
    campaign_id: uuid.UUID
    sequence: int
    player_action: str
    actor_character_id: uuid.UUID | None
    target_npc_id: uuid.UUID | None
    workflow_version: str
    status: str
    failure_stage: str | None
    error_code: str | None
    error_detail: str | None
    resumable: bool
    resume_status: str | None
    intent_output: dict | None
    resolution_id: uuid.UUID | None
    state_revision_before: int | None
    state_revision_after: int | None
    world_revision_before: int | None
    world_revision_after: int | None
    interpretation_prompt_version: str | None
    narration_prompt_version: str | None
    stage_started_at: datetime | None
    narration: str | None = Field(validation_alias="dm_narration")
    structured_output: dict | None
    created_at: datetime
    completed_at: datetime | None


class ProviderCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stage: str
    attempt: int
    provider: str
    model: str | None
    prompt_version: str
    status: str
    latency_ms: int | None
    input_tokens: int | None
    output_tokens: int | None
    structured_output: dict | None
    error_code: str | None
    error_detail: str | None
    created_at: datetime


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


class RuleResolutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    command_id: uuid.UUID
    campaign_id: uuid.UUID
    actor_character_id: uuid.UUID
    ruleset_release_id: str
    character_state_catalog_id: str
    ruleset_data_catalog_id: str
    dice_roll_id: uuid.UUID
    character_revision: int
    state_revision: int
    resolution_type: ResolutionType
    ability: str
    skill: str | None
    difficulty_class: int
    rule_definition_keys: list[str]
    source_ids: list[str]
    command: ResolutionCreate
    modifier_formula: str
    modifier_components: list[ModifierComponent]
    advantage_sources: list[AppliedAdjustmentSource]
    disadvantage_sources: list[AppliedAdjustmentSource]
    advantage_state: AdvantageState
    dice_notation: str
    dice_faces: list[int]
    selected_die: int
    modifier: int
    total: int
    outcome: ResolutionOutcome
    resolver_version: str
    rng_version: str
    created_at: datetime


class TurnInterpretationRead(BaseModel):
    turn: TurnExecutionRead
    intent: TurnIntent
    resolution: RuleResolutionRead | None


class TurnFinalizationRead(BaseModel):
    turn: TurnExecutionRead
    intent: TurnIntent
    resolution: RuleResolutionRead | None
    state: CampaignState


class RuleResolutionReplayRead(BaseModel):
    resolution_id: uuid.UUID
    equivalent: bool
    replayed: RuleResolutionRead


class HealthRead(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]
    environment: str
