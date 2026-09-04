import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

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
StableKey = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9][a-z0-9._-]*$",
    ),
]
WorldFactType = Literal["npc_attitude", "relationship_note", "promise", "discovery", "clue"]


class APIErrorRead(BaseModel):
    detail: str
    code: str | None = None
    recovery: str | None = None


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
    narrative_time_minutes: int
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


class QuestObjectiveRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    objective_key: str
    title: str
    description: str | None
    status: str
    position: int
    revision: int
    created_at: datetime


class QuestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quest_key: str
    title: str
    summary: str | None
    status: str
    revision: int
    objectives: list[QuestObjectiveRead]
    created_at: datetime


class DecisionOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    option_key: str
    label: str
    description: str | None
    position: int


class DecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    decision_key: str
    prompt: str
    status: str
    selected_option_key: str | None
    revision: int
    options: list[DecisionOptionRead]
    created_at: datetime


class FactionRelationshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    relation_type: Literal["attitude", "membership"]
    character_id: uuid.UUID | None
    npc_id: uuid.UUID | None
    value: str
    revision: int
    created_at: datetime


class FactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    faction_key: str
    name: str
    description: str | None
    status: str
    revision: int
    relationships: list[FactionRelationshipRead]
    created_at: datetime


class WorldStateRead(BaseModel):
    campaign_id: uuid.UUID
    world_revision: int
    narrative_time_minutes: int
    location: LocationRead
    scene: SceneRead
    present_npcs: list[NPCRead]
    facts: list[WorldFactRead]
    quests: list[QuestRead]
    decisions: list[DecisionRead]
    factions: list[FactionRead]


class HPDelta(BaseModel):
    type: Literal["hp_delta"]
    amount: int = Field(ge=-999, le=999)
    reason: ShortText


class MoveLocation(BaseModel):
    type: Literal["move_location"]
    location_name: ShortText
    description: str | None = Field(default=None, max_length=2000)


