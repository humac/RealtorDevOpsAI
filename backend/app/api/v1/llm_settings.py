"""LLM settings endpoints for switching AI providers."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.llm_settings import (
    LLMProvider,
    LLMProviderConfig,
    LLMSettingsResponse,
    LLMSettingsUpdate,
)

router = APIRouter()

PROVIDER_MODELS: dict[LLMProvider, list[str]] = {
    LLMProvider.openai: ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"],
    LLMProvider.anthropic: [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-haiku-4-20250414",
    ],
    LLMProvider.google: [
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
    ],
    LLMProvider.ollama: ["llama3", "llama3.1", "mistral", "mixtral", "codellama", "gemma2"],
}


def _get_model_for_provider(provider: LLMProvider) -> str:
    if provider == LLMProvider.openai:
        return settings.openai_model
    elif provider == LLMProvider.anthropic:
        return settings.anthropic_model
    elif provider == LLMProvider.google:
        return settings.google_model
    else:
        return settings.ollama_model


def _is_configured(provider: LLMProvider) -> bool:
    if provider == LLMProvider.openai:
        return bool(settings.openai_api_key)
    elif provider == LLMProvider.anthropic:
        return bool(settings.anthropic_api_key)
    elif provider == LLMProvider.google:
        return bool(settings.google_api_key)
    else:
        return bool(settings.ollama_base_url)


PROVIDER_LABELS = {
    LLMProvider.openai: "OpenAI",
    LLMProvider.anthropic: "Anthropic",
    LLMProvider.google: "Google",
    LLMProvider.ollama: "Ollama Cloud",
}


@router.get("", response_model=LLMSettingsResponse)
async def get_llm_settings():
    """Get current LLM provider settings."""
    providers = []
    for provider in LLMProvider:
        providers.append(
            LLMProviderConfig(
                provider=provider,
                label=PROVIDER_LABELS[provider],
                model=_get_model_for_provider(provider),
                available_models=PROVIDER_MODELS[provider],
                is_configured=_is_configured(provider),
            )
        )
    return LLMSettingsResponse(
        active_provider=LLMProvider(settings.llm_provider),
        providers=providers,
    )


@router.put("", response_model=LLMSettingsResponse)
async def update_llm_settings(update: LLMSettingsUpdate):
    """Update the active LLM provider and optionally the model."""
    settings.llm_provider = update.provider.value

    if update.model:
        if update.provider == LLMProvider.openai:
            settings.openai_model = update.model
        elif update.provider == LLMProvider.anthropic:
            settings.anthropic_model = update.model
        elif update.provider == LLMProvider.google:
            settings.google_model = update.model
        elif update.provider == LLMProvider.ollama:
            settings.ollama_model = update.model

    return await get_llm_settings()
