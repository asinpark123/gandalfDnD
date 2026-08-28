from typing import Any, Protocol

from app.schemas import DMTurnOutput


class DMProvider(Protocol):
    provider_name: str
    model_name: str | None

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput: ...