class NPCIntroduce(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["npc_introduce"]
    name: NPCName
    public_description: str | None = Field(default=None, max_length=2000)


class NPCArrive(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["npc_arrive"]
    npc_id: uuid.UUID


class NPCDepart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["npc_depart"]
    npc_id: uuid.UUID


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


class QuestObjectiveCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective_key: StableKey
    title: ShortText
    description: str | None = Field(default=None, max_length=2000)
    status: Literal["pending", "active"] = "pending"


class QuestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["quest_create"]
    quest_key: StableKey
    title: ShortText
    summary: str | None = Field(default=None, max_length=2000)
    objectives: list[QuestObjectiveCreate] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def unique_objective_keys(self) -> "QuestCreate":
        keys = [objective.objective_key for objective in self.objectives]
        if len(keys) != len(set(keys)):
            raise ValueError("Quest objective keys must be unique")
        return self


class QuestTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["quest_transition"]
    quest_id: uuid.UUID
    expected_revision: int = Field(ge=0)
    status: Literal["completed", "failed", "abandoned"]


class QuestObjectiveTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["quest_objective_transition"]
    objective_id: uuid.UUID
    expected_revision: int = Field(ge=0)
    status: Literal["active", "completed", "failed", "skipped"]


class DecisionFactConsequence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["record_fact"]
    fact_type: WorldFactType
    subject_npc_id: uuid.UUID | None = None
    value: NarrativeText


class DecisionQuestConsequence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["transition_quest"]
    quest_id: uuid.UUID
    expected_revision: int = Field(ge=0)
    status: Literal["completed", "failed", "abandoned"]


class DecisionObjectiveConsequence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["transition_objective"]
    objective_id: uuid.UUID
    expected_revision: int = Field(ge=0)
    status: Literal["active", "completed", "failed", "skipped"]


DecisionConsequence = Annotated[
    DecisionFactConsequence | DecisionQuestConsequence | DecisionObjectiveConsequence,
    Field(discriminator="type"),
]


class DecisionOptionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_key: StableKey
    label: ShortText
    description: str | None = Field(default=None, max_length=2000)
    consequences: list[DecisionConsequence] = Field(default_factory=list, max_length=10)


class DecisionOpen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["decision_open"]
    decision_key: StableKey
    prompt: NarrativeText
    options: list[DecisionOptionCreate] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def unique_option_keys(self) -> "DecisionOpen":
        keys = [option.option_key for option in self.options]
        if len(keys) != len(set(keys)):
            raise ValueError("Decision option keys must be unique")
        return self


class FactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["faction_create"]
    faction_key: StableKey
    name: ShortText
    description: str | None = Field(default=None, max_length=2000)


class FactionAttitudeSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["faction_attitude_set"]
    faction_id: uuid.UUID
    expected_revision: int | None = Field(default=None, ge=0)
    attitude: Literal["friendly", "neutral", "wary", "hostile"]


class FactionMembershipSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["faction_membership_set"]
    faction_id: uuid.UUID
    member_type: Literal["character", "npc"]
    member_id: uuid.UUID
    expected_revision: int | None = Field(default=None, ge=0)
    membership: Literal["member", "associate", "former_member"]


class NarrativeTimeAdvance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["narrative_time_advance"]
    minutes: int = Field(ge=1, le=10_080)
    reason: ShortText


StateChange = Annotated[
    HPDelta
    | MoveLocation
    | NPCIntroduce
    | NPCArrive
    | NPCDepart
    | InventoryChange
    | NPCAttitudeSet
    | RelationshipNoteAdd
    | PromiseRecord
    | DiscoveryRecord
    | ClueRecord
    | WorldFactSupersede
    | WorldFactReveal
    | QuestCreate
    | QuestTransition
    | QuestObjectiveTransition
    | DecisionOpen
    | FactionCreate
    | FactionAttitudeSet
    | FactionMembershipSet
    | NarrativeTimeAdvance,
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
    decision_id: uuid.UUID | None = None
    decision_option_key: StableKey | None = None

    @model_validator(mode="after")
    def complete_decision_choice(self) -> "TurnExecutionCreate":
        if (self.decision_id is None) != (self.decision_option_key is None):
            raise ValueError("decision_id and decision_option_key must be provided together")
        return self


class TurnExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    command_id: uuid.UUID
    campaign_id: uuid.UUID
    sequence: int
    player_action: str
    actor_character_id: uuid.UUID | None
    target_npc_id: uuid.UUID | None
    decision_id: uuid.UUID | None
    decision_option_key: str | None
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


class CombatCell(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: int = Field(ge=0, le=39)
    y: int = Field(ge=0, le=39)


class PartyCombatantCreate(CombatCell):
    character_id: uuid.UUID


class EnemyCombatantCreate(CombatCell):
    monster_definition_id: StableKey
    instance_name: NPCName


class CombatEncounterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    expected_world_revision: int = Field(ge=0)
    scene_id: uuid.UUID
    combat_catalog_id: str = Field(default="srd-5.2.1-combat-v1", max_length=100)
    grid_width: int = Field(default=12, ge=2, le=40)
    grid_height: int = Field(default=12, ge=2, le=40)
    party: list[PartyCombatantCreate] = Field(min_length=2, max_length=4)
    enemies: list[EnemyCombatantCreate] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def validate_unique_placements(self) -> "CombatEncounterCreate":
        character_ids = [item.character_id for item in self.party]
        if len(character_ids) != len(set(character_ids)):
            raise ValueError("party character IDs must be unique")
        cells = [(item.x, item.y) for item in [*self.party, *self.enemies]]
        if len(cells) != len(set(cells)):
            raise ValueError("combatant starting cells must be unique")
        if any(x >= self.grid_width or y >= self.grid_height for x, y in cells):
            raise ValueError("combatant starting cells must be inside the encounter grid")
        return self


class CombatStartCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    expected_encounter_revision: int = Field(ge=0)


class CombatTieResolutionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    expected_encounter_revision: int = Field(ge=0)
    ordered_combatant_ids: list[uuid.UUID] = Field(min_length=2, max_length=12)

    @model_validator(mode="after")
    def validate_unique_order(self) -> "CombatTieResolutionCreate":
        if len(self.ordered_combatant_ids) != len(set(self.ordered_combatant_ids)):
            raise ValueError("ordered combatant IDs must be unique")
        return self


class CombatantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    side: Literal["party", "enemy"]
    character_id: uuid.UUID | None
    monster_definition_id: str | None
    instance_name: str
    max_hp: int
    hp: int
    temporary_hp: int
    armor_class: int
    speed_feet: int
    position_x: int
    position_y: int
    initiative_modifier: int
    initiative_dice_faces: list[int] | None
    initiative_selected_die: int | None
    initiative_total: int | None
    initiative_order: int | None
    reaction_available: bool
    state: str
    revision: int


class CombatInitiativeTieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    initiative_total: int
    participant_ids: list[uuid.UUID]
    decided_order: list[uuid.UUID] | None
    status: Literal["pending", "resolved"]


class CombatEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sequence: int
    event_type: str
    visibility: Literal["player", "dm_only"]
    payload: dict
    created_at: datetime


class CombatTurnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    combatant_id: uuid.UUID
    round_number: int
    turn_index: int
    status: Literal["active", "completed"]
    movement_allowance_feet: int
    movement_spent_feet: int
    action_available: bool
    bonus_action_available: bool
    free_interaction_available: bool
    disengaged: bool
    started_encounter_revision: int
    completed_encounter_revision: int | None


class CombatEffectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_combatant_id: uuid.UUID
    target_combatant_id: uuid.UUID
    effect_id: str
    stacking_key: str
    status: Literal["active", "expired"]
    starts_round: int
    expires_on_source_turn_start: bool
    ended_round: int | None


class CombatReactionWindowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mover_combatant_id: uuid.UUID
    reactor_combatant_id: uuid.UUID
    round_number: int
    from_x: int
    from_y: int
    to_x: int
    to_y: int
    status: Literal["pending", "passed", "opportunity_attack_pending"]
    response: Literal["pass", "opportunity_attack"] | None
    opened_encounter_revision: int
    resolved_encounter_revision: int | None


class CombatEncounterRead(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    scene_id: uuid.UUID
    ruleset_release_id: str
    character_state_catalog_id: str
    combat_catalog_id: str
    combat_catalog_sha256: str
    resolver_version: str
    status: Literal["setup", "tie_pending", "active", "completed", "cancelled"]
    revision: int
    grid_width: int
    grid_height: int
    round_number: int
    active_turn_index: int | None
    combatants: list[CombatantRead]
    initiative_ties: list[CombatInitiativeTieRead]
    current_turn: CombatTurnRead | None = None
    effects: list[CombatEffectRead] = Field(default_factory=list)
    reaction_windows: list[CombatReactionWindowRead] = Field(default_factory=list)
    events: list[CombatEventRead]
    created_at: datetime


class CombatReplayRead(BaseModel):
    encounter_id: uuid.UUID
    equivalent: bool
    replayed_initiative_order: list[uuid.UUID]
    stored_initiative_order: list[uuid.UUID]
    encounter: CombatEncounterRead


class CombatMoveCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    actor_combatant_id: uuid.UUID
    expected_encounter_revision: int = Field(ge=0)
    expected_combatant_revision: int = Field(ge=0)
    path: list[CombatCell] = Field(min_length=1, max_length=40)

    @model_validator(mode="after")
    def reject_repeated_cells(self) -> "CombatMoveCreate":
        cells = [(cell.x, cell.y) for cell in self.path]
        if len(cells) != len(set(cells)):
            raise ValueError("movement path cannot repeat a cell")
        return self


class CombatActionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    actor_combatant_id: uuid.UUID
    expected_encounter_revision: int = Field(ge=0)
    expected_combatant_revision: int = Field(ge=0)
    action: Literal["dash", "disengage", "dodge"]


class CombatReactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    reactor_combatant_id: uuid.UUID
    expected_encounter_revision: int = Field(ge=0)
    expected_combatant_revision: int = Field(ge=0)
    response: Literal["pass", "opportunity_attack"]


class CombatEndTurnCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: uuid.UUID
    actor_combatant_id: uuid.UUID
    expected_encounter_revision: int = Field(ge=0)
    expected_combatant_revision: int = Field(ge=0)


class HealthRead(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]
    environment: str
