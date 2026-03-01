from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "RealtorDevOpsAI"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/realtor_devops"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 3600

    # LLM Provider: "openai", "anthropic", "google", "ollama"
    llm_provider: str = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Google
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"

    # Ollama
    ollama_base_url: str = "https://cloud.ollama.com"
    ollama_api_key: str = ""
    ollama_model: str = "llama3"

    # External APIs
    ottawa_open_data_url: str = "https://open.ottawa.ca/api"
    geo_ottawa_wfs_url: str = "https://maps.ottawa.ca/geoottawa/services/wfs"
    geo_ottawa_wms_url: str = "https://maps.ottawa.ca/geoottawa/services/wms"

    # Mapbox
    mapbox_access_token: str = ""

    # Auth
    auth0_domain: str = ""
    auth0_api_audience: str = ""
    auth0_algorithms: list[str] = ["RS256"]

    # Rate Limiting
    rate_limit_per_minute: int = 60

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
