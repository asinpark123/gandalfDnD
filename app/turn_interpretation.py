from typing import Annotated, Literal

from pydantic import Field, TypeAdapter, model_validator

from app.character_creation import AbilityName, StrictModel
from app.resolution import ReasonText, ResolutionType
from app.turn_errors import TurnProviderError


class NarrativeIntent(StrictModel):
    type: Literal["narrative"]
    summary: ReasonText


class D20ResolutionRequest(StrictModel):
    resolution_type: ResolutionType
    ability: AbilityName
    skill: str | None = Field(default=None, pattern=r"^[a-z][a-z_]{1,39}$")
    difficulty_class: int = Field(ge=1, le=100)
    purpose: ReasonText
    advantage_reasons: list[ReasonText] = Field(default_factory=list, max_length=10)
    disadvantage_reasons: list[ReasonText] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def validate_resolution_shape(self) -> "D20ResolutionRequest":
        if self.resolution_type == "saving_throw" and self.skill is not None:
            raise ValueError("saving throws cannot use a skill")
        return self


class D20TestIntent(StrictModel):
    type: Literal["d20_test"]
    summary: ReasonText
    resolution: D20ResolutionRequest


TurnIntent = Annotated[NarrativeIntent | D20TestIntent, Field(discriminator="type")]
TURN_INTENT_ADAPTER = TypeAdapter(TurnIntent)


def validate_turn_intent(value: object) -> TurnIntent:
    return TURN_INTENT_ADAPTER.validate_python(value)


class TurnInterpretationError(TurnProviderError):
    """A provider attempt failed before an authoritative resolution was created."""
