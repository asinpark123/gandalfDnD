from typing import Any, Protocol

from app.schemas import DMTurnOutput, RuleResolutionRead, TurnNarrationOutput
from app.turn_interpretation import TurnIntent


class DMProvider(Protocol):
    provider_name: str
    model_name: str | None

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput: ...


class TurnInterpretationProvider(Protocol):
    provider_name: str
    model_name: str | None
    interpretation_prompt_version: str

    def interpret_action(self, context: dict[str, Any], player_action: str) -> TurnIntent: ...


class TurnNarrationProvider(Protocol):
    provider_name: str
    model_name: str | None
    narration_prompt_version: str

    def narrate_outcome(
        self,
        context: dict[str, Any],
        player_action: str,
        intent: TurnIntent,
        resolution: RuleResolutionRead | None,
    ) -> TurnNarrationOutput: ...
