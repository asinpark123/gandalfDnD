from typing import Any

from app.schemas import (
    DMTurnOutput,
    HPDelta,
    InventoryChange,
    MoveLocation,
    RuleResolutionRead,
    TurnNarrationOutput,
)
from app.turn_interpretation import (
    D20ResolutionRequest,
    D20TestIntent,
    NarrativeIntent,
    TurnIntent,
)


class DeterministicDMProvider:
    """Offline provider for development, tests, and persistence checks."""

    provider_name = "deterministic"
    model_name = None
    interpretation_prompt_version = "deterministic-intent-1.0.0"
    narration_prompt_version = "deterministic-narration-1.0.0"

    def interpret_action(self, context: dict[str, Any], player_action: str) -> TurnIntent:
        """Provide stable offline adjudications for M2 development fixtures."""
        normalized = player_action.strip().casefold()
        if "resist" in normalized and ("poison" in normalized or "toxin" in normalized):
            return D20TestIntent(
                type="d20_test",
                summary="The acting character attempts to resist a poison.",
                resolution=D20ResolutionRequest(
                    resolution_type="saving_throw",
                    ability="constitution",
                    difficulty_class=13,
                    purpose="Resist the poison's effects",
                ),
            )
        if "climb" in normalized:
            return D20TestIntent(
                type="d20_test",
                summary="The acting character attempts a difficult climb.",
                resolution=D20ResolutionRequest(
                    resolution_type="ability_check",
                    ability="strength",
                    skill="athletics",
                    difficulty_class=12,
                    purpose="Complete the difficult climb",
                ),
            )
        if "sneak" in normalized or "move quietly" in normalized:
            return D20TestIntent(
                type="d20_test",
                summary="The acting character attempts to move without being noticed.",
                resolution=D20ResolutionRequest(
                    resolution_type="ability_check",
                    ability="dexterity",
                    skill="stealth",
                    difficulty_class=12,
                    purpose="Move without being noticed",
                ),
            )
        return NarrativeIntent(
            type="narrative",
            summary="The action does not require a check or saving throw in this fixture.",
        )

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: RuleResolutionRead | None,
    ) -> TurnNarrationOutput:
        """Narrate stored outcomes and propose bounded M2 development-fixture changes."""
        normalized = player_action.strip().casefold()
        resolution_id = resolution.id if resolution else None
        outcome = resolution.outcome if resolution else None
        if resolution is not None:
            if resolution.outcome == "success":
                narration = "The attempt succeeds, and the character gains the intended position."
                changes = (
                    [
                        MoveLocation(
                            type="move_location",
                            location_name="Wall Top",
                            description="The top of the difficult stone wall.",
                        )
                    ]
                    if "climb" in normalized
                    else []
                )
            else:
                narration = "The attempt fails, and the character suffers a minor setback."
                changes = (
                    [HPDelta(type="hp_delta", amount=-2, reason="Minor fall from the wall")]
                    if "climb" in normalized
                    else []
                )
            return TurnNarrationOutput(
                narration=narration,
                resolution_id=resolution_id,
                acknowledged_outcome=outcome,
                state_changes=changes,
            )
        if "old tower" in normalized:
            return TurnNarrationOutput(
                narration="The party travels along the old road and arrives at the Old Tower.",
                state_changes=[
                    MoveLocation(
                        type="move_location",
                        location_name="Old Tower",
                        description="A weathered tower overlooking the old road.",
                    )
                ],
            )
        if "javelin" in normalized and ("use" in normalized or "leave" in normalized):
            return TurnNarrationOutput(
                narration="The character uses a Javelin to leave a clear marker on the trail.",
                state_changes=[
                    InventoryChange(
                        type="inventory_change",
                        item_name="Javelin",
                        quantity_delta=-1,
                        reason="Used as a trail marker",
                    )
                ],
            )
        return TurnNarrationOutput(
            narration="The innkeeper returns the greeting and waits to hear what comes next."
        )

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput:
        location = context["location"]["name"]
        return DMTurnOutput(
            narration=(
                f"At {location}, the world responds to your choice: {player_action.strip()} "
                "The next moment is yours to shape."
            )
        )
