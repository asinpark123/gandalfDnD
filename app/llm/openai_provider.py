import json
from typing import Any

from openai import OpenAI

from app.schemas import DMTurnOutput

_DM_INSTRUCTIONS = """You are GandalfDnD's solo dungeon master for a Phase 0 feasibility test.
Return a concise, vivid continuation using the supplied canonical state. The database state is
authoritative. Propose only state changes that directly follow from the player's action. Never
invent or request dice; checks and saves use the separate authoritative turn-execution pipeline.
Never reduce HP below zero, increase it above max_hp, or remove inventory the character does not
possess. Do not expose hidden campaign information. The application will validate every proposed
change before it commits anything.
"""


class OpenAIDMProvider:
    provider_name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        self.model_name = model
        self._client = OpenAI(api_key=api_key)

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput:
        response = self._client.responses.parse(
            model=self.model_name,
            instructions=_DM_INSTRUCTIONS,
            input=json.dumps({"canonical_state": context, "player_action": player_action}),
            text_format=DMTurnOutput,
            store=False,
        )
        if response.output_parsed is None:
            raise RuntimeError("The model did not return a valid structured DM turn")
        return response.output_parsed
