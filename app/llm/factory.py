from functools import lru_cache

from app.config import get_settings
from app.llm.base import DMProvider, TurnInterpretationProvider
from app.llm.deterministic import DeterministicDMProvider
from app.llm.openai_provider import OpenAIDMProvider


@lru_cache
def get_dm_provider() -> DMProvider:
    settings = get_settings()
    if settings.llm_provider == "deterministic":
        return DeterministicDMProvider()
    if settings.openai_api_key is None or not settings.openai_api_key.get_secret_value():
        raise RuntimeError("GANDALF_OPENAI_API_KEY is required for the OpenAI provider")
    return OpenAIDMProvider(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.openai_model,
    )


@lru_cache
def get_turn_interpreter() -> TurnInterpretationProvider:
    settings = get_settings()
    if settings.llm_provider != "deterministic":
        raise RuntimeError(
            "M2 interpretation is restricted to the deterministic provider until the M2.5 gate"
        )
    return DeterministicDMProvider()
