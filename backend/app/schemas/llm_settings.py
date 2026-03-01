"""Schemas for LLM provider settings."""

from enum import Enum

from pydantic import BaseModel


class LLMProvider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"
    ollama = "ollama"


class LLMProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""

    provider: LLMProvider
    label: str
    model: str
    available_models: list[str]
    is_configured: bool


class LLMSettingsResponse(BaseModel):
    """Current LLM settings."""

    active_provider: LLMProvider
    providers: list[LLMProviderConfig]


class LLMSettingsUpdate(BaseModel):
    """Request to update LLM settings."""

    provider: LLMProvider
    model: str | None = None
