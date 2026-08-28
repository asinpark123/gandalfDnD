from typing import Any

from app.schemas import DMTurnOutput


class DeterministicDMProvider:
    """Offline provider for development, tests, and persistence checks."""

    provider_name = "deterministic"
    model_name = None

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput:
        location = context["location"]["name"]
        return DMTurnOutput(
            narration=(
                f"At {location}, the world responds to your choice: {player_action.strip()} "
                "The next moment is yours to shape."
            )
        )
