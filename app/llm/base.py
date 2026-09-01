from typing import Any, Protocol

from app.schemas import DMTurnOutput
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
