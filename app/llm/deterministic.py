from typing import Any

from app.schemas import DMTurnOutput
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

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput:
        location = context["location"]["name"]
        return DMTurnOutput(
            narration=(
                f"At {location}, the world responds to your choice: {player_action.strip()} "
                "The next moment is yours to shape."
            )
        )
