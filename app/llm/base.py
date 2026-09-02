from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar

from app.schemas import DMTurnOutput, RuleResolutionRead, TurnNarrationOutput
from app.turn_interpretation import TurnIntent

OutputT = TypeVar("OutputT")


@dataclass(frozen=True)
class ProviderResult(Generic[OutputT]):
    """A typed provider output plus optional provider-reported token usage."""

    output: OutputT
    input_tokens: int | None = None
    output_tokens: int | None = None

    def __post_init__(self) -> None:
        if self.input_tokens is not None and self.input_tokens < 0:
            raise ValueError("input_tokens cannot be negative")
        if self.output_tokens is not None and self.output_tokens < 0:
            raise ValueError("output_tokens cannot be negative")


class ProviderTimeoutError(TimeoutError):
    """The provider operation exceeded its configured deadline."""


class ProviderConnectionError(ConnectionError):
    """The provider could not be reached."""


class ProviderRefusalError(RuntimeError):
    """The provider explicitly refused the requested structured operation."""


class ProviderEmptyOutputError(RuntimeError):
    """The provider completed without returning parsed structured output."""


class DMProvider(Protocol):
    provider_name: str
    model_name: str | None

    def generate_turn(self, context: dict[str, Any], player_action: str) -> DMTurnOutput: ...


class TurnInterpretationProvider(Protocol):
    provider_name: str
    model_name: str | None
    interpretation_prompt_version: str

    def interpret_action(
        self, context: dict[str, Any], player_action: str
    ) -> TurnIntent | ProviderResult[TurnIntent]: ...


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
    ) -> TurnNarrationOutput | ProviderResult[TurnNarrationOutput]: ...
