from functools import lru_cache

from app.config import get_settings
from app.llm.base import DMProvider, TurnInterpretationProvider, TurnNarrationProvider
from app.llm.deterministic import DeterministicDMProvider
from app.llm.openai_provider import OpenAIDMProvider
from app.llm.openclaw_provider import OpenClawTurnProvider


@lru_cache
def get_dm_provider() -> DMProvider:
    settings = get_settings()
    if settings.llm_provider == "deterministic":
        return DeterministicDMProvider()
    if settings.llm_provider == "openclaw":
        raise RuntimeError("The OpenClaw provider supports only the authoritative two-stage API")
    if settings.openai_api_key is None or not settings.openai_api_key.get_secret_value():
        raise RuntimeError("GANDALF_OPENAI_API_KEY is required for the OpenAI provider")
    return OpenAIDMProvider(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.openai_model,
    )


@lru_cache
def get_turn_interpreter() -> TurnInterpretationProvider:
    settings = get_settings()
    if settings.llm_provider == "deterministic":
        return DeterministicDMProvider()
    if settings.llm_provider == "openclaw":
        return _openclaw_provider()
    raise RuntimeError("The direct OpenAI provider does not yet implement M2 interpretation")


@lru_cache
def get_turn_narrator() -> TurnNarrationProvider:
    settings = get_settings()
    if settings.llm_provider == "deterministic":
        return DeterministicDMProvider()
    if settings.llm_provider == "openclaw":
        return _openclaw_provider()
    raise RuntimeError("The direct OpenAI provider does not yet implement M2 narration")


@lru_cache
def _openclaw_provider() -> OpenClawTurnProvider:
    settings = get_settings()
    token = (
        settings.openclaw_gateway_token.get_secret_value()
        if settings.openclaw_gateway_token is not None
        else ""
    )
    if not token:
        raise RuntimeError("GANDALF_OPENCLAW_GATEWAY_TOKEN is required for the OpenClaw provider")
    return OpenClawTurnProvider(
        base_url=settings.openclaw_base_url,
        gateway_token=token,
        agent_id=settings.openclaw_agent_id,
        model=settings.openclaw_model,
        gm_style=settings.openclaw_gm_style,
        timeout_seconds=settings.turn_stage_timeout_seconds,
    )
